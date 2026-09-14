"""Accounting Forensics and Earnings Quality Engine."""

from typing import Any, Dict, Tuple


class ForensicsEngine:
    """Detects accounting anomalies, accrual inflation, and bankruptcy risk."""

    def compute_piotroski_f_score(self, data: Dict[str, Any]) -> Tuple[int, Dict[str, bool]]:
        """
        Calculates the 9-point Piotroski F-Score across 3 dimensions:
        1. Profitability (ROA, CFO, delta ROA, CFO > Net Income)
        2. Leverage, Liquidity and Source of Funds (delta Long-term Debt, delta Current Ratio, Dilution)
        3. Operating Efficiency (delta Gross Margin, delta Asset Turnover)
        """
        breakdown: Dict[str, bool] = {}

        ni = data.get("net_income", 0)
        cfo = data.get("operating_cash_flow", 0)
        assets_curr = max(data.get("total_assets_current", 1.0), 1.0)
        assets_prior = max(data.get("total_assets_prior", 1.0), 1.0)

        # 1. Profitability
        roa_curr = ni / assets_curr
        roa_prior = ni / assets_prior
        breakdown["positive_net_income"] = ni > 0
        breakdown["positive_cfo"] = cfo > 0
        breakdown["improving_roa"] = roa_curr >= roa_prior
        breakdown["cfo_greater_than_net_income"] = cfo > ni

        # 2. Leverage & Liquidity
        debt_curr = data.get("long_term_debt_current", 0)
        debt_prior = data.get("long_term_debt_prior", 0)
        breakdown["lower_long_term_debt"] = debt_curr <= debt_prior

        cr_curr = data.get("current_ratio_current", 1.0)
        cr_prior = data.get("current_ratio_prior", 1.0)
        breakdown["improving_current_ratio"] = cr_curr >= cr_prior

        shares_curr = data.get("shares_current", 1)
        shares_prior = data.get("shares_prior", 1)
        breakdown["no_dilution"] = shares_curr <= shares_prior

        # 3. Operating Efficiency
        gm_curr = data.get("gross_margin_current", 0.4)
        gm_prior = data.get("gross_margin_prior", 0.4)
        breakdown["improving_gross_margin"] = gm_curr >= gm_prior

        sales_curr = data.get("sales", 1.0)
        at_curr = sales_curr / assets_curr
        at_prior = sales_curr / assets_prior
        breakdown["improving_asset_turnover"] = at_curr >= at_prior

        score = sum(1 for passed in breakdown.values() if passed)
        return score, breakdown

    def compute_altman_z_score(self, data: Dict[str, Any]) -> Tuple[float, str]:
        """
        Altman Z-Score for public non-financial companies:
        Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5
        X1 = Working Capital / Total Assets
        X2 = Retained Earnings / Total Assets
        X3 = EBIT / Total Assets
        X4 = Market Value of Equity / Total Liabilities
        X5 = Sales / Total Assets
        """
        assets = max(data.get("total_assets_current", 1.0), 1.0)
        wc = data.get("current_assets", 0) - data.get("current_liabilities", 0)
        re = data.get("retained_earnings", 0)
        ebit = data.get("ebit", 0)
        market_cap = data.get("market_cap", 1.0)
        liabilities = max(data.get("total_liabilities", 1.0), 1.0)
        sales = data.get("sales", 0)

        x1 = wc / assets
        x2 = re / assets
        x3 = ebit / assets
        x4 = market_cap / liabilities
        x5 = sales / assets

        z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5

        if z > 2.99:
            status = "Safe Zone"
        elif z >= 1.81:
            status = "Grey Zone"
        else:
            status = "Distress Zone"

        return round(z, 2), status

    def compute_sloan_accruals(
        self, net_income: float, operating_cash_flow: float, total_assets: float
    ) -> float:
        """
        Sloan Accrual Ratio = (Net Income - Operating Cash Flow) / Total Assets.
        Ratios > 0.10 indicate aggressive accrual accounting / low cash conversion.
        """
        assets = max(total_assets, 1.0)
        return round((net_income - operating_cash_flow) / assets, 4)
