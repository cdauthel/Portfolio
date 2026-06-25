from portfolio_app.features import compute_all_features
from portfolio_app.modeling import train_churn_model, train_revenue_model
from portfolio_app.simulation import simulate_finance_data, simulate_retail_data


def test_model_training_metrics_exist() -> None:
    retail = simulate_retail_data(
        seed=9,
        n_stores=20,
        n_customers=3000,
        n_products=600,
        n_orders=10000,
        start_date="2023-01-01",
        end_date="2023-12-31",
    )
    finance = simulate_finance_data(seed=9, n_assets=8, start_date="2023-01-01", end_date="2023-12-31")
    feats = compute_all_features({**retail, **finance})

    churn = train_churn_model(feats["customer_features"])
    revenue = train_revenue_model(feats["store_daily"])

    assert "roc_auc" in churn.metrics
    assert "rmse" in revenue.metrics
