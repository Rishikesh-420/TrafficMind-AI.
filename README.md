# 🚦 TrafficMind AI

> **IBM Bobathon 2026 · Student Category**
> Theme: **Smarter Streets, Better Living**
> Developer: Rajri · Stack: Python · Streamlit · AI Agents

---

## 🌐 Overview

TrafficMind AI is an intelligent traffic management assistant built specifically
for **Bengaluru commuters**. It combines real-time (simulated) traffic data with
AI agents to help citizens navigate the city's notoriously congested roads.

---

## ✨ Features

| Module | Description |
|---|---|
| 🏠 **Dashboard** | City-wide KPIs, AI congestion summary, speed gauge, 24-hour trend |
| 🚗 **Live Traffic Map** | Interactive Folium map with congestion overlays on 15+ corridors |
| ⚠️ **Accident Zones** | Heatmap + risk rankings for Bengaluru's most dangerous junctions |
| 🗺️ **Route Advisor** | AI-powered alternative route recommendations with live ETAs |
| 🔔 **Safety Alerts** | Real-time feed of incidents, waterlogging, road works, signal faults |
| 📄 **Report Analyser** | Paste any traffic bulletin — AI extracts severity, locations & tips |

---

## 🏗️ Project Structure

```
TrafficMind-AI/
├── app.py                   # Main Streamlit application
├── requirements.txt
├── README.md
├── .env                     # (optional) OPENAI_API_KEY=sk-...
│
├── agents/
│   ├── __init__.py
│   ├── congestion_agent.py  # Hotspot detection + city severity score
│   ├── accident_agent.py    # Risk ranking + safety advisories
│   ├── route_agent.py       # Alternative route recommendation
│   └── report_agent.py      # NLP traffic report parser
│
├── data/
│   ├── __init__.py
│   └── bengaluru_data.py    # Simulated Bengaluru traffic data generator
│
└── utils/
    ├── __init__.py
    ├── map_utils.py          # Folium map builders
    └── chart_utils.py        # Plotly chart builders
```

---

## 🚀 Quick Start

### 1. Clone / unzip the project

```bash
cd TrafficMind-AI
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Add OpenAI API key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

Without this key, all AI features degrade gracefully to intelligent rule-based responses.

### 5. Run the app

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🤖 AI Agent Architecture

```
User Action
    │
    ├─► CongestionAgent   → detects hotspots, generates city severity score
    ├─► AccidentAgent     → ranks risk zones, flags active incidents
    ├─► RouteAgent        → recommends fastest route with congestion multipliers
    └─► ReportAgent       → parses free-text bulletins into structured insights
                               │
                               ├─ Rule-based (always works, no API needed)
                               └─ GPT-4o-mini enhancement (if OPENAI_API_KEY set)
```

---

## 📍 Bengaluru Coverage

15 major corridors including:
Silk Board · Marathahalli · Hebbal · KR Puram · Tin Factory · Whitefield ·
Electronic City · Bannerghatta Road · Mysore Road · Tumkur Road · ORR · MG Road

8 accident-prone zones fully mapped with YTD incident counts and peak-hour data.

---

## 🏆 IBM Bobathon 2026

- **Category:** Student
- **Theme:** Smarter Streets, Better Living
- **Technology:** Python, Streamlit, AI Agents, OpenAI (optional), Folium, Plotly
- **Data:** Simulated Bengaluru traffic (upgradeable to BBMP / Google Maps API)

---

## 📄 License

MIT — free to use, modify and distribute.
