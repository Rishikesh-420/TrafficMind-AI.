"""
data/bengaluru_data.py
Simulated real-time Bengaluru traffic data generator.
All coordinates are real Bengaluru landmarks/junctions.
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ── Core Bengaluru road network ───────────────────────────────────────────────
BENGALURU_CORRIDORS = [
    {"id": "C01", "name": "Silk Board Junction",        "lat": 12.9172, "lon": 77.6231, "type": "junction"},
    {"id": "C02", "name": "Marathahalli Bridge",        "lat": 12.9591, "lon": 77.6971, "type": "junction"},
    {"id": "C03", "name": "Hebbal Flyover",             "lat": 13.0358, "lon": 77.5970, "type": "flyover"},
    {"id": "C04", "name": "KR Puram Bridge",            "lat": 13.0050, "lon": 77.6960, "type": "bridge"},
    {"id": "C05", "name": "Tin Factory Junction",       "lat": 12.9971, "lon": 77.6601, "type": "junction"},
    {"id": "C06", "name": "Whitefield Main Road",       "lat": 12.9698, "lon": 77.7499, "type": "arterial"},
    {"id": "C07", "name": "Electronic City Flyover",    "lat": 12.8399, "lon": 77.6770, "type": "flyover"},
    {"id": "C08", "name": "Bannerghatta Road",          "lat": 12.8921, "lon": 77.5970, "type": "arterial"},
    {"id": "C09", "name": "Mysore Road (Kengeri)",      "lat": 12.9141, "lon": 77.4820, "type": "arterial"},
    {"id": "C10", "name": "Tumkur Road (Yeshwanthpur)", "lat": 13.0200, "lon": 77.5500, "type": "arterial"},
    {"id": "C11", "name": "Hosur Road (BTM Layout)",   "lat": 12.9100, "lon": 77.6100, "type": "arterial"},
    {"id": "C12", "name": "Old Madras Road (Banaswadi)","lat": 13.0100, "lon": 77.6500, "type": "arterial"},
    {"id": "C13", "name": "Outer Ring Road (ORR)",     "lat": 12.9600, "lon": 77.7100, "type": "ring_road"},
    {"id": "C14", "name": "MG Road",                   "lat": 12.9750, "lon": 77.6090, "type": "arterial"},
    {"id": "C15", "name": "Bellary Road (Hebbal→Airport)","lat": 13.0600, "lon": 77.5900, "type": "arterial"},
]

# ── Accident-prone zones ──────────────────────────────────────────────────────
ACCIDENT_PRONE_ZONES = [
    {"zone": "Silk Board Junction",    "lat": 12.9172, "lon": 77.6231, "severity": "High",   "incidents_ytd": 48, "peak_hours": "8–10 AM, 6–9 PM"},
    {"zone": "Marathahalli Bridge",    "lat": 12.9591, "lon": 77.6971, "severity": "High",   "incidents_ytd": 41, "peak_hours": "7–10 AM, 5–8 PM"},
    {"zone": "Hebbal Flyover",         "lat": 13.0358, "lon": 77.5970, "severity": "Medium", "incidents_ytd": 29, "peak_hours": "8–11 AM"},
    {"zone": "KR Puram Bridge",        "lat": 13.0050, "lon": 77.6960, "severity": "High",   "incidents_ytd": 37, "peak_hours": "7–9 AM, 6–8 PM"},
    {"zone": "Electronic City Flyover","lat": 12.8399, "lon": 77.6770, "severity": "Medium", "incidents_ytd": 22, "peak_hours": "9–11 AM, 5–7 PM"},
    {"zone": "Bannerghatta Road",      "lat": 12.8921, "lon": 77.5970, "severity": "Low",    "incidents_ytd": 15, "peak_hours": "7–9 PM"},
    {"zone": "Mysore Road (Kengeri)",  "lat": 12.9141, "lon": 77.4820, "severity": "Medium", "incidents_ytd": 26, "peak_hours": "8–10 AM"},
    {"zone": "Tin Factory Junction",   "lat": 12.9971, "lon": 77.6601, "severity": "High",   "incidents_ytd": 33, "peak_hours": "8–10 AM, 6–9 PM"},
]

# ── Alternative route pairs ───────────────────────────────────────────────────
ROUTE_ALTERNATIVES = {
    "Silk Board → Whitefield": {
        "primary":     {"name": "ORR via Marathahalli",           "distance_km": 22.4, "base_time_min": 65},
        "alt1":        {"name": "Sarjapur Road → Bellandur",      "distance_km": 20.1, "base_time_min": 50},
        "alt2":        {"name": "Hosur Road → Electronic City",   "distance_km": 28.7, "base_time_min": 55},
    },
    "Hebbal → Electronic City": {
        "primary":     {"name": "NH 44 via Silk Board",           "distance_km": 30.2, "base_time_min": 75},
        "alt1":        {"name": "Bellary Road → Tumkur Road loop","distance_km": 38.0, "base_time_min": 60},
        "alt2":        {"name": "Mysore Road via NICE Road",      "distance_km": 34.5, "base_time_min": 58},
    },
    "KR Puram → MG Road": {
        "primary":     {"name": "Old Madras Road direct",         "distance_km": 14.2, "base_time_min": 45},
        "alt1":        {"name": "Banaswadi → Tin Factory → HAL",  "distance_km": 16.8, "base_time_min": 38},
        "alt2":        {"name": "Hoodi → Doddanekundi → Indiranagar","distance_km": 18.1, "base_time_min": 40},
    },
    "Yeshwanthpur → Koramangala": {
        "primary":     {"name": "Tumkur Road → Chord Road → Silk Board","distance_km": 25.5, "base_time_min": 70},
        "alt1":        {"name": "Rajajinagar → JC Road → Richmond","distance_km": 22.0, "base_time_min": 55},
        "alt2":        {"name": "Outer Ring Road full loop",      "distance_km": 30.0, "base_time_min": 60},
    },
}


def _congestion_level(speed_kmph: float) -> str:
    if speed_kmph >= 40:
        return "Free Flow"
    elif speed_kmph >= 25:
        return "Moderate"
    elif speed_kmph >= 12:
        return "Congested"
    else:
        return "Severely Congested"


def _congestion_color(level: str) -> str:
    return {"Free Flow": "#22c55e", "Moderate": "#f59e0b",
            "Congested": "#ef4444", "Severely Congested": "#7f1d1d"}.get(level, "#6b7280")


def get_live_traffic_data() -> pd.DataFrame:
    """Generate a snapshot of current traffic across all corridors."""
    hour = datetime.now().hour
    # Peak hours: 8–10 AM and 6–9 PM
    is_peak = (8 <= hour <= 10) or (18 <= hour <= 21)
    records = []
    for c in BENGALURU_CORRIDORS:
        base_speed = random.uniform(8, 22) if is_peak else random.uniform(25, 55)
        speed = round(np.clip(base_speed + random.gauss(0, 4), 5, 65), 1)
        level = _congestion_level(speed)
        congestion_pct = round(max(0, min(100, 100 - (speed / 65) * 100)), 1)
        records.append({
            "Corridor ID":       c["id"],
            "Location":          c["name"],
            "Latitude":          c["lat"],
            "Longitude":         c["lon"],
            "Type":              c["type"],
            "Speed (km/h)":      speed,
            "Congestion Level":  level,
            "Congestion (%)":    congestion_pct,
            "Color":             _congestion_color(level),
            "Last Updated":      datetime.now().strftime("%H:%M:%S"),
        })
    return pd.DataFrame(records)


def get_accident_data() -> pd.DataFrame:
    """Return accident-prone zone data with a live random incident flag."""
    records = []
    for z in ACCIDENT_PRONE_ZONES:
        active = random.random() < (0.3 if z["severity"] == "High" else 0.15)
        records.append({
            **z,
            "Active Incident": active,
            "Risk Score":      round(random.uniform(60, 99) if z["severity"] == "High"
                                     else random.uniform(30, 65), 1),
        })
    return pd.DataFrame(records)


def get_hourly_trend(corridor_id: str = "C01") -> pd.DataFrame:
    """Return a 24-hour simulated speed trend for a given corridor."""
    hours = list(range(24))
    # Natural traffic curve: slow at peak, fast at night
    base = [55, 58, 60, 62, 55, 38, 22, 14, 12, 18, 28, 35,
            38, 35, 30, 28, 18, 14, 12, 20, 32, 42, 50, 55]
    speeds = [round(np.clip(b + random.gauss(0, 3), 5, 65), 1) for b in base]
    return pd.DataFrame({
        "Hour":     [f"{h:02d}:00" for h in hours],
        "Speed":    speeds,
        "Congestion (%)": [round(max(0, 100 - (s / 65) * 100), 1) for s in speeds],
    })


def get_route_recommendations(origin: str = "Silk Board → Whitefield") -> dict:
    """Return route options with live congestion-adjusted travel times."""
    routes = ROUTE_ALTERNATIVES.get(origin, list(ROUTE_ALTERNATIVES.values())[0])
    result = {}
    for key, r in routes.items():
        multiplier = random.uniform(1.1, 2.5) if key == "primary" else random.uniform(0.9, 1.6)
        result[key] = {
            **r,
            "current_time_min": round(r["base_time_min"] * multiplier),
            "congestion_level": _congestion_level(random.uniform(8, 55)),
        }
    return result


def get_road_safety_alerts() -> list[dict]:
    """Generate a live list of road safety alerts."""
    possible_alerts = [
        {"type": "Waterlogging",  "location": "Silk Board Underpass",      "severity": "High",   "lat": 12.9172, "lon": 77.6231},
        {"type": "Pothole",       "location": "ORR near Marathahalli",      "severity": "Medium", "lat": 12.9591, "lon": 77.6971},
        {"type": "Accident",      "location": "KR Puram Bridge",            "severity": "High",   "lat": 13.0050, "lon": 77.6960},
        {"type": "Road Work",     "location": "Bellary Road (km 12)",       "severity": "Low",    "lat": 13.0500, "lon": 77.5850},
        {"type": "Signal Fault",  "location": "Tin Factory Junction",       "severity": "Medium", "lat": 12.9971, "lon": 77.6601},
        {"type": "Accident",      "location": "Electronic City Flyover",    "severity": "High",   "lat": 12.8399, "lon": 77.6770},
        {"type": "Fog Warning",   "location": "Mysore Road (Kengeri)",      "severity": "Low",    "lat": 12.9141, "lon": 77.4820},
        {"type": "VIP Movement",  "location": "MG Road → Residency Road",  "severity": "Medium", "lat": 12.9750, "lon": 77.6090},
        {"type": "Breakdown",     "location": "Bannerghatta Road (km 5)",  "severity": "Low",    "lat": 12.8921, "lon": 77.5970},
        {"type": "Heavy Rain",    "location": "Whitefield Main Road",       "severity": "Medium", "lat": 12.9698, "lon": 77.7499},
    ]
    # Randomly activate 3–6 alerts
    active = random.sample(possible_alerts, k=random.randint(3, 6))
    for a in active:
        a["timestamp"] = (datetime.now() - timedelta(minutes=random.randint(1, 30))).strftime("%H:%M")
    return active


def get_traffic_report_text() -> str:
    """Return a synthetic traffic report paragraph for AI analysis."""
    hour = datetime.now().strftime("%H:%M")
    reports = [
        f"As of {hour}, Bengaluru's ORR is experiencing heavy congestion near Marathahalli. "
        "Average speeds have dropped to 12 km/h. Commuters are advised to use Sarjapur Road as an alternative. "
        "An accident has been reported near KR Puram Bridge causing a 3-km tail-back. "
        "Electronic City phase-1 entry shows moderate flow at 28 km/h. BMTC route 500C is running 20 minutes late.",

        f"Traffic bulletin at {hour}: Silk Board junction remains the worst bottleneck with speeds below 10 km/h. "
        "Hebbal flyover is operating at 40% capacity due to ongoing metro construction. "
        "Whitefield corridor reports a multi-vehicle collision at Hoodi circle — one lane blocked. "
        "Alternate route via ITPL main road is recommended. Mysore Road reports free flow at 55 km/h.",

        f"[{hour}] Live update — Heavy rainfall has caused waterlogging on Hosur Road near Electronic City gate-1. "
        "Vehicles are diverting through Bommasandra industrial area. Bannerghatta Road is clear. "
        "Old Airport Road sees moderate traffic, average speed 30 km/h. "
        "Police personnel deployed at Tin Factory junction to manage signal failure.",
    ]
    return random.choice(reports)
