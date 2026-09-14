"""Intrinsic and Relative Valuation Engine."""

import math
from typing import Any, Dict, List, Tuple
import numpy as np


class ValuationEngine:
    """Calculates DCF intrinsic value, reverse DCF implied expectations, Graham Number, and peer rankings."""

    def compute_graham_number(self, eps: float, bvps: float) -> float:
        """
        Benjamin Graham Number = sqrt(22.5 * EPS * BVPS).
        Returns 0.0 if either EPS or BVPS is non-positive.
        """
        if eps <= 0 or bvps <= 0:
            return 0.0
        return round(math.sqrt(22.5 * eps * bvps), 2)

    def compute_dcf(
        self,
        base_fcf: float,
        growth_rate: float = 0.06,
        wacc: float = 0.085,
        terminal_growth: float = 0.025,
        projection_years: int = 5,
        shares_outstanding: float = 1.0,
        net_debt: float = 0.0,
    ) -> Dict[str, Any]:
        """
        5-Year Discounted Cash Flow (FCFF) intrinsic value calculation
        with perpetuity growth terminal value and 5x5 sensitivity matrix.
        """
        wacc = max(wacc, 0.04)
        terminal_growth = min(terminal_growth, 0.03)

        # 1. Project cash flows
        projected_fcf: List[float] = []
        discounted_fcf: List[float] = []
        curr_fcf = max(base_fcf, 1000.0)

        for year in range(1, projection_years + 1):
            # Fade growth rate slightly over the 5 years
            fade_factor = 1.0 - (year - 1) * 0.05
            effective_g = growth_rate * fade_factor
            curr_fcf *= (1.0 + effective_g)
            projected_fcf.append(curr_fcf)
            pv = curr_fcf / ((1.0 + wacc) ** year)
            discounted_fcf.append(pv)

        pv_fcf_sum = sum(discounted_fcf)

        # 2. Terminal Value
        terminal_val = (curr_fcf * (1.0 + terminal_growth)) / max(wacc - terminal_growth, 0.01)
        pv_terminal_val = terminal_val / ((1.0 + wacc) ** projection_years)

        enterprise_value = pv_fcf_sum + pv_terminal_val
        # Cap TV at 75% of EV if disproportionate
        if enterprise_value > 0 and (pv_terminal_val / enterprise_value) > 0.75:
            enterprise_value = pv_fcf_sum / 0.25

        equity_value = enterprise_value - net_debt
        shares = max(shares_outstanding, 1.0)
        intrinsic_per_share = max(equity_value / shares, 0.0)

        # 3. 5x5 Sensitivity Matrix (WACC delta vs Terminal Growth delta)
        wacc_deltas = [-0.01, -0.005, 0.0, 0.005, 0.01]
        tg_deltas = [-0.01, -0.005, 0.0, 0.005, 0.01]
        sensitivity_matrix: List[List[float]] = []

        for dw in wacc_deltas:
            row: List[float] = []
            for dt in tg_deltas:
                adj_wacc = max(wacc + dw, 0.04)
                adj_tg = min(terminal_growth + dt, adj_wacc - 0.005)
                
                adj_pv_sum = sum(fcf / ((1.0 + adj_wacc) ** y) for y, fcf in enumerate(projected_fcf, 1))
                adj_tv = (projected_fcf[-1] * (1.0 + adj_tg)) / (adj_wacc - adj_tg)
                adj_pv_tv = adj_tv / ((1.0 + adj_wacc) ** projection_years)
                adj_ev = adj_pv_sum + adj_pv_tv
                adj_eq = adj_ev - net_debt
                row.append(round(max(adj_eq / shares, 0.0), 2))
            sensitivity_matrix.append(row)

        return {
            "intrinsic_value_per_share": round(intrinsic_per_share, 2),
            "enterprise_value": round(enterprise_value, 2),
            "equity_value": round(equity_value, 2),
            "pv_fcf_sum": round(pv_fcf_sum, 2),
            "pv_terminal_value": round(pv_terminal_val, 2),
            "sensitivity_matrix": sensitivity_matrix,
            "wacc_used": round(wacc, 4),
            "terminal_growth_used": round(terminal_growth, 4),
        }

    def compute_reverse_dcf(
        self,
        current_price: float,
        base_fcf: float,
        wacc: float = 0.085,
        shares_outstanding: float = 1.0,
        net_debt: float = 0.0,
    ) -> float:
        """Finds the 5-year FCF CAGR implied by the current market price via binary search."""
        target_equity_value = current_price * shares_outstanding
        low_g = -0.50
        high_g = 1.00

        for _ in range(30):
            mid_g = (low_g + high_g) / 2
            dcf_res = self.compute_dcf(
                base_fcf=base_fcf,
                growth_rate=mid_g,
                wacc=wacc,
                shares_outstanding=shares_outstanding,
                net_debt=net_debt,
            )
            val = dcf_res["equity_value"]
            if val < target_equity_value:
                low_g = mid_g
            else:
                high_g = mid_g

        return round((low_g + high_g) / 2, 4)

    def compute_peer_percentile(
        self, company_multiple: float, peer_multiples: List[float]
    ) -> Tuple[float, float]:
        """
        Computes the percentile rank (0-100) of company's multiple vs peer group
        and the percentage discount/premium to peer median.
        """
        if not peer_multiples:
            return 50.0, 0.0

        clean_peers = sorted([p for p in peer_multiples if p > 0])
        if not clean_peers:
            return 50.0, 0.0

        median_peer = float(np.median(clean_peers))
        rank = sum(1 for p in clean_peers if company_multiple > p)
        percentile = (rank / len(clean_peers)) * 100

        discount = ((median_peer - company_multiple) / median_peer) * 100
        return round(percentile, 1), round(discount, 1)
