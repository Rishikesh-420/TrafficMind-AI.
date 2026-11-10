"""
utils/chart_utils.py
Plotly chart builders for traffic analytics.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


PALETTE = {
    "bg":       "#0f172a",
    "surface":  "#1e293b",
    "border":   "#334155",
    "text":     "#f8fafc",
    "muted":    "#94a3b8",
    "green":    "#22c55e",
    "amber":    "#f59e0b",
    "red":      "#ef4444",
    "darkred":  "#7f1d1d",
    "blue":     "#3b82f6",
    "purple":   "#8b5cf6",
}

_LAYOUT_DEFAULTS = dict(
    paper_bgcolor=PALETTE["bg"],
    plot_bgcolor=PALETTE["surface"],
    font=dict(color=PALETTE["text"], family="Inter, system-ui, sans-serif", size=12),
    margin=dict(l=16, r=16, t=40, b=16),
    xaxis=dict(gridcolor=PALETTE["border"], zerolinecolor=PALETTE["border"]),
    yaxis=dict(gridcolor=PALETTE["border"], zerolinecolor=PALETTE["border"]),
)


def congestion_bar_chart(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of congestion % per corridor."""
    df_sorted = df.sort_values("Congestion (%)", ascending=True)
    colors = df_sorted["Color"].tolist()

    fig = go.Figure(go.Bar(
        y=df_sorted["Location"],
        x=df_sorted["Congestion (%)"],
        orientation="h",
        marker_color=colors,
        text=df_sorted["Congestion (%)"].apply(lambda v: f"{v}%"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Congestion: %{x}%<extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title=dict(text="Live Congestion by Corridor", font=dict(size=15)),
        xaxis_title="Congestion (%)",
        yaxis_title=None,
        height=420,
    )
    return fig


def speed_gauge(current_speed: float, location: str = "Bengaluru Avg") -> go.Figure:
    """Gauge chart for average speed."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_speed,
        delta={"reference": 40, "valueformat": ".1f"},
        number={"suffix": " km/h", "font": {"size": 28}},
        title={"text": f"Avg Speed — {location}", "font": {"size": 13}},
        gauge={
            "axis": {"range": [0, 65], "tickcolor": PALETTE["muted"]},
            "bar":  {"color": PALETTE["blue"]},
            "steps": [
                {"range": [0,  12], "color": PALETTE["darkred"]},
                {"range": [12, 25], "color": PALETTE["red"]},
                {"range": [25, 40], "color": PALETTE["amber"]},
                {"range": [40, 65], "color": PALETTE["green"]},
            ],
            "threshold": {"line": {"color": "white", "width": 3}, "value": 40},
        },
    ))
    fig.update_layout(
        paper_bgcolor=PALETTE["bg"],
        font=dict(color=PALETTE["text"]),
        margin=dict(l=20, r=20, t=60, b=20),
        height=260,
    )
    return fig


def hourly_trend_chart(trend_df: pd.DataFrame, corridor_name: str = "") -> go.Figure:
    """Area chart of 24-hour speed / congestion trend."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend_df["Hour"],
        y=trend_df["Speed"],
        name="Speed (km/h)",
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.20)",
        line=dict(color=PALETTE["blue"], width=2),
        hovertemplate="%{x}: %{y} km/h<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=trend_df["Hour"],
        y=trend_df["Congestion (%)"],
        name="Congestion (%)",
        line=dict(color=PALETTE["red"], width=2, dash="dot"),
        yaxis="y2",
        hovertemplate="%{x}: %{y}%<extra></extra>",
    ))
    

    fig.update_layout(
        **{k: v for k, v in _LAYOUT_DEFAULTS.items() if k != "yaxis"},
        title=dict(text=f"24-Hour Trend — {corridor_name}", font=dict(size=15)),
        yaxis=dict(title="Speed (km/h)", gridcolor=PALETTE["border"]),
        yaxis2=dict(
            title="Congestion (%)",
            overlaying="y",
            side="right",
            gridcolor=PALETTE["border"],
            range=[0, 100],
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=320,
    )
    return fig






def accident_severity_pie(accident_df: pd.DataFrame) -> go.Figure:
    """Pie chart of accident zone severity breakdown."""
    counts = accident_df["severity"].value_counts().reset_index()
    counts.columns = ["Severity", "Count"]
    color_map = {"High": PALETTE["red"], "Medium": PALETTE["amber"], "Low": PALETTE["green"]}
    colors = [color_map.get(s, "#6b7280") for s in counts["Severity"]]

    fig = go.Figure(go.Pie(
        labels=counts["Severity"],
        values=counts["Count"],
        marker=dict(colors=colors, line=dict(color=PALETTE["bg"], width=2)),
        textinfo="label+percent",
        hole=0.45,
        hovertemplate="<b>%{label}</b><br>Zones: %{value}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title=dict(text="Accident Zones by Severity", font=dict(size=15)),
        showlegend=False,
        height=280,
        margin=dict(l=10, r=10, t=44, b=10),
    )
    return fig


def incidents_bar(accident_df: pd.DataFrame) -> go.Figure:
    """Bar chart of yearly incident counts per zone."""
    df_sorted = accident_df.sort_values("incidents_ytd", ascending=False)
    fig = go.Figure(go.Bar(
        x=df_sorted["zone"],
        y=df_sorted["incidents_ytd"],
        marker_color=PALETTE["red"],
        text=df_sorted["incidents_ytd"],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Incidents: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT_DEFAULTS,
        title=dict(text="Incidents Year-to-Date by Zone", font=dict(size=15)),
        xaxis_tickangle=-30,
        yaxis_title="Incidents",
        height=340,
    )
    return fig
