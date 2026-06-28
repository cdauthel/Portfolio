import datetime as dt

import requests

import app.main as main


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        if not self.ok:
            raise requests.HTTPError(f"HTTP {self.status_code}")


def _feedback() -> dict:
    return {
        "reference": "PF-TEST",
        "category": "Recommandation technique",
        "priority": "Normale",
        "page": "Accueil",
        "title": "Test Jira",
        "description": "Validation automatique de la connexion Jira.",
        "reproduction_steps": "",
        "expected_result": "Un ticket est créé.",
        "name": "Test",
        "email": "test@example.com",
        "organization": "",
        "allow_follow_up": False,
        "submitted_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def test_jira_scoped_gateway_fallback(monkeypatch) -> None:
    secrets = {
        "JIRA_BASE_URL": "https://portfolio-test.atlassian.net",
        "JIRA_EMAIL": "owner@example.com",
        "JIRA_API_TOKEN": "secret-token",
        "JIRA_PROJECT_KEY": "PORT",
        "JIRA_DEFAULT_ISSUE_TYPE": "Task",
    }
    monkeypatch.setattr(
        main,
        "_secret_value",
        lambda *names, default=None: next(
            (secrets[name] for name in names if name in secrets),
            default,
        ),
    )
    monkeypatch.setattr(
        main.requests,
        "get",
        lambda url, **_kwargs: _FakeResponse(
            200,
            {"cloudId": "cloud-123"},
        ),
    )
    called_urls: list[str] = []

    def fake_post(url: str, **_kwargs):
        called_urls.append(url)
        if url.startswith("https://portfolio-test.atlassian.net"):
            return _FakeResponse(401, {}, '{"message":"Unauthorized"}')
        return _FakeResponse(201, {"key": "PORT-42"})

    monkeypatch.setattr(main.requests, "post", fake_post)

    ok, status, issue_url = main._create_feedback_jira_issue(_feedback())

    assert ok is True
    assert status == "Ticket Jira PORT-42."
    assert issue_url == "https://portfolio-test.atlassian.net/browse/PORT-42"
    assert any("/ex/jira/cloud-123/rest/api/3/issue" in url for url in called_urls)


def test_jira_detects_project_issue_type_after_bad_request(monkeypatch) -> None:
    secrets = {
        "JIRA_BASE_URL": "https://portfolio-test.atlassian.net",
        "JIRA_EMAIL": "owner@example.com",
        "JIRA_API_TOKEN": "secret-token",
        "JIRA_PROJECT_KEY": "PORT",
        "JIRA_DEFAULT_ISSUE_TYPE": "Task",
    }
    monkeypatch.setattr(
        main,
        "_secret_value",
        lambda *names, default=None: next(
            (secrets[name] for name in names if name in secrets),
            default,
        ),
    )

    def fake_get(url: str, **_kwargs):
        if url.endswith("/_edge/tenant_info"):
            return _FakeResponse(200, {"cloudId": "cloud-123"})
        return _FakeResponse(
            200,
            {"issueTypes": [{"id": "10001", "name": "Task", "subtask": False}]},
        )

    submitted_payloads: list[dict] = []

    def fake_post(_url: str, **kwargs):
        submitted_payloads.append(kwargs["json"])
        issue_type = kwargs["json"]["fields"]["issuetype"]
        if issue_type == {"id": "10001"}:
            return _FakeResponse(201, {"key": "PORT-43"})
        return _FakeResponse(400, {}, '{"errors":{"issuetype":"Issue type invalid"}}')

    monkeypatch.setattr(main.requests, "get", fake_get)
    monkeypatch.setattr(main.requests, "post", fake_post)

    ok, status, _ = main._create_feedback_jira_issue(_feedback())

    assert ok is True
    assert status == "Ticket Jira PORT-43."
    assert any(payload["fields"]["issuetype"] == {"id": "10001"} for payload in submitted_payloads)
