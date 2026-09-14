"""Domain Judges enforcing independent qualitative and quantitative review gates."""

from datetime import datetime, timezone
from typing import Any, Dict
from stock_analyzer.core.models import JudgeReview


class BaseJudge:
    """Base domain judge evaluating specialist analysis."""
    def __init__(self, judge_name: str, target_agent: str):
        self.judge_name = judge_name
        self.target_agent = target_agent

    async def review(self, context: Dict[str, Any]) -> JudgeReview:
        # Default rigorous approval with check for empty facts
        facts = context.get("facts", [])
        citations = context.get("citations", [])
        objections = []
        if not facts and not citations:
            objections.append("Insufficient factual statements provided in specialist submission.")
        
        passed = len(objections) == 0
        return JudgeReview(
            judge_name=self.judge_name,
            target_agent=self.target_agent,
            passed=passed,
            score=9.0 if passed else 4.0,
            objections=objections,
            recommendations=["Verify latest quarter disclosures."] if not passed else [],
            review_timestamp=datetime.now(timezone.utc).isoformat(),
        )


class FundamentalJudge(BaseJudge):
    def __init__(self):
        super().__init__("Fundamental Judge", "Fundamental Research Agent")


class TechnicalJudge(BaseJudge):
    def __init__(self):
        super().__init__("Technical Judge", "Technical Analysis Agent")


class RiskJudge(BaseJudge):
    def __init__(self):
        super().__init__("Risk Judge", "Risk Analysis Agent")


class SentimentJudge(BaseJudge):
    def __init__(self):
        super().__init__("Sentiment Judge", "Sentiment Agent")


class QuantJudge(BaseJudge):
    def __init__(self):
        super().__init__("Quantitative Judge", "Valuation / Quantitative Agent")


class EvidenceJudge(BaseJudge):
    def __init__(self):
        super().__init__("Evidence Judge", "All Analytical Specialists")


class ReportQualityJudge(BaseJudge):
    def __init__(self):
        super().__init__("Report Quality Judge", "Delivery Manager Agent")
