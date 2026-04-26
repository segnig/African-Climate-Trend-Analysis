from __future__ import annotations

import json
from pathlib import Path

from src.compare import (
    consecutive_dry_days,
    extreme_heat_days,
    load_cleaned_countries,
    plot_multi_country_t2m,
    summary_stats,
    temperature_significance_test,
)

COUNTRIES = ["ethiopia", "kenya", "sudan", "tanzania", "nigeria"]


def main() -> None:
    data_dir = Path("data")
    reports_dir = Path("reports")
    figures_dir = reports_dir / "figures"
    tables_dir = reports_dir / "tables"
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    df = load_cleaned_countries(data_dir=data_dir, countries=COUNTRIES)

    plot_multi_country_t2m(df, figures_dir / "compare_monthly_t2m.png")

    t2m_stats = summary_stats(df, "T2M")
    precip_stats = summary_stats(df, "PRECTOTCORR")
    heat_days = extreme_heat_days(df)
    dry_days = consecutive_dry_days(df)

    t2m_stats.to_csv(tables_dir / "t2m_summary_stats.csv")
    precip_stats.to_csv(tables_dir / "precip_summary_stats.csv")
    heat_days.to_csv(tables_dir / "extreme_heat_days_by_year.csv", index=False)
    dry_days.to_csv(tables_dir / "max_consecutive_dry_days_by_year.csv", index=False)

    anova = temperature_significance_test(df, method="anova")
    kruskal = temperature_significance_test(df, method="kruskal")
    with open(tables_dir / "significance_tests.json", "w", encoding="utf-8") as f:
        json.dump({"anova": anova, "kruskal": kruskal}, f, indent=2)

    print("Cross-country outputs saved under reports/")


if __name__ == "__main__":
    main()
