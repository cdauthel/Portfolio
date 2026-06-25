from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass
class ModelResult:
    model: Any
    metrics: dict[str, float]
    y_true: np.ndarray
    y_pred: np.ndarray
    y_score: np.ndarray | None = None


def train_churn_model(customer_features: pd.DataFrame, random_state: int = 42) -> ModelResult:
    df = customer_features.copy()
    target = "churn_label"
    features = [
        "frequency",
        "monetary",
        "avg_order_amount",
        "recency_days",
        "active_span_days",
        "tenure_days",
        "loyalty_tier",
        "acquisition_channel",
        "gender",
    ]
    X = df[features]
    y = df[target].astype(int)

    num_cols = ["frequency", "monetary", "avg_order_amount", "recency_days", "active_span_days", "tenure_days"]
    cat_cols = ["loyalty_tier", "acquisition_channel", "gender"]

    pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), num_cols),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("ohe", OneHotEncoder(handle_unknown="ignore"))]), cat_cols),
        ]
    )
    clf = Pipeline(
        steps=[
            ("pre", pre),
            ("model", RandomForestClassifier(n_estimators=200, max_depth=8, random_state=random_state, n_jobs=-1)),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=random_state)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    y_score = clf.predict_proba(X_test)[:, 1]

    metrics = {
        "roc_auc": float(roc_auc_score(y_test, y_score)),
        "pr_auc": float(average_precision_score(y_test, y_score)),
        "f1": float(f1_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
    }
    return ModelResult(model=clf, metrics=metrics, y_true=y_test.to_numpy(), y_pred=y_pred, y_score=y_score)


def train_revenue_model(store_daily: pd.DataFrame, random_state: int = 42) -> ModelResult:
    df = store_daily.copy()
    df["weekday"] = pd.to_datetime(df["date"]).dt.weekday
    df["month"] = pd.to_datetime(df["date"]).dt.month

    features = [
        "txns",
        "items",
        "avg_basket",
        "items_per_txn",
        "promo_share",
        "promo_uplift",
        "discount_rate",
        "margin_rate",
        "unique_customers",
        "revenue_per_customer",
        "weekday",
        "month",
        "store_type",
        "region",
    ]
    target = "revenue"
    available_features = [f for f in features if f in df.columns]
    X = df[available_features]
    y = df[target].astype(float)

    num_cols = [c for c in ["txns", "items", "avg_basket", "items_per_txn", "promo_share", "promo_uplift", "discount_rate", "margin_rate", "unique_customers", "revenue_per_customer", "weekday", "month"] if c in available_features]
    cat_cols = [c for c in ["store_type", "region"] if c in available_features]
    pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), num_cols),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("ohe", OneHotEncoder(handle_unknown="ignore"))]), cat_cols),
        ]
    )
    model = Pipeline(
        steps=[
            ("pre", pre),
            ("model", RandomForestRegressor(n_estimators=220, max_depth=10, random_state=random_state, n_jobs=-1)),
        ]
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=random_state)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    mae = float(mean_absolute_error(y_test, y_pred))
    mape = float(np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1e-6))))
    r2 = float(np.corrcoef(y_test, y_pred)[0, 1] ** 2)
    metrics = {"rmse": rmse, "mae": mae, "mape": mape, "r2": r2}
    return ModelResult(model=model, metrics=metrics, y_true=y_test.to_numpy(), y_pred=y_pred)


def forecast_store_revenue(
    store_daily: pd.DataFrame,
    store_id: int,
    horizon: int = 30,
) -> tuple[pd.DataFrame, dict[str, float]]:
    series = (
        store_daily[store_daily["store_id"] == store_id]
        .groupby("date", as_index=False)["revenue"]
        .sum()
        .sort_values("date")
    )
    if len(series) < 90:
        return series.assign(forecast=np.nan), {"rmse": float("nan"), "mae": float("nan")}

    train = series.iloc[:-horizon].copy()
    test = series.iloc[-horizon:].copy()

    yhat = None
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        model = ExponentialSmoothing(train["revenue"], trend="add", seasonal="add", seasonal_periods=7)
        fit = model.fit(optimized=True)
        yhat = fit.forecast(horizon).to_numpy()
    except Exception:
        # Robust fallback if statsmodels is unavailable in runtime.
        rolling = train["revenue"].rolling(14, min_periods=3).mean()
        baseline = rolling.iloc[-1]
        yhat = np.repeat(float(baseline), horizon)

    rmse = float(np.sqrt(mean_squared_error(test["revenue"], yhat)))
    mae = float(mean_absolute_error(test["revenue"], yhat))
    out = pd.concat(
        [
            train.assign(split="train", forecast=np.nan),
            test.assign(split="test", forecast=yhat),
        ],
        ignore_index=True,
    )
    return out, {"rmse": rmse, "mae": mae}
