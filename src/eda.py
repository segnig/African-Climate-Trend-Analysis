from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")


def monthly_temperature(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("YearMonth")["T2M"].mean().reset_index()
    out = out.rename(columns={"T2M": "monthly_avg_t2m"})
    return out


def monthly_precip(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("YearMonth")["PRECTOTCORR"].sum().reset_index()
    out = out.rename(columns={"PRECTOTCORR": "monthly_total_precip"})
    return out


def plot_monthly_t2m(df: pd.DataFrame, country: str, output_dir: str | Path) -> Path:
    monthly = monthly_temperature(df)
    monthly = monthly.reset_index(drop=True)
    monthly["x"] = monthly.index
    x_values = monthly["x"].to_numpy(dtype=float)
    y_values = monthly["monthly_avg_t2m"].to_numpy(dtype=float)
    warmest_idx = int(y_values.argmax())
    coolest_idx = int(y_values.argmin())
    warmest_x = x_values[warmest_idx]
    coolest_x = x_values[coolest_idx]
    warmest_y = y_values[warmest_idx]
    coolest_y = y_values[coolest_idx]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{country.lower()}_monthly_t2m.png"

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(monthly["x"], monthly["monthly_avg_t2m"], linewidth=2)
    ax.scatter([warmest_x, coolest_x], [warmest_y, coolest_y], zorder=3)
    ax.annotate("Warmest", (warmest_x, warmest_y))
    ax.annotate("Coolest", (coolest_x, coolest_y))
    tick_step = max(1, len(monthly) // 12)
    tick_pos = monthly["x"].iloc[::tick_step]
    tick_lbl = monthly["YearMonth"].dt.strftime("%Y-%m").iloc[::tick_step]
    ax.set_xticks(tick_pos)
    ax.set_xticklabels(tick_lbl, rotation=45)
    ax.set_title(f"{country}: Monthly Average T2M (2015–2026)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Temperature (°C)")
    fig.tight_layout()
    fig.savefig(str(out_file), dpi=150)
    plt.close(fig)
    return out_file


def plot_monthly_precip(df: pd.DataFrame, country: str, output_dir: str | Path) -> Path:
    monthly = monthly_precip(df)
    precip_values = monthly["monthly_total_precip"].to_numpy(dtype=float)
    peak_idx = int(precip_values.argmax())
    peak_val = precip_values[peak_idx]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{country.lower()}_monthly_precip.png"

    fig, ax = plt.subplots(figsize=(12, 4))
    x_positions = range(len(monthly))
    ax.bar(x_positions, monthly["monthly_total_precip"], width=0.9)
    ax.set_xticks(range(0, len(monthly), max(1, len(monthly) // 12)))
    ax.set_xticklabels(monthly["YearMonth"].dt.strftime("%Y-%m").iloc[:: max(1, len(monthly) // 12)], rotation=45)
    ax.set_title(f"{country}: Monthly Total PRECTOTCORR")
    ax.set_xlabel("Month")
    ax.set_ylabel("Precipitation (mm)")
    ax.annotate(
        "Peak rainy month",
        xy=(peak_idx, peak_val),
        xytext=(10, 10),
        textcoords="offset points",
    )
    fig.tight_layout()
    fig.savefig(str(out_file), dpi=150)
    plt.close(fig)
    return out_file


def plot_correlation_heatmap(df: pd.DataFrame, country: str, output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{country.lower()}_correlation_heatmap.png"

    numeric_df = df.select_dtypes(include="number")
    corr = numeric_df.corr(numeric_only=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, cmap="coolwarm", center=0, ax=ax)
    ax.set_title(f"{country}: Correlation Heatmap")
    fig.tight_layout()
    fig.savefig(str(out_file), dpi=150)
    plt.close(fig)
    return out_file
