# -*- coding: utf-8 -*-
"""Reconnaissance of the lalafo-kg-cars listings table.

Same goal as the phones recon: understand shape, quality issues ("the mess")
and which columns map onto the taught topics (vectors, dot product / cosine,
descriptive stats + KDE + centroids, boxplots / IQR / RobustScaler).
NO correlation coefficient anywhere (students haven't covered it). Images ignored.
"""
import re
import numpy as np
import pandas as pd

pd.set_option("display.width", 130)
df = pd.read_parquet("data/listings.parquet")


def h(t): print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def num(x):
    if not isinstance(x, str):
        return np.nan
    m = re.search(r"(\d+(?:[.,]\d+)?)", x)
    return float(m.group(1).replace(",", ".")) if m else np.nan


df["year_n"]    = df["year"].map(num)
df["mileage_n"] = df["mileage_km"].map(num)
df["engine_n"]  = df["engine_volume_l"].map(num)

h("A. OVERVIEW")
print("shape:", df.shape)

h("B. NULL RATE (%)")
cols = ["price", "currency", "brand", "model", "year", "mileage_km", "engine_volume_l",
        "fuel", "transmission", "body_type", "drive", "condition", "technical_condition",
        "customs_cleared", "registration_country", "battery_capacity", "color",
        "views", "callers_count", "favorite_count"]
print((df[cols].isna().mean() * 100).round(1).sort_values(ascending=False).to_string())

h("C. PRICE (currency mix + outliers)")
print("currency:\n", df["currency"].value_counts(dropna=False).head().to_string())
p = df["price"]
print("\ndescribe:\n", p.describe().round(0).to_string())
print("\npercentiles:")
print(p.quantile([0, .01, .05, .25, .5, .75, .95, .99, .999, 1]).round(0).to_string())
print("\ngarbage: price<=1:", int((p <= 1).sum()), "| <=100:", int((p <= 100).sum()),
      "| >1e7:", int((p > 1e7).sum()), "| NaN:", int(p.isna().sum()))
# USD vs KGS medians (cars are often listed in USD!)
for c in ["KGS", "USD"]:
    s = df.loc[df["currency"] == c, "price"].dropna()
    if len(s):
        print(f"  {c}: n={len(s)} median={s.median():.0f}")

h("D. YEAR / MILEAGE / ENGINE (string -> number, garbage hunt)")
print("year_n describe:\n", df["year_n"].describe().round(1).to_string())
print("  year <1950:", int((df.year_n < 1950).sum()), "| >2026:", int((df.year_n > 2026).sum()))
print("\nmileage_n describe:\n", df["mileage_n"].describe().round(0).to_string())
print("  mileage==0:", int((df.mileage_n == 0).sum()), "| <1000:", int((df.mileage_n < 1000).sum()),
      "| >1e6:", int((df.mileage_n > 1e6).sum()))
print("\nengine_n describe:\n", df["engine_n"].describe().round(2).to_string())
print("  engine==0:", int((df.engine_n == 0).sum()), "| >8:", int((df.engine_n > 8).sum()))

h("E. CATEGORICALS")
for c in ["brand", "fuel", "transmission", "body_type", "drive",
          "customs_cleared", "registration_country", "condition", "technical_condition"]:
    vc = df[c].value_counts(dropna=False).head(8)
    print(f"\n[{c}] nunique={df[c].nunique()}")
    print(vc.to_string())

h("F. battery_capacity availability by fuel (EV-only trap?)")
df["has_batt"] = df["battery_capacity"].notna()
print((df.groupby("fuel")["has_batt"].mean() * 100).round(0).sort_values(ascending=False).head(6).to_string())

h("G. ENGAGEMENT")
print(df[["views", "impressions", "favorite_count", "callers_count", "writers_count"]].describe().round(0).to_string())

h("H. DUPLICATES / DEALERS (автосалоны)")
print("dup titles:", int(df["title"].duplicated().sum()))
print("ads per user (top):")
print(df["user_id"].value_counts().head(6).to_string())
print("users with >=20 ads:", int((df["user_id"].value_counts() >= 20).sum()))
print("share of ads from such users: %.1f%%" %
      (df["user_id"].map(df["user_id"].value_counts() >= 20).mean() * 100))

h("I. SIGNAL CHECKS (no correlation, medians only)")
kgs = df[(df.currency == "KGS") & df.price.notna()].copy()
q1, q3 = kgs.price.quantile([.25, .75]); iqr = q3 - q1
clean = kgs[(kgs.price >= 30000) & (kgs.price <= q3 + 1.5 * iqr)].copy()
print("KGS clean n=", len(clean))
print("\nmedian price by YEAR (depreciation ladder):")
byyear = clean[clean.year_n.between(2000, 2025)].groupby(clean.year_n.astype("Int64")).price.median()
print(byyear.round(0).to_string())
print("\nmedian price by BRAND (top-10 by count):")
tb = clean.brand.value_counts().head(10).index
print(clean[clean.brand.isin(tb)].groupby("brand").price.median().sort_values().round(0).to_string())
print("\nmedian price by MILEAGE bucket:")
mb = clean[clean.mileage_n.between(1, 500000)].copy()
mb["mbucket"] = pd.cut(mb.mileage_n, [0, 50000, 100000, 150000, 200000, 300000, 500000])
print(mb.groupby("mbucket", observed=True).price.median().round(0).to_string())
print("\nmedian price by TRANSMISSION:")
print(clean.groupby("transmission").price.median().sort_values().round(0).to_string())
