"""Reusable preprocessing helpers for the Economic Shock Detector project."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class GroupMedianImputer(BaseEstimator, TransformerMixin):
    """Impute numeric columns with train-only medians by group."""

    def __init__(self, group_col: str, feature_cols: list[str] | None = None):
        self.group_col = group_col
        self.feature_cols = feature_cols

    def fit(self, X, y=None):
        X_df = self._to_dataframe(X)
        self.feature_cols_ = self._resolve_feature_cols(X_df)
        self.group_medians_ = X_df.groupby(self.group_col)[self.feature_cols_].median()
        self.global_medians_ = X_df[self.feature_cols_].median()
        return self

    def transform(self, X):
        X_df = self._to_dataframe(X)
        result = X_df[self.feature_cols_].copy()

        for col in self.feature_cols_:
            group_fill_values = X_df[self.group_col].map(self.group_medians_[col])
            result[col] = result[col].fillna(group_fill_values)
            result[col] = result[col].fillna(self.global_medians_[col])

        return result

    def get_feature_names_out(self, input_features=None):
        return np.array(self.feature_cols_, dtype=object)

    def _resolve_feature_cols(self, X_df: pd.DataFrame) -> list[str]:
        if self.feature_cols is not None:
            return list(self.feature_cols)
        return [col for col in X_df.columns if col != self.group_col]

    @staticmethod
    def _to_dataframe(X) -> pd.DataFrame:
        if isinstance(X, pd.DataFrame):
            return X
        return pd.DataFrame(X)
