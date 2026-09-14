"""Sentiment Specialist Agent."""

from typing import Any, Dict
from stock_analyzer.agents.base import BaseAgent
from stock_analyzer.core.models import AgentOutput


class SentimentAgent(BaseAgent):
    """Analyzes news tone, retail attention, and narrative direction across 1h, 24h, and 7d horizons."""

    def __init__(self):
        super().__init__(
            name="Sentiment Agent",
            role="Assess news tone, retail sentiment, and attention shifts against baseline levels.",
        )

    def _run_offline_mock(self, context: Dict[str, Any]) -> AgentOutput:
        symbol = context.get("symbol", "SECURITY")
        company = context.get("company_name", symbol)

        facts = [
            "News tone over the preceding 7 days is positive (+1.45 on GDELT tone scale).",
            "Article volume increased 12.5% compared to 30-day baseline without negative cluster spikes.",
            "Retail narrative focuses predominantly on high-margin product ecosystem expansion.",
        ]
        inferences = [
            "Market narrative exhibits healthy constructive enthusiasm rather than irrational euphoria.",
            "Sentiment direction supports price stability near key moving averages.",
        ]

        return AgentOutput(
            agent_name=self.name,
            status="COMPLETED",
            summary=f"Sentiment for {company} ({symbol}) is moderately bullish with stable attention volume.",
            facts=facts,
            calculations={"sentiment_tone": 1.45, "attention_delta_pct": 12.5},
            inferences=inferences,
            uncertainties=["Sentiment can shift rapidly following quarterly earnings release announcements."],
            citations=["GDELT Project Global News Stream", "Financial Headline Aggregate"],
            confidence=0.85,
        )
