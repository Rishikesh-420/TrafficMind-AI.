"""
agents/congestion_agent.py
AI agent: detects congestion hotspots and generates natural-language summaries.
Uses rule-based inference + optional OpenAI API (graceful fallback if no key).
"""

import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


class CongestionAgent:
    """
    Analyses live traffic DataFrame and produces:
    - Hotspot list (corridors with congestion > threshold)
    - Natural-language alert string
    - Severity score (0–100)
    """

    SEVERITY_MAP = {
        "Free Flow":           0,
        "Moderate":            35,
        "Congested":           70,
        "Severely Congested": 100,
    }

    def __init__(self, congestion_threshold: float = 60.0):
        self.threshold = congestion_threshold
        self._openai_available = bool(os.getenv("OPENAI_API_KEY"))

    # ── Core analysis ─────────────────────────────────────────────────────────

    def detect_hotspots(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return rows where congestion exceeds the threshold."""
        return df[df["Congestion (%)"] >= self.threshold].sort_values(
            "Congestion (%)", ascending=False
        ).reset_index(drop=True)

    def city_severity_score(self, df: pd.DataFrame) -> float:
        """Weighted average severity across all corridors (0–100)."""
        weights = df["Congestion Level"].map(self.SEVERITY_MAP).fillna(0)
        return round(weights.mean(), 1)

    def generate_summary(self, df: pd.DataFrame) -> str:
        """
        Generate a plain-English congestion summary.
        If OPENAI_API_KEY is set, enhance with GPT; otherwise use rule-based text.
        """
        hotspots = self.detect_hotspots(df)
        score    = self.city_severity_score(df)
        worst    = df.loc[df["Congestion (%)"].idxmax(), "Location"] if len(df) else "N/A"
        best     = df.loc[df["Congestion (%)"].idxmin(), "Location"] if len(df) else "N/A"

        base_text = self._rule_based_summary(hotspots, score, worst, best)

        if self._openai_available:
            return self._gpt_enhance(base_text, hotspots, score)
        return base_text

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _rule_based_summary(
        self,
        hotspots: pd.DataFrame,
        score: float,
        worst: str,
        best: str,
    ) -> str:
        if score >= 80:
            severity_label = "🔴 Critical"
            advice = "Avoid all major corridors if possible. Work-from-home recommended."
        elif score >= 55:
            severity_label = "🟠 Severe"
            advice = "Expect significant delays on primary routes. Consider public transit."
        elif score >= 30:
            severity_label = "🟡 Moderate"
            advice = "Some corridors are slow. Allow extra travel time."
        else:
            severity_label = "🟢 Light"
            advice = "Traffic is largely free-flowing across the city."

        hot_names = ", ".join(hotspots["Location"].tolist()[:4]) if len(hotspots) else "None"

        return (
            f"**City Congestion Status: {severity_label}** (Score {score}/100)\n\n"
            f"- **Worst corridor:** {worst}\n"
            f"- **Least congested:** {best}\n"
            f"- **Active hotspots ({len(hotspots)}):** {hot_names}\n\n"
            f"💡 *{advice}*"
        )

    def _gpt_enhance(self, base_text: str, hotspots: pd.DataFrame, score: float) -> str:
        """Call OpenAI to enhance the summary (only if API key is present)."""
        try:
            from openai import OpenAI
            client = OpenAI()
            prompt = (
                "You are a Bengaluru traffic analyst. Enhance this traffic summary "
                "with one additional insight or commuter tip. Keep it under 60 words. "
                "Do NOT repeat info already present:\n\n" + base_text
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.7,
            )
            tip = resp.choices[0].message.content.strip()
            return base_text + f"\n\n🤖 *AI Insight:* {tip}"
        except Exception:
            return base_text
