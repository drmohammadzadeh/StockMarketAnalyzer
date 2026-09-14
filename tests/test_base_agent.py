"""Tests for BaseAgent and Gemini Flash 3.8 / Mock Runner."""

import pytest
from stock_analyzer.agents.base import BaseAgent
from stock_analyzer.core.models import AgentOutput

@pytest.mark.asyncio
async def test_base_agent_offline_mock():
    agent = BaseAgent(name="TestAgent", role="Financial Tester")
    context = {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "revenue": 391035000000,
        "close": 225.50,
    }
    output = await agent.run(context)
    assert isinstance(output, AgentOutput)
    assert output.agent_name == "TestAgent"
    assert output.status == "COMPLETED"
    assert len(output.facts) > 0 or len(output.summary) > 0
    assert 0.0 <= output.confidence <= 1.0

@pytest.mark.asyncio
async def test_base_agent_prompt_builder():
    agent = BaseAgent(name="TestAgent", role="Financial Tester")
    prompt = agent.build_prompt({"symbol": "AAPL", "task": "analyze_growth"})
    assert "AAPL" in prompt
    assert "TestAgent" in prompt
