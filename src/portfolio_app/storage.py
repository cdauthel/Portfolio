from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from portfolio_app.simulation import simulate_finance_data, simulate_retail_data


DATE_COLUMNS: dict[str, list[str]] = {
    "stores": ["open_date"],
    "customers": ["signup_date", "dob"],
    "orders": ["order_datetime"],
    "promotions": ["start_date", "end_date"],
    "weather_store_day": ["date"],
    "events_city_day": ["date"],
    "inventory_store_day": ["date"],
    "returns": ["return_date"],
    "prices_daily": ["date"],
    "macro": ["date"],
    "portfolios_daily": ["date"],
    "trades": ["date"],
}


def _write_table(df: pd.DataFrame, path_prefix: Path) -> Path:
    parquet_path = path_prefix.with_suffix(".parquet")
    csv_path = path_prefix.with_suffix(".csv")
    try:
        df.to_parquet(parquet_path, index=False)
        if csv_path.exists():
            csv_path.unlink()
        return parquet_path
    except Exception:
        df.to_csv(csv_path, index=False)
        if parquet_path.exists():
            parquet_path.unlink()
        return csv_path


def _read_table(path_prefix: Path, table_name: str) -> pd.DataFrame:
    parquet_path = path_prefix.with_suffix(".parquet")
    csv_path = path_prefix.with_suffix(".csv")
    date_cols = DATE_COLUMNS.get(table_name, [])
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    if csv_path.exists():
        return pd.read_csv(csv_path, parse_dates=date_cols if date_cols else None)
    raise FileNotFoundError(f"Missing table {table_name} at {parquet_path} or {csv_path}")


def ensure_data_bundle(
    data_dir: Path | str = "data/processed",
    force: bool = False,
    sim_kwargs: dict[str, Any] | None = None,
) -> Path:
    """Generate and store portfolio data if it does not already exist."""

    sim_kwargs = sim_kwargs or {}
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)
    sentinel = data_path / ".bundle_ready"
    if sentinel.exists() and not force:
        return data_path

    retail = simulate_retail_data(**{k: v for k, v in sim_kwargs.items() if k != "n_assets"})
    finance = simulate_finance_data(
        seed=sim_kwargs.get("seed", 42),
        n_assets=sim_kwargs.get("n_assets", 20),
        start_date=sim_kwargs.get("start_date", "2022-01-01"),
        end_date=sim_kwargs.get("end_date", "2024-12-31"),
        missing_rate=sim_kwargs.get("missing_rate", 0.0),
    )
    tables = {**retail, **finance}

    for table_name, df in tables.items():
        _write_table(df, data_path / table_name)

    duckdb_path = data_path / "portfolio.duckdb"
    build_duckdb(data_path, duckdb_path)
    sentinel.write_text("ok", encoding="utf-8")
    return data_path


def load_data_bundle(data_dir: Path | str = "data/processed") -> dict[str, pd.DataFrame]:
    """Load all simulated tables into memory."""

    data_path = Path(data_dir)
    table_names = [
        "stores",
        "products",
        "customers",
        "orders",
        "order_items",
        "promotions",
        "weather_store_day",
        "events_city_day",
        "inventory_store_day",
        "returns",
        "assets",
        "prices_daily",
        "macro",
        "portfolios_daily",
        "trades",
    ]
    return {name: _read_table(data_path / name, name) for name in table_names}


def build_duckdb(data_dir: Path | str, db_path: Path | str | None = None) -> Path:
    """Build a local DuckDB file with all tables loaded."""

    data_path = Path(data_dir)
    db_file = Path(db_path) if db_path else data_path / "portfolio.duckdb"
    if db_file.exists():
        db_file.unlink()

    tables = load_data_bundle(data_path)
    with duckdb.connect(str(db_file)) as conn:
        for table_name, df in tables.items():
            conn.register("df_temp", df)
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df_temp")
    return db_file
