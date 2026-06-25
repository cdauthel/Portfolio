from portfolio_app.features import compute_all_features
from portfolio_app.simulation import simulate_finance_data, simulate_retail_data


def test_compute_all_features_expected_keys() -> None:
    retail = simulate_retail_data(
        seed=1,
        n_stores=15,
        n_customers=1200,
        n_products=250,
        n_orders=5000,
        start_date="2023-01-01",
        end_date="2023-09-30",
    )
    finance = simulate_finance_data(seed=1, n_assets=6, start_date="2023-01-01", end_date="2023-09-30")
    data = {**retail, **finance}
    feats = compute_all_features(data)
    expected = {
        "store_daily",
        "customer_features",
        "product_features",
        "affinity",
        "geo_orders",
        "spatial_store",
        "finance_metrics",
    }
    assert expected.issubset(set(feats.keys()))
    assert len(feats["store_daily"]) > 0
