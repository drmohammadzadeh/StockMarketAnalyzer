"""Fundamental Research Specialist Agent."""

from typing import Any, Dict
from stock_analyzer.agents.base import BaseAgent
from stock_analyzer.core.models import AgentOutput


class FundamentalAgent(BaseAgent):
    """Analyzes growth, margins, free cash flow, ROIC, and capital allocation."""

    def __init__(self):
        super().__init__(
            name="Fundamental Research Agent",
            role="Analyze GAAP statements, margins, ROIC, balance sheet solvency, and earnings quality.",
        )

    def _run_offline_mock(self, context: Dict[str, Any]) -> AgentOutput:
        symbol = context.get("symbol", "SECURITY")
        company = context.get("company_name", symbol)
        rev = context.get("revenue", 0)

        facts = [
            f"Latest annualized revenue reported at ${rev:,.0f} from primary filings.",
            "Operating cash flows consistently exceed reported net income across reporting cycles.",
            "Return on Invested Capital (ROIC) exceeds estimated cost of capital (WACC).",
        ]
        inferences = [
            "Company demonstrates strong capital efficiency and pricing power.",
            "Balance sheet exhibits robust liquidity with conservative debt-to-EBITDA coverage.",
        ]

        return AgentOutput(
            agent_name=self.name,
            status="COMPLETED",
            summary=f"Fundamental analysis for {company} ({symbol}) confirms high financial quality.",
            facts=facts,
            calculations={"revenue": rev, "quality_tier": "Tier-1 High Quality"},
            inferences=inferences,
            uncertainties=["Long-term margin trajectory depends on continued service expansion."],
            citations=["SEC EDGAR Form 10-K / 10-Q XBRL", "Company Facts Database"],
            confidence=0.92,
        )
