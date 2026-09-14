"""Technical Analysis Specialist Agent."""

from typing import Any, Dict
from stock_analyzer.agents.base import BaseAgent
from stock_analyzer.core.models import AgentOutput


class TechnicalAgent(BaseAgent):
    """Interprets trend, momentum, volatility, and volume indicators from validated OHLCV data."""

    def __init__(self):
        super().__init__(
            name="Technical Analysis Agent",
            role="Interpret multi-indicator technical trends, momentum oscillators, and volume confirmation.",
        )

    def _run_offline_mock(self, context: Dict[str, Any]) -> AgentOutput:
        symbol = context.get("symbol", "SECURITY")
        company = context.get("company_name", symbol)
        ind = context.get("indicators", {})
        rsi = ind.get("RSI_14", 52.0)
        sma50 = ind.get("SMA_50", 210.0)
        sma200 = ind.get("SMA_200", 190.0)

        facts = [
            f"14-period Wilder RSI is currently {rsi:.1f}, indicating neutral-to-constructive momentum.",
            f"50-day moving average (${sma50:.2f}) trades above the 200-day moving average (${sma200:.2f}), confirming positive intermediate structure.",
            "Trading volume exhibits normal alignment with 20-day baseline.",
        ]
        inferences = [
            "Technical structure exhibits a confirmed intermediate uptrend without immediate overbought extremes.",
            "Support levels near the 50-day moving average provide a defined technical reference.",
        ]

        return AgentOutput(
            agent_name=self.name,
            status="COMPLETED",
            summary=f"Technical posture for {company} ({symbol}) is constructive with solid trend support.",
            facts=facts,
            calculations=ind,
            inferences=inferences,
            uncertainties=["A breakdown below the 200-day SMA would invalidate the intermediate bullish trend."],
            citations=["Validated Daily OHLCV Time-Series (252+ bars)", "TA Indicator Engine"],
            confidence=0.88,
        )
