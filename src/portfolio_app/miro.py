from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any
from urllib import parse, request
from urllib.error import HTTPError, URLError

from portfolio_app.erd import ErdModel

try:
    import requests
except Exception:  # pragma: no cover - optional dependency in runtime
    requests = None  # type: ignore[assignment]


class MiroServiceError(RuntimeError):
    """Raised when Miro operations fail."""


@dataclass
class SyncOptions:
    clear_previous: bool = True
    app_tag: str = "portfolio_erd"


@dataclass
class BoardStatus:
    board_id: str
    ready: bool
    status: str
    detail: str = ""


class MiroErdService:
    def __init__(
        self,
        access_token: str | None = None,
        base_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        boards_registry_path: Path | str = "data/metadata/miro_boards.json",
    ) -> None:
        self.access_token = access_token or os.getenv("MIRO_ACCESS_TOKEN", "")
        self.base_url = (base_url or os.getenv("MIRO_API_BASE_URL", "https://api.miro.com/v2")).rstrip("/")
        self.client_id = client_id or os.getenv("MIRO_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("MIRO_CLIENT_SECRET", "")
        self.redirect_uri = redirect_uri or os.getenv("MIRO_REDIRECT_URI", "")
        self.boards_registry_path = Path(boards_registry_path)
        self.boards_registry_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def is_configured(self) -> bool:
        return bool(self.access_token)

    def validate_access_token(self) -> dict[str, Any]:
        if not self.access_token:
            return {"ok": False, "detail": "MIRO_ACCESS_TOKEN absent."}

        token_url = "https://api.miro.com/v1/oauth-token"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.access_token}",
        }
        if requests is not None:
            try:
                resp = requests.get(token_url, headers=headers, timeout=20)
                payload = resp.json() if resp.text else {}
                if resp.status_code >= 400:
                    return {"ok": False, "detail": f"HTTP {resp.status_code}", "payload": payload}
                return {"ok": True, "detail": "Token valide.", "payload": payload}
            except Exception as exc:
                return {"ok": False, "detail": f"Validation token impossible: {exc}"}

        try:
            out = self._request_raw("GET", token_url, body=None, bearer=True)
            return {"ok": True, "detail": "Token valide.", "payload": out}
        except Exception as exc:
            return {"ok": False, "detail": f"Validation token impossible: {exc}"}

    def build_oauth_authorize_url(self, state: str, scopes: list[str] | None = None) -> str:
        if not self.client_id or not self.redirect_uri:
            raise MiroServiceError("OAuth Miro non configuré (MIRO_CLIENT_ID / MIRO_REDIRECT_URI manquants).")
        scope = " ".join(scopes or ["boards:read", "boards:write"])
        query = parse.urlencode(
            {
                "response_type": "code",
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "scope": scope,
                "state": state,
            }
        )
        return f"https://miro.com/oauth/authorize?{query}"

    def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        if not self.client_id or not self.client_secret or not self.redirect_uri:
            raise MiroServiceError(
                "OAuth Miro incomplet: MIRO_CLIENT_ID, MIRO_CLIENT_SECRET et MIRO_REDIRECT_URI sont requis."
            )
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        return self._request_raw("POST", "https://api.miro.com/v1/oauth/token", body=body, bearer=False)

    def create_or_get_board(
        self,
        user_id: str,
        workspace_key: str,
        database_key: str,
    ) -> dict[str, str]:
        board_key = f"{user_id}:{workspace_key}:{database_key}"
        registry = self._load_registry()
        if board_key in registry:
            board = registry[board_key]
            return {"boardId": board["board_id"], "boardUrl": board["board_url"]}

        if not self.is_configured:
            raise MiroServiceError("MIRO_ACCESS_TOKEN absent. Synchronisation Miro indisponible.")

        payload = {"name": f"ERD | {database_key}"}
        resp = self._request("POST", "/boards", body=payload)
        board_id = str(resp.get("id", "")).strip()
        if not board_id:
            raise MiroServiceError("Création board Miro échouée: identifiant de board absent.")
        board_url = str(resp.get("viewLink") or resp.get("link") or f"https://miro.com/app/board/{board_id}/")

        registry[board_key] = {
            "board_id": board_id,
            "board_url": board_url,
            "workspace_key": workspace_key,
            "database_key": database_key,
        }
        self._save_registry(registry)
        return {"boardId": board_id, "boardUrl": board_url}

    def sync_erd_to_board(
        self,
        board_id: str,
        erd_model: ErdModel,
        options: SyncOptions | None = None,
    ) -> dict[str, Any]:
        if not self.is_configured:
            raise MiroServiceError("MIRO_ACCESS_TOKEN absent. Impossible de synchroniser le board.")

        sync_options = options or SyncOptions()

        if sync_options.clear_previous:
            self._clear_owned_items(board_id, app_tag=sync_options.app_tag)

        node_to_item_id: dict[str, str] = {}
        created_count = 0

        for node in erd_model.nodes:
            columns_lines: list[str] = []
            for col in node.columns:
                tags: list[str] = []
                if col.pk:
                    tags.append("PK")
                if col.fk:
                    tags.append("FK")
                suffix = f" [{' / '.join(tags)}]" if tags else ""
                nullable = " (nullable)" if col.nullable else ""
                columns_lines.append(f"{col.name} : {col.type}{suffix}{nullable}")
            content = f"<b>{node.table_name}</b><br>" + "<br>".join(columns_lines)

            shape_payload = {
                "data": {"shape": "rectangle", "content": content},
                "position": {"x": float(node.x), "y": float(node.y)},
                "geometry": {"width": float(node.width), "height": float(node.height)},
                "style": {
                    "fillColor": "light_yellow",
                    "borderColor": "#1f2937",
                    "fontFamily": "open_sans",
                    "fontSize": "12",
                    "textAlign": "left",
                },
                "metadata": {
                    "portfolio_app": {
                        "app_tag": sync_options.app_tag,
                        "kind": "erd_node",
                        "table": node.table_name,
                    }
                },
            }
            shape_resp = self._request("POST", f"/boards/{board_id}/shapes", body=shape_payload)
            item_id = str(shape_resp.get("id", "")).strip()
            if item_id:
                node_to_item_id[node.id] = item_id
                created_count += 1

        for edge in erd_model.edges:
            start_id = node_to_item_id.get(edge.from_table)
            end_id = node_to_item_id.get(edge.to_table)
            if not start_id or not end_id:
                continue
            connector_payload = {
                "startItem": {"id": start_id},
                "endItem": {"id": end_id},
                "style": {
                    "strokeColor": "#6b7280",
                    "strokeWidth": "1",
                    "strokeStyle": "normal" if getattr(edge, "relation_kind", "FK") == "PK" else "dashed",
                },
                "captions": [
                    {
                        "content": f"[{getattr(edge, 'relation_kind', 'FK')}] {edge.from_column} -> {edge.to_column}",
                        "position": "50%",
                    }
                ],
                "metadata": {
                    "portfolio_app": {
                        "app_tag": sync_options.app_tag,
                        "kind": "erd_edge",
                        "edge": edge.id,
                    }
                },
            }
            try:
                self._request("POST", f"/boards/{board_id}/connectors", body=connector_payload)
                created_count += 1
            except MiroServiceError:
                # Connector endpoint can be restricted by plan/permissions.
                continue

        return {"boardId": board_id, "itemCount": created_count}

    def get_embed_info(self, board_id: str) -> dict[str, str]:
        embed_url = (
            f"https://miro.com/app/live-embed/{board_id}/"
            "?autoplay=true&embedMode=view_only_without_ui"
        )
        return {"embedUrl": embed_url}

    def get_board_status(self, board_id: str) -> BoardStatus:
        if not self.is_configured:
            return BoardStatus(
                board_id=board_id,
                ready=False,
                status="not_configured",
                detail="MIRO_ACCESS_TOKEN absent.",
            )
        try:
            self._request("GET", f"/boards/{board_id}")
            return BoardStatus(board_id=board_id, ready=True, status="ready", detail="Board accessible.")
        except MiroServiceError as exc:
            return BoardStatus(board_id=board_id, ready=False, status="error", detail=str(exc))

    def _clear_owned_items(self, board_id: str, app_tag: str) -> None:
        items = self._list_items(board_id)
        for item in items:
            item_id = str(item.get("id", "")).strip()
            if not item_id:
                continue
            metadata = item.get("metadata") or {}
            app_meta = metadata.get("portfolio_app") if isinstance(metadata, dict) else None
            if not isinstance(app_meta, dict):
                continue
            if app_meta.get("app_tag") != app_tag:
                continue
            try:
                self._request("DELETE", f"/boards/{board_id}/items/{item_id}")
            except MiroServiceError:
                continue

    def _list_items(self, board_id: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            suffix = f"?limit=50{f'&cursor={parse.quote(cursor)}' if cursor else ''}"
            resp = self._request("GET", f"/boards/{board_id}/items{suffix}")
            data = resp.get("data", [])
            if isinstance(data, list):
                out.extend([d for d in data if isinstance(d, dict)])
            cursor = resp.get("cursor")
            if not cursor:
                break
        return out

    def _request(self, method: str, endpoint: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.access_token:
            raise MiroServiceError("MIRO_ACCESS_TOKEN manquant.")
        url = f"{self.base_url}{endpoint}"
        return self._request_raw(method, url, body=body, bearer=True)

    def _request_raw(
        self,
        method: str,
        url: str,
        body: dict[str, Any] | None = None,
        bearer: bool = True,
    ) -> dict[str, Any]:
        data_bytes: bytes | None = None
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if bearer and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        if body is not None:
            data_bytes = json.dumps(body).encode("utf-8")

        req = request.Request(url=url, data=data_bytes, method=method.upper(), headers=headers)
        try:
            with request.urlopen(req, timeout=45) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise MiroServiceError(f"Miro API HTTP {exc.code}: {detail or exc.reason}") from exc
        except URLError as exc:
            raise MiroServiceError(f"Miro API inaccessible: {exc.reason}") from exc
        except Exception as exc:
            raise MiroServiceError(f"Erreur Miro API: {exc}") from exc

    def _load_registry(self) -> dict[str, dict[str, str]]:
        if not self.boards_registry_path.exists():
            return {}
        try:
            raw = self.boards_registry_path.read_text(encoding="utf-8")
            payload = json.loads(raw)
            if isinstance(payload, dict):
                return payload  # type: ignore[return-value]
            return {}
        except Exception:
            return {}

    def _save_registry(self, payload: dict[str, dict[str, str]]) -> None:
        self.boards_registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.boards_registry_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
