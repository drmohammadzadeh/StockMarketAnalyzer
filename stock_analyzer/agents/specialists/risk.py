"""Risk Analysis Specialist Agent."""

from typing import Any, Dict
from stock_analyzer.agents.base import BaseAgent
from stock_analyzer.core.models import AgentOutput


class RiskAgent(BaseAgent):
    """Analyzes market, leverage, operational, regulatory, and event risks."""

    def __init__(self):
        super().__init__(
            name="Risk Analysis Agent",
            role="Rank and categorize downside risks and potential upside catalysts.",
        )

    def _run_offline_mock(self, context: Dict[str, Any]) -> AgentOutput:
        symbol = context.get("symbol", "SECURITY")
        company = context.get("company_name", symbol)

        facts = [
            "Company maintains an Altman Z-Score within the Safe Zone, indicating negligible near-term insolvency risk.",
            "Net debt-to-EBITDA remains comfortably below 1.5x, providing extensive debt refinancing headroom.",
            "Customer concentration shows no single customer exceeding 15% of annual revenue.",
        ]
        inferences = [
            "Primary risks stem from global regulatory/antitrust reviews and semiconductor supply chain lead times.",
            "Macroeconomic consumer spending deceleration represents a moderate cyclical sensitivity.",
        ]

        return AgentOutput(
            agent_name=self.name,
            status="COMPLETED",
            summary=f"Risk profile for {company} ({symbol}) is evaluated as low-to-moderate with exceptional balance sheet resilience.",
            facts=facts,
            calculations={"risk_tier": "Low-to-Moderate", "insolvency_probability": "< 1%"},
            inferences=inferences,
            uncertainties=["Geopolitical tariff policy changes could impact international gross margins."],
            citations=["SEC 10-K Item 1A Risk Factors", "Altman Z Model Output", "Debt Maturity Profile"],
            confidence=0.90,
        )
