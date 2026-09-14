"""Valuation Specialist Agent."""

from typing import Any, Dict
from stock_analyzer.agents.base import BaseAgent
from stock_analyzer.core.models import AgentOutput


class ValuationAgent(BaseAgent):
    """Evaluates DCF intrinsic value, reverse DCF implied growth, Graham Number, and peer multiples."""

    def __init__(self):
        super().__init__(
            name="Valuation Agent",
            role="Perform DCF, reverse DCF, Graham Number, and industry peer valuation analysis.",
        )

    def _run_offline_mock(self, context: Dict[str, Any]) -> AgentOutput:
        symbol = context.get("symbol", "SECURITY")
        company = context.get("company_name", symbol)
        val = context.get("valuation", {})
        intrinsic = val.get("intrinsic_value_per_share", 215.0)
        graham = val.get("graham_number", 65.0)

        facts = [
            f"Base 5-year DCF fair value estimated at ${intrinsic:.2f} per share under an 8.5% WACC and 2.5% terminal growth rate.",
            f"Benjamin Graham defensive value benchmark is ${graham:.2f} per share.",
            "Valuation multiples trade near historical 5-year median for Tier-1 technology peers.",
        ]
        inferences = [
            "Current market pricing reflects reasonable growth expectations rather than speculative excess.",
            "Market is pricing in approximately 6-8% sustained free cash flow expansion over the next five years.",
        ]

        return AgentOutput(
            agent_name=self.name,
            status="COMPLETED",
            summary=f"Valuation analysis for {company} ({symbol}) indicates fair valuation relative to long-term cash generation.",
            facts=facts,
            calculations=val,
            inferences=inferences,
            uncertainties=["Valuation sensitivity is sensitive to changes in the 10-Year Treasury risk-free rate."],
            citations=["5-Year FCFF DCF Model", "Graham Defensive Formula", "Industry Peer Benchmark Database"],
            confidence=0.86,
        )
