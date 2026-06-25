from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd


CITY_CATALOG = [
    ("New York", "Northeast", 40.7128, -74.0060),
    ("Boston", "Northeast", 42.3601, -71.0589),
    ("Miami", "South", 25.7617, -80.1918),
    ("Atlanta", "South", 33.7490, -84.3880),
    ("Chicago", "Midwest", 41.8781, -87.6298),
    ("Dallas", "South", 32.7767, -96.7970),
    ("Denver", "West", 39.7392, -104.9903),
    ("Phoenix", "West", 33.4484, -112.0740),
    ("San Francisco", "West", 37.7749, -122.4194),
    ("Seattle", "West", 47.6062, -122.3321),
]

CITY_STORE_ANCHORS = {
    "New York": [
        (40.7580, -73.9855),
        (40.7282, -73.7949),
        (40.6782, -73.9442),
        (40.8448, -73.8648),
        (40.7306, -73.9352),
    ],
    "Boston": [
        (42.3601, -71.0589),
        (42.3496, -71.1003),
        (42.3318, -71.1212),
        (42.3770, -71.1167),
        (42.3097, -71.1151),
    ],
    "Miami": [
        (25.7743, -80.3090),
        (25.7340, -80.2560),
        (25.8218, -80.2410),
        (25.6866, -80.3130),
        (25.7610, -80.2450),
    ],
    "Atlanta": [
        (33.7490, -84.3880),
        (33.7765, -84.3897),
        (33.7488, -84.4720),
        (33.8205, -84.3690),
        (33.7115, -84.3490),
    ],
    "Chicago": [
        (41.8781, -87.6298),
        (41.9214, -87.6513),
        (41.8030, -87.6060),
        (41.9470, -87.7470),
        (41.7620, -87.6440),
    ],
    "Dallas": [
        (32.7767, -96.7970),
        (32.8029, -96.7699),
        (32.8350, -96.8720),
        (32.7040, -96.8400),
        (32.8650, -96.7700),
    ],
    "Denver": [
        (39.7392, -104.9903),
        (39.6781, -104.9618),
        (39.7618, -105.0076),
        (39.7055, -105.0840),
        (39.7840, -104.8760),
    ],
    "Phoenix": [
        (33.4484, -112.0740),
        (33.5092, -112.0730),
        (33.4152, -111.8315),
        (33.3054, -112.0146),
        (33.5950, -112.1180),
    ],
    "San Francisco": [
        (37.7890, -122.4010),
        (37.7599, -122.4148),
        (37.7806, -122.4730),
        (37.7485, -122.4940),
        (37.7290, -122.3910),
    ],
    "Seattle": [
        (47.6062, -122.3321),
        (47.6205, -122.3493),
        (47.6614, -122.3130),
        (47.5480, -122.3150),
        (47.6710, -122.3860),
    ],
}

CITY_COORD_BOUNDS = {
    "New York": (40.55, 40.90, -74.05, -73.70),
    "Boston": (42.25, 42.43, -71.20, -70.95),
    "Miami": (25.63, 25.90, -80.40, -80.18),
    "Atlanta": (33.60, 33.90, -84.55, -84.25),
    "Chicago": (41.70, 42.02, -87.85, -87.52),
    "Dallas": (32.62, 32.92, -96.95, -96.65),
    "Denver": (39.60, 39.86, -105.12, -104.82),
    "Phoenix": (33.25, 33.70, -112.20, -111.80),
    "San Francisco": (37.70, 37.82, -122.51, -122.36),
    "Seattle": (47.50, 47.73, -122.42, -122.25),
}

CITY_COORD_JITTER = {
    "New York": (0.012, 0.012),
    "Boston": (0.010, 0.010),
    "Miami": (0.012, 0.012),
    "Chicago": (0.014, 0.014),
    "San Francisco": (0.007, 0.007),
    "Seattle": (0.010, 0.010),
}

PRODUCT_MAP = {
    "Food": ["Snacks", "Beverages", "Frozen"],
    "Electronics": ["Phone", "Accessories", "Computing"],
    "Home": ["Furniture", "Kitchen", "Decor"],
    "Beauty": ["Skincare", "Haircare", "Wellness"],
    "Sport": ["Outdoor", "Fitness", "Cycling"],
}

PAYMENT_METHODS = ["card", "cash", "wallet", "installment"]
STORE_TYPES = ["urban", "suburban", "mall", "delivery_hub"]
LOYALTY_TIERS = ["bronze", "silver", "gold", "platinum"]
ACQ_CHANNELS = ["organic", "ads", "referral", "partner"]
EVENT_TYPES = ["concert", "sports", "festival", "trade_show"]
PROMO_TYPES = ["discount", "bogo"]
RETURN_REASONS = ["damaged", "late_delivery", "wrong_item", "quality_issue", "change_mind"]

PROTECTED_COLUMNS = {
    "date",
    "order_datetime",
    "start_date",
    "end_date",
    "open_date",
    "signup_date",
    "dob",
    "gender",
    "return_date",
    "order_status",
}


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def _sample_store_coordinates(rng: np.random.Generator, cities: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lats: list[float] = []
    lons: list[float] = []
    catalog_centers = {city: (float(lat), float(lon)) for city, _, lat, lon in CITY_CATALOG}

    for city_value in cities:
        city = str(city_value)
        anchors = CITY_STORE_ANCHORS.get(city, [catalog_centers[city]])
        base_lat, base_lon = anchors[int(rng.integers(0, len(anchors)))]
        lat_jitter, lon_jitter = CITY_COORD_JITTER.get(city, (0.020, 0.020))
        lat = float(base_lat + rng.uniform(-lat_jitter, lat_jitter))
        lon = float(base_lon + rng.uniform(-lon_jitter, lon_jitter))
        lat_min, lat_max, lon_min, lon_max = CITY_COORD_BOUNDS.get(city, (-90.0, 90.0, -180.0, 180.0))
        lats.append(round(float(np.clip(lat, lat_min, lat_max)), 6))
        lons.append(round(float(np.clip(lon, lon_min, lon_max)), 6))

    return np.array(lats, dtype=float), np.array(lons, dtype=float)


def _inject_missing_values(
    tables: dict[str, pd.DataFrame],
    rng: np.random.Generator,
    missing_rate: float,
) -> dict[str, pd.DataFrame]:
    """Inject missing values randomly at table level on non-key columns."""

    if missing_rate <= 0:
        return tables

    missing_rate = float(np.clip(missing_rate, 0.0, 0.4))
    out: dict[str, pd.DataFrame] = {}
    for table_name, df in tables.items():
        temp = df.copy()
        candidate_cols = [
            col
            for col in temp.columns
            if not col.endswith("_id")
            and col not in PROTECTED_COLUMNS
            and not col.startswith("is_")
        ]
        if len(temp) == 0 or len(candidate_cols) == 0:
            out[table_name] = temp
            continue

        n_rows = len(temp)
        n_cols = len(candidate_cols)
        total_cells = n_rows * n_cols
        n_missing = int(round(total_cells * missing_rate))
        if n_missing <= 0:
            out[table_name] = temp
            continue

        flat_idx = rng.choice(total_cells, size=min(n_missing, total_cells), replace=False)
        row_idx = flat_idx // n_cols
        col_idx = flat_idx % n_cols
        col_positions = np.array([int(temp.columns.get_loc(c)) for c in candidate_cols], dtype=int)
        for r, c in zip(row_idx, col_idx):
            temp.iat[int(r), int(col_positions[int(c)])] = np.nan
        out[table_name] = temp
    return out


def _generate_stores(rng: np.random.Generator, n_stores: int, dates: pd.DatetimeIndex) -> pd.DataFrame:
    city_idx = rng.integers(0, len(CITY_CATALOG), size=n_stores)
    city_data = np.array([CITY_CATALOG[i] for i in city_idx], dtype=object)
    lat, lon = _sample_store_coordinates(rng, city_data[:, 0])

    stores = pd.DataFrame(
        {
            "store_id": np.arange(1, n_stores + 1),
            "name": [f"Store_{i:03d}" for i in range(1, n_stores + 1)],
            "lat": lat,
            "lon": lon,
            "city": city_data[:, 0],
            "region": city_data[:, 1],
            "store_type": rng.choice(STORE_TYPES, size=n_stores, p=[0.35, 0.3, 0.2, 0.15]),
            "open_date": rng.choice(
                pd.date_range(dates.min() - pd.Timedelta(days=365), dates.max() - pd.Timedelta(days=120)),
                size=n_stores,
            ),
            "capacity": rng.integers(40, 220, size=n_stores),
        }
    )
    return stores


def _generate_products(rng: np.random.Generator, n_products: int) -> pd.DataFrame:
    categories = rng.choice(list(PRODUCT_MAP.keys()), size=n_products, p=[0.3, 0.22, 0.2, 0.15, 0.13])
    subcategories = [rng.choice(PRODUCT_MAP[c]) for c in categories]
    base_price = np.round(np.exp(rng.normal(2.7, 0.85, size=n_products)), 2)
    cost = np.round(base_price * rng.uniform(0.45, 0.8, size=n_products), 2)

    products = pd.DataFrame(
        {
            "product_id": np.arange(1, n_products + 1),
            "category": categories,
            "subcategory": subcategories,
            "brand": [f"Brand_{x}" for x in rng.integers(1, 180, size=n_products)],
            "base_price": base_price,
            "cost": cost,
            "margin_target": np.round((base_price - cost) / np.maximum(base_price, 1e-6), 4),
            "is_perishable": np.where(categories == "Food", True, rng.random(n_products) < 0.08),
        }
    )
    return products


def _generate_customers(
    rng: np.random.Generator, n_customers: int, stores: pd.DataFrame, dates: pd.DatetimeIndex
) -> pd.DataFrame:
    home_store = stores.sample(n=n_customers, replace=True, random_state=int(rng.integers(0, 1_000_000)))
    customers = pd.DataFrame(
        {
            "customer_id": np.arange(1, n_customers + 1),
            "signup_date": rng.choice(dates, size=n_customers),
            "dob": rng.choice(pd.date_range("1948-01-01", "2004-12-31"), size=n_customers),
            "gender": rng.choice(["F", "M"], size=n_customers, p=[0.5, 0.5]),
            "loyalty_tier": rng.choice(LOYALTY_TIERS, size=n_customers, p=[0.5, 0.28, 0.17, 0.05]),
            "home_lat": np.round(home_store["lat"].to_numpy() + rng.normal(0, 0.2, size=n_customers), 6),
            "home_lon": np.round(home_store["lon"].to_numpy() + rng.normal(0, 0.2, size=n_customers), 6),
            "acquisition_channel": rng.choice(ACQ_CHANNELS, size=n_customers, p=[0.45, 0.3, 0.18, 0.07]),
        }
    )
    return customers


def _generate_promotions(
    rng: np.random.Generator, n_products: int, n_stores: int, dates: pd.DatetimeIndex
) -> pd.DataFrame:
    n_promos = max(30, int(n_products * 0.04))
    start_dates = rng.choice(dates[:-21], size=n_promos)
    durations = rng.integers(7, 22, size=n_promos)
    end_dates = start_dates + pd.to_timedelta(durations, unit="D")
    target_scope = rng.choice(["product", "store"], size=n_promos, p=[0.7, 0.3])
    target_id = np.where(
        target_scope == "product",
        rng.integers(1, n_products + 1, size=n_promos),
        rng.integers(1, n_stores + 1, size=n_promos),
    )
    promotions = pd.DataFrame(
        {
            "promo_id": np.arange(1, n_promos + 1),
            "start_date": start_dates,
            "end_date": end_dates,
            "promo_type": rng.choice(PROMO_TYPES, size=n_promos, p=[0.8, 0.2]),
            "target_scope": target_scope,
            "target_id": target_id,
            "expected_uplift": np.round(np.clip(rng.normal(0.12, 0.16, size=n_promos), -0.1, 0.5), 4),
        }
    )
    return promotions


def _generate_weather(
    rng: np.random.Generator, stores: pd.DataFrame, dates: pd.DatetimeIndex
) -> pd.DataFrame:
    n_store, n_date = len(stores), len(dates)
    store_ids = np.repeat(stores["store_id"].to_numpy(), n_date)
    date_values = np.tile(dates.to_numpy(), n_store)
    doy = pd.DatetimeIndex(date_values).dayofyear.to_numpy()

    lat = np.repeat(stores["lat"].to_numpy(), n_date)
    temp = 16 + 11 * np.sin((2 * np.pi * (doy - 30)) / 365.25) - 0.12 * (np.abs(lat) - 35)
    temp += rng.normal(0, 4, size=n_store * n_date)
    precip = np.clip(rng.gamma(1.7, 2.4, size=n_store * n_date) + rng.normal(0, 0.8, size=n_store * n_date), 0, None)
    wind = np.clip(rng.normal(14, 7, size=n_store * n_date), 0, None)
    is_extreme = (precip > np.quantile(precip, 0.97)) | (wind > 35) | (temp > 38) | (temp < -8)

    weather = pd.DataFrame(
        {
            "store_id": store_ids,
            "date": pd.to_datetime(date_values),
            "temp_c": np.round(temp, 2),
            "precip_mm": np.round(precip, 2),
            "wind_kmh": np.round(wind, 2),
            "is_extreme_weather": is_extreme,
        }
    )
    return weather


def _generate_events(rng: np.random.Generator, stores: pd.DataFrame, dates: pd.DatetimeIndex) -> pd.DataFrame:
    cities = stores["city"].drop_duplicates().tolist()
    rows: list[tuple[Any, ...]] = []
    event_id = 1
    for city in cities:
        event_days = dates[rng.random(len(dates)) < 0.015]
        for date in event_days:
            rows.append(
                (
                    event_id,
                    city,
                    date,
                    rng.choice(EVENT_TYPES),
                    int(rng.integers(400, 50000)),
                )
            )
            event_id += 1
    return pd.DataFrame(rows, columns=["event_id", "city", "date", "event_type", "expected_attendance"])


def simulate_retail_data(
    seed: int = 42,
    n_stores: int = 120,
    n_customers: int = 20000,
    n_products: int = 3000,
    n_orders: int = 120000,
    start_date: str = "2022-01-01",
    end_date: str = "2024-12-31",
    missing_rate: float = 0.0,
) -> dict[str, pd.DataFrame]:
    """Simulate retail data with realistic spatio-temporal and promotional effects."""

    rng = np.random.default_rng(seed)
    dates = pd.date_range(start_date, end_date, freq="D")

    stores = _generate_stores(rng, n_stores, dates)
    products = _generate_products(rng, n_products)
    customers = _generate_customers(rng, n_customers, stores, dates)
    promotions = _generate_promotions(rng, n_products, n_stores, dates)
    weather = _generate_weather(rng, stores, dates)
    events = _generate_events(rng, stores, dates)

    n_outages = max(3, n_stores // 25)
    outage_stores = rng.choice(stores["store_id"], size=n_outages, replace=False)
    outage_starts = rng.choice(dates[:-4], size=n_outages, replace=False)
    outage_dates = pd.concat(
        [pd.DataFrame({"store_id": sid, "date": pd.date_range(sd, periods=3, freq="D")}) for sid, sd in zip(outage_stores, outage_starts)],
        ignore_index=True,
    )
    outage_dates["is_closed"] = True

    daily_season = (
        1
        + 0.22 * np.sin((2 * np.pi * dates.dayofyear.to_numpy()) / 365.25)
        + 0.25 * (dates.weekday.to_numpy() >= 5)
        + 0.36 * ((dates.month.to_numpy() == 11) | (dates.month.to_numpy() == 12))
    )
    daily_probs = daily_season / daily_season.sum()
    sampled_dates = rng.choice(dates, size=n_orders, p=daily_probs)

    store_probs = stores["capacity"].to_numpy(dtype=float)
    store_probs = store_probs / store_probs.sum()
    sampled_store_ids = rng.choice(stores["store_id"], size=n_orders, p=store_probs)
    sampled_customer_ids = rng.choice(customers["customer_id"], size=n_orders)

    orders = pd.DataFrame(
        {
            "order_id": np.arange(1, n_orders + 1),
            "customer_id": sampled_customer_ids,
            "store_id": sampled_store_ids,
            "order_datetime": sampled_dates
            + pd.to_timedelta(rng.integers(7 * 60, 22 * 60, size=n_orders), unit="m")
            + pd.to_timedelta(rng.integers(0, 60, size=n_orders), unit="s"),
            "payment_method": rng.choice(PAYMENT_METHODS, size=n_orders, p=[0.55, 0.15, 0.2, 0.1]),
        }
    )
    orders["date"] = orders["order_datetime"].dt.normalize()

    promo_prob = 0.18 + 0.04 * (orders["date"].dt.month.isin([11, 12]).astype(float))
    has_promo = rng.random(n_orders) < promo_prob
    orders["promo_id"] = np.where(has_promo, rng.integers(1, len(promotions) + 1, size=n_orders), pd.NA)

    orders = orders.merge(
        weather[["store_id", "date", "precip_mm", "is_extreme_weather"]],
        on=["store_id", "date"],
        how="left",
    )
    logits = (
        -1.6
        + 0.09 * orders["precip_mm"].fillna(0).to_numpy()
        + 1.2 * orders["is_extreme_weather"].eq(True).astype(int).to_numpy()
    )
    p_delivery = _sigmoid(logits)
    orders["channel"] = np.where(rng.random(n_orders) < p_delivery, "delivery", "in_store")
    orders["order_status"] = "completed"

    orders = orders.merge(outage_dates, on=["store_id", "date"], how="left")
    orders.loc[orders["is_closed"].eq(True), "order_status"] = "cancelled_store_closed"
    orders.drop(columns=["is_closed"], inplace=True)

    item_counts = rng.integers(1, 5, size=n_orders)
    order_idx = np.repeat(np.arange(n_orders), item_counts)
    n_lines = len(order_idx)
    item_order_ids = orders["order_id"].to_numpy()[order_idx]

    product_ids = rng.integers(1, n_products + 1, size=n_lines)
    product_base_price = products.set_index("product_id")["base_price"]
    base_price = product_base_price.reindex(product_ids).to_numpy()

    promo_uplift = promotions.set_index("promo_id")["expected_uplift"].to_dict()
    promo_uplift_series = orders["promo_id"].map(promo_uplift).fillna(0.0).to_numpy()
    uplift_line = np.repeat(np.clip(promo_uplift_series, 0, 0.5), item_counts)

    qty = np.clip(rng.poisson(1.4, size=n_lines) + 1 + (rng.random(n_lines) < uplift_line).astype(int), 1, 10)
    base_discount = np.repeat(np.where(orders["promo_id"].isna(), 0.01, 0.08 + 0.2 * np.clip(promo_uplift_series, 0, 0.5)), item_counts)
    discount_pct = np.clip(rng.normal(base_discount, 0.03, size=n_lines), 0, 0.65)
    unit_price = np.round(np.clip(base_price * rng.lognormal(mean=0, sigma=0.08, size=n_lines), 0.5, None), 2)

    order_status_line = np.repeat(orders["order_status"].to_numpy(), item_counts)
    qty = np.where(order_status_line == "completed", qty, 0)
    line_amount = np.round(qty * unit_price * (1 - discount_pct), 2)

    order_items = pd.DataFrame(
        {
            "order_id": item_order_ids,
            "product_id": product_ids,
            "qty": qty.astype(int),
            "unit_price": unit_price,
            "discount_pct": np.round(discount_pct, 4),
            "line_amount": line_amount,
        }
    )

    completed_order_ids = orders.loc[orders["order_status"] == "completed", "order_id"].to_numpy()
    outlier_orders = rng.choice(completed_order_ids, size=max(20, int(len(completed_order_ids) * 0.002)), replace=False)
    outlier_mask = order_items["order_id"].isin(outlier_orders).to_numpy()
    order_items.loc[outlier_mask, "line_amount"] = np.round(order_items.loc[outlier_mask, "line_amount"] * rng.uniform(4, 11), 2)

    order_totals = order_items.groupby("order_id", as_index=False)["line_amount"].sum().rename(columns={"line_amount": "order_amount"})
    orders = orders.merge(order_totals, on="order_id", how="left")
    orders["order_amount"] = orders["order_amount"].fillna(0.0)

    return_candidates = order_items.loc[
        (order_items["line_amount"] > 0) & (order_items["qty"] > 0),
        ["order_id", "product_id", "line_amount"],
    ]
    n_returns = max(60, int(len(return_candidates) * 0.015))
    sampled_returns = return_candidates.sample(n=min(n_returns, len(return_candidates)), random_state=int(rng.integers(0, 1_000_000)))
    returns = sampled_returns.copy()
    returns.insert(0, "return_id", np.arange(1, len(returns) + 1))
    returns["return_date"] = orders.set_index("order_id").loc[returns["order_id"], "date"].to_numpy() + pd.to_timedelta(rng.integers(1, 20, size=len(returns)), unit="D")
    returns["return_reason"] = rng.choice(RETURN_REASONS, size=len(returns), p=[0.23, 0.18, 0.19, 0.25, 0.15])
    returns["refund_amount"] = np.round(returns["line_amount"] * rng.uniform(0.75, 1.0, size=len(returns)), 2)
    returns = returns[["return_id", "order_id", "product_id", "return_date", "return_reason", "refund_amount"]]

    inv_products = products["product_id"].sample(n=min(120, len(products)), random_state=seed).to_numpy()
    inv_dates = pd.date_range(dates.min(), dates.max(), freq="MS")
    inv_frame = pd.MultiIndex.from_product(
        [stores["store_id"].to_numpy(), inv_products, inv_dates], names=["store_id", "product_id", "date"]
    ).to_frame(index=False)
    n_inv = len(inv_frame)
    inv_frame["stock_on_hand"] = rng.integers(40, 450, size=n_inv)
    inv_frame["stock_in"] = rng.integers(20, 220, size=n_inv)
    inv_frame["stock_out"] = rng.integers(15, 200, size=n_inv)
    inv_frame["spoilage_qty"] = rng.poisson(2, size=n_inv)

    orders = orders[
        [
            "order_id",
            "customer_id",
            "store_id",
            "order_datetime",
            "channel",
            "payment_method",
            "promo_id",
            "order_status",
            "order_amount",
        ]
    ]

    tables = {
        "stores": stores,
        "products": products,
        "customers": customers,
        "orders": orders,
        "order_items": order_items,
        "promotions": promotions,
        "weather_store_day": weather,
        "events_city_day": events,
        "inventory_store_day": inv_frame,
        "returns": returns,
    }
    return _inject_missing_values(tables, rng=rng, missing_rate=missing_rate)


def simulate_finance_data(
    seed: int = 42,
    n_assets: int = 20,
    start_date: str = "2022-01-01",
    end_date: str = "2024-12-31",
    missing_rate: float = 0.0,
) -> dict[str, pd.DataFrame]:
    """Simulate finance tables with market regimes and macro factors."""

    rng = np.random.default_rng(seed + 13)
    dates = pd.date_range(start_date, end_date, freq="B")
    n_days = len(dates)

    sectors = ["Tech", "Energy", "Health", "Retail", "Industry", "Finance"]
    asset_types = ["equity", "fx", "commodity"]

    assets = pd.DataFrame(
        {
            "asset_id": np.arange(1, n_assets + 1),
            "ticker": [f"AST{i:03d}" for i in range(1, n_assets + 1)],
            "asset_type": rng.choice(asset_types, size=n_assets, p=[0.75, 0.1, 0.15]),
            "sector": rng.choice(sectors, size=n_assets),
        }
    )

    crash_idx = int(n_days * 0.72)
    crash_window = np.arange(max(0, crash_idx - 7), min(n_days, crash_idx + 15))
    crash_signal = np.zeros(n_days)
    crash_signal[crash_window] = -0.035

    interest_rate = np.clip(1.2 + np.cumsum(rng.normal(0, 0.015, n_days)), 0.2, 8.0)
    cpi = np.clip(2.0 + np.cumsum(rng.normal(0, 0.01, n_days)), -1.0, 9.0)
    gdp = np.clip(2.2 + np.cumsum(rng.normal(0, 0.008, n_days)), -3.0, 6.0)
    vix = np.clip(18 + np.cumsum(rng.normal(0, 0.3, n_days)) + 90 * np.abs(crash_signal), 10, 85)

    macro = pd.DataFrame(
        {
            "date": dates,
            "interest_rate": np.round(interest_rate, 4),
            "cpi": np.round(cpi, 4),
            "gdp_growth_proxy": np.round(gdp, 4),
            "volatility_index_proxy": np.round(vix, 4),
        }
    )

    price_rows: list[pd.DataFrame] = []
    for _, asset in assets.iterrows():
        mu = rng.normal(0.07, 0.04)
        sigma = np.clip(rng.normal(0.22, 0.08), 0.08, 0.45)
        beta_macro = rng.normal(0.25, 0.1)
        beta_crash = rng.uniform(0.8, 1.5) if asset["asset_type"] == "equity" else rng.uniform(0.3, 0.9)

        noise = rng.normal(0, 1, n_days)
        macro_term = beta_macro * (np.diff(np.r_[interest_rate[0], interest_rate]) * -0.01)
        vix_term = -0.0008 * (vix - vix.mean())
        ret = (mu / 252) + sigma * noise / np.sqrt(252) + macro_term + vix_term + beta_crash * crash_signal

        close = np.exp(np.cumsum(ret)) * rng.uniform(35, 260)
        open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.004, n_days))
        high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0.007, 0.003, n_days)))
        low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0.007, 0.003, n_days)))
        volume = np.maximum(1000, rng.lognormal(mean=12.2, sigma=0.45, size=n_days)).astype(int)

        asset_prices = pd.DataFrame(
            {
                "date": dates,
                "asset_id": int(asset["asset_id"]),
                "open": np.round(open_, 4),
                "high": np.round(high, 4),
                "low": np.round(low, 4),
                "close": np.round(close, 4),
                "volume": volume,
                "adj_close": np.round(close * (1 + rng.normal(0, 0.0005, n_days)), 4),
            }
        )
        price_rows.append(asset_prices)

    prices = pd.concat(price_rows, ignore_index=True)

    portfolio_ids = [1, 2, 3]
    rebalance_dates = pd.date_range(dates.min(), dates.max(), freq="MS")
    portfolios_rows: list[pd.DataFrame] = []
    for pid in portfolio_ids:
        for rd in rebalance_dates:
            weights = rng.dirichlet(np.ones(n_assets))
            temp = pd.DataFrame(
                {
                    "portfolio_id": pid,
                    "date": rd,
                    "asset_id": assets["asset_id"],
                    "weight": np.round(weights, 6),
                }
            )
            portfolios_rows.append(temp)
    portfolios = pd.concat(portfolios_rows, ignore_index=True).sort_values(["portfolio_id", "date", "asset_id"])

    monthly_prices = prices.assign(month=lambda x: x["date"].dt.to_period("M")).groupby(["asset_id", "month"], as_index=False)["close"].last()
    monthly_prices["prev_close"] = monthly_prices.groupby("asset_id")["close"].shift(1)
    monthly_prices["mom"] = (monthly_prices["close"] / monthly_prices["prev_close"]) - 1
    top_mom = monthly_prices.sort_values(["month", "mom"], ascending=[True, False]).groupby("month").head(4)
    trades = top_mom.copy()
    trades["trade_id"] = np.arange(1, len(trades) + 1)
    trades["date"] = trades["month"].dt.to_timestamp()
    trades["action"] = np.where(trades["mom"] > 0, "BUY", "SELL")
    trades["qty"] = rng.integers(10, 250, size=len(trades))
    trades["price"] = np.round(trades["close"], 4)
    trades["strategy_id"] = "MOM_1M"
    trades["pnl"] = np.round(trades["qty"] * trades["price"] * trades["mom"].fillna(0), 3)
    trades = trades[["trade_id", "date", "asset_id", "action", "qty", "price", "pnl", "strategy_id"]]

    tables = {
        "assets": assets,
        "prices_daily": prices,
        "macro": macro,
        "portfolios_daily": portfolios,
        "trades": trades,
    }
    return _inject_missing_values(tables, rng=rng, missing_rate=missing_rate)


def top_basket_pairs(order_items: pd.DataFrame, max_orders: int = 20000) -> pd.DataFrame:
    """Utility for market-basket affinity scores used in dashboards."""

    sample_order_ids = order_items["order_id"].drop_duplicates().sample(
        n=min(max_orders, order_items["order_id"].nunique()),
        random_state=42,
    )
    sample = order_items[order_items["order_id"].isin(sample_order_ids)]
    grouped = sample.groupby("order_id")["product_id"].apply(lambda x: sorted(set(x.tolist())))
    pair_counts: dict[tuple[int, int], int] = {}
    for items in grouped:
        if len(items) < 2:
            continue
        for pair in combinations(items[:20], 2):
            pair_counts[pair] = pair_counts.get(pair, 0) + 1

    if not pair_counts:
        return pd.DataFrame(columns=["product_a", "product_b", "pair_count"])
    rows = [(a, b, c) for (a, b), c in pair_counts.items()]
    return pd.DataFrame(rows, columns=["product_a", "product_b", "pair_count"]).sort_values("pair_count", ascending=False)
