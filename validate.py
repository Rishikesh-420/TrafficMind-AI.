"""
validate.py -- TrafficMind AI pre-flight check
Run: python validate.py
"""
import sys
print(f"Python {sys.version}")

print("1/4  Importing data layer...", end=" ", flush=True)
from data.bengaluru_data import (
    get_live_traffic_data, get_accident_data,
    get_hourly_trend, get_route_recommendations,
    get_road_safety_alerts, get_traffic_report_text,
)
print("OK")

print("2/4  Running data generators...", end=" ", flush=True)
df   = get_live_traffic_data()
acc  = get_accident_data()
trd  = get_hourly_trend("C01")
rts  = get_route_recommendations("Silk Board → Whitefield")
alts = get_road_safety_alerts()
rpt  = get_traffic_report_text()
assert len(df)  == 15, f"Expected 15 corridors, got {len(df)}"
assert len(acc) ==  8, f"Expected 8 accident zones, got {len(acc)}"
assert len(trd) == 24, f"Expected 24-hour trend, got {len(trd)}"
assert len(rts) ==  3, f"Expected 3 routes, got {len(rts)}"
assert len(alts) >=  3, "Expected ≥3 alerts"
assert len(rpt)  >  50, "Report text too short"
print(f"OK  ({len(df)} corridors, {len(acc)} accident zones, {len(alts)} alerts)")

print("3/4  Importing agents...", end=" ", flush=True)
from agents.congestion_agent import CongestionAgent
from agents.accident_agent   import AccidentAgent
from agents.route_agent      import RouteAgent
from agents.report_agent     import ReportAgent
print("OK")

print("4/4  Running agent logic...", end=" ", flush=True)
ca = CongestionAgent()
aa = AccidentAgent()
ra = RouteAgent()
rpa = ReportAgent()

hotspots = ca.detect_hotspots(df)
score    = ca.city_severity_score(df)
summary  = ca.generate_summary(df)
ranked   = aa.rank_zones(acc)
safety   = aa.city_safety_summary(acc)
rec      = ra.format_recommendation("Silk Board → Whitefield", rts)
analysis = rpa.analyse(rpt)
print(f"OK  (score={score}, hotspots={len(hotspots)}, severity={analysis['severity']})")

print()
print("=" * 56)
print("  ✅  All checks passed — TrafficMind AI is ready!")
print("  Run:  streamlit run app.py")
print("=" * 56)
