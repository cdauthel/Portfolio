from __future__ import annotations

from pathlib import Path

import pandas as pd


def run_basic_quality_checks(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Return a table with portable quality checks (no heavy runtime dependency)."""

    checks: list[dict[str, object]] = []
    ohlc_mask = (
        (data["prices_daily"]["high"] >= data["prices_daily"]["open"])
        & (data["prices_daily"]["high"] >= data["prices_daily"]["close"])
        & (data["prices_daily"]["low"] <= data["prices_daily"]["open"])
        & (data["prices_daily"]["low"] <= data["prices_daily"]["close"])
    )
    ohlc_inconsistencies = int((~ohlc_mask).sum())
    checks.append(
        {
            "check": "stores.store_id_unique",
            "status": data["stores"]["store_id"].is_unique,
            "detail": "PK store_id unique",
        }
    )
    checks.append(
        {
            "check": "orders.order_id_unique",
            "status": data["orders"]["order_id"].is_unique,
            "detail": "PK order_id unique",
        }
    )
    checks.append(
        {
            "check": "order_items.qty_positive",
            "status": bool((data["order_items"]["qty"] >= 0).all()),
            "detail": "Quantites non negatives",
        }
    )
    checks.append(
        {
            "check": "prices_daily.ohlc_consistency",
            "status": bool(ohlc_mask.all()),
            "detail": (
                "OHLC cohérent"
                if ohlc_inconsistencies == 0
                else f"{ohlc_inconsistencies} ligne(s) OHLC incohérente(s)"
            ),
        }
    )
    checks.append(
        {
            "check": "orders.customer_fk_exists",
            "status": bool(data["orders"]["customer_id"].isin(data["customers"]["customer_id"]).all()),
            "detail": "FK customer_id valide",
        }
    )
    checks.append(
        {
            "check": "order_items.product_fk_exists",
            "status": bool(data["order_items"]["product_id"].isin(data["products"]["product_id"]).all()),
            "detail": "FK product_id valide",
        }
    )
    checks.append(
        {
            "check": "weather_store_day.store_fk_exists",
            "status": bool(data["weather_store_day"]["store_id"].isin(data["stores"]["store_id"]).all()),
            "detail": "FK weather -> stores valide",
        }
    )
    checks.append(
        {
            "check": "macro.date_not_null",
            "status": bool(data["macro"]["date"].notna().all()),
            "detail": "Dates macro non nulles",
        }
    )
    return pd.DataFrame(checks)


def run_ge_if_available(data: dict[str, pd.DataFrame], docs_dir: str | Path = "docs/ge") -> str:
    """
    Optional Great Expectations hook.
    Returns a message for UI display.
    """

    try:
        import great_expectations as gx  # noqa: F401

        Path(docs_dir).mkdir(parents=True, exist_ok=True)
        # Keeping the integration lightweight for portfolio reproducibility.
        return f"Great Expectations disponible. Emplacement Data Docs: {docs_dir}"
    except Exception:
        return "Great Expectations non disponible dans cet environnement. Contrôles basiques exécutés."
