"""Adversarial Chief Reviewer Agent."""

from typing import Any, Dict, List
from stock_analyzer.core.models import ChiefReviewOutput


class ChiefReviewer:
    """
    Adversarial reviewer tasked with challenging the core thesis,
    detecting unaddressed contradictions, and preventing unjustified certainty.
    """

    def __init__(self):
        self.name = "Chief Reviewer"

    async def adversarial_review(self, context: Dict[str, Any]) -> ChiefReviewOutput:
        """Evaluate complete analysis bundle for critical defects, contradictions, and bias."""
        contradictions = context.get("contradictions", [])
        weak_assumptions = context.get("weak_assumptions", [])
        symbol = context.get("symbol", "SECURITY")

        falsification_challenges = [
            f"What happens if terminal cost of capital rises 100 bps faster than anticipated?",
            f"Are consumer hardware refresh cycles extending beyond historical 3-year baselines?",
            f"Does the valuation peer group over-represent high-multiple cloud software comparables?",
        ]

        critical_defects: List[str] = []
        if contradictions:
            critical_defects.extend([f"Critical contradiction detected: {c}" for c in contradictions])
        if len(weak_assumptions) > 2:
            critical_defects.append("Excessive ungrounded assumptions identified across valuation inputs.")

        passed = len(critical_defects) == 0

        return ChiefReviewOutput(
            passed=passed,
            critical_defects=critical_defects,
            falsification_challenges=falsification_challenges,
            unresolved_contradictions=contradictions,
            confidence_penalty=0.0 if passed else 0.25,
            approved_for_delivery=passed,
        )
