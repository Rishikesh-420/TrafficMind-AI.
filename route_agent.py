"""
agents/route_agent.py
AI agent: recommends the best alternative route given origin/destination
and live congestion data.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class RouteAgent:
    """
    Evaluates route alternatives and picks the fastest option
    given current congestion multipliers.
    """

    CONGESTION_SCORE = {
        "Free Flow":           1,
        "Moderate":            2,
        "Congested":           3,
        "Severely Congested":  4,
    }

    def __init__(self):
        self._openai_available = bool(os.getenv("OPENAI_API_KEY"))

    def best_route(self, routes: dict) -> tuple[str, dict]:
        """Return the key and data of the recommended route."""
        scored = {
            k: v["current_time_min"] + self.CONGESTION_SCORE.get(v["congestion_level"], 2) * 5
            for k, v in routes.items()
        }
        best_key = min(scored, key=scored.get)
        return best_key, routes[best_key]

    def format_recommendation(self, origin: str, routes: dict) -> str:
        """Format a human-readable route recommendation."""
        best_key, best = self.best_route(routes)

        lines = [f"## 🗺 Route Recommendations: *{origin}*\n"]
        for key, r in routes.items():
            tag = " ✅ **RECOMMENDED**" if key == best_key else ""
            congestion_emoji = {
                "Free Flow": "🟢", "Moderate": "🟡",
                "Congested": "🟠", "Severely Congested": "🔴",
            }.get(r["congestion_level"], "⚪")
            lines.append(
                f"**{r['name']}**{tag}\n"
                f"- Distance: {r['distance_km']} km\n"
                f"- Est. Travel Time: ~{r['current_time_min']} min\n"
                f"- Traffic: {congestion_emoji} {r['congestion_level']}\n"
            )

        recommendation = (
            f"\n💡 **Best Choice:** Take **{best['name']}** — "
            f"estimated **{best['current_time_min']} minutes** "
            f"({best['distance_km']} km)."
        )
        lines.append(recommendation)

        if self._openai_available:
            return self._gpt_route_tip("\n".join(lines), best)
        return "\n".join(lines)

    def _gpt_route_tip(self, text: str, best: dict) -> str:
        try:
            from openai import OpenAI
            client = OpenAI()
            prompt = (
                f"You are a Bengaluru navigator. The recommended route is '{best['name']}' "
                f"taking ~{best['current_time_min']} min. Add one short local tip "
                "(landmarks, fuel stops, etc.) for this specific Bengaluru route. Max 40 words."
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.8,
            )
            tip = resp.choices[0].message.content.strip()
            return text + f"\n\n🤖 *Navigator Tip:* {tip}"
        except Exception:
            return text
