from __future__ import annotations

from pathlib import Path

import pandas as pd

COUNTRIES = ["ethiopia", "kenya", "sudan", "tanzania", "nigeria"]


def load_clean_data(data_dir: str | Path = "data") -> pd.DataFrame:
    data_dir = Path(data_dir)
    frames = []
    for country in COUNTRIES:
        file_path = data_dir / f"{country}_clean.csv"
        if not file_path.exists():
            continue
        df = pd.read_csv(file_path, parse_dates=["DATE"])
        df["Country"] = country.title()
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    combined["Year"] = combined["DATE"].dt.year
    combined["YearMonth"] = combined["DATE"].dt.to_period("M").dt.to_timestamp()
    return combined


def filter_data(df: pd.DataFrame, selected_countries: list[str], year_range: tuple[int, int]) -> pd.DataFrame:
    if df.empty:
        return df
    start_year, end_year = year_range
    return df[(df["Country"].isin(selected_countries)) & (df["Year"].between(start_year, end_year))]
