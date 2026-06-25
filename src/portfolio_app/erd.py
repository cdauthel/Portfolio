from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from math import ceil, sqrt
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


DEFAULT_PRIMARY_KEY_HINTS: dict[str, set[str]] = {
    "stores": {"store_id"},
    "products": {"product_id"},
    "customers": {"customer_id"},
    "orders": {"order_id"},
    "order_items": {"order_id", "product_id"},
    "promotions": {"promo_id"},
    "weather_store_day": {"store_id", "date"},
    "events_city_day": {"event_id"},
    "inventory_store_day": {"store_id", "product_id", "date"},
    "returns": {"return_id"},
    "assets": {"asset_id"},
    "prices_daily": {"date", "asset_id"},
    "macro": {"date"},
    "portfolios_daily": {"portfolio_id", "date", "asset_id"},
    "trades": {"trade_id"},
    "features_store_daily": {"store_id", "date"},
    "features_customer": {"customer_id"},
    "features_product": {"product_id"},
    "features_finance": {"asset_id"},
}

DEFAULT_RELATION_HINTS: dict[str, dict[str, str]] = {
    "orders": {"customer_id": "customers", "store_id": "stores", "promo_id": "promotions"},
    "order_items": {"order_id": "orders", "product_id": "products"},
    "weather_store_day": {"store_id": "stores"},
    "inventory_store_day": {"store_id": "stores", "product_id": "products"},
    "returns": {"order_id": "orders", "product_id": "products"},
    "prices_daily": {"asset_id": "assets"},
    "portfolios_daily": {"asset_id": "assets"},
    "trades": {"asset_id": "assets"},
    "features_store_daily": {"store_id": "stores"},
    "features_customer": {"customer_id": "customers"},
    "features_product": {"product_id": "products"},
    "features_finance": {"asset_id": "assets"},
}


@dataclass
class ColumnDef:
    name: str
    data_type: str
    nullable: bool
    is_primary_key: bool = False
    is_foreign_key: bool = False


@dataclass
class ForeignKeyDef:
    source_table: str
    source_column: str
    target_table: str
    target_column: str


@dataclass
class IndexDef:
    name: str
    columns: list[str]
    unique: bool = False


@dataclass
class TableDef:
    name: str
    columns: list[ColumnDef]
    primary_key: list[str] = field(default_factory=list)
    foreign_keys: list[ForeignKeyDef] = field(default_factory=list)
    indexes: list[IndexDef] = field(default_factory=list)


@dataclass
class DatabaseSchema:
    connection_id: str
    database: str
    schema: str | None
    tables: list[TableDef]


@dataclass
class ErdColumn:
    name: str
    type: str
    nullable: bool
    pk: bool = False
    fk: bool = False


@dataclass
class ErdNode:
    id: str
    table_name: str
    columns: list[ErdColumn]
    x: float = 0.0
    y: float = 0.0
    width: float = 360.0
    height: float = 180.0


@dataclass
class ErdEdge:
    id: str
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relation_kind: str = "FK"


@dataclass
class ErdModel:
    nodes: list[ErdNode]
    edges: list[ErdEdge]
    meta: dict[str, Any]


class ErdIntrospectionError(RuntimeError):
    """Raised when schema introspection fails."""


def discover_duckdb_files(search_roots: list[Path | str] | None = None) -> list[Path]:
    roots = search_roots or [Path("data/processed"), Path(".")]
    files: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        root_path = Path(root)
        if not root_path.exists():
            continue
        for db_file in sorted(root_path.glob("*.duckdb")):
            resolved = db_file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            files.append(resolved)
    return files


def list_database_schemas(db_path: Path | str) -> list[str]:
    path = Path(db_path)
    if not path.exists():
        raise ErdIntrospectionError(f"Base introuvable: {path}")
    with duckdb.connect(str(path), read_only=True) as conn:
        rows = conn.execute(
            """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
            ORDER BY schema_name
            """
        ).fetchall()
    schemas = [str(row[0]) for row in rows if row and row[0]]
    return schemas or ["main"]


def _resolve_database_path(database_name: str, db_path: Path | str | None = None) -> Path:
    if db_path is not None:
        path = Path(db_path)
        if path.exists():
            return path.resolve()
        raise ErdIntrospectionError(f"Base introuvable: {path}")

    candidates = discover_duckdb_files()
    if not candidates:
        raise ErdIntrospectionError("Aucune base DuckDB détectée.")

    for candidate in candidates:
        if candidate.stem == database_name or candidate.name == database_name:
            return candidate

    # fallback: nom direct sur disque
    as_path = Path(database_name)
    if as_path.exists():
        return as_path.resolve()

    raise ErdIntrospectionError(f"Base '{database_name}' introuvable.")


def _fetch_declared_pk(conn: duckdb.DuckDBPyConnection, schema_name: str) -> dict[str, list[str]]:
    try:
        rows = conn.execute(
            """
            SELECT
                kcu.table_name,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
             AND tc.table_name = kcu.table_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = ?
            ORDER BY kcu.table_name, kcu.ordinal_position
            """,
            [schema_name],
        ).fetchall()
    except Exception:
        return {}

    out: dict[str, list[str]] = {}
    for table_name, col_name in rows:
        table = str(table_name)
        out.setdefault(table, []).append(str(col_name))
    return out


def _fetch_declared_fk(conn: duckdb.DuckDBPyConnection, schema_name: str) -> list[ForeignKeyDef]:
    try:
        rows = conn.execute(
            """
            SELECT
                kcu.table_name AS source_table,
                kcu.column_name AS source_column,
                ccu.table_name AS target_table,
                ccu.column_name AS target_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
             AND tc.table_name = kcu.table_name
            JOIN information_schema.constraint_column_usage ccu
              ON tc.constraint_name = ccu.constraint_name
             AND tc.table_schema = ccu.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = ?
            ORDER BY source_table, source_column
            """,
            [schema_name],
        ).fetchall()
    except Exception:
        return []

    fks: list[ForeignKeyDef] = []
    for src_table, src_col, tgt_table, tgt_col in rows:
        fks.append(
            ForeignKeyDef(
                source_table=str(src_table),
                source_column=str(src_col),
                target_table=str(tgt_table),
                target_column=str(tgt_col),
            )
        )
    return fks


def _infer_primary_keys(
    table_name: str,
    column_names: list[str],
    declared_pk: dict[str, list[str]],
    pk_hints: dict[str, set[str]],
) -> list[str]:
    if table_name in declared_pk and declared_pk[table_name]:
        return declared_pk[table_name]

    hinted = [c for c in column_names if c in pk_hints.get(table_name, set())]
    if hinted:
        return hinted

    if "id" in column_names:
        return ["id"]

    singular = table_name[:-1] if table_name.endswith("s") else table_name
    candidate = f"{singular}_id"
    if candidate in column_names:
        return [candidate]

    generic_ids = [c for c in column_names if c.endswith("_id")]
    if len(generic_ids) == 1:
        return generic_ids

    return []


def _infer_foreign_keys(
    tables: list[str],
    columns_by_table: dict[str, list[str]],
    primary_keys_by_table: dict[str, list[str]],
    declared_fks: list[ForeignKeyDef],
    relation_hints: dict[str, dict[str, str]],
) -> list[ForeignKeyDef]:
    fk_set: set[tuple[str, str, str, str]] = set()

    for fk in declared_fks:
        fk_set.add((fk.source_table, fk.source_column, fk.target_table, fk.target_column))

    pk_reverse_index: dict[str, list[str]] = {}
    for table_name, pk_cols in primary_keys_by_table.items():
        for pk_col in pk_cols:
            pk_reverse_index.setdefault(pk_col, []).append(table_name)

    def _is_joinable_date_key(column_name: str) -> bool:
        lowered = column_name.lower()
        return lowered == "date" or lowered.endswith("_datetime") or lowered in {"datetime", "timestamp"}

    for source_table in tables:
        source_cols = columns_by_table.get(source_table, [])
        for col in source_cols:
            hint_target = relation_hints.get(source_table, {}).get(col)
            if hint_target and hint_target in tables:
                target_pk = set(primary_keys_by_table.get(hint_target, []))
                target_cols = set(columns_by_table.get(hint_target, []))
                if col in target_pk:
                    fk_set.add((source_table, col, hint_target, col))
                elif col in target_cols:
                    fk_set.add((source_table, col, hint_target, col))
                elif col.endswith("_datetime") and "date" in target_cols:
                    fk_set.add((source_table, col, hint_target, "date"))
                elif col == "date":
                    if "date" in target_cols:
                        fk_set.add((source_table, col, hint_target, "date"))
                continue

            if col.endswith("_id"):
                possible_targets = [t for t in pk_reverse_index.get(col, []) if t != source_table]
                for target in possible_targets:
                    fk_set.add((source_table, col, target, col))

            # Connexions temporelles: permet de relier les tables sur des clés de date pertinentes.
            if _is_joinable_date_key(col):
                for target in tables:
                    if target == source_table:
                        continue
                    target_cols = columns_by_table.get(target, [])
                    candidate_target_cols: set[str] = set()
                    if col in target_cols:
                        candidate_target_cols.add(col)
                    if "date" in target_cols:
                        candidate_target_cols.add("date")
                    if col == "date":
                        for target_col in target_cols:
                            target_lower = target_col.lower()
                            if target_lower.endswith("_datetime") or target_lower in {"datetime", "timestamp"}:
                                candidate_target_cols.add(target_col)
                    for target_col in sorted(candidate_target_cols):
                        fk_set.add((source_table, col, target, target_col))

    inferred = [
        ForeignKeyDef(
            source_table=src_t,
            source_column=src_c,
            target_table=tgt_t,
            target_column=tgt_c,
        )
        for src_t, src_c, tgt_t, tgt_c in sorted(fk_set)
        if src_t in tables and tgt_t in tables
    ]
    return inferred


def get_database_schema(
    connection_id: str,
    database_name: str,
    schema_name: str | None = None,
    db_path: Path | str | None = None,
    primary_key_hints: dict[str, set[str]] | None = None,
    relation_hints: dict[str, dict[str, str]] | None = None,
) -> DatabaseSchema:
    path = _resolve_database_path(database_name, db_path)
    pk_hints = primary_key_hints or DEFAULT_PRIMARY_KEY_HINTS
    rel_hints = relation_hints or DEFAULT_RELATION_HINTS

    with duckdb.connect(str(path), read_only=True) as conn:
        available_schemas = list_database_schemas(path)
        active_schema = schema_name or (available_schemas[0] if available_schemas else "main")
        if active_schema not in available_schemas:
            raise ErdIntrospectionError(
                f"Schéma '{active_schema}' non trouvé dans {path.name}. Disponibles: {', '.join(available_schemas)}"
            )

        table_rows = conn.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = ?
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """,
            [active_schema],
        ).fetchall()
        table_names = [str(row[0]) for row in table_rows]
        if not table_names:
            raise ErdIntrospectionError(f"Aucune table détectée dans le schéma '{active_schema}'.")

        columns_meta: dict[str, list[tuple[str, str, bool]]] = {}
        for table_name in table_names:
            col_rows = conn.execute(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = ?
                  AND table_name = ?
                ORDER BY ordinal_position
                """,
                [active_schema, table_name],
            ).fetchall()
            cols: list[tuple[str, str, bool]] = []
            for col_name, data_type, is_nullable in col_rows:
                cols.append((str(col_name), str(data_type), str(is_nullable).upper() == "YES"))
            columns_meta[table_name] = cols

        declared_pk = _fetch_declared_pk(conn, active_schema)
        declared_fks = _fetch_declared_fk(conn, active_schema)

    return _build_database_schema(
        connection_id=connection_id,
        database_name=path.name,
        schema_name=active_schema,
        table_names=table_names,
        columns_meta=columns_meta,
        primary_key_hints=pk_hints,
        relation_hints=rel_hints,
        declared_pk=declared_pk,
        declared_fks=declared_fks,
    )


def _build_database_schema(
    connection_id: str,
    database_name: str,
    schema_name: str | None,
    table_names: list[str],
    columns_meta: dict[str, list[tuple[str, str, bool]]],
    primary_key_hints: dict[str, set[str]],
    relation_hints: dict[str, dict[str, str]],
    declared_pk: dict[str, list[str]] | None = None,
    declared_fks: list[ForeignKeyDef] | None = None,
) -> DatabaseSchema:
    declared_pk = declared_pk or {}
    declared_fks = declared_fks or []

    columns_by_table: dict[str, list[str]] = {
        table_name: [c[0] for c in columns_meta.get(table_name, [])]
        for table_name in table_names
    }
    primary_keys_by_table = {
        t: _infer_primary_keys(t, columns_by_table.get(t, []), declared_pk, primary_key_hints)
        for t in table_names
    }
    foreign_keys = _infer_foreign_keys(
        tables=table_names,
        columns_by_table=columns_by_table,
        primary_keys_by_table=primary_keys_by_table,
        declared_fks=declared_fks,
        relation_hints=relation_hints,
    )
    fk_map: dict[tuple[str, str], ForeignKeyDef] = {
        (fk.source_table, fk.source_column): fk for fk in foreign_keys
    }

    tables: list[TableDef] = []
    for table_name in table_names:
        pk_cols = set(primary_keys_by_table.get(table_name, []))
        table_fks = [fk for fk in foreign_keys if fk.source_table == table_name]
        columns: list[ColumnDef] = []
        for col_name, data_type, nullable in columns_meta.get(table_name, []):
            columns.append(
                ColumnDef(
                    name=col_name,
                    data_type=data_type,
                    nullable=nullable,
                    is_primary_key=col_name in pk_cols,
                    is_foreign_key=(table_name, col_name) in fk_map,
                )
            )
        tables.append(
            TableDef(
                name=table_name,
                columns=columns,
                primary_key=list(pk_cols),
                foreign_keys=table_fks,
                indexes=[],
            )
        )

    return DatabaseSchema(
        connection_id=connection_id,
        database=database_name,
        schema=schema_name,
        tables=tables,
    )


def get_database_schema_from_dataframes(
    connection_id: str,
    database_name: str,
    tables_data: dict[str, pd.DataFrame],
    schema_name: str | None = "in_memory",
    primary_key_hints: dict[str, set[str]] | None = None,
    relation_hints: dict[str, dict[str, str]] | None = None,
) -> DatabaseSchema:
    if not tables_data:
        raise ErdIntrospectionError("Aucune table en mémoire fournie pour construire le schéma ERD.")

    pk_hints = primary_key_hints or DEFAULT_PRIMARY_KEY_HINTS
    rel_hints = relation_hints or DEFAULT_RELATION_HINTS

    table_names = sorted(tables_data.keys())
    columns_meta: dict[str, list[tuple[str, str, bool]]] = {}
    for table_name in table_names:
        df = tables_data[table_name]
        rows: list[tuple[str, str, bool]] = []
        for col_name in df.columns:
            series = df[col_name]
            rows.append((str(col_name), str(series.dtype), bool(series.isna().any())))
        columns_meta[table_name] = rows

    return _build_database_schema(
        connection_id=connection_id,
        database_name=database_name,
        schema_name=schema_name,
        table_names=table_names,
        columns_meta=columns_meta,
        primary_key_hints=pk_hints,
        relation_hints=rel_hints,
        declared_pk={},
        declared_fks=[],
    )


def build_erd_model(schema: DatabaseSchema) -> ErdModel:
    nodes: list[ErdNode] = []
    edges: list[ErdEdge] = []

    for table in schema.tables:
        pk_cols = set(table.primary_key)
        erd_cols = [
            ErdColumn(
                name=col.name,
                type=col.data_type,
                nullable=col.nullable,
                pk=col.is_primary_key,
                fk=col.is_foreign_key,
            )
            for col in table.columns
        ]

        content_lines = max(len(erd_cols), 1)
        base_height = 60.0
        line_height = 19.0
        rendered_lines = [table.name]
        for c in erd_cols:
            tags: list[str] = []
            if c.pk:
                tags.append("PK")
            if c.fk:
                tags.append("FK")
            suffix = f" [{' / '.join(tags)}]" if tags else ""
            nullable = " (nullable)" if c.nullable else ""
            rendered_lines.append(f"{c.name} : {c.type}{suffix}{nullable}")
        longest_line = max((len(x) for x in rendered_lines), default=24)
        node_height = base_height + line_height * (content_lines + 1)
        node_width = max(520.0, min(1500.0, 120.0 + float(longest_line) * 9.4))

        nodes.append(
            ErdNode(
                id=table.name,
                table_name=table.name,
                columns=erd_cols,
                width=node_width,
                height=node_height,
            )
        )

        for fk in table.foreign_keys:
            edge_id = f"{fk.source_table}.{fk.source_column}->{fk.target_table}.{fk.target_column}"
            relation_kind = "PK" if fk.source_column in pk_cols else "FK"
            edges.append(
                ErdEdge(
                    id=edge_id,
                    from_table=fk.source_table,
                    from_column=fk.source_column,
                    to_table=fk.target_table,
                    to_column=fk.target_column,
                    relation_kind=relation_kind,
                )
            )

    return ErdModel(
        nodes=nodes,
        edges=edges,
        meta={
            "database": schema.database,
            "schema": schema.schema,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "connectionId": schema.connection_id,
        },
    )


def layout_erd(model: ErdModel) -> ErdModel:
    if not model.nodes:
        return model

    degree: dict[str, int] = {node.id: 0 for node in model.nodes}
    for edge in model.edges:
        degree[edge.from_table] = degree.get(edge.from_table, 0) + 1
        degree[edge.to_table] = degree.get(edge.to_table, 0) + 1

    ordered_nodes = sorted(model.nodes, key=lambda n: (-degree.get(n.id, 0), n.table_name))
    n_nodes = len(ordered_nodes)
    grid_cols = max(1, int(ceil(sqrt(n_nodes))))

    max_width = max((node.width for node in ordered_nodes), default=360.0)
    max_height = max((node.height for node in ordered_nodes), default=180.0)
    x_gap = max_width + 190.0
    y_gap = max_height + 130.0

    for idx, node in enumerate(ordered_nodes):
        row = idx // grid_cols
        col = idx % grid_cols
        node.x = col * x_gap
        node.y = -row * y_gap

    id_to_node = {node.id: node for node in ordered_nodes}
    model.nodes = [id_to_node[node.id] for node in model.nodes if node.id in id_to_node]
    return model


def schema_to_dict(schema: DatabaseSchema) -> dict[str, Any]:
    return asdict(schema)


def erd_model_to_dict(model: ErdModel) -> dict[str, Any]:
    return asdict(model)


def summarize_schema(schema: DatabaseSchema) -> dict[str, Any]:
    rel_count = sum(len(t.foreign_keys) for t in schema.tables)
    col_count = sum(len(t.columns) for t in schema.tables)
    return {
        "database": schema.database,
        "schema": schema.schema,
        "tables": len(schema.tables),
        "columns": col_count,
        "relations": rel_count,
    }
