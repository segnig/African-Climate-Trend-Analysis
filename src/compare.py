from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import f_oneway, kruskal

sns.set_theme(style="whitegrid")


def load_cleaned_countries(data_dir: str | Path, countries: list[str]) -> pd.DataFrame:
    data_dir = Path(data_dir)
    frames = []
    for country in countries:
        file_path = data_dir / f"{country.lower()}_clean.csv"
        df = pd.read_csv(file_path, parse_dates=["DATE"])
        df["Country"] = country.title()
        if "YearMonth" in df.columns:
            df["YearMonth"] = pd.to_datetime(df["YearMonth"])
        else:
            df["YearMonth"] = df["DATE"].dt.to_period("M").dt.to_timestamp()
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def summary_stats(df: pd.DataFrame, column: str) -> pd.DataFrame:
    out = df.groupby("Country")[column].agg(mean="mean", median="median", std="std").round(3)
    out = out.reset_index().sort_values(by="mean", ascending=False)
    return out.set_index("Country")


def extreme_heat_days(df: pd.DataFrame, threshold: float = 35.0) -> pd.DataFrame:
    tmp = df.copy()
    tmp["Year"] = tmp["DATE"].dt.year
    tmp["is_extreme_heat"] = tmp["T2M_MAX"] > threshold
    out = tmp.groupby(["Country", "Year"])["is_extreme_heat"].sum().reset_index()
    return out


def consecutive_dry_days(df: pd.DataFrame, precip_threshold: float = 1.0) -> pd.DataFrame:
    out_rows = []
    for country, country_df in df.sort_values("DATE").groupby("Country"):
        country_df = country_df.copy()
        country_df["Year"] = country_df["DATE"].dt.year
        for year, year_df in country_df.groupby("Year"):
            dry = (year_df["PRECTOTCORR"] < precip_threshold).astype(int)
            max_streak = 0
            current = 0
            for value in dry:
                if value == 1:
                    current += 1
                    max_streak = max(max_streak, current)
                else:
                    current = 0
            out_rows.append({"Country": country, "Year": year, "max_consecutive_dry_days": max_streak})
    return pd.DataFrame(out_rows)


def temperature_significance_test(df: pd.DataFrame, method: str = "anova") -> dict[str, float | str]:
    groups = [grp["T2M"].dropna().to_numpy() for _, grp in df.groupby("Country")]
    if method == "anova":
        stat, pvalue = f_oneway(*groups)
        return {"method": "ANOVA", "statistic": float(stat), "pvalue": float(pvalue)}
    stat, pvalue = kruskal(*groups)
    return {"method": "Kruskal-Wallis", "statistic": float(stat), "pvalue": float(pvalue)}


def plot_multi_country_t2m(df: pd.DataFrame, output_file: str | Path) -> None:
    monthly = df.groupby(["Country", "YearMonth"])["T2M"].mean().reset_index()
    plt.figure(figsize=(12, 5))
    sns.lineplot(data=monthly, x="YearMonth", y="T2M", hue="Country")
    plt.title("Monthly Average T2M by Country (2015–2026)")
    plt.xlabel("Month")
    plt.ylabel("Temperature (°C)")
    plt.tight_layout()
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_file), dpi=150)
    plt.close()
