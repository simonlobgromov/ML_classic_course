# -*- coding: utf-8 -*-
"""Reconnaissance of the lalafo-kg-phones listings table.

Goal: understand data shape, quality issues ("the mess") and which columns
map onto the topics students have studied (vectors, dot product / cosine,
descriptive stats + KDE + centroids, boxplots / IQR / RobustScaler).
Images are intentionally ignored.
"""
import re
import numpy as np
import pandas as pd

pd.set_option("display.width", 120)
df = pd.read_parquet("data/listings.parquet")


def h(title):
    print("\n" + "=" * 78 + f"\n{title}\n" + "=" * 78)


h("A. OVERVIEW")
print("shape:", df.shape)
print("memory MB:", round(df.memory_usage(deep=True).sum() / 1e6, 1))

h("B. NULL RATE (%) for analysis-relevant columns")
cols = ["title", "description", "price", "old_price", "national_price", "currency",
        "brand", "model", "condition", "color", "storage", "ram", "battery_health_pct",
        "device_class", "sim", "imei_status", "city", "region", "lat", "lng",
        "views", "impressions", "favorite_count", "callers_count", "writers_count",
        "is_negotiable", "is_vip", "is_premium", "image_count"]
nullpct = (df[cols].isna().mean() * 100).round(1).sort_values(ascending=False)
print(nullpct.to_string())

h("C. PRICE SANITY (the boxplot / outlier playground)")
print("currency counts:\n", df["currency"].value_counts(dropna=False).to_string())
p = df["price"]
print("\nprice describe:\n", p.describe().round(1).to_string())
qs = [0, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999, 1.0]
print("\nprice percentiles:")
print(p.quantile(qs).round(1).to_string())
print("\ngarbage-ish prices:")
print("  price <= 1 :", int((p <= 1).sum()))
print("  price <= 100 (≈ <$1.1):", int((p <= 100).sum()))
print("  price <= 500 :", int((p <= 500).sum()))
print("  price > 100000 (≈>$1100):", int((p > 100000).sum()))
print("  price > 1e6 :", int((p > 1e6).sum()))
print("  price is NaN :", int(p.isna().sum()))
# IQR fences on KGS prices only
kgs = df.loc[df["currency"] == "KGS", "price"].dropna()
q1, q3 = kgs.quantile([.25, .75])
iqr = q3 - q1
lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
print(f"\nKGS only: Q1={q1:.0f} Q3={q3:.0f} IQR={iqr:.0f} -> fences [{lo:.0f}, {hi:.0f}]")
print(f"  below low fence: {(kgs < lo).sum()} | above high fence: {(kgs > hi).sum()} ({(kgs>hi).mean()*100:.1f}%)")

h("D. CATEGORICALS")
for c in ["brand", "condition", "device_class", "city", "region"]:
    vc = df[c].value_counts(dropna=False).head(10)
    print(f"\n[{c}] nunique={df[c].nunique(dropna=True)}")
    print(vc.to_string())

h("E. storage / ram PARSING (string -> number, noise hunt)")
for c in ["storage", "ram"]:
    print(f"\n[{c}] raw unique values (top 20):")
    print(df[c].value_counts(dropna=False).head(20).to_string())


def to_gb(x):
    if not isinstance(x, str):
        return np.nan
    m = re.search(r"(\d+(?:[.,]\d+)?)", x)
    if not m:
        return np.nan
    v = float(m.group(1).replace(",", "."))
    if "тб" in x.lower() or "tb" in x.lower():
        v *= 1024
    return v


for c in ["storage", "ram"]:
    g = df[c].map(to_gb)
    print(f"\n[{c}] parsed GB describe:")
    print(g.describe().round(1).to_string())
    print(f"  suspicious {c} values:", sorted(g.dropna().unique().tolist())[:25])

h("F. battery_health_pct (stored as STRING -> needs parsing)")
raw = df["battery_health_pct"].dropna()
print("non-null count:", len(raw), f"({len(raw)/len(df)*100:.1f}%)  dtype:", df["battery_health_pct"].dtype)
print("raw sample values:", raw.unique()[:15].tolist())
b = raw.map(to_gb)  # reuse numeric extractor
print("parsed describe:\n", b.describe().round(1).to_string())
print("out of [0,100]:", int(((b < 0) | (b > 100)).sum()))

h("G. ENGAGEMENT metrics")
eng = ["views", "impressions", "favorite_count", "callers_count", "writers_count"]
print(df[eng].describe().round(1).to_string())
print("\nrows with views==0:", int((df["views"] == 0).sum()))
print("corr(views, favorite_count):", round(df["views"].corr(df["favorite_count"]), 3))
print("corr(views, callers_count):", round(df["views"].corr(df["callers_count"]), 3))

h("H. DUPLICATES / SPAM signals")
print("exact duplicate titles:", int(df["title"].duplicated().sum()))
print("exact duplicate descriptions:", int(df["description"].duplicated(keep=False).sum()),
      "(rows sharing text)")
print("\ntop repeated titles:")
print(df["title"].value_counts().head(6).to_string())
print("\nads per user (top sellers):")
print(df["user_id"].value_counts().head(6).to_string())
print("users with >=20 ads:", int((df["user_id"].value_counts() >= 20).sum()))

h("I. LANGUAGE MIX in title (Russian vs Kyrgyz vs Latin)")
ky = re.compile(r"[өүңӨҮҢ]")            # kyrgyz-specific cyrillic letters
lat = re.compile(r"[A-Za-z]")
cyr = re.compile(r"[А-Яа-яЁё]")
t = df["title"].fillna("")
print("titles with kyrgyz letters (ө/ү/ң):", int(t.str.contains(ky).sum()),
      f"({t.str.contains(ky).mean()*100:.1f}%)")
print("titles with latin letters        :", int(t.str.contains(lat).sum()),
      f"({t.str.contains(lat).mean()*100:.1f}%)")
print("titles with cyrillic letters      :", int(t.str.contains(cyr).sum()),
      f"({t.str.contains(cyr).mean()*100:.1f}%)")
print("title length describe:")
print(t.str.len().describe().round(1).to_string())

h("J. FEATURE-VECTOR readiness (numeric columns usable for vectors/cosine)")
num = df.select_dtypes("number")
usable = [c for c in num.columns if df[c].notna().mean() > 0.5 and df[c].nunique() > 5]
print("numeric cols with >50% filled & >5 unique:")
print(usable)
