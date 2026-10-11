"""Chart generation engine for Institutional Stock Research.
Generates:
1. GuruFocus-style Radar / Spider Score Chart (5-dimensional polygon).
2. TradingView-style Technical Indicator Speedometer Gauges (Oscillators, Summary, Moving Averages).
3. Trend Ribbon & Technical Price Action Chart (252-day price, 50/200 SMA ribbon, volume, 14-day RSI).
4. Financial Conversion & Cash Flow Waterfall Chart (Revenue -> EBIT -> Net Income -> CFO -> FCF).
5. Valuation Margin-of-Safety Gauge (Horizontal DCF Fair Value vs Market Price vs Graham Floor).
"""

from pathlib import Path
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
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


def generate_price_action_chart(
    df: pd.DataFrame,
    symbol: str,
    company_name: str,
    output_path: Path,
) -> Path:
    """
    Renders 252-day price action with 50/200 SMA trend ribbon, volume, and 14-day RSI.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean_df = df.copy()
    if clean_df.empty:
        raise ValueError("DataFrame cannot be empty")
    if "close" not in clean_df.columns:
        raise ValueError("DataFrame must contain 'close' column")

    close = clean_df["close"].astype(float)
    sma50 = close.rolling(50, min_periods=1).mean()
    sma200 = close.rolling(200, min_periods=1).mean()

    # RSI 14
    delta = close.diff()
    gain = delta.clip(lower=0.0).fillna(0.0)
    loss = (-delta.clip(upper=0.0)).fillna(0.0)
    avg_gain = gain.rolling(14, min_periods=1).mean()
    avg_loss = loss.rolling(14, min_periods=1).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-6)
    rsi14 = 100.0 - (100.0 / (1.0 + rs))

    fig, (ax_price, ax_rsi) = plt.subplots(
        2,
        1,
        figsize=(10, 6.5),
        dpi=200,
        facecolor="#0f172a",
        gridspec_kw={"height_ratios": [3.2, 1.2], "hspace": 0.15},
    )

    x = np.arange(len(close))
    ax_price.set_facecolor("#1e293b")
    ax_price.plot(x, close, color="#f8fafc", linewidth=2.0, label="Daily Close")
    ax_price.plot(x, sma50, color="#38bdf8", linewidth=1.8, label="50-Day SMA")
    ax_price.plot(x, sma200, color="#fbbf24", linewidth=1.8, label="200-Day SMA")

    # Shaded ribbon between SMAs
    ax_price.fill_between(
        x,
        sma50,
        sma200,
        where=(sma50 >= sma200),
        color="#22c55e",
        alpha=0.25,
        label="Bullish Regime",
    )
    ax_price.fill_between(
        x,
        sma50,
        sma200,
        where=(sma50 < sma200),
        color="#ef4444",
        alpha=0.25,
        label="Bearish Regime",
    )

    # Volume bars
    if "volume" in clean_df.columns:
        vol = clean_df["volume"].astype(float)
        ax_vol = ax_price.twinx()
        ax_vol.bar(x, vol, color="#64748b", alpha=0.3, width=0.8)
        max_vol = float(vol.max()) if len(vol) > 0 and vol.max() > 0 else 1.0
        ax_vol.set_ylim(0, max_vol * 4.0)
        ax_vol.axis("off")

    curr_p = close.iloc[-1]
    ax_price.set_title(
        f"{company_name} ({symbol}) — Price Action & Trend Ribbon | Close: ${curr_p:.2f}",
        fontsize=13,
        fontweight="bold",
        color="#f8fafc",
        pad=10,
    )
    ax_price.grid(color="#334155", linestyle="--", linewidth=0.7, alpha=0.6)
    ax_price.tick_params(colors="#94a3b8")
    ax_price.legend(
        loc="upper left",
        facecolor="#1e293b",
        edgecolor="#334155",
        labelcolor="#f8fafc",
        fontsize=9,
    )
    ax_price.set_xlim(0, max(1, len(close) - 1))
    ax_price.set_xticklabels([])

    # RSI Sub-panel
    ax_rsi.set_facecolor("#1e293b")
    ax_rsi.plot(x, rsi14, color="#a855f7", linewidth=1.8)
    ax_rsi.axhline(70, color="#ef4444", linestyle=":", linewidth=1.2, alpha=0.8)
    ax_rsi.axhline(30, color="#22c55e", linestyle=":", linewidth=1.2, alpha=0.8)
    ax_rsi.fill_between(x, 70, 100, color="#ef4444", alpha=0.15)
    ax_rsi.fill_between(x, 0, 30, color="#22c55e", alpha=0.15)
    ax_rsi.set_ylim(0, 100)
    ax_rsi.set_xlim(0, max(1, len(close) - 1))
    curr_rsi = rsi14.iloc[-1]
    ax_rsi.set_ylabel(
        f"RSI(14): {curr_rsi:.1f}", color="#f8fafc", fontsize=10, fontweight="bold"
    )
    ax_rsi.grid(color="#334155", linestyle="--", linewidth=0.7, alpha=0.6)
    ax_rsi.tick_params(colors="#94a3b8")

    if isinstance(clean_df.index, pd.DatetimeIndex) and len(clean_df) > 0:
        step = max(1, len(clean_df) // 6)
        tick_locs = list(range(0, len(clean_df), step))
        if tick_locs[-1] != len(clean_df) - 1:
            tick_locs.append(len(clean_df) - 1)
        tick_labels = [clean_df.index[i].strftime("%b %y") for i in tick_locs]
        ax_rsi.set_xticks(tick_locs)
        ax_rsi.set_xticklabels(tick_labels, color="#94a3b8", fontsize=8)

    plt.savefig(
        output_path,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        dpi=200,
    )
    plt.close(fig)
    return output_path


def generate_financial_waterfall_chart(
    financials: Dict[str, float],
    symbol: str,
    company_name: str,
    output_path: Path,
) -> Path:
    """
    Renders 5 operational pillars: Revenue, EBIT, Net Income, CFO, and FCF.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    financials_dict = financials or {}
    rev = float(financials_dict.get("revenue", 0.0) or 0.0) / 1e9
    op_inc = float(financials_dict.get("operating_income", 0.0) or 0.0) / 1e9
    ni = float(financials_dict.get("net_income", 0.0) or 0.0) / 1e9
    cfo = float(financials_dict.get("operating_cash_flow", 0.0) or 0.0) / 1e9
    fcf = float(financials_dict.get("free_cash_flow", 0.0) or 0.0) / 1e9

    categories = [
        "Revenue",
        "Operating\nIncome",
        "Net\nIncome",
        "Operating\nCash Flow",
        "Free Cash\nFlow (FCF)",
    ]
    vals = [rev, op_inc, ni, cfo, fcf]
    colors = ["#2563eb", "#0284c7", "#10b981", "#059669", "#16a34a"]

    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200, facecolor="#0f172a")
    ax.set_facecolor("#1e293b")

    bars = ax.bar(
        categories,
        vals,
        color=colors,
        width=0.55,
        edgecolor="#ffffff",
        linewidth=1.2,
        zorder=3,
    )
    ax.grid(axis="y", color="#334155", linestyle="--", linewidth=0.7, alpha=0.7, zorder=0)

    max_v = max(vals)
    min_v = min(vals)
    val_range = max(max_v - min(0.0, min_v), 1.0)
    offset = val_range * 0.02

    # Annotate dollar billions and conversion ratios
    for b, val in zip(bars, vals):
        h = b.get_height()
        label_text = f"${val:.1f}B" if val >= 0 else f"-${abs(val):.1f}B"
        if val >= 0:
            ax.text(
                b.get_x() + b.get_width() / 2.0,
                h + offset,
                label_text,
                ha="center",
                va="bottom",
                color="#f8fafc",
                fontweight="bold",
                fontsize=10,
            )
        else:
            ax.text(
                b.get_x() + b.get_width() / 2.0,
                h - offset,
                label_text,
                ha="center",
                va="top",
                color="#f8fafc",
                fontweight="bold",
                fontsize=10,
            )

    op_m = (op_inc / rev * 100.0) if rev != 0 else 0.0
    net_m = (ni / rev * 100.0) if rev != 0 else 0.0
    fcf_conv = (fcf / ni * 100.0) if ni != 0 else 0.0

    subtitle = (
        f"Operating Margin: {op_m:.1f}%  |  "
        f"Net Margin: {net_m:.1f}%  |  "
        f"FCF Conversion: {fcf_conv:.1f}%"
    )
    ax.set_title(
        f"{company_name} ({symbol}) — Financial Conversion & Cash Flow Engine\n{subtitle}",
        fontsize=12,
        fontweight="bold",
        color="#f8fafc",
        pad=14,
    )
    ax.tick_params(colors="#94a3b8")
    ax.set_ylabel("USD ($ Billions)", color="#94a3b8", fontsize=10)

    y_top = max(max_v * 1.15, 1.0) if max_v >= 0 else 1.0
    y_bottom = min(min_v * 1.15, 0.0) if min_v < 0 else 0.0
    ax.set_ylim(y_bottom, y_top)

    plt.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor(), dpi=200)
    plt.close(fig)
    return output_path


def generate_valuation_margin_chart(
    valuation_data: Dict[str, float],
    symbol: str,
    company_name: str,
    output_path: Path,
) -> Path:
    """
    Renders horizontal target gauge comparing Market Price to DCF Intrinsic Value and Graham Number floor.
    Features:
    - 3 color-coded zones: Undervalued (< 0.85 DCF), Fair Value Range (0.85 - 1.15 DCF), Premium / Overheated (> 1.15 DCF).
    - DCF Fair Value line, Graham Number floor, Current Market Price pointer callout.
    - Margin of Safety discount/premium percentage banner in title.
    - Dark institutional aesthetic (#0f172a figure, #1e293b axes).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    val_dict = valuation_data or {}

    curr_p = float(val_dict.get("current_price") or 100.0)
    dcf_val = float(
        val_dict.get("intrinsic_value")
        or val_dict.get("intrinsic_value_per_share")
        or curr_p
    )
    if curr_p <= 0.0:
        curr_p = dcf_val if dcf_val > 0.0 else 100.0
    if dcf_val <= 0.0:
        dcf_val = curr_p if curr_p > 0.0 else 100.0

    graham_val = val_dict.get("graham_number")
    graham = float(graham_val) if (graham_val is not None and float(graham_val) > 0.0) else None

    low_52_val = val_dict.get("fifty_two_week_low")
    low_52 = float(low_52_val) if (low_52_val is not None and float(low_52_val) > 0.0) else (curr_p * 0.7)

    high_52_val = val_dict.get("fifty_two_week_high")
    high_52 = float(high_52_val) if (high_52_val is not None and float(high_52_val) > 0.0) else (curr_p * 1.3)

    min_candidates = [dcf_val * 0.7, curr_p * 0.8, low_52]
    if graham is not None:
        min_candidates.append(graham)
    min_x = max(0.0, min(min_candidates) * 0.95)

    max_candidates = [dcf_val * 1.3, curr_p * 1.15, high_52]
    max_x = max(max_candidates) * 1.05
    if max_x <= min_x:
        max_x = min_x + 50.0

    fig, ax = plt.subplots(figsize=(9.5, 3.8), dpi=200, facecolor="#0f172a")
    ax.set_facecolor("#1e293b")

    # Zones: Undervalued (up to 0.85 DCF), Fair Value (0.85 - 1.15 DCF), Premium / Overheated (> 1.15 DCF)
    underval_end = dcf_val * 0.85
    overval_start = dcf_val * 1.15

    ax.axvspan(min_x, underval_end, color="#22c55e", alpha=0.25, label="Undervalued Zone (< 0.85 DCF)")
    ax.axvspan(underval_end, overval_start, color="#f59e0b", alpha=0.25, label="Fair Value Range (0.85 - 1.15 DCF)")
    ax.axvspan(overval_start, max_x, color="#ef4444", alpha=0.25, label="Premium / Overheated Zone (> 1.15 DCF)")

    # Markers
    ax.plot(
        [dcf_val, dcf_val],
        [-0.5, 0.5],
        color="#38bdf8",
        linewidth=3.5,
        label=f"DCF Fair Value (${dcf_val:.2f})",
        zorder=5,
    )
    if graham is not None:
        ax.plot(
            [graham, graham],
            [-0.3, 0.3],
            color="#a855f7",
            linewidth=2.5,
            linestyle="--",
            label=f"Graham Floor (${graham:.2f})",
            zorder=5,
        )

    # Current Market Price pointer
    ax.scatter(
        [curr_p],
        [0.0],
        color="#f8fafc",
        s=180,
        edgecolors="#e11d48",
        linewidth=3.0,
        zorder=6,
        label=f"Market Price (${curr_p:.2f})",
    )
    ax.annotate(
        f"Current Close: ${curr_p:.2f}",
        (curr_p, 0.0),
        xytext=(0, 25),
        textcoords="offset points",
        ha="center",
        color="#f8fafc",
        fontweight="bold",
        fontsize=10.5,
        bbox=dict(boxstyle="round,pad=0.35", fc="#e11d48", ec="none"),
        zorder=7,
    )

    diff_pct = ((dcf_val - curr_p) / curr_p) * 100.0
    if diff_pct > 0.0:
        status_str = f"Discount: +{diff_pct:.1f}% (Undervalued)"
    else:
        status_str = f"Premium: {abs(diff_pct):.1f}% (Above DCF)"

    ax.set_title(
        f"{company_name} ({symbol}) — Valuation Range & Margin of Safety\n{status_str}",
        fontsize=12,
        fontweight="bold",
        color="#f8fafc",
        pad=12,
    )

    ax.set_xlim(min_x, max_x)
    ax.set_ylim(-0.8, 0.8)
    ax.set_yticks([])
    ax.tick_params(colors="#94a3b8")
    ax.grid(axis="x", color="#334155", linestyle="--", linewidth=0.7, alpha=0.6)

    if (max_x - min_x) < 10.0:
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: f"${val:.2f}"))
    else:
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: f"${val:.0f}"))

    ncol = 5 if graham is not None else 4
    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.48),
        ncol=ncol,
        facecolor="#1e293b",
        edgecolor="#334155",
        labelcolor="#f8fafc",
        fontsize=8.5,
    )

    plt.savefig(
        output_path,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        dpi=200,
    )
    plt.close(fig)
    return output_path


