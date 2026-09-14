"""Remaining Analytical Specialist Agents (Forensics, News, Business, Management, Macro, Quant)."""

from typing import Any, Dict
from stock_analyzer.agents.base import BaseAgent
from stock_analyzer.core.models import AgentOutput


class ForensicsAgent(BaseAgent):
    """Audits accruals, restatements, and earnings quality."""
    def __init__(self):
        super().__init__(name="Accounting Forensics Agent", role="Detect accounting anomalies and earnings inflation.")


class NewsEventsAgent(BaseAgent):
    """Detects corporate events, separating verified announcements from rumors."""
    def __init__(self):
        super().__init__(name="News & Event Intelligence Agent", role="Track and verify major corporate events and announcements.")


class BusinessAgent(BaseAgent):
    """Analyzes competitive moat, pricing power, and business model."""
    def __init__(self):
        super().__init__(name="Business & Competitive Analysis Agent", role="Assess economic moat, market position, and competitive barriers.")


class ManagementAgent(BaseAgent):
    """Analyzes insider transactions, executive compensation, and capital allocation."""
    def __init__(self):
        super().__init__(name="Management & Insider Agent", role="Evaluate insider buying/selling, share repurchases, and capital allocation.")


class MacroAgent(BaseAgent):
    """Translates macroeconomic trends and benchmark rates into company impact."""
    def __init__(self):
        super().__init__(name="Macro & Industry Agent", role="Analyze macro conditions, inflation, and interest rate sensitivities.")


class QuantAgent(BaseAgent):
    """Performs statistical return analysis, drawdown measurement, and factor exposures."""
    def __init__(self):
        super().__init__(name="Quantitative Research Agent", role="Compute statistical risk metrics, beta, volatility, and historical drawdowns.")
