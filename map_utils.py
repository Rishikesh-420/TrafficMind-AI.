"""
utils/map_utils.py
Folium map builder for Bengaluru traffic overlays.
"""

import folium
from folium.plugins import MarkerCluster, HeatMap
import pandas as pd


# Bengaluru city centre
BLORE_CENTER = [12.9716, 77.5946]


def build_traffic_map(traffic_df: pd.DataFrame, zoom: int = 12) -> folium.Map:
    """
    Build an interactive Folium map showing live congestion
    for every corridor in traffic_df.
    """
    m = folium.Map(
        location=BLORE_CENTER,
        zoom_start=zoom,
        tiles="CartoDB positron",
        prefer_canvas=True,
    )

    for _, row in traffic_df.iterrows():
        color = row["Color"]
        level = row["Congestion Level"]
        speed = row["Speed (km/h)"]
        name  = row["Location"]

        # Circle marker sized by congestion
        radius = 10 + (row["Congestion (%)"] / 10)
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            popup=folium.Popup(
                f"<b>{name}</b><br>"
                f"Level: {level}<br>"
                f"Speed: {speed} km/h<br>"
                f"Congestion: {row['Congestion (%)']}%<br>"
                f"Updated: {row['Last Updated']}",
                max_width=200,
            ),
            tooltip=f"{name} — {level}",
        ).add_to(m)

    _add_legend(m)
    return m


def build_accident_map(accident_df: pd.DataFrame, zoom: int = 11) -> folium.Map:
    """
    Build a heatmap + marker map for accident-prone zones.
    """
    m = folium.Map(location=BLORE_CENTER, zoom_start=zoom, tiles="CartoDB dark_matter")

    heat_data = [[r["lat"], r["lon"], r["Risk Score"] / 100] for _, r in accident_df.iterrows()]
    HeatMap(heat_data, radius=30, blur=20, max_zoom=13).add_to(m)

    severity_colors = {"High": "red", "Medium": "orange", "Low": "green"}
    for _, row in accident_df.iterrows():
        icon_color = severity_colors.get(row["severity"], "gray")
        active_tag = " 🔴 ACTIVE INCIDENT" if row.get("Active Incident") else ""
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(
                f"<b>{row['zone']}</b>{active_tag}<br>"
                f"Severity: {row['severity']}<br>"
                f"Incidents YTD: {row['incidents_ytd']}<br>"
                f"Peak Hours: {row['peak_hours']}<br>"
                f"Risk Score: {row['Risk Score']}",
                max_width=220,
            ),
            tooltip=f"{row['zone']} — {row['severity']} risk",
            icon=folium.Icon(color=icon_color, icon="exclamation-sign", prefix="glyphicon"),
        ).add_to(m)

    return m


def build_alerts_map(alerts: list[dict], zoom: int = 12) -> folium.Map:
    """
    Pin road safety alerts on the map.
    """
    m = folium.Map(location=BLORE_CENTER, zoom_start=zoom, tiles="CartoDB positron")
    severity_colors = {"High": "red", "Medium": "orange", "Low": "blue"}

    cluster = MarkerCluster().add_to(m)
    for a in alerts:
        color = severity_colors.get(a["severity"], "gray")
        folium.Marker(
            location=[a["lat"], a["lon"]],
            popup=folium.Popup(
                f"<b>{a['type']}</b><br>"
                f"Location: {a['location']}<br>"
                f"Severity: {a['severity']}<br>"
                f"Reported: {a.get('timestamp', 'N/A')}",
                max_width=200,
            ),
            tooltip=f"⚠ {a['type']} — {a['location']}",
            icon=folium.Icon(color=color, icon="warning-sign", prefix="glyphicon"),
        ).add_to(cluster)

    return m


def _add_legend(m: folium.Map) -> None:
    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                background:#1e293b;border-radius:8px;padding:12px 16px;
                font-family:sans-serif;font-size:13px;color:#f8fafc;
                box-shadow:0 4px 12px rgba(0,0,0,0.4);">
      <b>Congestion Level</b><br>
      <span style="color:#22c55e;">●</span> Free Flow (&gt;40 km/h)<br>
      <span style="color:#f59e0b;">●</span> Moderate (25–40 km/h)<br>
      <span style="color:#ef4444;">●</span> Congested (12–25 km/h)<br>
      <span style="color:#7f1d1d;">●</span> Severely Congested (&lt;12 km/h)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
