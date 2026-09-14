"""Tests for Analytical Specialist Agents."""

import pytest
from stock_analyzer.agents.specialists.fundamental import FundamentalAgent
from stock_analyzer.agents.specialists.technical import TechnicalAgent
from stock_analyzer.agents.specialists.valuation import ValuationAgent
from stock_analyzer.agents.specialists.risk import RiskAgent
from stock_analyzer.agents.specialists.sentiment import SentimentAgent
from stock_analyzer.agents.specialists.scenario import ScenarioAgent

@pytest.mark.asyncio
async def test_specialists_execution():
    context = {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "revenue": 391035000000,
        "close": 225.50,
        "indicators": {"RSI_14": 55.4, "SMA_50": 218.0, "SMA_200": 195.0},
        "valuation": {"intrinsic_value_per_share": 210.0, "graham_number": 60.47},
    }

    fund_agent = FundamentalAgent()
    out_fund = await fund_agent.run(context)
    assert out_fund.status == "COMPLETED"
    assert out_fund.agent_name == "Fundamental Research Agent"

    tech_agent = TechnicalAgent()
    out_tech = await tech_agent.run(context)
    assert out_tech.status == "COMPLETED"
    assert out_tech.agent_name == "Technical Analysis Agent"

    val_agent = ValuationAgent()
    out_val = await val_agent.run(context)
    assert out_val.status == "COMPLETED"

    risk_agent = RiskAgent()
    out_risk = await risk_agent.run(context)
    assert out_risk.status == "COMPLETED"

    sent_agent = SentimentAgent()
    out_sent = await sent_agent.run(context)
    assert out_sent.status == "COMPLETED"

    scen_agent = ScenarioAgent()
    out_scen = await scen_agent.run(context)
    assert out_scen.status == "COMPLETED"
    assert "Bull Case" in str(out_scen.facts) or "Bull Case" in str(out_scen.inferences) or "Bull Case" in out_scen.summary
