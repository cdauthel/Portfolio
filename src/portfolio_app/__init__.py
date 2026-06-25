"""Core package for the portfolio data application."""

from portfolio_app.features import compute_all_features
from portfolio_app.modeling import train_churn_model, train_revenue_model
from portfolio_app.preprocessing import apply_missing_value_strategy
from portfolio_app.simulation import simulate_finance_data, simulate_retail_data
from portfolio_app.storage import ensure_data_bundle, load_data_bundle

__all__ = [
    "simulate_retail_data",
    "simulate_finance_data",
    "ensure_data_bundle",
    "load_data_bundle",
    "compute_all_features",
    "apply_missing_value_strategy",
    "train_churn_model",
    "train_revenue_model",
]
