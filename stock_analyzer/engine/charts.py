"""Chart generation engine for Institutional Stock Research.
Generates:
1. GuruFocus-style Radar / Spider Score Chart (5-dimensional polygon).
2. TradingView-style Technical Indicator Speedometer Gauges (Oscillators, Summary, Moving Averages).
"""

from pathlib import Path
from typing import Any, Dict, Optional
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Rectangle


def generate_radar_chart(
    symbol: str,
    company_name: str,
    score_100: float,
    dimensions: Dict[str, float],
    output_path: Path,
    year: int = 2026,
) -> Path:
    """
    Renders a GuruFocus-style Radar / Spider Chart with 5 key axes:
    - Profitability (top)
    - Valuation / GF Value (top right)
    - Momentum (bottom right)
    - Financial Strength (bottom left)
    - Growth (top left)
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    categories = [
        "Profitability",
        "Valuation",
        "Momentum",
        "Financial\nStrength",
        "Growth",
    ]
    
    values = [
        float(dimensions.get("profitability", 90.0)),
        float(dimensions.get("valuation", 65.0)),
        float(dimensions.get("momentum", 85.0)),
        float(dimensions.get("financial_strength", 80.0)),
        float(dimensions.get("growth", 88.0)),
    ]
    # Bound between 10 and 100
    values = [max(15.0, min(100.0, v)) for v in values]
    num_vars = len(categories)

    # Angles starting from 0 to 2*pi, offset to top (12 o'clock) and moving clockwise
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values_closed = values + [values[0]]
    angles_closed = angles + [angles[0]]

    fig = plt.figure(figsize=(7.5, 7.5), dpi=200, facecolor="white")
    ax = fig.add_subplot(111, polar=True, facecolor="white")
    ax.set_theta_offset(np.pi / 2)   # start at top (12 o'clock)
    ax.set_theta_direction(-1)       # clockwise direction

    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels([])

    # Shaded concentric rings matching GuruFocus soft green/mint aesthetic
    theta_full = np.linspace(0, 2 * np.pi, 200)
    ax.fill_between(theta_full, 0, 100, color="#f0fdf4", alpha=0.55)
    ax.fill_between(theta_full, 0, 80, color="#dcfce7", alpha=0.55)
    ax.fill_between(theta_full, 0, 60, color="#bbf7d0", alpha=0.50)
    ax.fill_between(theta_full, 0, 40, color="#86efac", alpha=0.35)
    ax.fill_between(theta_full, 0, 20, color="#4ade80", alpha=0.25)

    ax.grid(color="#86efac", linestyle="-", linewidth=1.2, alpha=0.7)
    ax.spines["polar"].set_color("#4ade80")
    ax.spines["polar"].set_linewidth(1.8)

    # Plot filled polygon
    ax.plot(angles_closed, values_closed, color="#15803d", linewidth=3.0, linestyle="solid", zorder=8)
    ax.fill(angles_closed, values_closed, color="#22c55e", alpha=0.50, zorder=7)
    ax.scatter(angles, values, color="#166534", s=85, zorder=10, edgecolors="white", linewidth=2.0)

    # Category labels on vertices
    ax.set_xticks(angles)
    ax.set_xticklabels(categories, fontsize=12, fontweight="bold", color="#0f172a")

    # Fine-tune category label padding
    ax.tick_params(pad=16)

    # Top banner matching GuruFocus GF Score™ header
    score_display = int(round(score_100))
    fig.text(
        0.08,
        0.93,
        f"GF Score™: {score_display} / 100",
        fontsize=20,
        fontweight="bold",
        color="#0f172a",
    )
    fig.text(
        0.66,
        0.93,
        f"Year: {year}",
        fontsize=13,
        fontweight="bold",
        color="#334155",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.2),
    )
    fig.text(
        0.08,
        0.88,
        f"{company_name} ({symbol}) — Comprehensive Performance Pentagon",
        fontsize=11,
        color="#64748b",
    )

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.88])
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output_path


def _draw_gauge(
    ax: plt.Axes,
    center_x: float,
    center_y: float,
    radius: float,
    needle_angle_deg: float,
    title: str,
    verdict: str,
    sell_count: int,
    neutral_count: int,
    buy_count: int,
    verdict_color: str = "#2563eb",
):
    """Draws a single TradingView-style semicircular speedometer gauge."""
    arc_width = radius * 0.18

    # Red zone (Sell: 180° to 120°)
    wedge_sell = Wedge(
        (center_x, center_y),
        radius,
        120,
        180,
        width=arc_width,
        facecolor="#ef4444",
        edgecolor="white",
        linewidth=1.8,
        zorder=4,
    )
    ax.add_patch(wedge_sell)

    # Gray zone (Neutral: 120° to 60°)
    wedge_neutral = Wedge(
        (center_x, center_y),
        radius,
        60,
        120,
        width=arc_width,
        facecolor="#94a3b8",
        edgecolor="white",
        linewidth=1.8,
        zorder=4,
    )
    ax.add_patch(wedge_neutral)

    # Blue zone (Buy: 60° to 0°)
    wedge_buy = Wedge(
        (center_x, center_y),
        radius,
        0,
        60,
        width=arc_width,
        facecolor="#3b82f6",
        edgecolor="white",
        linewidth=1.8,
        zorder=4,
    )
    ax.add_patch(wedge_buy)

    # Ticks along the arc
    for deg in [180, 150, 120, 90, 60, 30, 0]:
        rad = np.radians(deg)
        x_inner = center_x + (radius - arc_width) * np.cos(rad)
        y_inner = center_y + (radius - arc_width) * np.sin(rad)
        x_outer = center_x + radius * np.cos(rad)
        y_outer = center_y + radius * np.sin(rad)
        ax.plot([x_inner, x_outer], [y_inner, y_outer], color="white", linewidth=1.5, zorder=5)

    # Needle
    needle_rad = np.radians(needle_angle_deg)
    needle_len = radius * 0.88
    nx = center_x + needle_len * np.cos(needle_rad)
    ny = center_y + needle_len * np.sin(needle_rad)

    ax.plot([center_x, nx], [center_y, ny], color="#0f172a", linewidth=3.8, solid_capstyle="round", zorder=8)
    pivot = plt.Circle((center_x, center_y), radius * 0.12, facecolor="#0f172a", edgecolor="white", linewidth=1.8, zorder=9)
    ax.add_patch(pivot)

    # Title and Verdict text beneath gauge
    ax.text(center_x, center_y - radius * 0.22, title, fontsize=13, color="#475569", ha="center", va="top", zorder=10)
    ax.text(center_x, center_y - radius * 0.44, verdict, fontsize=16, fontweight="bold", color=verdict_color, ha="center", va="top", zorder=10)

    # Breakdown card box (Sell | Neutral | Buy)
    box_w = radius * 1.55
    box_h = radius * 0.46
    box_bottom = center_y - radius * 1.15

    rect = Rectangle(
        (center_x - box_w / 2, box_bottom),
        box_w,
        box_h,
        facecolor="#f8fafc",
        edgecolor="#cbd5e1",
        linewidth=1.2,
        zorder=6,
    )
    ax.add_patch(rect)

    # Column centers
    col_step = box_w / 3
    col1 = center_x - col_step
    col2 = center_x
    col3 = center_x + col_step

    label_y = box_bottom + box_h * 0.65
    val_y = box_bottom + box_h * 0.25

    # Headers
    ax.text(col1, label_y, "Sell", fontsize=9, color="#64748b", ha="center", va="center", zorder=10)
    ax.text(col2, label_y, "Neutral", fontsize=9, color="#64748b", ha="center", va="center", zorder=10)
    ax.text(col3, label_y, "Buy", fontsize=9, color="#64748b", ha="center", va="center", zorder=10)

    # Values
    ax.text(col1, val_y, str(sell_count), fontsize=12, fontweight="bold", color="#ef4444", ha="center", va="center", zorder=10)
    ax.text(col2, val_y, str(neutral_count), fontsize=12, fontweight="bold", color="#475569", ha="center", va="center", zorder=10)
    ax.text(col3, val_y, str(buy_count), fontsize=12, fontweight="bold", color="#3b82f6", ha="center", va="center", zorder=10)


def generate_technical_gauges(
    symbol: str,
    company_name: str,
    current_price: float,
    price_change: float,
    price_change_pct: float,
    technical_votes: Optional[Dict[str, Any]] = None,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Renders TradingView-style 3 Semicircular Technical Gauges:
    - Oscillators (Left)
    - Summary (Center)
    - Moving Averages (Right)
    """
    if output_path is None:
        output_path = Path("technical_gauges.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    votes = technical_votes or {}
    
    # Oscillators
    osc_sell = votes.get("osc_sell", 1)
    osc_neutral = votes.get("osc_neutral", 9)
    osc_buy = votes.get("osc_buy", 1)
    osc_verdict = votes.get("osc_verdict", "Neutral")
    osc_color = "#64748b" if osc_verdict == "Neutral" else ("#3b82f6" if "Buy" in osc_verdict else "#ef4444")
    osc_angle = 90.0 if osc_verdict == "Neutral" else (40.0 if "Buy" in osc_verdict else 140.0)

    # Moving Averages
    ma_sell = votes.get("ma_sell", 2)
    ma_neutral = votes.get("ma_neutral", 1)
    ma_buy = votes.get("ma_buy", 12)
    ma_verdict = votes.get("ma_verdict", "Strong buy")
    ma_color = "#2563eb" if "Buy" in ma_verdict else ("#ef4444" if "Sell" in ma_verdict else "#64748b")
    ma_angle = 20.0 if "Strong" in ma_verdict else (45.0 if "Buy" in ma_verdict else 140.0)

    # Summary
    sum_sell = osc_sell + ma_sell
    sum_neutral = osc_neutral + ma_neutral
    sum_buy = osc_buy + ma_buy
    if sum_buy >= sum_sell + 8:
        sum_verdict = "Strong buy"
        sum_angle = 25.0
        sum_color = "#2563eb"
    elif sum_buy > sum_sell + 2:
        sum_verdict = "Buy"
        sum_angle = 45.0
        sum_color = "#2563eb"
    elif sum_sell > sum_buy + 2:
        sum_verdict = "Sell"
        sum_angle = 135.0
        sum_color = "#ef4444"
    else:
        sum_verdict = "Neutral"
        sum_angle = 90.0
        sum_color = "#64748b"

    fig, ax = plt.subplots(figsize=(13, 6.8), dpi=200, facecolor="white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 13)
    ax.set_ylim(-1.5, 5.8)
    ax.axis("off")

    change_sign = "+" if price_change >= 0 else ""
    change_color = "#16a34a" if price_change >= 0 else "#dc2626"

    # Header section matching TradingView
    fig.text(0.06, 0.93, f"{company_name}", fontsize=22, fontweight="bold", color="#0f172a")
    fig.text(
        0.06,
        0.87,
        f"{symbol} • Nasdaq Stock Market • USD",
        fontsize=11,
        fontweight="bold",
        color="#475569",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.0),
    )
    fig.text(
        0.06,
        0.78,
        f"${current_price:.2f}",
        fontsize=28,
        fontweight="bold",
        color="#0f172a",
    )
    fig.text(
        0.24,
        0.79,
        f"{change_sign}{price_change:.2f}  {change_sign}{price_change_pct:.2f}%",
        fontsize=15,
        fontweight="bold",
        color=change_color,
    )

    # Subtitle matching user image
    fig.text(0.06, 0.70, "Indicators' summary", fontsize=15, fontweight="bold", color="#1e293b")
    fig.text(
        0.06,
        0.65,
        "Technical analysis overview across momentum oscillators, trend moving averages, and pivot levels.",
        fontsize=11,
        color="#64748b",
    )

    radius = 1.45
    center_y = 1.8

    # Left Gauge: Oscillators
    _draw_gauge(
        ax=ax,
        center_x=2.5,
        center_y=center_y,
        radius=radius,
        needle_angle_deg=osc_angle,
        title="Oscillators",
        verdict=osc_verdict,
        sell_count=osc_sell,
        neutral_count=osc_neutral,
        buy_count=osc_buy,
        verdict_color=osc_color,
    )

    # Center Gauge: Summary
    _draw_gauge(
        ax=ax,
        center_x=6.5,
        center_y=center_y + 0.1,
        radius=radius * 1.15,
        needle_angle_deg=sum_angle,
        title="Summary",
        verdict=sum_verdict,
        sell_count=sum_sell,
        neutral_count=sum_neutral,
        buy_count=sum_buy,
        verdict_color=sum_color,
    )

    # Right Gauge: Moving Averages
    _draw_gauge(
        ax=ax,
        center_x=10.5,
        center_y=center_y,
        radius=radius,
        needle_angle_deg=ma_angle,
        title="Moving Averages",
        verdict=ma_verdict,
        sell_count=ma_sell,
        neutral_count=ma_neutral,
        buy_count=ma_buy,
        verdict_color=ma_color,
    )

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.96])
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output_path
