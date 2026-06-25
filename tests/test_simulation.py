from portfolio_app.simulation import CITY_COORD_BOUNDS, simulate_finance_data, simulate_retail_data


def test_simulate_retail_data_has_expected_tables() -> None:
    data = simulate_retail_data(
        seed=42,
        n_stores=20,
        n_customers=2000,
        n_products=400,
        n_orders=8000,
        start_date="2023-01-01",
        end_date="2023-12-31",
    )
    expected = {
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
    }
    assert expected.issubset(set(data.keys()))
    assert len(data["orders"]) == 8000
    assert len(data["order_items"]) > 8000


def test_store_coordinates_stay_inside_city_bounds() -> None:
    data = simulate_retail_data(
        seed=7,
        n_stores=80,
        n_customers=500,
        n_products=120,
        n_orders=1200,
        start_date="2023-01-01",
        end_date="2023-03-31",
    )
    stores = data["stores"]

    for city, group in stores.groupby("city"):
        lat_min, lat_max, lon_min, lon_max = CITY_COORD_BOUNDS[city]
        assert group["lat"].between(lat_min, lat_max).all()
        assert group["lon"].between(lon_min, lon_max).all()


def test_simulate_finance_data_has_expected_columns() -> None:
    data = simulate_finance_data(seed=42, n_assets=8, start_date="2023-01-01", end_date="2023-12-31")
    assert {"assets", "prices_daily", "macro", "portfolios_daily", "trades"}.issubset(set(data.keys()))
    assert {"open", "high", "low", "close", "adj_close"}.issubset(set(data["prices_daily"].columns))
