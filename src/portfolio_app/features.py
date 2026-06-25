from __future__ import annotations

import math
from itertools import combinations

import numpy as np
import pandas as pd


def haversine_km(lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """Vectorized haversine distance in kilometers."""

    r = 6371.0
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return 2 * r * np.arctan2(np.sqrt(a), np.sqrt(np.maximum(1 - a, 1e-12)))


def compute_store_daily_kpis(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    products: pd.DataFrame,
    stores: pd.DataFrame,
) -> pd.DataFrame:
    orders = orders.copy()
    orders["date"] = pd.to_datetime(orders["order_datetime"]).dt.normalize()
    completed = orders[orders["order_status"] == "completed"]

    items = order_items.merge(products[["product_id", "cost"]], on="product_id", how="left")
    items["gross_line"] = items["qty"] * items["unit_price"]
    items["discount_amount"] = np.clip(items["gross_line"] - items["line_amount"], 0.0, None)
    items["line_margin"] = items["line_amount"] - (items["cost"].fillna(0.0) * items["qty"])
    item_summary = items.groupby("order_id", as_index=False).agg(
        order_amount_items=("line_amount", "sum"),
        gross_sales=("gross_line", "sum"),
        discount_amount=("discount_amount", "sum"),
        item_count=("qty", "sum"),
        margin=("line_margin", "sum"),
        avg_discount_pct=("discount_pct", "mean"),
    )
    completed = completed.merge(item_summary, on="order_id", how="left")
    completed["item_count"] = completed["item_count"].fillna(0.0)
    completed["margin"] = completed["margin"].fillna(0.0)
    completed["gross_sales"] = completed["gross_sales"].fillna(0.0)
    completed["discount_amount"] = completed["discount_amount"].fillna(0.0)
    completed["avg_discount_pct"] = completed["avg_discount_pct"].fillna(0.0)
    if "order_amount" in completed.columns:
        completed["order_amount"] = completed["order_amount"].fillna(completed["order_amount_items"])
    else:
        completed["order_amount"] = completed["order_amount_items"]
    completed["order_amount"] = completed["order_amount"].fillna(0.0)
    completed = completed.drop(columns=["order_amount_items"])
    completed["has_promo"] = completed["promo_id"].notna()

    daily = completed.groupby(["store_id", "date"], as_index=False).agg(
        revenue=("order_amount", "sum"),
        gross_sales=("gross_sales", "sum"),
        discount_amount=("discount_amount", "sum"),
        txns=("order_id", "nunique"),
        unique_customers=("customer_id", "nunique"),
        items=("item_count", "sum"),
        margin=("margin", "sum"),
        promo_share=("has_promo", "mean"),
        avg_discount_pct=("avg_discount_pct", "mean"),
    )
    daily["avg_basket"] = np.where(daily["txns"] > 0, daily["revenue"] / daily["txns"], 0.0)
    daily["items_per_txn"] = np.where(daily["txns"] > 0, daily["items"] / daily["txns"], 0.0)
    daily["discount_rate"] = np.where(daily["gross_sales"] > 0, daily["discount_amount"] / daily["gross_sales"], 0.0)
    daily["margin_rate"] = np.where(daily["revenue"] > 0, daily["margin"] / daily["revenue"], 0.0)
    daily["revenue_per_customer"] = np.where(daily["unique_customers"] > 0, daily["revenue"] / daily["unique_customers"], 0.0)
    daily["txn_per_customer"] = np.where(daily["unique_customers"] > 0, daily["txns"] / daily["unique_customers"], 0.0)
    daily["revenue_per_item"] = np.where(daily["items"] > 0, daily["revenue"] / daily["items"], 0.0)
    daily["is_weekend"] = pd.to_datetime(daily["date"]).dt.weekday >= 5

    promo_stats = completed.groupby(["store_id", "has_promo"], as_index=False)["order_amount"].mean()
    promo_pivot = promo_stats.pivot(index="store_id", columns="has_promo", values="order_amount").reset_index()
    promo_pivot = promo_pivot.rename(columns={False: "baseline_order_amount", True: "promo_order_amount"})
    if "baseline_order_amount" not in promo_pivot.columns:
        promo_pivot["baseline_order_amount"] = np.nan
    if "promo_order_amount" not in promo_pivot.columns:
        promo_pivot["promo_order_amount"] = np.nan
    promo_pivot["promo_uplift"] = np.where(
        promo_pivot["baseline_order_amount"] > 0,
        (promo_pivot["promo_order_amount"] - promo_pivot["baseline_order_amount"])
        / promo_pivot["baseline_order_amount"],
        0.0,
    )
    daily = daily.merge(promo_pivot[["store_id", "promo_uplift"]], on="store_id", how="left")
    daily = daily.merge(stores[["store_id", "city", "region", "store_type", "lat", "lon"]], on="store_id", how="left")
    return daily.sort_values(["date", "store_id"])


def compute_customer_features(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    orders = orders.copy()
    orders["date"] = pd.to_datetime(orders["order_datetime"]).dt.normalize()
    completed = orders[orders["order_status"] == "completed"]
    amounts = (
        order_items.groupby("order_id", as_index=False)["line_amount"]
        .sum()
        .rename(columns={"line_amount": "order_amount_items"})
    )
    completed = completed.merge(amounts, on="order_id", how="left")
    if "order_amount" in completed.columns:
        completed["order_amount"] = completed["order_amount"].fillna(completed["order_amount_items"])
    else:
        completed["order_amount"] = completed["order_amount_items"]
    completed["order_amount"] = completed["order_amount"].fillna(0.0)
    completed = completed.drop(columns=["order_amount_items"])

    ref_date = completed["date"].max()
    if pd.isna(ref_date):
        ref_date = pd.Timestamp.today().normalize()

    customer_agg = completed.groupby("customer_id", as_index=False).agg(
        frequency=("order_id", "nunique"),
        monetary=("order_amount", "sum"),
        avg_order_amount=("order_amount", "mean"),
        last_order_date=("date", "max"),
        first_order_date=("date", "min"),
    )
    order_gaps = (
        completed.sort_values(["customer_id", "date"])
        .groupby("customer_id")["date"]
        .diff()
        .dt.days
    )
    gap_summary = (
        completed.assign(order_gap_days=order_gaps)
        .groupby("customer_id", as_index=False)["order_gap_days"]
        .mean()
        .rename(columns={"order_gap_days": "avg_interpurchase_days"})
    )
    recent_cutoff = ref_date - pd.Timedelta(days=90)
    recent_summary = (
        completed[completed["date"] >= recent_cutoff]
        .groupby("customer_id", as_index=False)
        .agg(orders_last_90d=("order_id", "nunique"), revenue_last_90d=("order_amount", "sum"))
    )
    customer_agg = customer_agg.merge(gap_summary, on="customer_id", how="left")
    customer_agg = customer_agg.merge(recent_summary, on="customer_id", how="left")
    customer_agg["recency_days"] = (ref_date - customer_agg["last_order_date"]).dt.days
    customer_agg["active_span_days"] = (customer_agg["last_order_date"] - customer_agg["first_order_date"]).dt.days.clip(lower=1)

    feats = customers.merge(customer_agg, on="customer_id", how="left")
    fill_cols = [
        "frequency",
        "monetary",
        "avg_order_amount",
        "recency_days",
        "active_span_days",
        "avg_interpurchase_days",
        "orders_last_90d",
        "revenue_last_90d",
    ]
    feats[fill_cols] = feats[fill_cols].fillna(0.0)
    feats["signup_date"] = pd.to_datetime(feats["signup_date"])
    feats["tenure_days"] = (ref_date - feats["signup_date"]).dt.days.clip(lower=1)
    feats["repeat_rate"] = (feats["frequency"] > 1).astype(int)
    feats["churn_label"] = (feats["recency_days"] > 90).astype(int)
    feats["purchase_frequency_90d"] = feats["orders_last_90d"] / 90.0
    feats["monetary_per_day"] = np.where(feats["tenure_days"] > 0, feats["monetary"] / feats["tenure_days"], 0.0)
    feats["churn_risk_proxy"] = 1 / (1 + np.exp(-(0.04 * feats["recency_days"] - 0.3 * feats["frequency"])))
    feats["rfm_score"] = (
        (pd.qcut(feats["recency_days"].rank(method="first"), 5, labels=False) + 1).astype(int)
        + (pd.qcut(feats["frequency"].rank(method="first"), 5, labels=False) + 1).astype(int)
        + (pd.qcut(feats["monetary"].rank(method="first"), 5, labels=False) + 1).astype(int)
    )
    feats["clv_proxy"] = np.round(
        feats["monetary"] * np.log1p(feats["frequency"]) * (365 / feats["tenure_days"].clip(lower=30)),
        3,
    )
    return feats


def compute_product_features(
    order_items: pd.DataFrame,
    products: pd.DataFrame,
    max_orders_for_basket: int = 15000,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    items = order_items.merge(products[["product_id", "category", "subcategory", "cost"]], on="product_id", how="left")
    items["gross_line"] = items["qty"] * items["unit_price"]
    items["discount_amount"] = np.clip(items["gross_line"] - items["line_amount"], 0.0, None)
    items["margin_contribution"] = items["line_amount"] - items["cost"].fillna(0.0) * items["qty"]
    prod_summary = items.groupby(["product_id", "category", "subcategory"], as_index=False).agg(
        units=("qty", "sum"),
        revenue=("line_amount", "sum"),
        margin=("margin_contribution", "sum"),
        gross_sales=("gross_line", "sum"),
        discount_amount=("discount_amount", "sum"),
        avg_unit_price=("unit_price", "mean"),
        avg_discount_pct=("discount_pct", "mean"),
        unique_orders=("order_id", "nunique"),
    )
    n_orders_total = max(order_items["order_id"].nunique(), 1)
    prod_summary["discount_rate"] = np.where(
        prod_summary["gross_sales"] > 0,
        prod_summary["discount_amount"] / prod_summary["gross_sales"],
        0.0,
    )
    prod_summary["margin_rate"] = np.where(
        prod_summary["revenue"] > 0,
        prod_summary["margin"] / prod_summary["revenue"],
        0.0,
    )
    prod_summary["order_penetration"] = prod_summary["unique_orders"] / n_orders_total
    prod_summary["revenue_share_pct"] = np.where(
        prod_summary["revenue"].sum() > 0,
        100.0 * prod_summary["revenue"] / prod_summary["revenue"].sum(),
        0.0,
    )

    sample_ids = order_items["order_id"].drop_duplicates().sample(
        n=min(max_orders_for_basket, order_items["order_id"].nunique()),
        random_state=42,
    )
    sampled = order_items[order_items["order_id"].isin(sample_ids)]
    grouped = sampled.groupby("order_id")["product_id"].apply(lambda x: sorted(set(x.tolist())))
    pair_counts: dict[tuple[int, int], int] = {}
    for products_in_order in grouped:
        if len(products_in_order) < 2:
            continue
        for pair in combinations(products_in_order[:15], 2):
            pair_counts[pair] = pair_counts.get(pair, 0) + 1
    affinity = pd.DataFrame(
        [(a, b, count) for (a, b), count in pair_counts.items()],
        columns=["product_a", "product_b", "pair_count"],
    ).sort_values("pair_count", ascending=False)
    return prod_summary, affinity


def _moran_i(values: np.ndarray, lat: np.ndarray, lon: np.ndarray, k_neighbors: int = 5) -> float:
    n = len(values)
    if n < 4:
        return float("nan")
    coords = np.column_stack([lat, lon])
    dmat = np.sqrt(((coords[:, None, :] - coords[None, :, :]) ** 2).sum(axis=2))
    np.fill_diagonal(dmat, np.inf)
    weights = np.zeros_like(dmat)
    neighbor_idx = np.argsort(dmat, axis=1)[:, :k_neighbors]
    for i in range(n):
        for j in neighbor_idx[i]:
            weights[i, j] = 1.0 / max(dmat[i, j], 1e-6)
    s0 = weights.sum()
    if s0 == 0:
        return float("nan")
    x = values
    x_mean = x.mean()
    num = 0.0
    den = ((x - x_mean) ** 2).sum()
    if den <= 1e-9:
        return float("nan")
    for i in range(n):
        for j in range(n):
            num += weights[i, j] * (x[i] - x_mean) * (x[j] - x_mean)
    return float((n / s0) * (num / den))


def compute_spatial_features(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    stores: pd.DataFrame,
    store_daily: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    completed = orders[orders["order_status"] == "completed"][["order_id", "customer_id", "store_id"]]
    geo = completed.merge(customers[["customer_id", "home_lat", "home_lon"]], on="customer_id", how="left")
    geo = geo.merge(stores[["store_id", "lat", "lon", "city", "region"]], on="store_id", how="left")
    geo["distance_km"] = haversine_km(
        geo["home_lat"].to_numpy(),
        geo["home_lon"].to_numpy(),
        geo["lat"].to_numpy(),
        geo["lon"].to_numpy(),
    )
    geo = geo.replace([np.inf, -np.inf], np.nan).dropna(subset=["distance_km"])

    rev_store = store_daily.groupby(["store_id", "lat", "lon"], as_index=False)["revenue"].sum()
    moran = _moran_i(rev_store["revenue"].to_numpy(), rev_store["lat"].to_numpy(), rev_store["lon"].to_numpy())
    store_spatial = rev_store.copy()
    store_spatial["moran_i_global"] = moran
    return geo, store_spatial


def compute_finance_metrics(prices_daily: pd.DataFrame, assets: pd.DataFrame) -> pd.DataFrame:
    prices = prices_daily.sort_values(["asset_id", "date"]).copy()
    prices["returns"] = prices.groupby("asset_id")["adj_close"].pct_change()
    market_series = prices.groupby("date")["returns"].mean().rename("market_returns")
    prices = prices.merge(market_series, on="date", how="left")

    rows = []
    for asset_id, grp in prices.groupby("asset_id"):
        ret = grp["returns"].dropna()
        if ret.empty:
            continue
        volatility_ann = np.sqrt(252) * ret.std(ddof=0)
        mean_daily_return = ret.mean()
        sharpe = np.sqrt(252) * ret.mean() / (ret.std(ddof=0) + 1e-9)
        downside = ret[ret < 0]
        sortino = np.sqrt(252) * ret.mean() / (downside.std(ddof=0) + 1e-9) if len(downside) else math.nan
        cum = (1 + ret).cumprod()
        drawdown = cum / cum.cummax() - 1
        max_dd = drawdown.min()
        var_95 = np.quantile(ret, 0.05)
        cov = np.cov(ret, grp.loc[ret.index, "market_returns"].fillna(0.0).to_numpy())[0, 1]
        mkt_var = np.var(grp.loc[ret.index, "market_returns"].fillna(0.0).to_numpy()) + 1e-9
        beta = cov / mkt_var
        cagr = (cum.iloc[-1] ** (252 / max(len(ret), 1))) - 1
        rows.append((asset_id, mean_daily_return, volatility_ann, sharpe, sortino, max_dd, var_95, beta, cagr))

    metrics = pd.DataFrame(
        rows,
        columns=[
            "asset_id",
            "mean_daily_return",
            "volatility_ann",
            "sharpe",
            "sortino",
            "max_drawdown",
            "var_95",
            "beta_vs_market",
            "cagr",
        ],
    ).merge(assets[["asset_id", "ticker", "sector"]], on="asset_id", how="left")
    return metrics.sort_values("sharpe", ascending=False)


def compute_all_features(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    store_daily = compute_store_daily_kpis(
        data["orders"],
        data["order_items"],
        data["products"],
        data["stores"],
    )
    customer_features = compute_customer_features(data["orders"], data["order_items"], data["customers"])
    product_features, affinity = compute_product_features(data["order_items"], data["products"])
    geo_orders, spatial_store = compute_spatial_features(
        data["orders"],
        data["customers"],
        data["stores"],
        store_daily,
    )
    finance_metrics = compute_finance_metrics(data["prices_daily"], data["assets"])

    return {
        "store_daily": store_daily,
        "customer_features": customer_features,
        "product_features": product_features,
        "affinity": affinity,
        "geo_orders": geo_orders,
        "spatial_store": spatial_store,
        "finance_metrics": finance_metrics,
    }
