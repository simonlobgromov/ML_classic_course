"""Anomaly injection and ground truth (TZ §7).

Adds structured, parameterised anomalies on top of the generated
fact_transactions and logs their ground truth to `labels/`, so each future
student task ("find the anomaly") has a checkable answer. Kept modest (~0.1-1%
of events, PaySim-calibrated).

Injected here (post-hoc over the fact table):
  §7.2  network/hardware faults  → downtime windows: 91/92/96, no dispense
  §7.8  stuck terminal           → flatline windows: constant amounts/telemetry
  §7.7  skimming/fraud           → night off-us magstripe bursts, atypical sums
  §7.10 geo-impossibility        → one card on far ATMs within minutes

Baked in elsewhere, only a label spec is written here:
  §7.1  out_of_cash  (cash_ops.py → labels/cash_events)
  §7.3  bank run     (intensity FX factor → labels/events)
  §7.4  cold start   (dim_atm.install_date → labels/cold_start)
  §7.5  holidays     (dim_calendar)
  §7.6  concept drift (intensity trend → labels/drift_spec)

Window anomalies rewrite the affected partitions; row injections (fraud, geo)
are appended to the matching year/month partition. fact_atm_status is extended
with the new fault/stuck intervals.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from . import PROJECT_ROOT
from .geography import ZONES

log = logging.getLogger(__name__)

FAULT_CODES = ["91", "92", "96"]


# --------------------------------------------------------------------------- #
# Planning: build event windows and injected rows before touching partitions
# --------------------------------------------------------------------------- #

def _plan_network_faults(atms, calendar, config, rng) -> list[dict]:
    """Random downtime windows per ATM (§7.2)."""
    cfg = config["anomalies"]["network_fault"]
    years = len(calendar) / 365.0
    lam = cfg["events_per_atm_year"] * years
    start = pd.Timestamp(calendar["date"].iloc[0])
    span_days = (pd.Timestamp(calendar["date"].iloc[-1]) - start).days

    windows = []
    for atm_id in atms["atm_id"]:
        for _ in range(rng.poisson(lam)):
            t0 = start + pd.Timedelta(days=int(rng.integers(0, span_days)),
                                      hours=int(rng.integers(0, 24)))
            dur = int(rng.integers(1, cfg["max_duration_hours"] + 1))
            windows.append(dict(atm_id=atm_id, start=t0,
                                end=t0 + pd.Timedelta(hours=dur),
                                kind=rng.choice(["network_down", "hardware_fault"])))
    return windows


def _plan_stuck(atms, calendar, config, rng) -> list[dict]:
    """Flatline windows across the network (§7.8)."""
    cfg = config["anomalies"]["stuck_terminal"]
    start = pd.Timestamp(calendar["date"].iloc[0])
    span_days = (pd.Timestamp(calendar["date"].iloc[-1]) - start).days
    picks = rng.choice(atms["atm_id"].to_numpy(), size=cfg["events_total"], replace=True)
    windows = []
    for atm_id in picks:
        t0 = start + pd.Timedelta(days=int(rng.integers(0, span_days)),
                                  hours=int(rng.integers(0, 24)))
        dur = int(rng.integers(2, cfg["max_duration_hours"] + 1))
        windows.append(dict(atm_id=atm_id, start=t0,
                            end=t0 + pd.Timedelta(hours=dur), kind="stuck"))
    return windows


def _blank_rows(n: int, template: pd.DataFrame) -> dict:
    """Column dict matching the fact schema, filled with neutral defaults."""
    d = {}
    for col in template.columns:
        dt = template[col].dtype
        if col in ("customer_id", "auth_code", "card_id"):
            d[col] = np.array([None] * n, dtype=object)
        elif pd.api.types.is_datetime64_any_dtype(dt):
            d[col] = np.empty(n, dtype="datetime64[ns]")
        elif pd.api.types.is_bool_dtype(dt):
            d[col] = np.zeros(n, dtype=bool)
        elif pd.api.types.is_numeric_dtype(dt):
            d[col] = np.zeros(n, dtype=dt)
        else:                                    # object / string / time
            d[col] = np.array([""] * n, dtype=object)
    return d


def _plan_fraud(atms, cards, calendar, template, config, rng, txn_id0) -> pd.DataFrame:
    """Night off-us magstripe bursts with atypical sums (§7.7)."""
    cfg = config["anomalies"]["fraud_skimming"]
    victims = rng.choice(atms["atm_id"].to_numpy(), size=cfg["n_atms_affected"], replace=False)
    start = pd.Timestamp(calendar["date"].iloc[0])
    span_days = (pd.Timestamp(calendar["date"].iloc[-1]) - start).days
    atm_lookup = atms.set_index("atm_id")

    rows = []
    for atm_id in victims:
        a = atm_lookup.loc[atm_id]
        for _ in range(cfg["bursts_per_atm"]):
            day = start + pd.Timedelta(days=int(rng.integers(0, span_days)))
            base = day + pd.Timedelta(hours=int(rng.integers(1, 5)))   # 01:00-04:59
            k = cfg["txns_per_burst"]
            ts = [base + pd.Timedelta(seconds=int(s))
                  for s in np.sort(rng.integers(0, 1800, size=k))]
            for t in ts:
                amt = int(rng.integers(15, 26)) * 1000 - int(rng.choice([0, 100, 300, 700]))
                rows.append((atm_id, a["terminal_id"], a["district_id"], t, amt))

    n = len(rows)
    d = _blank_rows(n, template)
    d["txn_id"] = np.arange(txn_id0, txn_id0 + n, dtype=np.int64)
    d["atm_id"] = np.array([r[0] for r in rows], dtype=object)
    d["terminal_id"] = np.array([r[1] for r in rows], dtype=object)
    d["district_id"] = np.array([r[2] for r in rows], dtype=object)
    ts = pd.to_datetime([r[3] for r in rows])
    d["timestamp"] = ts.values
    d["local_time"] = ts.time
    d["date"] = ts.normalize().values
    d["hour"] = ts.hour.to_numpy().astype(np.int8)
    amt = np.array([r[4] for r in rows], dtype=np.int64)
    d["requested_amount"] = amt
    d["dispensed_amount"] = amt
    d["is_on_us"] = np.zeros(n, dtype=bool)
    schemes = rng.choice(["Visa", "Mastercard", "UnionPay"], size=n)
    d["card_scheme"] = schemes.astype(object)
    d["card_bin"] = np.array([f"{rng.integers(400000, 700000)}" for _ in range(n)], dtype=object)
    d["card_id"] = np.array([f"OFFUS-{i:08d}" for i in rng.integers(0, 10**8, size=n)], dtype=object)
    d["mcc"] = np.full(n, 6011, dtype=np.int32)
    d["txn_type"] = np.full(n, "withdrawal", dtype=object)
    d["entry_mode"] = rng.choice(["magstripe", "fallback"], size=n).astype(object)
    d["currency"] = np.full(n, "KGS", dtype=object)
    d["fee_amount"] = np.full(n, 150, dtype=np.int32)
    d["fx_rate"] = np.ones(n)
    d["response_code"] = np.full(n, "00", dtype=object)
    d["is_approved"] = np.ones(n, dtype=bool)
    d["auth_code"] = np.array([f"{c:06d}" for c in rng.integers(0, 10**6, size=n)], dtype=object)
    d["pin_attempts"] = np.ones(n, dtype=np.int8)
    d["session_duration_s"] = rng.integers(15, 40, size=n).astype(np.int32)
    d["network_latency_ms"] = rng.integers(120, 1500, size=n).astype(np.int32)
    d["balance_after"] = np.full(n, -1, dtype=np.int64)
    d["device_cash_level_after"] = np.full(n, -1, dtype=np.int64)
    d["rrn"] = np.array([f"{v:012d}" for v in rng.integers(0, 10**12, size=n)], dtype=object)
    d["stan"] = rng.integers(1, 10**6, size=n).astype(np.int32)
    df = pd.DataFrame(d)[template.columns]
    df["_fraud_kind"] = "skimming"
    return df


def _plan_geo(atms, cards, calendar, template, config, rng, txn_id0) -> pd.DataFrame:
    """One card used on far-apart ATMs within minutes (§7.10)."""
    cfg = config["anomalies"]["geo_impossible"]
    start = pd.Timestamp(calendar["date"].iloc[0])
    span_days = (pd.Timestamp(calendar["date"].iloc[-1]) - start).days
    active = cards[cards["is_active"]].reset_index(drop=True)

    # Rank ATM pairs by distance; sample far pairs.
    a = atms.reset_index(drop=True)
    lat, lon = a["lat"].to_numpy(), a["lon"].to_numpy()

    rows = []
    for _ in range(cfg["n_cases"]):
        i = int(rng.integers(0, len(a)))
        d2 = (lat - lat[i]) ** 2 + (lon - lon[i]) ** 2
        j = int(np.argmax(d2))                       # farthest ATM
        card = active.iloc[int(rng.integers(0, len(active)))]
        t0 = start + pd.Timedelta(days=int(rng.integers(0, span_days)),
                                  hours=int(rng.integers(8, 22)))
        gap = int(rng.integers(60, 360))             # 1-6 minutes apart
        for atm_row, t in [(a.iloc[i], t0),
                           (a.iloc[j], t0 + pd.Timedelta(seconds=gap))]:
            amt = int(rng.integers(3, 15)) * 1000
            rows.append((atm_row, t, amt, card))

    n = len(rows)
    d = _blank_rows(n, template)
    d["txn_id"] = np.arange(txn_id0, txn_id0 + n, dtype=np.int64)
    d["atm_id"] = np.array([r[0]["atm_id"] for r in rows], dtype=object)
    d["terminal_id"] = np.array([r[0]["terminal_id"] for r in rows], dtype=object)
    d["district_id"] = np.array([r[0]["district_id"] for r in rows], dtype=object)
    ts = pd.to_datetime([r[1] for r in rows])
    d["timestamp"] = ts.values
    d["local_time"] = ts.time
    d["date"] = ts.normalize().values
    d["hour"] = ts.hour.to_numpy().astype(np.int8)
    amt = np.array([r[2] for r in rows], dtype=np.int64)
    d["requested_amount"] = amt
    d["dispensed_amount"] = amt
    d["is_on_us"] = np.ones(n, dtype=bool)
    d["card_id"] = np.array([r[3]["card_id"] for r in rows], dtype=object)
    d["customer_id"] = np.array([r[3]["customer_id"] for r in rows], dtype=object)
    d["card_scheme"] = np.array([r[3]["scheme"] for r in rows], dtype=object)
    d["card_bin"] = np.array([r[3]["bin"] for r in rows], dtype=object)
    d["mcc"] = np.full(n, 6011, dtype=np.int32)
    d["txn_type"] = np.full(n, "withdrawal", dtype=object)
    d["entry_mode"] = np.full(n, "chip", dtype=object)
    d["currency"] = np.full(n, "KGS", dtype=object)
    d["fx_rate"] = np.ones(n)
    d["response_code"] = np.full(n, "00", dtype=object)
    d["is_approved"] = np.ones(n, dtype=bool)
    d["auth_code"] = np.array([f"{c:06d}" for c in rng.integers(0, 10**6, size=n)], dtype=object)
    d["pin_attempts"] = np.ones(n, dtype=np.int8)
    d["session_duration_s"] = rng.integers(15, 60, size=n).astype(np.int32)
    d["network_latency_ms"] = rng.integers(120, 1500, size=n).astype(np.int32)
    d["balance_after"] = np.full(n, -1, dtype=np.int64)
    d["device_cash_level_after"] = np.full(n, -1, dtype=np.int64)
    d["rrn"] = np.array([f"{v:012d}" for v in rng.integers(0, 10**12, size=n)], dtype=object)
    d["stan"] = rng.integers(1, 10**6, size=n).astype(np.int32)
    df = pd.DataFrame(d)[template.columns]
    df["_fraud_kind"] = "geo_velocity"
    return df


# --------------------------------------------------------------------------- #
# Apply to partitions
# --------------------------------------------------------------------------- #

def _apply(root, windows, injections, template, rng) -> tuple[list, list]:
    """Rewrite partitions: apply fault/stuck windows and append injected rows."""
    status_rows, fault_labels = [], []
    inj_by_ym = {ym: df.drop(columns=["_fraud_kind"]) for ym, df in injections}

    for p in sorted(root.rglob("part.parquet")):
        parts = {x.split("=")[0]: x.split("=")[1] for x in p.parts if "=" in x}
        ym = f"{parts['year']}-{parts['month']}"
        df = pd.read_parquet(p)
        ts = df["timestamp"].to_numpy()
        atm = df["atm_id"].to_numpy()

        for w in windows:
            if w["end"] < df["timestamp"].iloc[0] or w["start"] > df["timestamp"].iloc[-1]:
                continue
            mask = (atm == w["atm_id"]) & (ts >= np.datetime64(w["start"])) & (ts < np.datetime64(w["end"]))
            k = int(mask.sum())
            if k == 0:
                continue
            if w["kind"] == "stuck":
                # Flatline: constant telemetry (zero variance is the tell). Leave
                # response_code / is_approved untouched so they stay consistent.
                fixed = int(df.loc[mask, "requested_amount"].iloc[0]) or 5000
                df.loc[mask, "session_duration_s"] = 30
                df.loc[mask, "network_latency_ms"] = 400
                cash_mask = mask & df["txn_type"].isin(
                    ["withdrawal", "fast_cash", "deposit"]).to_numpy() & df["is_approved"].to_numpy()
                df.loc[cash_mask, ["requested_amount", "dispensed_amount"]] = fixed
                status = "hardware_fault"
            else:
                df.loc[mask, "response_code"] = rng.choice(FAULT_CODES, size=k)
                df.loc[mask, "dispensed_amount"] = 0
                df.loc[mask, "is_approved"] = False
                df.loc[mask, "auth_code"] = ""
                status = w["kind"]
            status_rows.append(dict(atm_id=w["atm_id"], start_ts=w["start"], end_ts=w["end"],
                                    status=status, uptime_pct=0.0))
            fault_labels.append(dict(atm_id=w["atm_id"], start_ts=w["start"], end_ts=w["end"],
                                     kind=w["kind"], n_txns_affected=k))

        if ym in inj_by_ym:
            df = pd.concat([df, inj_by_ym[ym]], ignore_index=True)
            df = df.sort_values("timestamp", kind="stable").reset_index(drop=True)

        df.to_parquet(p, index=False)
    return status_rows, fault_labels


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

def inject_anomalies(config, tables, rng=None) -> dict:
    """Inject §7 anomalies, rewrite partitions, and write labels/."""
    if rng is None:
        rng = np.random.default_rng(config["seed"] + 5)

    atms = tables["dim_atm"]
    calendar = tables["dim_calendar"]
    cards = tables["dim_card"]
    data_dir = PROJECT_ROOT / config["output"]["data_dir"]
    root = data_dir / "fact_transactions"
    labels_dir = PROJECT_ROOT / "labels"
    labels_dir.mkdir(parents=True, exist_ok=True)

    parts = sorted(root.rglob("part.parquet"))
    template = pd.read_parquet(parts[0]).head(0)
    max_txn = max(int(pd.read_parquet(p, columns=["txn_id"])["txn_id"].max()) for p in parts)

    log.info("Anomalies: planning windows and injections …")
    windows = _plan_network_faults(atms, calendar, config, rng) + \
              _plan_stuck(atms, calendar, config, rng)
    fraud = _plan_fraud(atms, cards, calendar, template, config, rng, max_txn + 1)
    geo = _plan_geo(atms, cards, calendar, template, config, rng, max_txn + 1 + len(fraud))

    inj = pd.concat([fraud, geo], ignore_index=True)
    inj_by_ym = list(inj.assign(_ym=pd.to_datetime(inj["timestamp"]).dt.strftime("%Y-%m"))
                     .groupby("_ym"))
    inj_by_ym = [(ym, g.drop(columns=["_ym"])) for ym, g in inj_by_ym]

    log.info("Anomalies: applying to partitions (%d windows, %d injected rows) …",
             len(windows), len(inj))
    status_rows, fault_labels = _apply(root, windows, inj_by_ym, template, rng)

    # Extend fact_atm_status with the new fault/stuck intervals.
    status_path = data_dir / "fact_atm_status.parquet"
    new_status = pd.DataFrame(status_rows)
    if status_path.exists():
        old = pd.read_parquet(status_path)
        new_status.insert(0, "event_id", np.arange(len(old) + 1, len(old) + 1 + len(new_status)))
        pd.concat([old, new_status], ignore_index=True).to_parquet(status_path, index=False)
    else:
        new_status.insert(0, "event_id", np.arange(1, len(new_status) + 1))
        new_status.to_parquet(status_path, index=False)

    # Ground-truth labels.
    pd.DataFrame(fault_labels).to_parquet(labels_dir / "faults.parquet", index=False)
    fraud_labels = inj[["txn_id", "atm_id", "timestamp", "card_id", "_fraud_kind"]].rename(
        columns={"_fraud_kind": "kind"})
    fraud_labels.to_parquet(labels_dir / "fraud.parquet", index=False)
    _write_specs(atms, calendar, config, labels_dir)

    return {"fault_windows": len(windows),
            "fault_txns": int(sum(f["n_txns_affected"] for f in fault_labels)),
            "fraud_rows": len(fraud), "geo_rows": len(geo)}


def _write_specs(atms, calendar, config, labels_dir) -> None:
    """Label specs for baked-in anomalies (§7.3, §7.4, §7.6)."""
    # §7.3 bank run: FX-shock days already boosted network-wide by intensity.
    fx = calendar.loc[calendar["fx_shock"], ["date", "fx_change_pct"]].copy()
    fx["event_type"] = "bank_run"
    fx.to_parquet(labels_dir / "events.parquet", index=False)

    # §7.4 cold start: ATMs commissioned inside the period.
    start = pd.Timestamp(calendar["date"].iloc[0])
    cold = atms.loc[pd.to_datetime(atms["install_date"]) > start,
                    ["atm_id", "install_date", "atm_type"]]
    cold.to_parquet(labels_dir / "cold_start.parquet", index=False)

    # §7.6 concept drift: parameters of the year-2 trend.
    pd.DataFrame([{
        "year2_uplift": config["intensity"]["trend_year2_uplift"],
        "channel_shift": "chip→contactless/qr in year 2",
        "amount_inflation": 0.08,
    }]).to_parquet(labels_dir / "drift_spec.parquet", index=False)


def _smoke() -> None:
    from . import load_config
    from .build_dims import build_all_dims
    from .transactions import build_transactions
    from .cash_ops import build_cash_ops

    config = load_config()
    tables = build_all_dims(config)
    rng = np.random.default_rng(config["seed"])
    build_transactions(config, tables, rng, months=["2024-03"])
    build_cash_ops(config, tables, np.random.default_rng(config["seed"] + 1))

    summary = inject_anomalies(config, tables, np.random.default_rng(config["seed"] + 5))
    print("\n=== anomalies smoke (2024-03) ===")
    for k, v in summary.items():
        print(f"  {k:14s} {v:,}")

    labels = PROJECT_ROOT / "labels"
    for f in sorted(labels.glob("*.parquet")):
        n = len(pd.read_parquet(f))
        print(f"  labels/{f.name:20s} {n:,} rows")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    _smoke()
