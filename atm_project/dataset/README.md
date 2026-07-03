---
license: cc-by-4.0
language:
- ru
pretty_name: MBank ATM Dataset (Bishkek 2024–2025)
tags:
- finance
- atm
- time-series
- anomaly-detection
- rfm
- kyrgyzstan
task_categories:
- time-series-forecasting
- tabular-classification
- tabular-regression
size_categories:
- 10M<n<100M
configs:
- config_name: fact_transactions
  data_files:
  - split: train
    path: facts/fact_transactions/**/*.parquet
- config_name: fact_cash_ops
  data_files: facts/fact_cash_ops.parquet
- config_name: fact_atm_status
  data_files: facts/fact_atm_status.parquet
- config_name: dim_atm
  data_files: dimensions/dim_atm.parquet
- config_name: dim_calendar
  data_files: dimensions/dim_calendar.parquet
- config_name: dim_customer
  data_files: dimensions/dim_customer.parquet
- config_name: dim_card
  data_files: dimensions/dim_card.parquet
- config_name: dim_district
  data_files: dimensions/dim_district.parquet
- config_name: labels_fraud
  data_files: labels/fraud.parquet
- config_name: labels_cash_events
  data_files: labels/cash_events.parquet
- config_name: labels_faults
  data_files: labels/faults.parquet
- config_name: labels_cold_start
  data_files: labels/cold_start.parquet
- config_name: labels_events
  data_files: labels/events.parquet
---

# MBank ATM Dataset (Bishkek, 2024–2025)

Per-second dataset of a network of **120 ATMs** over **731 days**
(2024-01-01 … 2025-12-31). Card-processing style records (ISO-8583-inspired),
grounded in the real-world context of Kyrgyzstan: ERA5 weather, the USD/KGS rate
of the National Bank of the KR, and ATM coordinates from OpenStreetMap.

Intended as a training ground: demand forecasting, ATM clustering, RFM analysis,
anomaly detection. Every anomaly has a checkable "answer key" in `labels/`.

---

## Google Colab — install & load (in the browser)

In a fresh Colab cell, install the libraries and download the dataset:

```python
# 1. Libraries (pandas/pyarrow ship with Colab; only the HF client is needed)
!pip install -q huggingface_hub datasets

# 2. Download the whole dataset in one call
from huggingface_hub import snapshot_download
path = snapshot_download("aiacademy-kg/mbank-atm-bishkek", repo_type="dataset")
print("Dataset at:", path)

# 3. Read tables with plain pandas
import pandas as pd
dim_atm  = pd.read_parquet(f"{path}/dimensions/dim_atm.parquet")
calendar = pd.read_parquet(f"{path}/dimensions/dim_calendar.parquet")
fraud    = pd.read_parquet(f"{path}/labels/fraud.parquet")
print(dim_atm.shape, calendar.shape)
```

**Transactions (12M rows) — read only the columns/months you need, not all at once:**

```python
import pyarrow.dataset as ds
tx = ds.dataset(f"{path}/facts/fact_transactions", partitioning="hive")
march = tx.to_table(
    filter=(ds.field("year") == 2024) & (ds.field("month") == 3),
    columns=["timestamp", "atm_id", "dispensed_amount", "response_code"],
).to_pandas()
print(march.shape)
```

**Or via 🤗 `datasets` (each table is a separate subset):**

```python
from datasets import load_dataset
tx  = load_dataset("aiacademy-kg/mbank-atm-bishkek", "fact_transactions", split="train")
atm = load_dataset("aiacademy-kg/mbank-atm-bishkek", "dim_atm", split="train")
# subsets: fact_transactions, fact_cash_ops, fact_atm_status, dim_atm, dim_calendar,
#          dim_customer, dim_card, dim_district, labels_fraud, labels_cash_events, …
```

If the dataset is private, authenticate first:
`from huggingface_hub import login; login("hf_YOUR_TOKEN")`.

---

## Quick start (local)

```python
import pandas as pd
import pyarrow.dataset as ds

# Reference tables
dim_atm = pd.read_parquet("dataset/dimensions/dim_atm.parquet")
cal     = pd.read_parquet("dataset/dimensions/dim_calendar.parquet")

# Transaction fact — 12M rows, partitioned by year/month. Read columnar / filtered:
tx = ds.dataset("dataset/facts/fact_transactions", partitioning="hive")
march = tx.to_table(filter=(ds.field("year") == 2024) & (ds.field("month") == 3),
                    columns=["timestamp","atm_id","dispensed_amount","response_code"]).to_pandas()

# Anomaly ground truth
fraud = pd.read_parquet("dataset/labels/fraud.parquet")
```

> ⚠️ `fact_transactions` is 12M rows (~727 MB). Don't load it whole — read the
> columns you need and filter by the `year=/month=` partitions.

---

## Folder layout

```
dataset/
├── README.md            ← this file
├── DATA_DICTIONARY.md   ← full field dictionary (types, values)
├── MANIFEST.md          ← auto-inventory: tables, row counts, sizes
├── dimensions/          ← reference tables (star schema)
│   ├── dim_district.parquet (+csv)   16 zones of Bishkek
│   ├── dim_calendar.parquet (+csv)   731 days: holidays, weather, FX rate
│   ├── dim_atm.parquet      (+csv)   120 ATMs (passport)
│   ├── dim_customer.parquet          550k customers
│   └── dim_card.parquet              700k cards (on-us)
├── facts/
│   ├── fact_transactions/            12M transactions, partitioned year=/month=
│   ├── fact_cash_ops.parquet         8.8k cash replenishments
│   └── fact_atm_status.parquet       9.8k status/downtime intervals
├── labels/              ← anomaly ground truth
│   ├── fraud.parquet          skimming + geo-impossibility
│   ├── cash_events.parquet    depletions (out_of_cash)
│   ├── faults.parquet         network faults / stuck terminals
│   ├── cold_start.parquet     new ATMs (truncated history)
│   ├── events.parquet         network-wide surges (FX shocks)
│   └── drift_spec.parquet     year-2 concept-drift parameters
└── external/            ← external real-world inputs (reference)
    ├── weather_daily.parquet  Open-Meteo ERA5 weather
    ├── fx_usd_kgs.parquet      NBKR exchange rate
    └── atm_locations.parquet   OSM coordinates
```

---

## Star schema (table relationships)

```
                    ┌──────────────┐
                    │ dim_calendar │  date
                    └──────┬───────┘
                           │ date
   ┌────────────┐   ┌──────┴────────────┐   ┌──────────────┐
   │ dim_district│──│  fact_transactions │──│  dim_atm     │
   └────────────┘   │      (12M)        │   └──────────────┘
      district_id   └──────┬─────┬──────┘      atm_id
                    card_id│     │customer_id
                     ┌─────┴──┐ ┌┴───────────┐
                     │dim_card│ │dim_customer│
                     └────────┘ └────────────┘
```

**Keys and relationships (JOIN):**

| From | Field | To | Note |
|---|---|---|---|
| fact_transactions | `atm_id` | dim_atm | ATM |
| fact_transactions | `district_id` | dim_district | zone (denormalized) |
| fact_transactions | `date` | dim_calendar | day (weekday/holiday/weather/FX) |
| fact_transactions | `card_id` | dim_card | card (on-us only; off-us → `OFFUS-*`, not in dim_card) |
| fact_transactions | `customer_id` | dim_customer | customer (null for off-us) |
| dim_card | `customer_id` | dim_customer | cardholder |
| fact_cash_ops / fact_atm_status | `atm_id` | dim_atm | ATM |

> **on-us vs off-us:** `is_on_us=True` — MBank card (present in `dim_card`/`dim_customer`).
> `is_on_us=False` — other bank / tourist: `card_id` like `OFFUS-*`, empty `customer_id`,
> an interchange `fee_amount` is charged.

---

## Anomaly ground truth (`labels/`)

Every anomaly is parameterized and logged — each task has a checkable answer.

| File | Anomaly | What to look for | Method |
|---|---|---|---|
| `cash_events` | Depletion 7.1 | withdrawal drop + `99` spike | rules, DBSCAN over day-ATM |
| `faults` | Network fault 7.2 / stuck 7.8 | `91/92/96` runs, flatlined telemetry | downtime detection, variance |
| `events` | Surge 7.3 | network-wide day anomaly (FX shock) | collective outlier |
| `cold_start` | New ATM 7.4 | truncated history | model robustness |
| `drift_spec` | Concept drift 7.6 | year-1 model degrades on year-2 | drift monitoring |
| `fraud` | Skimming 7.7 / geo 7.10 | night off-us runs, card at far ATMs | IsolationForest, velocity rules |

`fraud`/`cash_events` reference concrete `txn_id`/`atm_id`+interval in the fact
table, so labels can be matched exactly to transactions.

---

## External inputs (`external/`)

The dataset is grounded in real-world context of Kyrgyzstan — these series
**actually drive** behavior:

| File | Source | Effect in the data |
|---|---|---|
| `weather_daily` | Open-Meteo ERA5 (CC BY 4.0) | frost/snow → drop at street ATMs |
| `fx_usd_kgs` | National Bank of the KR | rate jump → cash run |
| `atm_locations` | OpenStreetMap (ODbL) | ATM coordinates (placement skeleton) |

Verified: frost on 16–17 Feb 2024 → street ATMs −22%; FX shock on 20 Mar 2025
(−1.41 KGS) → volume ×3.

Full field descriptions — in [DATA_DICTIONARY.md](DATA_DICTIONARY.md).
