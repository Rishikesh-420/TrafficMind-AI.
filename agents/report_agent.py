"""
agents/report_agent.py
AI agent: accepts free-form traffic report text and extracts structured
insights — congestion mentions, incidents, affected areas, and commuter tips.
Falls back to keyword extraction if no OpenAI key is present.
"""

import re
import os
from dotenv import load_dotenv

load_dotenv()

# Known Bengaluru locations for keyword extraction fallback
_KNOWN_LOCATIONS = [
    "Silk Board", "Marathahalli", "Hebbal", "KR Puram", "Electronic City",
    "Whitefield", "Bannerghatta", "Mysore Road", "Tumkur Road", "ORR",
    "Outer Ring Road", "Old Madras Road", "Tin Factory", "MG Road",
    "Hosur Road", "Sarjapur", "Koramangala", "Indiranagar", "BTM",
    "Yeshwanthpur", "Rajajinagar", "Banaswadi", "Hoodi", "ITPL",
    "Bellary Road", "Kengeri", "NICE Road", "HAL", "Airport Road",
    "Bommasandra",
]

_SEVERITY_KEYWORDS = {
    "critical": ["blocked", "accident", "collision", "standstill", "zero movement"],
    "high":     ["heavy", "severe", "tail-back", "jam", "diverting"],
    "moderate": ["slow", "congested", "delays", "moderate"],
    "low":      ["clear", "free flow", "smooth", "light traffic"],
}


class ReportAgent:
    """
    Parses a traffic report text and returns structured insights.
    """

    def __init__(self):
        self._openai_available = bool(os.getenv("OPENAI_API_KEY"))

    def analyse(self, report_text: str) -> dict:
        """
        Main entry point. Returns a dict with keys:
        - summary:      short plain-English summary
        - locations:    list of mentioned Bengaluru locations
        - severity:     "Critical" | "High" | "Moderate" | "Low"
        - tips:         list of commuter tip strings
        - full_analysis: formatted markdown block
        """
        if self._openai_available:
            return self._gpt_analyse(report_text)
        return self._rule_analyse(report_text)

    # ── Rule-based fallback ───────────────────────────────────────────────────

    def _rule_analyse(self, text: str) -> dict:
        text_lower = text.lower()

        # Extract mentioned locations
        locations = [loc for loc in _KNOWN_LOCATIONS if loc.lower() in text_lower]

        # Determine severity
        severity = "Low"
        for sev, keywords in _SEVERITY_KEYWORDS.items():
            if any(k in text_lower for k in keywords):
                severity = sev.capitalize()
                break

        # Simple tip extraction: sentences containing "advised", "recommend", "alternate"
        tips = []
        for sentence in re.split(r"[.!]", text):
            if any(w in sentence.lower() for w in ["advis", "recommend", "alternate", "avoid", "use"]):
                tip = sentence.strip()
                if tip:
                    tips.append(tip)

        summary = (
            f"Report mentions **{len(locations)} location(s)** in Bengaluru. "
            f"Estimated severity: **{severity}**."
        )

        full_analysis = (
            f"### 📋 Traffic Report Analysis\n\n"
            f"**Severity Assessment:** {severity}\n\n"
            f"**Locations Identified:** {', '.join(locations) if locations else 'None detected'}\n\n"
            f"**Commuter Tips Extracted:**\n"
            + ("\n".join(f"- {t}" for t in tips) if tips else "- No specific tips found.\n")
            + f"\n\n*Analysis powered by keyword extraction (rule-based mode)*"
        )

        return {
            "summary":       summary,
            "locations":     locations,
            "severity":      severity,
            "tips":          tips,
            "full_analysis": full_analysis,
        }

    # ── GPT-powered analysis ──────────────────────────────────────────────────

    def _gpt_analyse(self, text: str) -> dict:
        try:
            from openai import OpenAI
            client = OpenAI()
            prompt = f"""You are a Bengaluru traffic analyst. Analyse the following traffic report.
Return a JSON object with these fields:
- "summary": one-sentence plain-English summary (max 30 words)
- "locations": list of Bengaluru locations mentioned
- "severity": one of "Critical", "High", "Moderate", "Low"
- "tips": list of up to 3 actionable commuter tips

Traffic Report:
\"\"\"{text}\"\"\"

Respond ONLY with the JSON object."""

            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            import json
            data = json.loads(resp.choices[0].message.content)
            locations = data.get("locations", [])
            severity  = data.get("severity", "Moderate")
            tips      = data.get("tips", [])
            summary   = data.get("summary", "")

            full_analysis = (
                f"### 📋 AI Traffic Report Analysis\n\n"
                f"**Summary:** {summary}\n\n"
                f"**Severity Assessment:** {severity}\n\n"
                f"**Locations Identified:** {', '.join(locations) if locations else 'None'}\n\n"
                f"**Commuter Tips:**\n"
                + "\n".join(f"- {t}" for t in tips)
                + "\n\n*Analysis powered by GPT-4o-mini*"
            )

            return {
                "summary":       summary,
                "locations":     locations,
                "severity":      severity,
                "tips":          tips,
                "full_analysis": full_analysis,
            }
        except Exception:
            # Graceful fallback
            return self._rule_analyse(text)
