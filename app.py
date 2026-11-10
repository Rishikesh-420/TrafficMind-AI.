"""
app.py — TrafficMind AI
IBM Bobathon 2026 | Student Category | Theme: Smarter Streets, Better Living
Developer: Rajri | Stack: Python · Streamlit · AI Agents
"""

import time
import streamlit as st
import pandas as pd

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="TrafficMind AI — Bengaluru",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Lazy imports (keep startup fast) ─────────────────────────────────────────
from data.bengaluru_data import (
    get_live_traffic_data,
    get_accident_data,
    get_hourly_trend,
    get_route_recommendations,
    get_road_safety_alerts,
    get_traffic_report_text,
    ROUTE_ALTERNATIVES,
)
from utils.map_utils   import build_traffic_map, build_accident_map, build_alerts_map
from utils.chart_utils import (
    congestion_bar_chart,
    speed_gauge,
    hourly_trend_chart,
    accident_severity_pie,
    incidents_bar,
)
from agents.congestion_agent import CongestionAgent
from agents.accident_agent   import AccidentAgent
from agents.route_agent      import RouteAgent
from agents.report_agent     import ReportAgent

try:
    from streamlit_folium import st_folium
    _FOLIUM_OK = True
except ImportError:
    _FOLIUM_OK = False

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}
[data-testid="stAppViewContainer"] {
    background: #0f172a;
    color: #f8fafc;
}
[data-testid="stSidebar"] {
    background: #1e293b;
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] * { color: #f1f5f9 !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px;
}
[data-testid="stMetricValue"]  { color: #38bdf8 !important; font-size: 2rem !important; }
[data-testid="stMetricLabel"]  { color: #94a3b8 !important; }
[data-testid="stMetricDelta"]  { font-size: 0.85rem !important; }

/* ── Section headers ── */
h1 { color: #38bdf8 !important; }
h2 { color: #7dd3fc !important; border-bottom: 1px solid #334155; padding-bottom: 6px; }
h3 { color: #bae6fd !important; }

/* ── Alert boxes ── */
.alert-high   { background:#450a0a; border-left:4px solid #ef4444; padding:10px 14px; border-radius:6px; margin:6px 0; }
.alert-medium { background:#431407; border-left:4px solid #f59e0b; padding:10px 14px; border-radius:6px; margin:6px 0; }
.alert-low    { background:#052e16; border-left:4px solid #22c55e; padding:10px 14px; border-radius:6px; margin:6px 0; }

/* ── Tabs ── */
[data-testid="stTabs"] button          { color: #94a3b8 !important; }
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8;
}

/* ── Buttons ── */
.stButton > button {
    background: #1d4ed8;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    transition: background 0.2s;
}
.stButton > button:hover { background: #2563eb; }

/* ── Selectbox / text area ── */
.stSelectbox div[data-baseweb="select"] > div,
.stTextArea textarea {
    background: #1e293b !important;
    color: #f1f5f9 !important;
    border: 1px solid #334155 !important;
    border-radius: 6px;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #475569;
    font-size: 12px;
    padding: 20px 0 8px;
    border-top: 1px solid #1e293b;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if "traffic_df" not in st.session_state:
    st.session_state.traffic_df = get_live_traffic_data()
if "accident_df" not in st.session_state:
    st.session_state.accident_df = get_accident_data()
if "alerts" not in st.session_state:
    st.session_state.alerts = get_road_safety_alerts()


def refresh_data():
    st.session_state.traffic_df   = get_live_traffic_data()
    st.session_state.accident_df  = get_accident_data()
    st.session_state.alerts       = get_road_safety_alerts()
    st.session_state.last_refresh = time.time()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Traffic_lights_4_states.svg/"
        "60px-Traffic_lights_4_states.svg.png",
        width=52,
    )
    st.markdown("## 🚦 TrafficMind AI")
    st.markdown("*Smarter Streets · Better Living*")
    st.divider()

    st.markdown("### ⚙️ Controls")
    auto_refresh = st.toggle("Auto-refresh (30s)", value=False)
    if st.button("🔄 Refresh Now"):
        refresh_data()
        st.rerun()

    st.divider()
    st.markdown("### 🗂 Navigation")
    page = st.radio(
        "Select Module",
        [
            "🏠 Dashboard",
            "🚗 Live Traffic Map",
            "⚠️ Accident Zones",
            "🗺️ Route Advisor",
            "🔔 Safety Alerts",
            "📄 Report Analyser",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    from datetime import datetime
    last = datetime.fromtimestamp(st.session_state.last_refresh).strftime("%H:%M:%S")
    st.caption(f"Last updated: {last}")
    st.caption("📍 Bengaluru, Karnataka")
    st.markdown('<div class="footer">IBM Bobathon 2026<br>Student Category</div>', unsafe_allow_html=True)

# ── Auto-refresh logic ────────────────────────────────────────────────────────
if auto_refresh and (time.time() - st.session_state.last_refresh > 30):
    refresh_data()
    st.rerun()

# ── Shared data ───────────────────────────────────────────────────────────────
traffic_df  = st.session_state.traffic_df
accident_df = st.session_state.accident_df
alerts      = st.session_state.alerts


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ════════════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown("# 🚦 TrafficMind AI — Bengaluru")
    st.markdown("*Real-time traffic intelligence powered by AI agents · IBM Bobathon 2026*")
    st.divider()

    # ── KPI row ───────────────────────────────────────────────────────────────
    agent_c = CongestionAgent()
    agent_a = AccidentAgent()

    avg_speed    = round(traffic_df["Speed (km/h)"].mean(), 1)
    city_score   = agent_c.city_severity_score(traffic_df)
    hotspot_cnt  = len(agent_c.detect_hotspots(traffic_df))
    active_inc   = len(agent_a.active_incidents(accident_df))
    alert_cnt    = len(alerts)
    free_flow_pct = round(
        (traffic_df["Congestion Level"] == "Free Flow").sum() / len(traffic_df) * 100
    )

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("🏎️ Avg City Speed",      f"{avg_speed} km/h",   delta=f"{'▲' if avg_speed > 30 else '▼'} vs 30 km/h")
    k2.metric("📊 Congestion Score",     f"{city_score}/100",   delta="City-wide index")
    k3.metric("🔥 Active Hotspots",      hotspot_cnt,           delta="Corridors > 60%")
    k4.metric("🚨 Active Incidents",     active_inc,            delta="Accident zones")
    k5.metric("🔔 Live Safety Alerts",   alert_cnt,             delta="Updated now")

    st.divider()

    # ── AI Summary ────────────────────────────────────────────────────────────
    col_s, col_c = st.columns([1.3, 1])
    with col_s:
        st.markdown("### 🤖 AI Congestion Summary")
        with st.spinner("Analysing traffic…"):
            summary = agent_c.generate_summary(traffic_df)
        st.markdown(summary)

    with col_c:
        st.markdown("### 🌡️ City Speed Gauge")
        st.plotly_chart(speed_gauge(avg_speed, "Bengaluru Average"), use_container_width=True)

    st.divider()

    # ── Charts row ────────────────────────────────────────────────────────────
    col_b, col_t = st.columns(2)
    with col_b:
        st.markdown("### 📊 Congestion by Corridor")
        st.plotly_chart(congestion_bar_chart(traffic_df), use_container_width=True)

    with col_t:
        st.markdown("### ⏱️ 24-Hour Trend — Silk Board Junction")
        trend = get_hourly_trend("C01")
        st.plotly_chart(hourly_trend_chart(trend, "Silk Board"), use_container_width=True)

    # ── Safety summary ────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🛡️ City Safety Summary")
    st.markdown(agent_a.city_safety_summary(accident_df))

    # ── Active alerts ticker ──────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🔔 Active Alerts Ticker")
    sev_class = {"High": "alert-high", "Medium": "alert-medium", "Low": "alert-low"}
    for a in alerts[:5]:
        css = sev_class.get(a["severity"], "alert-low")
        st.markdown(
            f'<div class="{css}"><b>{a["type"]}</b> — {a["location"]} '
            f'<span style="color:#94a3b8;font-size:12px">({a["severity"]} · {a.get("timestamp","?")})</span></div>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: LIVE TRAFFIC MAP
# ════════════════════════════════════════════════════════════════════════════════
elif page == "🚗 Live Traffic Map":
    st.markdown("## 🚗 Live Traffic Map")
    st.markdown("Interactive congestion overlay across Bengaluru's major corridors.")

    col_m, col_t = st.columns([1.7, 1])

    with col_m:
        fmap = build_traffic_map(traffic_df)
        if _FOLIUM_OK:
            st_folium(fmap, width=700, height=500)
        else:
            st.info("Install `streamlit-folium` to view the interactive map.")
            st.components.v1.html(fmap._repr_html_(), height=500)

    with col_t:
        st.markdown("### 📋 Corridor Status Table")
        display_cols = ["Location", "Speed (km/h)", "Congestion Level", "Congestion (%)"]
        styled = traffic_df[display_cols].style.applymap(
            lambda v: "color: #ef4444" if v in ("Congested", "Severely Congested")
            else ("color: #f59e0b" if v == "Moderate" else "color: #22c55e"),
            subset=["Congestion Level"],
        )
        st.dataframe(styled, use_container_width=True, height=460)

    st.divider()
    st.markdown("### 📈 Select Corridor for Trend")
    options = traffic_df["Location"].tolist()
    ids     = traffic_df["Corridor ID"].tolist()
    sel_name = st.selectbox("Corridor", options)
    sel_id   = ids[options.index(sel_name)]
    trend    = get_hourly_trend(sel_id)
    st.plotly_chart(hourly_trend_chart(trend, sel_name), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: ACCIDENT ZONES
# ════════════════════════════════════════════════════════════════════════════════
elif page == "⚠️ Accident Zones":
    st.markdown("## ⚠️ Accident-Prone Zone Identification")
    st.markdown("AI-ranked risk zones based on historical incident data and live flags.")

    agent_a = AccidentAgent()
    ranked  = agent_a.rank_zones(accident_df)

    col_m, col_p = st.columns([1.6, 1])
    with col_m:
        amap = build_accident_map(accident_df)
        if _FOLIUM_OK:
            st_folium(amap, width=680, height=460)
        else:
            st.components.v1.html(amap._repr_html_(), height=460)

    with col_p:
        st.markdown("### 🔢 Zone Risk Rankings")
        st.plotly_chart(accident_severity_pie(accident_df), use_container_width=True)
        st.plotly_chart(incidents_bar(accident_df), use_container_width=True)

    st.divider()
    st.markdown("### 🔍 Zone-by-Zone Advisories")
    for _, row in ranked.iterrows():
        active_badge = " 🔴 **INCIDENT ACTIVE**" if row["Active Incident"] else ""
        with st.expander(f"{row['zone']} — Risk {row['Risk Score']}/100{active_badge}"):
            st.markdown(agent_a.zone_advisory(row))


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: ROUTE ADVISOR
# ════════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Route Advisor":
    st.markdown("## 🗺️ AI Route Advisor")
    st.markdown("Smart alternative route recommendations with live congestion multipliers.")

    agent_r  = RouteAgent()
    origins  = list(ROUTE_ALTERNATIVES.keys())

    col_l, col_r = st.columns([1, 1.4])
    with col_l:
        st.markdown("### 🔀 Select Your Journey")
        selected_origin = st.selectbox("Origin → Destination", origins)
        st.markdown("---")
        routes = get_route_recommendations(selected_origin)

        if st.button("🚀 Get Route Recommendation"):
            with st.spinner("AI Route Agent analysing…"):
                time.sleep(0.6)
                recommendation = agent_r.format_recommendation(selected_origin, routes)
            st.session_state["route_result"] = recommendation

    with col_r:
        st.markdown("### 📊 Route Comparison")
        if routes:
            names = [r["name"] for r in routes.values()]
            times = [r["current_time_min"] for r in routes.values()]
            dists = [r["distance_km"] for r in routes.values()]
            congest = [r["congestion_level"] for r in routes.values()]

            import plotly.graph_objects as go
            color_map = {"Free Flow": "#22c55e", "Moderate": "#f59e0b",
                         "Congested": "#ef4444", "Severely Congested": "#7f1d1d"}
            bar_colors = [color_map.get(c, "#6b7280") for c in congest]

            fig = go.Figure(data=[
                go.Bar(name="Est. Time (min)", x=names, y=times, marker_color=bar_colors,
                       text=times, textposition="outside"),
            ])
            fig.update_layout(
                paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                font=dict(color="#f8fafc"), height=280,
                margin=dict(l=8, r=8, t=36, b=8),
                title=dict(text="Estimated Travel Time per Route", font=dict(size=14)),
                yaxis_title="Minutes",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Distance comparison
            fig2 = go.Figure(data=[
                go.Bar(name="Distance (km)", x=names, y=dists,
                       marker_color="#8b5cf6", text=dists, textposition="outside"),
            ])
            fig2.update_layout(
                paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                font=dict(color="#f8fafc"), height=240,
                margin=dict(l=8, r=8, t=36, b=8),
                title=dict(text="Route Distance Comparison", font=dict(size=14)),
                yaxis_title="Kilometres",
            )
            st.plotly_chart(fig2, use_container_width=True)

    if "route_result" in st.session_state:
        st.divider()
        st.markdown(st.session_state["route_result"])


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: SAFETY ALERTS
# ════════════════════════════════════════════════════════════════════════════════
elif page == "🔔 Safety Alerts":
    st.markdown("## 🔔 Real-Time Road Safety Alerts")
    st.markdown("Live incident feed for Bengaluru's road network.")

    col_m2, col_feed = st.columns([1.6, 1])
    with col_m2:
        amap2 = build_alerts_map(alerts)
        if _FOLIUM_OK:
            st_folium(amap2, width=680, height=460)
        else:
            st.components.v1.html(amap2._repr_html_(), height=460)

    with col_feed:
        st.markdown("### 📡 Incident Feed")
        sev_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
        sev_class = {"High": "alert-high", "Medium": "alert-medium", "Low": "alert-low"}
        for a in alerts:
            icon = sev_icon.get(a["severity"], "⚪")
            css  = sev_class.get(a["severity"], "alert-low")
            st.markdown(
                f'<div class="{css}">'
                f'{icon} <b>{a["type"]}</b><br>'
                f'<span style="font-size:13px">{a["location"]}</span><br>'
                f'<span style="color:#94a3b8;font-size:11px">Severity: {a["severity"]} · {a.get("timestamp","?")} ago</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown("### 📊 Alert Breakdown")
    if alerts:
        sev_counts = pd.Series([a["severity"] for a in alerts]).value_counts().reset_index()
        sev_counts.columns = ["Severity", "Count"]
        type_counts = pd.Series([a["type"] for a in alerts]).value_counts().reset_index()
        type_counts.columns = ["Type", "Count"]

        import plotly.express as px
        c1, c2 = st.columns(2)
        with c1:
            fig_s = px.pie(sev_counts, values="Count", names="Severity",
                           color="Severity",
                           color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"},
                           title="Alerts by Severity",
                           template="plotly_dark")
            fig_s.update_layout(paper_bgcolor="#0f172a", height=280, margin=dict(t=40))
            st.plotly_chart(fig_s, use_container_width=True)
        with c2:
            fig_t = px.bar(type_counts, x="Type", y="Count",
                           title="Alerts by Type",
                           template="plotly_dark",
                           color_discrete_sequence=["#3b82f6"])
            fig_t.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#1e293b",
                                height=280, margin=dict(t=40))
            st.plotly_chart(fig_t, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════════
# PAGE: REPORT ANALYSER
# ════════════════════════════════════════════════════════════════════════════════
elif page == "📄 Report Analyser":
    st.markdown("## 📄 AI Traffic Report Analyser")
    st.markdown(
        "Paste any Bengaluru traffic report and the AI agent will extract "
        "structured insights, severity level, and commuter tips."
    )

    agent_r2 = ReportAgent()

    col_in, col_out = st.columns(2)
    with col_in:
        st.markdown("### 📥 Input Report")
        if st.button("📡 Load Live Sample Report"):
            st.session_state["report_text"] = get_traffic_report_text()

        report_text = st.text_area(
            "Traffic Report Text",
            value=st.session_state.get("report_text", ""),
            height=240,
            placeholder="Paste a traffic report here, or click 'Load Live Sample Report'…",
            label_visibility="collapsed",
        )

        if st.button("🤖 Analyse Report"):
            if report_text.strip():
                with st.spinner("AI Report Agent analysing…"):
                    result = agent_r2.analyse(report_text)
                st.session_state["report_result"] = result
            else:
                st.warning("Please enter or load a report first.")

    with col_out:
        st.markdown("### 📤 AI Analysis Output")
        if "report_result" in st.session_state:
            res = st.session_state["report_result"]

            # Severity badge
            sev = res.get("severity", "Unknown")
            badge_color = {"Critical": "#7f1d1d", "High": "#450a0a",
                           "Moderate": "#431407", "Low": "#052e16"}.get(sev, "#1e293b")
            st.markdown(
                f'<div style="display:inline-block;padding:4px 14px;border-radius:20px;'
                f'background:{badge_color};color:#f8fafc;font-weight:700;font-size:14px;'
                f'margin-bottom:12px;">Severity: {sev}</div>',
                unsafe_allow_html=True,
            )

            st.markdown(res.get("full_analysis", ""))

            # Locations as tags
            locs = res.get("locations", [])
            if locs:
                st.markdown("**📍 Locations detected:**")
                tags_html = " ".join(
                    f'<span style="background:#1e3a5f;color:#93c5fd;padding:3px 10px;'
                    f'border-radius:12px;font-size:12px;margin:2px;display:inline-block;">{loc}</span>'
                    for loc in locs
                )
                st.markdown(tags_html, unsafe_allow_html=True)
        else:
            st.info("Load a sample report and click **Analyse Report** to see results here.")

    # ── History / recent reports ──────────────────────────────────────────────
    st.divider()
    st.markdown("### 🕒 Load Historical Report Samples")
    c1, c2, c3 = st.columns(3)
    samples = [get_traffic_report_text() for _ in range(3)]
    for btn_col, sample, label in zip([c1, c2, c3], samples, ["Sample A", "Sample B", "Sample C"]):
        with btn_col:
            with st.expander(f"📄 {label}"):
                st.write(sample[:300] + "…")
                if st.button(f"Load {label}", key=f"load_{label}"):
                    st.session_state["report_text"] = sample
                    st.rerun()


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">'
    '🚦 <b>TrafficMind AI</b> · IBM Bobathon 2026 · Student Category · '
    'Theme: Smarter Streets, Better Living · Built with Streamlit &amp; Python'
    '</div>',
    unsafe_allow_html=True,
)
