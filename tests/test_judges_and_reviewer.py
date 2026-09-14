"""Tests for Independent Domain Judges and Adversarial Chief Reviewer."""

import pytest
from stock_analyzer.agents.judges.domain_judges import (
    FundamentalJudge,
    TechnicalJudge,
    EvidenceJudge,
    QuantJudge,
)
from stock_analyzer.agents.chief_reviewer import ChiefReviewer
from stock_analyzer.core.models import AgentOutput, JudgeReview, ChiefReviewOutput

@pytest.mark.asyncio
async def test_domain_judges():
    fund_judge = FundamentalJudge()
    review = await fund_judge.review({"facts": ["Revenue grew 5%"], "evidence": [{"source": "10-K"}]})
    assert isinstance(review, JudgeReview)
    assert review.passed is True
    assert review.judge_name == "Fundamental Judge"

    tech_judge = TechnicalJudge()
    rev_tech = await tech_judge.review({"facts": ["50 SMA above 200 SMA"]})
    assert rev_tech.passed is True

    ev_judge = EvidenceJudge()
    rev_ev = await ev_judge.review({"citations": ["SEC 10-K"]})
    assert rev_ev.passed is True

@pytest.mark.asyncio
async def test_chief_reviewer_adversarial_critique():
    reviewer = ChiefReviewer()
    # Scenario without critical defects
    clean_context = {
        "symbol": "AAPL",
        "contradictions": [],
        "weak_assumptions": [],
    }
    out = await reviewer.adversarial_review(clean_context)
    assert isinstance(out, ChiefReviewOutput)
    assert out.passed is True
    assert out.approved_for_delivery is True
    assert len(out.falsification_challenges) > 0

@pytest.mark.asyncio
async def test_chief_reviewer_rework_trigger():
    reviewer = ChiefReviewer()
    # Scenario with critical contradiction
    defect_context = {
        "symbol": "AAPL",
        "contradictions": ["Stock technicals flag extreme overbought while DCF models severe growth contraction."],
        "weak_assumptions": ["Revenue assumed to grow 50% despite 0% historical CAGR."],
    }
    out = await reviewer.adversarial_review(defect_context)
    assert out.passed is False
    assert out.approved_for_delivery is False
    assert len(out.critical_defects) > 0
