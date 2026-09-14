"""Scenario Analysis Specialist Agent."""

from typing import Any, Dict
from stock_analyzer.agents.base import BaseAgent
from stock_analyzer.core.models import AgentOutput


class ScenarioAgent(BaseAgent):
    """Constructs Bull, Base, Bear, and Stress cases with explicit operational assumptions."""

    def __init__(self):
        super().__init__(
            name="Scenario Analysis Agent",
            role="Formulate Bull, Base, Bear, and Stress investment scenarios with invalidation criteria.",
            system_instructions=(
                "You are the Scenario Analysis Agent. You must formulate four explicit investment scenarios: "
                "Bull Case, Base Case, Bear Case, and Stress Case with target estimates and invalidation criteria. "
                "Explicitly include 'Bull Case', 'Base Case', 'Bear Case', and 'Stress Case' in your facts or inferences."
            ),
        )

    def _run_offline_mock(self, context: Dict[str, Any]) -> AgentOutput:
        symbol = context.get("symbol", "SECURITY")
        company = context.get("company_name", symbol)
        curr_price = context.get("close", 220.0)

        bull_target = round(curr_price * 1.25, 2)
        base_target = round(curr_price * 1.08, 2)
        bear_target = round(curr_price * 0.82, 2)
        stress_target = round(curr_price * 0.65, 2)

        facts = [
            f"Bull Case Target: ${bull_target} — Accelerated high-margin software/services adoption and enterprise hardware refresh cycle.",
            f"Base Case Target: ${base_target} — Steady single-digit top-line expansion with stable operating margins and ongoing share buybacks.",
            f"Bear Case Target: ${bear_target} — Cyclical consumer spending slowdown combined with regulatory app store fee compression.",
            f"Stress Case Target: ${stress_target} — Global trade dislocation combined with acute component supply disruptions.",
        ]
        inferences = [
            "Probability-weighted expected value indicates asymmetric upside over a 12-month horizon.",
            "Key invalidation trigger: Operating margin contraction exceeding 300 basis points YoY.",
        ]

        return AgentOutput(
            agent_name=self.name,
            status="COMPLETED",
            summary=f"Scenario analysis for {company} ({symbol}): Base Case ${base_target}, Bull Case ${bull_target}, Bear Case ${bear_target}.",
            facts=facts,
            calculations={
                "bull_target": bull_target,
                "base_target": base_target,
                "bear_target": bear_target,
                "stress_target": stress_target,
            },
            inferences=inferences,
            uncertainties=["Scenarios represent model estimates and depend on timely product release cycles."],
            citations=["5-Year Scenario Simulation Model", "Historical Drawdown Distribution"],
            confidence=0.87,
        )
