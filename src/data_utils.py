from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import zscore

EXPECTED_COLUMNS = [
    "YEAR",
    "DOY",
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "T2M_RANGE",
    "PRECTOTCORR",
    "RH2M",
    "WS2M",
    "WS2M_MAX",
    "PS",
    "QV2M",
]

COUNTRY_METADATA = {
    "Ethiopia": {"latitude": 9.03, "longitude": 38.74, "location": "Addis Ababa"},
    "Kenya": {"latitude": -1.2921, "longitude": 36.8219, "location": "Nairobi"},
    "Sudan": {"latitude": 15.5007, "longitude": 32.5599, "location": "Khartoum"},
    "Tanzania": {"latitude": -6.7924, "longitude": 39.2083, "location": "Dar es Salaam"},
    "Nigeria": {"latitude": 6.5244, "longitude": 3.3792, "location": "Lagos"},
}

WEATHER_COLUMNS = [
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "T2M_RANGE",
    "PRECTOTCORR",
    "RH2M",
    "WS2M",
    "WS2M_MAX",
    "PS",
    "QV2M",
]

ZSCORE_COLUMNS = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "WS2M", "WS2M_MAX"]


def _find_header_row(file_path: str | Path) -> int:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for idx, line in enumerate(file):
            normalized = line.strip().replace(" ", "")
            if "YEAR" in normalized and "DOY" in normalized:
                return idx
    return 0


def _read_nasa_power_csv(file_path: str | Path) -> pd.DataFrame:
    header_row = _find_header_row(file_path)
    return pd.read_csv(file_path, header=header_row)


def validate_expected_schema(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing expected columns from Data Legend: {missing_columns}")

    for col in EXPECTED_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def parse_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    invalid_doy = ~df["DOY"].between(1, 366)
    df.loc[invalid_doy, "DOY"] = np.nan
    df["DATE"] = pd.to_datetime(df["YEAR"] * 1000 + df["DOY"], format="%Y%j", errors="coerce")
    df["Month"] = df["DATE"].dt.month
    df["YearMonth"] = df["DATE"].dt.to_period("M").dt.to_timestamp()
    return df


def load_country_csv(file_path: str | Path, country: str) -> pd.DataFrame:
    df = _read_nasa_power_csv(file_path)
    df = validate_expected_schema(df)
    canonical_country = country.strip().title()
    df["Country"] = canonical_country

    metadata = COUNTRY_METADATA.get(canonical_country)
    if metadata:
        df["Latitude"] = metadata["latitude"]
        df["Longitude"] = metadata["longitude"]
        df["Location"] = metadata["location"]

    return parse_date_columns(df)


def sentinel_to_nan(df: pd.DataFrame, sentinel: float = -999) -> pd.DataFrame:
    return df.replace(sentinel, np.nan)


def duplicate_report(df: pd.DataFrame) -> tuple[int, list[str]]:
    duplicate_count = int(df.duplicated().sum())
    duplicate_columns: list[str] = []
    if duplicate_count:
        duplicate_rows = df[df.duplicated(keep=False)]
        duplicate_columns = [col for col in df.columns if duplicate_rows[col].nunique(dropna=False) > 1]
    return duplicate_count, duplicate_columns


def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


def missingness_table(df: pd.DataFrame) -> pd.DataFrame:
    missing_count = df.isna().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)
    out = pd.DataFrame({"missing_count": missing_count, "missing_pct": missing_pct})
    return out.sort_values("missing_pct", ascending=False)


def detect_outliers_zscore(df: pd.DataFrame, columns: Iterable[str] = ZSCORE_COLUMNS, threshold: float = 3.0) -> pd.DataFrame:
    cols = [col for col in columns if col in df.columns]
    z_matrix = pd.DataFrame(index=df.index)
    for col in cols:
        series = df[col].astype(float)
        z_matrix[col] = zscore(series, nan_policy="omit")
    outlier_mask = z_matrix.abs().gt(threshold).any(axis=1)
    return df.loc[outlier_mask].copy()


def clean_country_data(df: pd.DataFrame, drop_outliers: bool = False) -> tuple[pd.DataFrame, dict]:
    metrics: dict[str, int | float] = {}

    metrics["sentinel_minus999_count"] = int((df == -999).sum(numeric_only=False).sum())
    df = sentinel_to_nan(df)
    metrics["duplicates_before_drop"] = int(df.duplicated().sum())
    df = drop_duplicates(df)
    metrics["invalid_or_unparsed_dates"] = int(df["DATE"].isna().sum())

    outliers = detect_outliers_zscore(df)
    metrics["outlier_rows_flagged"] = int(len(outliers))

    if drop_outliers and len(outliers) > 0:
        df = df.drop(index=outliers.index)
        metrics["outlier_rows_dropped"] = int(len(outliers))
    else:
        metrics["outlier_rows_dropped"] = 0

    row_missing_ratio = df.isna().mean(axis=1)
    heavy_missing_mask = row_missing_ratio > 0.30
    metrics["rows_dropped_missing_gt_30pct"] = int(heavy_missing_mask.sum())
    df = df.loc[~heavy_missing_mask].copy()

    weather_cols = [col for col in WEATHER_COLUMNS if col in df.columns]
    df[weather_cols] = df[weather_cols].ffill()

    df = df.sort_values("DATE").reset_index(drop=True)
    metrics["rows_after_cleaning"] = int(len(df))

    return df, metrics


def export_clean_csv(df: pd.DataFrame, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
