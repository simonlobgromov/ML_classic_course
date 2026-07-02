"""Geography of Bishkek: districts/zones used to place ATMs and locate customers.

Bishkek has 4 administrative districts (Sverdlovsky, Leninsky, Pervomaisky,
Oktyabrsky). We refine them into ~16 recognisable zones (markets, residential
microdistricts, business centre, transit hubs) with approximate coordinates.

Each zone carries:
  - pop_weight:     relative share of resident customers living there
  - type_affinity:  unnormalised weights for which ATM archetype is plausible here

These couplings make geography drive behaviour (a market zone gets market ATMs,
a residential microdistrict gets residential/pension ATMs), without hard-coding
the global archetype mix, which is controlled separately via config shares.
"""

import pandas as pd

# Administrative districts of Bishkek.
ADMIN_DISTRICTS = ["Sverdlovsky", "Leninsky", "Pervomaisky", "Oktyabrsky"]

# Zone records. Coordinates are approximate (Bishkek centre ~42.875, 74.603).
# type_affinity keys must match config atm_types.
ZONES = [
    {
        "district_id": "ZN-CENTER", "name": "Центр (Ала-Тоо/Чуй)",
        "admin_district": "Pervomaisky", "zone_type": "central",
        "pop_weight": 0.06, "business_share": 0.85,
        "lat_center": 42.8760, "lon_center": 74.6122,
        "type_affinity": {"office_business": 5, "tourist_center": 4,
                          "shopping_mall": 3, "transport_market": 1},
    },
    {
        "district_id": "ZN-ERKINDIK", "name": "Эркиндик / деловой центр",
        "admin_district": "Pervomaisky", "zone_type": "central",
        "pop_weight": 0.03, "business_share": 0.90,
        "lat_center": 42.8718, "lon_center": 74.6050,
        "type_affinity": {"office_business": 6, "tourist_center": 2,
                          "shopping_mall": 1},
    },
    {
        "district_id": "ZN-OSHBAZAR", "name": "Ошский рынок",
        "admin_district": "Leninsky", "zone_type": "market",
        "pop_weight": 0.04, "business_share": 0.70,
        "lat_center": 42.8752, "lon_center": 74.5730,
        "type_affinity": {"transport_market": 8, "office_business": 1},
    },
    {
        "district_id": "ZN-DORDOI", "name": "Рынок Дордой",
        "admin_district": "Sverdlovsky", "zone_type": "market",
        "pop_weight": 0.03, "business_share": 0.75,
        "lat_center": 42.9262, "lon_center": 74.6200,
        "type_affinity": {"transport_market": 9},
    },
    {
        "district_id": "ZN-WESTBUS", "name": "Западный автовокзал",
        "admin_district": "Leninsky", "zone_type": "transit",
        "pop_weight": 0.03, "business_share": 0.50,
        "lat_center": 42.8620, "lon_center": 74.5570,
        "type_affinity": {"transport_market": 5, "highway_gas": 3},
    },
    {
        "district_id": "ZN-VOSTOK5", "name": "Восток-5",
        "admin_district": "Pervomaisky", "zone_type": "residential",
        "pop_weight": 0.09, "business_share": 0.20,
        "lat_center": 42.8700, "lon_center": 74.6400,
        "type_affinity": {"residential": 7, "pension_social": 3,
                          "shopping_mall": 1},
    },
    {
        "district_id": "ZN-ALAMEDIN1", "name": "Аламедин-1",
        "admin_district": "Sverdlovsky", "zone_type": "residential",
        "pop_weight": 0.08, "business_share": 0.20,
        "lat_center": 42.8820, "lon_center": 74.6380,
        "type_affinity": {"residential": 7, "pension_social": 2},
    },
    {
        "district_id": "ZN-JAL", "name": "Джал",
        "admin_district": "Leninsky", "zone_type": "residential",
        "pop_weight": 0.09, "business_share": 0.25,
        "lat_center": 42.8350, "lon_center": 74.5600,
        "type_affinity": {"residential": 6, "shopping_mall": 2,
                          "pension_social": 1},
    },
    {
        "district_id": "ZN-KOKJAR", "name": "Кок-Жар",
        "admin_district": "Leninsky", "zone_type": "suburb",
        "pop_weight": 0.06, "business_share": 0.15,
        "lat_center": 42.8000, "lon_center": 74.5550,
        "type_affinity": {"residential": 4, "highway_gas": 3,
                          "pension_social": 1},
    },
    {
        "district_id": "ZN-UCHKUN", "name": "Учкун / Городок строителей",
        "admin_district": "Sverdlovsky", "zone_type": "residential",
        "pop_weight": 0.07, "business_share": 0.30,
        "lat_center": 42.9050, "lon_center": 74.6050,
        "type_affinity": {"residential": 5, "highway_gas": 2,
                          "office_business": 1},
    },
    {
        "district_id": "ZN-YUG2", "name": "Юг-2",
        "admin_district": "Leninsky", "zone_type": "residential",
        "pop_weight": 0.08, "business_share": 0.20,
        "lat_center": 42.8450, "lon_center": 74.5850,
        "type_affinity": {"residential": 7, "pension_social": 2},
    },
    {
        "district_id": "ZN-TUNGUCH", "name": "Тунгуч / Асанбай",
        "admin_district": "Oktyabrsky", "zone_type": "residential",
        "pop_weight": 0.08, "business_share": 0.25,
        "lat_center": 42.8520, "lon_center": 74.6220,
        "type_affinity": {"residential": 6, "shopping_mall": 2,
                          "pension_social": 1},
    },
    {
        "district_id": "ZN-MALLS", "name": "ТЦ (Бишкек Парк / Vefa / Asia Mall)",
        "admin_district": "Oktyabrsky", "zone_type": "central",
        "pop_weight": 0.02, "business_share": 0.80,
        "lat_center": 42.8680, "lon_center": 74.6000,
        "type_affinity": {"shopping_mall": 8, "office_business": 2},
    },
    {
        "district_id": "ZN-SOCIAL", "name": "Соцфонд / поликлиники",
        "admin_district": "Oktyabrsky", "zone_type": "central",
        "pop_weight": 0.04, "business_share": 0.40,
        "lat_center": 42.8600, "lon_center": 74.6100,
        "type_affinity": {"pension_social": 8, "residential": 2},
    },
    {
        "district_id": "ZN-PROMZONE", "name": "Промзона / ТЭЦ",
        "admin_district": "Sverdlovsky", "zone_type": "industrial",
        "pop_weight": 0.03, "business_share": 0.55,
        "lat_center": 42.9100, "lon_center": 74.5850,
        "type_affinity": {"highway_gas": 4, "office_business": 3,
                          "transport_market": 1},
    },
    {
        "district_id": "ZN-HIGHWAY", "name": "Трассы / АЗС (окраины)",
        "admin_district": "Sverdlovsky", "zone_type": "suburb",
        "pop_weight": 0.04, "business_share": 0.30,
        "lat_center": 42.8950, "lon_center": 74.5400,
        "type_affinity": {"highway_gas": 8, "transport_market": 1},
    },
]

# Public columns of the dim_district reference table.
_DIM_COLUMNS = [
    "district_id", "name", "admin_district", "zone_type",
    "population_density", "business_share", "lat_center", "lon_center",
]


def build_districts(config: dict | None = None) -> pd.DataFrame:
    """Return the dim_district reference table."""
    rows = []
    for z in ZONES:
        rows.append({
            "district_id": z["district_id"],
            "name": z["name"],
            "admin_district": z["admin_district"],
            "zone_type": z["zone_type"],
            # population_density is a relative proxy derived from pop_weight.
            "population_density": round(z["pop_weight"], 4),
            "business_share": z["business_share"],
            "lat_center": z["lat_center"],
            "lon_center": z["lon_center"],
        })
    return pd.DataFrame(rows, columns=_DIM_COLUMNS)
