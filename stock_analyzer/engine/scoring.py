"""Deterministic Scoring Engine and Confidence Assessment."""

from typing import Dict
from stock_analyzer.core.models import ScoringResult


class ScoringEngine:
    """Calculates all 1.0-10.0 sub-scores, composite AI Score, and confidence metrics."""

    WEIGHT_FUNDAMENTAL: float = 0.40
    WEIGHT_TECHNICAL: float = 0.35
    WEIGHT_SENTIMENT: float = 0.15
    WEIGHT_MACRO_EVENT: float = 0.10

    def calculate_scores(
        self, sub_scores: Dict[str, float], penalties: Dict[str, float]
    ) -> ScoringResult:
        """
        Calculates Base AI Score, Extended AI Score, 0-100 normalized score,
        and Confidence score with itemized deductions.
        """
        # Clamp all sub-scores to [1.0, 10.0]
        clamped_scores = {k: max(1.0, min(10.0, float(v))) for k, v in sub_scores.items()}

        fund = clamped_scores.get("fundamental", 5.0)
        tech = clamped_scores.get("technical", 5.0)
        sent = clamped_scores.get("sentiment", 5.0)
        macro = clamped_scores.get("macro_event_risk", clamped_scores.get("event_risk", 5.0))

        # Base AI Score (1.0 to 10.0)
        base_ai_score = (
            self.WEIGHT_FUNDAMENTAL * fund
            + self.WEIGHT_TECHNICAL * tech
            + self.WEIGHT_SENTIMENT * sent
            + self.WEIGHT_MACRO_EVENT * macro
        )
        base_ai_score = round(max(1.0, min(10.0, base_ai_score)), 2)

        # Extended AI Score (incorporating Quality, Valuation, Growth, Moat, Management)
        extended_weights = {
            "fundamental": 0.25,
            "technical": 0.20,
            "valuation": 0.15,
            "quality": 0.10,
            "growth": 0.10,
            "sentiment": 0.08,
            "business_strength": 0.06,
            "event_risk": 0.06,
        }
        extended_sum = 0.0
        weight_total = 0.0
        for metric, w in extended_weights.items():
            if metric in clamped_scores:
                extended_sum += w * clamped_scores[metric]
                weight_total += w
        
        extended_ai_score = (
            round(extended_sum / max(weight_total, 0.01), 2)
            if weight_total > 0 else base_ai_score
        )

        # Normalized 0-100 Score
        # (Score - 1.0) / 9.0 * 100
        normalized_100_score = round(((base_ai_score - 1.0) / 9.0) * 100.0, 1)

        # Confidence Score (0.0 to 1.0)
        total_penalties = sum(max(0.0, float(p)) for p in penalties.values())
        confidence_score = round(max(0.0, min(1.0, 1.0 - total_penalties)), 2)

        return ScoringResult(
            sub_scores=clamped_scores,
            base_ai_score=base_ai_score,
            extended_ai_score=extended_ai_score,
            normalized_100_score=normalized_100_score,
            confidence_score=confidence_score,
            penalties=penalties,
        )
