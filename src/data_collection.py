"""
World Bank Economic Shock Dataset — Data Collection (Raw Phase)
===============================================================
Aligned with: Fiche de Cadrage — Projet Machine Learning
              Détecteur de Chocs Économiques — World Bank API

This script only collects and saves raw data.
Target variable (economic_shock) will be computed in a later step.

Features collected:
    - 8 core indicators  (cadrage §9)
    - 6 extra early-warning indicators
    - 2 engineered features (gdp_growth_lag1, gdp_growth_delta)
    - 1 engineered categorical (is_crisis_decade)
    - 3 country metadata columns (region, income_group, lending_type)

Expected output: ~13 000 rows × 20+ columns
"""

import numpy as np
import pandas as pd
import wbgapi as wb
import requests
from pathlib import Path


# ---------------------------------------------------------------------------
# 1.  Indicator catalogue (cadrage §9)
# ---------------------------------------------------------------------------

BASE_INDICATORS = {
    "gdp_growth":        "NY.GDP.MKTP.KD.ZG",    # GDP growth annual %
    "inflation":         "FP.CPI.TOTL.ZG",        # CPI inflation %
    "unemployment":      "SL.UEM.TOTL.ZS",        # Unemployment % labour force
    "gdp_per_capita":    "NY.GDP.PCAP.KD",        # GDP per capita USD constant
    "external_debt_pct": "DT.DOD.DECT.GN.ZS",    # External debt % GNI
    "trade_openness":    "NE.TRD.GNFS.ZS",        # Trade % GDP
    "fdi_inflows":       "BX.KLT.DINV.WD.GD.ZS", # FDI net inflows % GDP
    "gov_expenditure":   "GC.XPN.TOTL.GD.ZS",    # Govt expenditure % GDP
}

EXTRA_INDICATORS = {
    "current_account_pct":   "BN.CAB.XOKA.GD.ZS",  # Current account % GDP
    "fx_reserves_months":    "FI.RES.TOTL.MO",      # FX reserves (months of imports)
    "debt_service_pct":      "DT.TDS.DECT.EX.ZS",  # Debt service % exports
    "govt_debt_pct_gdp":     "GC.DOD.TOTL.GD.ZS",  # Central govt debt % GDP
    "domestic_credit_pct":   "FS.AST.DOMS.GD.ZS",  # Domestic credit % GDP
    "gni_per_capita_growth": "NY.GNP.PCAP.KD.ZG",  # GNI per capita growth %
}

ALL_INDICATORS = {**BASE_INDICATORS, **EXTRA_INDICATORS}


# ---------------------------------------------------------------------------
# 2.  Fetch raw indicator data
# ---------------------------------------------------------------------------

def fetch_indicators(
    country_codes=None,
    start_year: int = 1960,
    end_year:   int = 2022,
) -> pd.DataFrame:
    """
    Pull all indicators from the World Bank API via wbgapi.
    Returns a wide DataFrame: one row per (country, year).
    """
    if country_codes is None:
        country_codes = "all"

    frames = []
    print(f"\n📡 Fetching {len(ALL_INDICATORS)} indicators ({start_year}–{end_year})…\n")

    for col_name, wb_code in ALL_INDICATORS.items():
        try:
            raw = wb.data.DataFrame(
                wb_code,
                economy=country_codes,
                time=range(start_year, end_year + 1),
                skipBlanks=True,
                labels=False,
            )

            # wbgapi may return (economy × time) or (time × economy)
            # normalise so rows = time, columns = economy
            idx_name = raw.index.name or ""
            if "economy" in idx_name.lower():
                raw = raw.T

            long = raw.stack().reset_index()
            long.columns = ["year", "country", "value"]
            long["indicator"] = col_name
            frames.append(long)
            print(f"  ✔  {col_name:30s}  ({wb_code})")

        except Exception as exc:
            print(f"  ✗  {col_name:30s}  ({wb_code})  — {exc}")

    if not frames:
        raise RuntimeError("No data fetched. Check your internet connection.")

    long_df = pd.concat(frames, ignore_index=True)

    # Pivot to wide format: one row per (country, year)
    wide = long_df.pivot_table(
        index=["country", "year"],
        columns="indicator",
        values="value",
    ).reset_index()
    wide.columns.name = None

    # Normalise year to plain integer (wbgapi sometimes returns "YR2010")
    wide["year"] = (
        wide["year"].astype(str).str.extract(r"(\d{4})")[0].astype(int)
    )

    print(f"\n  → Raw shape: {wide.shape[0]:,} rows × {wide.shape[1]} columns")
    return wide






# ---------------------------------------------------------------------------
# 3.  Fetch country metadata (categorical features)
# ---------------------------------------------------------------------------

def fetch_country_metadata() -> pd.DataFrame:
    """
    Returns a DataFrame with static country-level categorical features:
        country, country_name, region, income_group, lending_type

    Uses the World Bank REST API directly (paginated) to avoid
    wbgapi version differences in economy.list() return types.
    """
    print("\nFetching country metadata…")

    BASE = "https://api.worldbank.org/v2/country"
    records = []
    page = 1

    while True:
        resp = requests.get(
            BASE,
            params={"per_page": 300, "page": page, "format": "json"},
            timeout=30,
        )
        resp.raise_for_status()
        payload   = resp.json()   # [meta_dict, [country, ...]]
        meta_info = payload[0]
        countries = payload[1] or []

        for c in countries:
            # region.id == "NA" is the World Bank flag for aggregates/regions
            region_id = (c.get("region") or {}).get("id", "")
            if region_id == "NA":
                continue

            records.append({
                "country":      c.get("id", ""),
                "country_name": c.get("name", ""),
                "region":       (c.get("region")      or {}).get("value", pd.NA),
                "income_group": (c.get("incomeLevel") or {}).get("value", pd.NA),
                "lending_type": (c.get("lendingType") or {}).get("value", pd.NA),
            })

        total_pages = int(meta_info.get("pages", 1))
        if page >= total_pages:
            break
        page += 1

    meta = pd.DataFrame(records)
    print(f"  → {len(meta)} individual economies loaded")
    return meta


# ---------------------------------------------------------------------------
# 4.  Engineered features (cadrage §9 — no target yet)
# ---------------------------------------------------------------------------

def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds three columns derived from gdp_growth:
        gdp_growth_lag1  — prior year's GDP growth (needed later for target)
        gdp_growth_delta — change in GDP growth vs prior year in pp
        is_crisis_decade — decade string label, e.g. '2000s'

    DataFrame must be sorted by (country, year) for lags to be correct.
    """
    df = df.sort_values(["country", "year"]).copy()

    df["gdp_growth_lag1"]  = df.groupby("country")["gdp_growth"].shift(1)
    df["gdp_growth_delta"] = df["gdp_growth"] - df["gdp_growth_lag1"]
    df["is_crisis_decade"] = (df["year"] // 10 * 10).astype(str) + "s"

    return df




#Optimized route

def chunked(iterable, size):
    """Yield chunks from iterable."""
    iterable = list(iterable)

    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]




# ---------------------------------------------------------------------------
# 5.  Main pipeline
# ---------------------------------------------------------------------------

def build_dataset(
    start_year:  int  = 1960,
    end_year:    int  = 2022,
    output_path: Path = Path("economic_shock_dataset_raw.csv"),
) -> pd.DataFrame:
    """
    Pipeline:
        1. Fetch indicators from World Bank API
        2. Fetch country metadata
        3. Merge on country code
        4. Add engineered features
        5. Save raw CSV (no target variable yet)
    """
    # Step 1 – time-series indicators
    wide = fetch_indicators(start_year=start_year, end_year=end_year)

    # Step 2 – static country metadata
    meta = fetch_country_metadata()

    # Step 3 – merge (left join: keeps all indicator rows even if metadata is missing)
    df = wide.merge(meta, on="country", how="left")

    # Step 4 – engineered features
    df = add_engineered_features(df)

    # Step 5 – save
    df.to_csv(output_path, index=False)
    print(f"\nRaw dataset saved → {output_path}")
    print(f"   Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"   Columns: {list(df.columns)}\n")

    return df


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    df = build_dataset(
        start_year=1960,
        end_year=2022,
        output_path=Path(__file__).parent.parent / "data" / "economic_shock_dataset_raw.csv"
    )