"""
agents/accident_agent.py
AI agent: identifies accident-prone zones, computes risk scores,
and generates safety advisories.
"""

import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


class AccidentAgent:
    """
    Processes accident-prone zone data to:
    - Rank zones by risk score
    - Flag active incidents
    - Generate safety advisories per zone
    """

    RISK_LABELS = {
        (75, 100): ("🔴 Critical Risk",  "Avoid if possible. Emergency services may be active."),
        (50,  75): ("🟠 High Risk",      "Exercise extreme caution. Reduce speed significantly."),
        (25,  50): ("🟡 Moderate Risk",  "Stay alert and maintain safe following distance."),
        (0,   25): ("🟢 Low Risk",       "Normal caution applies."),
    }

    def __init__(self):
        self._openai_available = bool(os.getenv("OPENAI_API_KEY"))

    def rank_zones(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return zones sorted by risk score descending."""
        return df.sort_values("Risk Score", ascending=False).reset_index(drop=True)

    def active_incidents(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return only zones with an active incident flag."""
        return df[df["Active Incident"] == True].reset_index(drop=True)

    def risk_label(self, score: float) -> tuple[str, str]:
        for (lo, hi), (label, advice) in self.RISK_LABELS.items():
            if lo <= score <= hi:
                return label, advice
        return ("⚪ Unknown", "No data available.")

    def zone_advisory(self, row: pd.Series) -> str:
        """Generate a short advisory string for a single zone row."""
        label, advice = self.risk_label(row["Risk Score"])
        active_str = " **⚠ ACTIVE INCIDENT**" if row.get("Active Incident") else ""
        return (
            f"{label}{active_str}\n"
            f"- **Location:** {row['zone']}\n"
            f"- **Severity Class:** {row['severity']}\n"
            f"- **Risk Score:** {row['Risk Score']}/100\n"
            f"- **Incidents YTD:** {row['incidents_ytd']}\n"
            f"- **Peak Hours:** {row['peak_hours']}\n"
            f"- **Advisory:** {advice}"
        )

    def city_safety_summary(self, df: pd.DataFrame) -> str:
        """High-level city-wide safety summary."""
        active = self.active_incidents(df)
        high_risk = df[df["severity"] == "High"]
        avg_risk = round(df["Risk Score"].mean(), 1)

        status = "🔴 Elevated" if len(active) >= 3 else ("🟡 Cautionary" if len(active) >= 1 else "🟢 Normal")

        summary = (
            f"**City Safety Status: {status}**\n\n"
            f"- Active incidents: **{len(active)}**\n"
            f"- High-risk zones: **{len(high_risk)}**\n"
            f"- Average risk score: **{avg_risk}/100**\n"
        )

        if len(active):
            locs = ", ".join(active["zone"].tolist())
            summary += f"- Active incident locations: {locs}\n"

        if self._openai_available:
            summary = self._gpt_safety_tip(summary)

        return summary

    def _gpt_safety_tip(self, summary: str) -> str:
        try:
            from openai import OpenAI
            client = OpenAI()
            prompt = (
                "You are a road safety expert for Bengaluru. Add one concise, "
                "actionable safety tip (max 40 words) to this traffic safety summary. "
                "Do not repeat existing content:\n\n" + summary
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.7,
            )
            tip = resp.choices[0].message.content.strip()
            return summary + f"\n🤖 *AI Safety Tip:* {tip}"
        except Exception:
            return summary
