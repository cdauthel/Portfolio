import numpy as np
import pandas as pd

import app.main as main


def _toy_series() -> tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(42)
    x = np.arange(0, 180, dtype=float)
    y = 100.0 + 0.35 * x + 8.0 * np.sin(2 * np.pi * x / 7.0) + rng.normal(0, 1.2, size=len(x))
    train = pd.Series(y[:140])
    test = pd.Series(y[140:])
    return train, test


def test_temporal_metrics_and_baseline_are_computable() -> None:
    y_train, y_test = _toy_series()
    y_pred = main._ts_baseline_roll_forecast(y_train, y_test, model_name="Moyenne mobile", seasonal_period=7)
    assert len(y_pred) == len(y_test)

    metrics = main._ts_forecast_metrics(y_test, y_pred, y_train, seasonal_period=7)
    assert "RMSE" in metrics and np.isfinite(metrics["RMSE"])
    assert "MAE" in metrics and np.isfinite(metrics["MAE"])


def test_run_store_forecasting_supports_extended_models() -> None:
    y_train, y_test = _toy_series()
    model_names = [
        "Naïf",
        "Moyenne mobile",
        "Lissage exponentiel (ETS additif)",
        "ETS (auto)",
        "ARIMA (1,1,1)",
        "Auto-ARIMA/SARIMA (AIC)",
    ]

    for model_name in model_names:
        pred, info, ci = main._run_store_forecasting_model(
            y_train=y_train,
            y_test=y_test,
            model_name=model_name,
            seasonal_period=7,
        )
        assert len(pred) == len(y_test)
        assert isinstance(info, dict)
        if ci is not None:
            assert len(ci) == len(y_test)


def test_temporal_examples_are_valid_on_generated_data() -> None:
    data, _features, _quality = main.load_all_data(
        seed=7,
        n_stores=20,
        n_customers=3000,
        n_products=500,
        n_orders=10000,
        n_assets=8,
        missing_rate_pct=0,
        numeric_missing_strategy="Imputation médiane",
        categorical_missing_strategy="Imputation mode",
        missing_model_dims=3,
    )
    examples = main._temporal_model_examples_catalog()
    invalid = [ex["name"] for ex in examples if not main._primary_example_is_valid(ex, data)]
    assert not invalid
