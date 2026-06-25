from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.preprocessing import StandardScaler

MissingStrategy = Literal[
    "Conserver (brut)",
    "Imputation médiane/mode",
    "Imputation zéro/Unknown",
    "Suppression des lignes incomplètes",
    "Forward fill temporel + mode",
    "Imputation ACP/ACM (modèle)",
]

NumericMissingStrategy = Literal[
    "Conserver (brut)",
    "Imputation médiane",
    "Imputation zéro",
    "Forward fill temporel",
    "Imputation ACP (modèle)",
]

CategoricalMissingStrategy = Literal[
    "Conserver (brut)",
    "Imputation mode",
    "Imputation Unknown",
    "Forward fill + mode",
    "Imputation ACM (modèle)",
]


def _fill_mode(series: pd.Series) -> pd.Series:
    mode = series.mode(dropna=True)
    if len(mode) == 0:
        return series.fillna("Unknown")
    return series.fillna(mode.iloc[0])


def _fill_temporal(df: pd.DataFrame) -> pd.DataFrame:
    temp = df.copy()
    date_cols = [col for col in ["date", "order_datetime"] if col in temp.columns]
    if date_cols:
        temp = temp.sort_values(date_cols)

    for col in temp.columns:
        if pd.api.types.is_numeric_dtype(temp[col]) and not pd.api.types.is_bool_dtype(temp[col]):
            temp[col] = temp[col].ffill().bfill().fillna(temp[col].median())
        elif pd.api.types.is_datetime64_any_dtype(temp[col]):
            temp[col] = temp[col].ffill().bfill()
        elif pd.api.types.is_bool_dtype(temp[col]):
            temp[col] = temp[col].fillna(False)
        else:
            temp[col] = _fill_mode(temp[col]).ffill().bfill()
    return temp


def _impute_numeric_with_pca(df_num: pd.DataFrame, n_components: int) -> pd.DataFrame:
    if df_num.empty:
        return df_num

    out = df_num.copy()
    missing_mask = out.isna()
    if not missing_mask.to_numpy().any():
        return out

    initial = out.fillna(out.median(numeric_only=True)).fillna(0.0)

    n_rows, n_cols = initial.shape
    max_components = min(n_components, n_cols, max(n_rows - 1, 1))
    if n_rows < 3 or n_cols < 2 or max_components < 1:
        return initial

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(initial)
    pca = PCA(n_components=max_components, random_state=42)
    scores = pca.fit_transform(x_scaled)
    recon_scaled = pca.inverse_transform(scores)
    recon = scaler.inverse_transform(recon_scaled)

    recon_df = pd.DataFrame(recon, columns=initial.columns, index=initial.index)
    out = out.where(~missing_mask, recon_df)
    return out


def _impute_categorical_with_mca(df_cat: pd.DataFrame, n_components: int) -> pd.DataFrame:
    if df_cat.empty:
        return df_cat

    out = df_cat.copy()
    original_dtypes = out.dtypes.to_dict()
    missing_mask = out.isna()
    if not missing_mask.to_numpy().any():
        return out

    filled = out.copy()
    for col in filled.columns:
        col_mode = filled[col].mode(dropna=True)
        default_value = col_mode.iloc[0] if not col_mode.empty else "Unknown"
        filled[col] = filled[col].astype("object").fillna(default_value).astype(str)

    dummy = pd.get_dummies(filled, prefix=filled.columns, prefix_sep="|||", dtype=float)
    if dummy.empty or dummy.shape[1] < 2 or len(dummy) < 3:
        return filled

    max_components = min(n_components, dummy.shape[1] - 1, len(dummy) - 1)
    if max_components < 1:
        return filled

    svd = TruncatedSVD(n_components=max_components, random_state=42)
    latent = svd.fit_transform(dummy)
    recon = svd.inverse_transform(latent)
    recon_df = pd.DataFrame(recon, columns=dummy.columns, index=dummy.index)

    for col in out.columns:
        miss_rows = missing_mask[col]
        if not miss_rows.any():
            continue
        level_cols = [c for c in recon_df.columns if c.startswith(f"{col}|||")]
        if not level_cols:
            continue

        score_block = recon_df.loc[miss_rows, level_cols]
        best_levels = score_block.idxmax(axis=1).astype(str).str.split("|||", n=1).str[-1]
        out.loc[miss_rows, col] = best_levels.to_numpy()

    for col, dtype in original_dtypes.items():
        if pd.api.types.is_bool_dtype(dtype):
            mapped = out[col].astype(str).str.lower().map({"true": True, "false": False, "1": True, "0": False})
            if mapped.notna().any():
                mode = mapped.mode(dropna=True)
                default_bool = bool(mode.iloc[0]) if not mode.empty else False
                out[col] = mapped.fillna(default_bool).astype(bool)
            else:
                out[col] = out[col].fillna(False).astype(bool)
        elif isinstance(dtype, pd.CategoricalDtype):
            out[col] = out[col].astype("category")

    return out


def _apply_numeric_strategy(series: pd.Series, strategy: NumericMissingStrategy) -> pd.Series:
    if strategy == "Conserver (brut)":
        return series
    if strategy == "Imputation médiane":
        return series.fillna(series.median())
    if strategy == "Imputation zéro":
        return series.fillna(0)
    if strategy == "Forward fill temporel":
        return series.ffill().bfill().fillna(series.median())
    return series


def _apply_categorical_strategy(series: pd.Series, strategy: CategoricalMissingStrategy) -> pd.Series:
    if strategy == "Conserver (brut)":
        return series
    if strategy == "Imputation mode":
        return _fill_mode(series)
    if strategy == "Imputation Unknown":
        return series.fillna("Unknown")
    if strategy == "Forward fill + mode":
        return _fill_mode(series).ffill().bfill()
    return series


def _apply_strategies_by_type(
    df: pd.DataFrame,
    numeric_strategy: NumericMissingStrategy,
    categorical_strategy: CategoricalMissingStrategy,
    n_components: int,
) -> pd.DataFrame:
    temp = df.copy()
    dims = int(np.clip(n_components, 2, 6))

    datetime_cols = [c for c in temp.columns if pd.api.types.is_datetime64_any_dtype(temp[c])]
    numeric_cols = [
        c for c in temp.columns if pd.api.types.is_numeric_dtype(temp[c]) and not pd.api.types.is_bool_dtype(temp[c])
    ]
    categorical_cols = [
        c
        for c in temp.columns
        if c not in numeric_cols and c not in datetime_cols
    ]
    bool_cols = [c for c in temp.columns if pd.api.types.is_bool_dtype(temp[c])]
    categorical_cols += [c for c in bool_cols if c not in categorical_cols]

    if numeric_cols:
        if numeric_strategy == "Imputation ACP (modèle)":
            temp.loc[:, numeric_cols] = _impute_numeric_with_pca(temp[numeric_cols], n_components=dims)
        else:
            for col in numeric_cols:
                temp[col] = _apply_numeric_strategy(temp[col], numeric_strategy)

    mca_cols = [c for c in categorical_cols if c not in datetime_cols]
    if mca_cols:
        if categorical_strategy == "Imputation ACM (modèle)":
            temp.loc[:, mca_cols] = _impute_categorical_with_mca(temp[mca_cols], n_components=dims)
        else:
            for col in mca_cols:
                temp[col] = _apply_categorical_strategy(temp[col], categorical_strategy)

    if datetime_cols and (
        numeric_strategy != "Conserver (brut)" or categorical_strategy != "Conserver (brut)"
    ):
        for col in datetime_cols:
            temp[col] = temp[col].ffill().bfill()

    # Final safety pass by nature
    if numeric_cols and numeric_strategy != "Conserver (brut)":
        for col in numeric_cols:
            if temp[col].isna().any():
                if numeric_strategy == "Imputation zéro":
                    temp[col] = temp[col].fillna(0)
                else:
                    temp[col] = temp[col].fillna(temp[col].median())

    if mca_cols and categorical_strategy != "Conserver (brut)":
        for col in mca_cols:
            if temp[col].isna().any():
                if categorical_strategy == "Imputation Unknown":
                    temp[col] = temp[col].fillna("Unknown")
                else:
                    temp[col] = _fill_mode(temp[col])

    return temp


def _apply_strategy_to_df(df: pd.DataFrame, strategy: MissingStrategy, n_components: int = 3) -> pd.DataFrame:
    if strategy == "Conserver (brut)":
        return df.copy()

    temp = df.copy()
    if strategy == "Suppression des lignes incomplètes":
        return temp.dropna()

    if strategy == "Forward fill temporel + mode":
        return _fill_temporal(temp)

    if strategy == "Imputation ACP/ACM (modèle)":
        return _apply_strategies_by_type(
            temp,
            numeric_strategy="Imputation ACP (modèle)",
            categorical_strategy="Imputation ACM (modèle)",
            n_components=n_components,
        )

    if strategy == "Imputation médiane/mode":
        return _apply_strategies_by_type(
            temp,
            numeric_strategy="Imputation médiane",
            categorical_strategy="Imputation mode",
            n_components=n_components,
        )

    if strategy == "Imputation zéro/Unknown":
        return _apply_strategies_by_type(
            temp,
            numeric_strategy="Imputation zéro",
            categorical_strategy="Imputation Unknown",
            n_components=n_components,
        )

    return temp


def apply_missing_value_strategy(
    data: dict[str, pd.DataFrame],
    strategy: MissingStrategy = "Conserver (brut)",
    n_components: int = 3,
    numeric_strategy: NumericMissingStrategy | None = None,
    categorical_strategy: CategoricalMissingStrategy | None = None,
) -> dict[str, pd.DataFrame]:
    """Apply missing-value strategy globally or by variable type."""

    out: dict[str, pd.DataFrame] = {}
    by_type = numeric_strategy is not None or categorical_strategy is not None
    for table_name, df in data.items():
        if by_type:
            cleaned = _apply_strategies_by_type(
                df,
                numeric_strategy=numeric_strategy or "Conserver (brut)",
                categorical_strategy=categorical_strategy or "Conserver (brut)",
                n_components=n_components,
            )
        else:
            cleaned = _apply_strategy_to_df(df, strategy, n_components=n_components)
        cleaned = cleaned.replace([np.inf, -np.inf], np.nan)
        out[table_name] = cleaned
    return out
