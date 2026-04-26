from __future__ import annotations

import argparse
from pathlib import Path

from src.data_utils import COUNTRY_METADATA, clean_country_data, export_clean_csv, load_country_csv, missingness_table
from src.eda import plot_correlation_heatmap, plot_monthly_precip, plot_monthly_t2m


def main() -> None:
    parser = argparse.ArgumentParser(description="Run EDA cleaning pipeline for one country")
    parser.add_argument("--country", required=True, help="Country name e.g. ethiopia")
    parser.add_argument("--input", required=True, help="Path to raw CSV")
    parser.add_argument("--output", default="data", help="Output data directory")
    parser.add_argument("--figures", default="reports/figures", help="Output figures directory")
    args = parser.parse_args()

    country = args.country.strip().title()
    raw_df = load_country_csv(args.input, country)
    clean_df, metrics = clean_country_data(raw_df, drop_outliers=False)

    output_dir = Path(args.output)
    clean_path = output_dir / f"{country.lower()}_clean.csv"
    export_clean_csv(clean_df, clean_path)

    figures_dir = Path(args.figures)
    plot_monthly_t2m(clean_df, country, figures_dir)
    plot_monthly_precip(clean_df, country, figures_dir)
    plot_correlation_heatmap(clean_df, country, figures_dir)

    print(f"Saved cleaned data to: {clean_path}")
    country_meta = COUNTRY_METADATA.get(country)
    if country_meta:
        print(
            f"Representative location: {country_meta['location']} "
            f"({country_meta['latitude']}, {country_meta['longitude']})"
        )
    print("Cleaning metrics:")
    for key, value in metrics.items():
        print(f"  - {key}: {value}")

    print("\nMissingness summary (top 10):")
    print(missingness_table(clean_df).head(10))


if __name__ == "__main__":
    main()
