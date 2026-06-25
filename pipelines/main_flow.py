from __future__ import annotations

from pathlib import Path

from portfolio_app.features import compute_all_features
from portfolio_app.modeling import train_churn_model, train_revenue_model
from portfolio_app.quality import run_basic_quality_checks
from portfolio_app.storage import ensure_data_bundle, load_data_bundle


def run_pipeline() -> None:
    sim_kwargs = {
        "seed": 42,
        "n_stores": 120,
        "n_customers": 20000,
        "n_products": 3000,
        "n_orders": 120000,
        "n_assets": 20,
        "start_date": "2022-01-01",
        "end_date": "2024-12-31",
    }
    ensure_data_bundle("data/processed", force=True, sim_kwargs=sim_kwargs)
    data = load_data_bundle("data/processed")
    quality = run_basic_quality_checks(data)
    features = compute_all_features(data)
    churn = train_churn_model(features["customer_features"])
    revenue = train_revenue_model(features["store_daily"])

    out = Path("models")
    out.mkdir(parents=True, exist_ok=True)
    quality.to_csv(out / "quality_checks.csv", index=False)
    (out / "metrics.txt").write_text(
        "Churn metrics:\n"
        + "\n".join(f"{k}: {v:.4f}" for k, v in churn.metrics.items())
        + "\n\nRevenue metrics:\n"
        + "\n".join(f"{k}: {v:.4f}" for k, v in revenue.metrics.items()),
        encoding="utf-8",
    )
    print("Pipeline completed. Artifacts in models/.")


def run_prefect_flow() -> None:
    try:
        from prefect import flow

        @flow(name="portfolio-generate-validate-train")
        def _pipeline() -> None:
            run_pipeline()

        _pipeline()
    except Exception:
        run_pipeline()


if __name__ == "__main__":
    run_prefect_flow()
