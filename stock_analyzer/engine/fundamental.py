"""Fundamental Financial Ratios and Health Metrics Engine."""

from typing import Any, Dict


class FundamentalEngine:
    """Calculates growth, quality, profitability, and balance-sheet solvency ratios."""

    def compute_metrics(
        self,
        revenue_current: float,
        revenue_prior: float,
        net_income: float,
        operating_cash_flow: float,
        capex: float,
        total_debt: float,
        cash_and_equiv: float,
        total_equity: float,
        operating_income: float,
        effective_tax_rate: float = 0.16,
    ) -> Dict[str, Any]:
        """Compute comprehensive fundamental metrics."""
        # Growth
        revenue_growth_yoy = ((revenue_current - revenue_prior) / max(abs(revenue_prior), 1.0)) * 100

        # Cash flow & margins
        fcf = operating_cash_flow - capex
        fcf_margin = (fcf / max(revenue_current, 1.0)) * 100
        net_margin = (net_income / max(revenue_current, 1.0)) * 100
        operating_margin = (operating_income / max(revenue_current, 1.0)) * 100

        # Capital efficiency (ROIC)
        # NOPAT = Operating Income * (1 - Tax Rate)
        # Invested Capital = Total Debt + Total Equity - Cash
        nopat = operating_income * (1.0 - effective_tax_rate)
        invested_capital = max(total_debt + total_equity - cash_and_equiv, 1000000.0)
        roic = nopat / invested_capital

        # Solvency
        net_debt = total_debt - cash_and_equiv
        net_debt_to_ebitda = net_debt / max(operating_income + capex * 0.5, 1.0)

        return {
            "revenue_growth_yoy": round(revenue_growth_yoy, 2),
            "free_cash_flow": round(fcf, 2),
            "fcf_margin": round(fcf_margin, 2),
            "net_margin": round(net_margin, 2),
            "operating_margin": round(operating_margin, 2),
            "roic": round(roic, 4),
            "net_debt": round(net_debt, 2),
            "net_debt_to_ebitda": round(net_debt_to_ebitda, 2),
        }
