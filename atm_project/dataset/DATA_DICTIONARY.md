# DATA DICTIONARY

Every table in the MBank ATM dataset, field by field. Types are as stored in
Parquet. See also [README.md](README.md).

---

## dimensions/dim_district — zones of Bishkek (16 rows)

Districts/zones ATMs and customers are attached to. PK: `district_id`.

| Field | Type | Description |
|---|---|---|
| `district_id` | string | zone ID (`ZN-*`), primary key |
| `name` | string | zone name (RU) |
| `admin_district` | string | Bishkek admin district (Sverdlovsky/Leninsky/Pervomaisky/Oktyabrsky) |
| `zone_type` | string | type: central/market/transit/residential/suburb/industrial |
| `population_density` | double | relative resident share (0..1) |
| `business_share` | double | share of business activity in the zone (0..1) |
| `lat_center`, `lon_center` | double | zone center coordinates |

---

## dimensions/dim_calendar — calendar (731 rows)

One day = one row. All temporal seasonality + weather and FX rate. PK: `date`.

| Field | Type | Description |
|---|---|---|
| `date` | timestamp | date (key) |
| `dow` | int | day of week (0=Mon … 6=Sun) |
| `is_weekend` | bool | weekend |
| `month` | int | month (1–12) |
| `holiday_name` | string | KR holiday name or null |
| `is_holiday` | bool | official public holiday |
| `is_pre_holiday` | bool | pre-holiday day (shopping peak) |
| `is_ramadan` | bool | Ramadan (Orozo) fasting period |
| `is_pension_day` | bool | pension payout window (10th–14th) |
| `is_payday` | bool | salary window (10th–14th and 25th–27th) |
| `season` | string | winter/spring/summer/autumn |
| `temp_avg` | double | mean temperature °C (ERA5) |
| `precip_mm` | double | precipitation, mm |
| `snowfall_mm` | double | snowfall, mm |
| `wind_max` | double | max wind, m/s |
| `weathercode` | int | WMO weather code |
| `usd_kgs_rate` | double | USD/KGS rate (NBKR) |
| `fx_change_pct` | double | daily rate change, % |
| `fx_shock` | bool | day of a sharp rate move (>0.7%) |
| `year_index` | int | 0 = year 1 (2024), 1 = year 2 (2025) |

---

## dimensions/dim_atm — ATM passport (120 rows)

PK: `atm_id`. `atm_type` is a latent archetype driving behavior (the target in clustering).

| Field | Type | Description |
|---|---|---|
| `atm_id` | string | ATM ID (`ATM-####`), key |
| `terminal_id` | string | terminal TID |
| `district_id` | string | zone (→ dim_district) |
| `location_name` | string | location name |
| `lat`, `lon` | double | coordinates (from the OSM pool) |
| `atm_type` | string | archetype: transport_market/office_business/residential/shopping_mall/tourist_center/pension_social/highway_gas |
| `placement` | string | street/indoor_branch/mall/gas_station |
| `is_24_7` | bool | open 24/7 |
| `firmware_version` | string | firmware version |
| `supports_nfc` | bool | contactless |
| `supports_qr` | bool | QR withdrawal |
| `is_recycler` | bool | recycler (accepts cash) |
| `supports_fx` | bool | currency operations |
| `num_cassettes` | int | cassette count (3–4) |
| `denominations` | list<int> | cassette denominations, KGS |
| `cash_capacity` | int | cash capacity, KGS |
| `txn_limit` | int | per-operation limit = 40 notes × median denomination (30k/40k/60k) |
| `daily_limit` | int | daily limit: 100k fee-free, up to 225k by tariff (MBank) |
| `service_route_id` | string | replenishment route |
| `install_date` | timestamp | commissioning date (12% inside the period → cold start) |
| `last_service_date` | timestamp | last service |
| `base_intensity` | double | baseline daily intensity λ0 (withdrawals/day) |

---

## dimensions/dim_customer — customers (550,000 rows)

On-us MBank customer base. PK: `customer_id`.

| Field | Type | Description |
|---|---|---|
| `customer_id` | string | customer ID (`CUST-#######`), key |
| `home_district_id` | string | home zone (→ dim_district) |
| `age_band` | string | 18-25/26-35/36-50/51-65/65+ |
| `gender` | string | M/F |
| `income_source` | string | salary/pension/social/business/remittance/student |
| `income_band` | string | low/mid/high |
| `segment` | string | mass/payroll/pensioner/affluent |
| `is_migrant_family` | bool | remittance receiver |
| `customer_since` | timestamp | account open date |
| `preferred_channel` | string | atm/mobile/branch (mobile → substitution in year 2) |

---

## dimensions/dim_card — cards (700,000 rows)

On-us MBank cards only. Off-us cards are not here. PK: `card_id`.

| Field | Type | Description |
|---|---|---|
| `card_id` | string | card ID (`CARD-########`), key |
| `customer_id` | string | owner (→ dim_customer) |
| `scheme` | string | Elcart/Visa/Mastercard/UnionPay/Mir |
| `bin` | string | first 6 digits (issuer/scheme) |
| `product` | string | debit_salary/debit_pension/debit_social/debit_classic/credit/virtual |
| `is_on_us` | bool | always True (MBank card) |
| `issuer_bank` | string | MBank |
| `issue_date`, `expiry` | timestamp | issue and expiry |
| `is_active` | bool | active |
| `contactless_enabled` | bool | contactless enabled |

---

## facts/fact_transactions — main fact (12,561,940 rows)

One row = one operation, to the second. Partitions `year=YYYY/month=MM/`. PK: `txn_id`.
Card-processing style fields (ISO-8583-inspired).

| Field | Type | Description |
|---|---|---|
| `txn_id` | int64 | running ID (contiguous 1..N), key |
| `rrn` | string | Retrieval Reference Number (12 digits) |
| `stan` | int | System Trace Audit Number |
| `timestamp` | timestamp | operation moment, **to the second** |
| `local_time` | time | terminal local time |
| `atm_id` | string | ATM (→ dim_atm) |
| `terminal_id` | string | TID |
| `district_id` | string | zone (denormalized, → dim_district) |
| `card_id` | string | card; on-us → `CARD-*` (dim_card), off-us → `OFFUS-*` |
| `customer_id` | string | customer (→ dim_customer); **null for off-us** |
| `card_scheme` | string | Elcart/Visa/Mastercard/UnionPay/Mir |
| `card_bin` | string | BIN (6 digits) |
| `is_on_us` | bool | MBank card (on-us) or other bank (off-us) |
| `mcc` | int | 6011 (ATM cash) |
| `txn_type` | string | withdrawal/fast_cash/balance_inquiry/mini_statement/transfer/deposit |
| `entry_mode` | string | chip/contactless/qr/magstripe/fallback |
| `requested_amount` | int | requested amount, KGS (0 for non-cash) |
| `dispensed_amount` | int | actually dispensed, KGS (≤ requested; 0 on decline / empty ATM) |
| `currency` | string | KGS |
| `fee_amount` | int | fee (off-us ~100–200, else 0) |
| `fx_rate` | double | rate if a currency operation (else 1.0) |
| `response_code` | string | `00` ok / `51` insufficient funds / `55` wrong PIN / `91` issuer unavailable / `92` no link / `94` duplicate / `96` malfunction / `99` out of cash |
| `is_approved` | bool | approved (equiv. `response_code=='00'`) |
| `auth_code` | string | authorization code (if approved) |
| `pin_attempts` | int8 | PIN attempts (1–3) |
| `session_duration_s` | int | session duration, s |
| `network_latency_ms` | int | authorization latency, ms |
| `is_remittance_cashout` | bool | cash-out of an incoming remittance |
| `balance_after` | int | account balance (-1 = not requested) |
| `device_cash_level_after` | int | **cash remaining in the ATM after the operation, KGS** |
| `date` | timestamp | date (for joins/partitions) |
| `hour` | int8 | hour (denormalized) |

---

## facts/fact_cash_ops — cash replenishments (9,195 rows)

Cash loading event. PK: `op_id`.

| Field | Type | Description |
|---|---|---|
| `op_id` | int64 | operation ID, key |
| `atm_id` | string | ATM (→ dim_atm) |
| `timestamp` | timestamp | replenishment moment |
| `op_type` | string | refill |
| `amount_loaded` | int | loaded, KGS |
| `balance_before` | int | balance before, KGS |
| `balance_after` | int | balance after (= capacity), KGS |
| `service_route_id` | string | route/crew |
| `cassette_breakdown` | string (JSON) | notes loaded per denomination, e.g. `{"5000":458,"1000":1561}` |

---

## facts/fact_atm_status — statuses and events (10,130 rows)

Unavailability/downtime intervals. PK: `event_id`.

| Field | Type | Description |
|---|---|---|
| `event_id` | int64 | event ID, key |
| `atm_id` | string | ATM (→ dim_atm) |
| `start_ts`, `end_ts` | timestamp | event interval |
| `status` | string | low_cash/out_of_cash/network_down/hardware_fault |
| `uptime_pct` | double | availability over the interval (0.0 = down) |

---

## labels/ — anomaly ground truth

### labels/fraud (256) — skimming (7.7) + geo-impossibility (7.10)
| Field | Type | Description |
|---|---|---|
| `txn_id` | int64 | reference to a fact row |
| `atm_id` | string | ATM |
| `timestamp` | timestamp | moment |
| `card_id` | string | card |
| `kind` | string | skimming / geo_velocity |

### labels/cash_events (206) — depletions (7.1)
| Field | Type | Description |
|---|---|---|
| `atm_id` | string | ATM |
| `start_ts`, `end_ts` | timestamp | depletion interval |
| `event_type` | string | out_of_cash |
| `n_declined` | int | number of `99` declines over the interval |

### labels/faults (717) — faults (7.2) and stuck terminals (7.8)
| Field | Type | Description |
|---|---|---|
| `atm_id` | string | ATM |
| `start_ts`, `end_ts` | timestamp | interval |
| `kind` | string | network_down / hardware_fault / stuck |
| `n_txns_affected` | int | operations affected |

### labels/cold_start (14) — new ATMs (7.4)
| Field | Type | Description |
|---|---|---|
| `atm_id` | string | ATM |
| `install_date` | timestamp | commissioning date within the period |
| `atm_type` | string | archetype |

### labels/events (3) — network-wide surges (7.3)
| Field | Type | Description |
|---|---|---|
| `date` | timestamp | FX-shock day |
| `fx_change_pct` | double | rate change, % |
| `event_type` | string | bank_run |

### labels/drift_spec (1) — concept drift (7.6)
| Field | Type | Description |
|---|---|---|
| `year2_uplift` | double | volume growth by the end of year 2 |
| `channel_shift` | string | channel-shift description |
| `amount_inflation` | double | average-ticket inflation |

---

## external/ — external real-world inputs

### external/weather_daily (731) — Open-Meteo ERA5 weather
`date, temp_avg, temp_max, temp_min, precip_mm, snowfall_mm, wind_max, weathercode`

### external/fx_usd_kgs (731) — NBKR exchange rate
`date, rate` (USD/KGS)

### external/atm_locations (193) — OSM coordinates
`source_id, lat, lon, address, district_hint, placement_hint, is_24_7_hint`
