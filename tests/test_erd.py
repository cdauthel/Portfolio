from pathlib import Path

from portfolio_app.erd import (
    build_erd_model,
    discover_duckdb_files,
    get_database_schema,
    layout_erd,
)
from portfolio_app.storage import ensure_data_bundle


def test_discover_duckdb_files_detects_local_bundle() -> None:
    ensure_data_bundle("data/processed", force=False)
    files = discover_duckdb_files([Path("data/processed")])
    assert any(path.name == "portfolio.duckdb" for path in files)


def test_get_database_schema_and_erd_model() -> None:
    ensure_data_bundle("data/processed", force=False)
    db_path = Path("data/processed/portfolio.duckdb")
    schema = get_database_schema(
        connection_id="duckdb_local",
        database_name=db_path.name,
        schema_name="main",
        db_path=db_path,
    )

    assert len(schema.tables) > 0
    table_names = {table.name for table in schema.tables}
    assert {"orders", "order_items", "stores", "customers"}.issubset(table_names)

    orders = next(table for table in schema.tables if table.name == "orders")
    assert "order_id" in set(orders.primary_key)
    assert any(fk.source_column == "store_id" and fk.target_table == "stores" for fk in orders.foreign_keys)

    model = build_erd_model(schema)
    assert len(model.nodes) == len(schema.tables)
    assert len(model.edges) >= 1

    laid_out = layout_erd(model)
    xs = {node.x for node in laid_out.nodes}
    ys = {node.y for node in laid_out.nodes}
    assert len(xs) >= 1
    assert len(ys) >= 1
    assert all(node.width > 0 and node.height > 0 for node in laid_out.nodes)
