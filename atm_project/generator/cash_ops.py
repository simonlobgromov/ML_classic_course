"""Cash management: balances, replenishments and out-of-cash events (TZ §6).

Walks the generated fact_transactions per ATM in chronological order, tracks the
running cash balance, issues replenishments and detects depletion:

  - balance starts at cash_capacity, drops by dispensed_amount each cash op;
  - a replenishment is triggered when the balance falls below 15% of capacity;
  - the crew arrives after a route-dependent lag (0-2 days), so under heavy
    demand the ATM can run dry first → out_of_cash: further cash requests get
    dispensed=0 / response_code='99' (§6, §7.1);
  - device_cash_level_after is filled back into fact_transactions.

Outputs:
  - fact_cash_ops    (refills: amounts, balances, cassette breakdown)   §3.7
  - fact_atm_status  (out_of_cash / low_cash intervals, uptime)         §3.8
  - labels/cash_events (ground truth of depletions)                     §7.1
  - rewrites fact_transactions partitions with device_cash_level_after
    and '99' codes in depletion windows.

Only balance-driven statuses live here; hardware/network faults are anomalies
handled by anomalies.py (Step 5). All state transitions are found with
searchsorted over cumulative dispense — a loop over refill cycles (~130 per ATM),
never over individual transactions (§8).
"""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from . import PROJECT_ROOT

log = logging.getLogger(__name__)

CASH_TXN_TYPES = ("withdrawal", "fast_cash", "deposit")
LOW_CASH_FRACTION = 0.25          # default replenishment threshold (config overrides)
MAX_REFILL_LAG_DAYS = 1           # default crew arrival lag (config overrides)


# --------------------------------------------------------------------------- #
# Per-ATM cash simulation
# --------------------------------------------------------------------------- #

def _cassette_breakdown(amount: int, denoms, rng) -> str:
    """Split a loaded amount across denominations (larger notes carry most)."""
    ds = sorted(int(d) for d in denoms)
    bd = {}
    remaining = int(amount)
    for d in reversed(ds[1:]):
        take = int((remaining * rng.uniform(0.35, 0.65)) // d)
        bd[str(d)] = take
        remaining -= take * d
    bd[str(ds[0])] = max(0, remaining // ds[0])
    return json.dumps(bd)


def _simulate_atm(df_atm: pd.DataFrame, atm: pd.Series, rng,
                  cash_after: np.ndarray, force99: np.ndarray,
                  cash_ops_rows: list, status_rows: list, label_rows: list,
                  low_frac: float, max_lag: int) -> None:
    """Simulate one ATM's cash balance; append events; fill global update arrays."""
    ts = df_atm["timestamp"].to_numpy()
    disp = df_atm["dispensed_amount"].to_numpy().astype(np.int64)
    tid = df_atm["txn_id"].to_numpy()
    is_cash = df_atm["txn_type"].isin(CASH_TXN_TYPES).to_numpy()
    n = len(df_atm)

    capacity = int(atm["cash_capacity"])
    threshold = low_frac * capacity
    denoms = atm["denominations"]
    route = atm["service_route_id"]
    atm_id = atm["atm_id"]

    cum = np.cumsum(disp)
    base = 0.0                      # cumulative dispense at last refill
    start_balance = float(capacity)
    pos = 0

    while pos < n:
        # Balance(i) = start_balance - (cum[i] - base). Trigger when < threshold.
        trigger_level = base + (start_balance - threshold)
        idx_thr = int(np.searchsorted(cum, trigger_level, side="left"))
        if idx_thr >= n:
            seg = slice(pos, n)
            cash_after[tid[seg] - 1] = (start_balance - (cum[seg] - base)).astype(np.int64)
            break

        # Crew arrives after a route-dependent lag.
        lag = int(rng.integers(0, max_lag + 1))
        refill_time = ts[idx_thr] + np.timedelta64(lag, "D")
        idx_refill = int(np.searchsorted(ts, refill_time, side="left"))
        idx_refill = min(max(idx_refill, pos + 1), n)

        # Depletion (balance ≤ 0) before the crew arrives?
        depl_level = base + start_balance
        idx_depl = int(np.searchsorted(cum, depl_level, side="left"))

        seg = slice(pos, idx_refill)
        bal = start_balance - (cum[seg] - base)

        # low_cash interval from trigger to refill.
        status_rows.append(dict(
            atm_id=atm_id, start_ts=pd.Timestamp(ts[idx_thr]),
            end_ts=pd.Timestamp(refill_time), status="low_cash", uptime_pct=1.0))

        if idx_depl < idx_refill:
            # Ran dry: cash requests from idx_depl onward fail with '99'.
            window = np.arange(idx_depl, idx_refill)
            dry = window[is_cash[idx_depl:idx_refill]]
            force99[tid[dry] - 1] = True
            bal = np.clip(bal, 0, None)
            status_rows.append(dict(
                atm_id=atm_id, start_ts=pd.Timestamp(ts[idx_depl]),
                end_ts=pd.Timestamp(refill_time), status="out_of_cash", uptime_pct=0.0))
            label_rows.append(dict(
                atm_id=atm_id, start_ts=pd.Timestamp(ts[idx_depl]),
                end_ts=pd.Timestamp(refill_time), event_type="out_of_cash",
                n_declined=int(len(dry))))

        cash_after[tid[seg] - 1] = bal.astype(np.int64)

        if idx_refill >= n:
            break

        # Record the refill at idx_refill (balance restored to capacity).
        balance_before = int(max(0.0, start_balance - (cum[idx_refill - 1] - base)))
        amount_loaded = capacity - balance_before
        cash_ops_rows.append(dict(
            atm_id=atm_id, timestamp=pd.Timestamp(refill_time), op_type="refill",
            amount_loaded=amount_loaded, balance_before=balance_before,
            balance_after=capacity, service_route_id=route,
            cassette_breakdown=_cassette_breakdown(amount_loaded, denoms, rng)))

        base = float(cum[idx_refill - 1])
        start_balance = float(capacity)
        pos = idx_refill


# --------------------------------------------------------------------------- #
# Partition IO
# --------------------------------------------------------------------------- #

def _load_light(root: Path) -> pd.DataFrame:
    """Load only the columns needed for the cash simulation from all partitions."""
    cols = ["txn_id", "atm_id", "timestamp", "dispensed_amount", "txn_type"]
    frames = [pd.read_parquet(p, columns=cols) for p in sorted(root.rglob("part.parquet"))]
    df = pd.concat(frames, ignore_index=True)
    df["atm_id"] = df["atm_id"].astype("category")
    df["txn_type"] = df["txn_type"].astype("category")
    return df


def _apply_updates(root: Path, cash_after: np.ndarray, force99: np.ndarray) -> None:
    """Rewrite partitions with device_cash_level_after and '99' depletion codes."""
    for p in sorted(root.rglob("part.parquet")):
        df = pd.read_parquet(p)
        tid = df["txn_id"].to_numpy() - 1
        df["device_cash_level_after"] = cash_after[tid]
        f99 = force99[tid]
        if f99.any():
            df.loc[f99, "response_code"] = "99"
            df.loc[f99, "dispensed_amount"] = 0
            df.loc[f99, "is_approved"] = False
            df.loc[f99, "auth_code"] = ""
        df.to_parquet(p, index=False)


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

def build_cash_ops(config: dict, tables: dict, rng=None) -> dict:
    """Simulate cash management over the generated fact_transactions."""
    if rng is None:
        rng = np.random.default_rng(config["seed"])

    atms = tables["dim_atm"].set_index("atm_id", drop=False)
    data_dir = PROJECT_ROOT / config["output"]["data_dir"]
    root = data_dir / "fact_transactions"

    log.info("Cash: loading transaction stream …")
    light = _load_light(root)
    total_txn = int(light["txn_id"].max())
    cash_after = np.full(total_txn, -1, dtype=np.int64)
    force99 = np.zeros(total_txn, dtype=bool)

    cash_cfg = config.get("cash", {})
    low_frac = cash_cfg.get("low_cash_fraction", LOW_CASH_FRACTION)
    max_lag = cash_cfg.get("max_refill_lag_days", MAX_REFILL_LAG_DAYS)

    cash_ops_rows, status_rows, label_rows = [], [], []
    log.info("Cash: simulating %d ATMs …", atms.shape[0])
    for atm_id, df_atm in light.groupby("atm_id", observed=True, sort=False):
        df_atm = df_atm.sort_values("timestamp", kind="stable")
        _simulate_atm(df_atm, atms.loc[atm_id], rng,
                      cash_after, force99, cash_ops_rows, status_rows, label_rows,
                      low_frac, max_lag)

    log.info("Cash: rewriting partitions with balances / '99' codes …")
    _apply_updates(root, cash_after, force99)

    # Assemble and write the new fact tables + ground-truth labels.
    cash_ops = pd.DataFrame(cash_ops_rows)
    cash_ops.insert(0, "op_id", np.arange(1, len(cash_ops) + 1))
    status = pd.DataFrame(status_rows)
    status.insert(0, "event_id", np.arange(1, len(status) + 1))
    labels = pd.DataFrame(label_rows)

    cash_ops.to_parquet(data_dir / "fact_cash_ops.parquet", index=False)
    status.to_parquet(data_dir / "fact_atm_status.parquet", index=False)
    labels_dir = PROJECT_ROOT / "labels"
    labels_dir.mkdir(parents=True, exist_ok=True)
    labels.to_parquet(labels_dir / "cash_events.parquet", index=False)

    return {"refills": len(cash_ops),
            "status_events": len(status),
            "out_of_cash": int((status["status"] == "out_of_cash").sum()) if len(status) else 0,
            "declined_99": int(force99.sum())}


def _smoke() -> None:
    from . import load_config
    from .build_dims import build_all_dims
    from .transactions import build_transactions

    config = load_config()
    tables = build_all_dims(config)
    rng = np.random.default_rng(config["seed"])
    build_transactions(config, tables, rng, months=["2024-03"])

    rng2 = np.random.default_rng(config["seed"] + 1)
    summary = build_cash_ops(config, tables, rng2)
    print("\n=== cash_ops smoke (2024-03) ===")
    for k, v in summary.items():
        print(f"  {k:14s} {v:,}")

    data_dir = PROJECT_ROOT / config["output"]["data_dir"]
    ops = pd.read_parquet(data_dir / "fact_cash_ops.parquet")
    part = data_dir / "fact_transactions" / "year=2024" / "month=03" / "part.parquet"
    tx = pd.read_parquet(part)
    print(f"\nrefill amount mean: {ops['amount_loaded'].mean():,.0f} KGS")
    print(f"device_cash_level_after filled: "
          f"{(tx['device_cash_level_after'] >= 0).mean():.3f} of rows")
    print(f"'99' share after cash sim: {(tx['response_code'] == '99').mean():.4f}")
    print("cassette_breakdown sample:", ops["cassette_breakdown"].iloc[0])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    _smoke()
