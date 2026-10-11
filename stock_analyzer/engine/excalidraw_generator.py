"""Strategic Business Moat & Flywheel Excalidraw and Vector Diagram Generator.

Generates:
1. Valid Excalidraw v2 JSON diagram file (.excalidraw) for interactive visual editing.
2. High-resolution dark-mode vector rendering (.png) for direct GitHub markdown embedding.
"""

import json
from pathlib import Path
import textwrap
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


# Default fallback content for empty or partial profiles
DEFAULT_PILLARS = [
    "Core Platform & Enterprise Solutions Engine",
    "Global Distribution & Operational Infrastructure",
    "High-Margin Recurring Monetization & Cash Flow",
]

DEFAULT_MOATS = [
    "High Switching Costs & Customer Ecosystem Lock-in",
    "Proprietary Platform Distribution & Network Scale",
    "Cost Advantage & Reinvestment Growth Flywheel",
]

DEFAULT_RISKS = [
    "Capital Expenditure Cycles & Margin Compression",
    "Regulatory, Antitrust & Compliance Headwinds",
    "Competitive Disruption & Pricing Encroachment",
]


def _extract_items(
    items: Optional[List[Any]],
    defaults: List[str],
    limit: int = 3,
) -> List[str]:
    """Extracts, cleans, and pads items with sensible defaults."""
    if not items or not isinstance(items, list):
        return defaults[:limit]
    
    cleaned = [str(x).strip() for x in items if str(x).strip()]
    if not cleaned:
        return defaults[:limit]
    
    # If fewer than limit, pad with remaining defaults
    result = cleaned[:limit]
    if len(result) < limit:
        for d in defaults:
            if d not in result:
                result.append(d)
            if len(result) == limit:
                break
    return result


def _make_excalidraw_rect(
    elem_id: str,
    x: float,
    y: float,
    width: float,
    height: float,
    stroke_color: str,
    bg_color: str = "#1e293b",
    stroke_width: int = 2,
    seed: int = 10001,
) -> Dict[str, Any]:
    """Helper to create an Excalidraw rectangle element."""
    return {
        "id": elem_id,
        "type": "rectangle",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "angle": 0,
        "strokeColor": stroke_color,
        "backgroundColor": bg_color,
        "fillStyle": "solid",
        "strokeWidth": stroke_width,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "groupIds": [],
        "roundness": {"type": 3},
        "seed": seed,
        "version": 1,
        "versionNonce": seed + 100,
        "isDeleted": False,
        "boundElements": None,
        "link": None,
        "locked": False,
    }


def _make_excalidraw_text(
    elem_id: str,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    font_size: int = 14,
    stroke_color: str = "#f8fafc",
    text_align: str = "center",
    vertical_align: str = "middle",
    container_id: Optional[str] = None,
    seed: int = 20001,
) -> Dict[str, Any]:
    """Helper to create an Excalidraw text element."""
    return {
        "id": elem_id,
        "type": "text",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "angle": 0,
        "strokeColor": stroke_color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "groupIds": [],
        "roundness": None,
        "seed": seed,
        "version": 1,
        "versionNonce": seed + 100,
        "isDeleted": False,
        "boundElements": None,
        "link": None,
        "locked": False,
        "text": text,
        "originalText": text,
        "fontSize": font_size,
        "fontFamily": 3,
        "textAlign": text_align,
        "verticalAlign": vertical_align,
        "containerId": container_id,
        "lineHeight": 1.25,
    }


def _make_excalidraw_arrow(
    elem_id: str,
    x: float,
    y: float,
    points: List[List[float]],
    stroke_color: str = "#38bdf8",
    stroke_style: str = "solid",
    stroke_width: int = 2,
    seed: int = 30001,
) -> Dict[str, Any]:
    """Helper to create an Excalidraw arrow element."""
    dx = abs(points[-1][0] - points[0][0])
    dy = abs(points[-1][1] - points[0][1])
    return {
        "id": elem_id,
        "type": "arrow",
        "x": x,
        "y": y,
        "width": max(dx, 10.0),
        "height": max(dy, 10.0),
        "angle": 0,
        "strokeColor": stroke_color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": stroke_width,
        "strokeStyle": stroke_style,
        "roughness": 0,
        "opacity": 100,
        "groupIds": [],
        "roundness": {"type": 2},
        "seed": seed,
        "version": 1,
        "versionNonce": seed + 100,
        "isDeleted": False,
        "boundElements": None,
        "link": None,
        "locked": False,
        "points": points,
        "startBinding": None,
        "endBinding": None,
        "startArrowhead": None,
        "endArrowhead": "arrow",
    }


def build_moat_excalidraw_document(
    symbol: str,
    company_name: str,
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Builds a complete, valid Excalidraw v2 document data structure representing
    the company's core business foundation, economic moats, flywheel loops, and risk shields.
    """
    moats = _extract_items(profile.get("thesis_moats"), DEFAULT_MOATS)
    risks = _extract_items(profile.get("thesis_risks"), DEFAULT_RISKS)
    pillars = _extract_items(
        profile.get("core_pillars") or profile.get("pillars"),
        DEFAULT_PILLARS,
    )
    moat_summary = str(profile.get("moat") or "Durable economic moat protected by structural competitive advantages.").strip()

    elements: List[Dict[str, Any]] = []
    seed_counter = 1000

    def next_seed() -> int:
        nonlocal seed_counter
        seed_counter += 17
        return seed_counter

    # 1. Header Banner
    elements.append(
        _make_excalidraw_rect(
            "header_box",
            x=60,
            y=30,
            width=1160,
            height=75,
            stroke_color="#334155",
            bg_color="#1e293b",
            stroke_width=2,
            seed=next_seed(),
        )
    )
    elements.append(
        _make_excalidraw_text(
            "header_title",
            x=80,
            y=42,
            width=1120,
            height=30,
            text=f"{company_name} ({symbol}) — Strategic Moats & Flywheel Architecture",
            font_size=20,
            stroke_color="#f8fafc",
            text_align="center",
            seed=next_seed(),
        )
    )
    elements.append(
        _make_excalidraw_text(
            "header_subtitle",
            x=80,
            y=74,
            width=1120,
            height=20,
            text="Institutional Business Architecture, Ecosystem Lock-in & Risk Vector Model",
            font_size=13,
            stroke_color="#94a3b8",
            text_align="center",
            seed=next_seed(),
        )
    )

    # 2. Section Headers / Column Badges
    col_x = [60, 470, 880]
    col_width = 340
    badges = [
        ("badge_pillars", "CORE BUSINESS ENGINE", "#38bdf8", "#0f2942"),
        ("badge_moats", "ECONOMIC MOATS & FLYWHEEL", "#22c55e", "#052e16"),
        ("badge_risks", "RISK VECTORS & HEADWINDS", "#ef4444", "#3f1219"),
    ]

    for idx, (b_id, label, border_c, bg_c) in enumerate(badges):
        x = col_x[idx]
        elements.append(
            _make_excalidraw_rect(
                b_id,
                x=x,
                y=125,
                width=col_width,
                height=38,
                stroke_color=border_c,
                bg_color=bg_c,
                stroke_width=1,
                seed=next_seed(),
            )
        )
        elements.append(
            _make_excalidraw_text(
                f"{b_id}_txt",
                x=x + 10,
                y=134,
                width=col_width - 20,
                height=20,
                text=label,
                font_size=13,
                stroke_color=border_c,
                text_align="center",
                seed=next_seed(),
            )
        )

    # 3. Column Cards & Text
    y_starts = [185, 335, 485]
    card_h = 125

    # Column 1: Core Business Pillars (#38bdf8 stroke, #1e293b fill)
    for idx, pillar in enumerate(pillars):
        y = y_starts[idx]
        cid = f"pillar_card_{idx+1}"
        elements.append(
            _make_excalidraw_rect(
                cid,
                x=col_x[0],
                y=y,
                width=col_width,
                height=card_h,
                stroke_color="#38bdf8",
                bg_color="#1e293b",
                stroke_width=2,
                seed=next_seed(),
            )
        )
        elements.append(
            _make_excalidraw_text(
                f"{cid}_tag",
                x=col_x[0] + 15,
                y=y + 12,
                width=col_width - 30,
                height=18,
                text=f"PILLAR {idx+1}",
                font_size=12,
                stroke_color="#38bdf8",
                text_align="left",
                seed=next_seed(),
            )
        )
        wrapped_p = "\n".join(textwrap.wrap(pillar, width=38))
        elements.append(
            _make_excalidraw_text(
                f"{cid}_body",
                x=col_x[0] + 15,
                y=y + 40,
                width=col_width - 30,
                height=65,
                text=wrapped_p,
                font_size=13,
                stroke_color="#f8fafc",
                text_align="left",
                vertical_align="top",
                seed=next_seed(),
            )
        )

    # Column 2: Economic Moats (#22c55e stroke, #1e293b fill)
    for idx, moat in enumerate(moats):
        y = y_starts[idx]
        cid = f"moat_card_{idx+1}"
        elements.append(
            _make_excalidraw_rect(
                cid,
                x=col_x[1],
                y=y,
                width=col_width,
                height=card_h,
                stroke_color="#22c55e",
                bg_color="#1e293b",
                stroke_width=2,
                seed=next_seed(),
            )
        )
        elements.append(
            _make_excalidraw_text(
                f"{cid}_tag",
                x=col_x[1] + 15,
                y=y + 12,
                width=col_width - 30,
                height=18,
                text=f"MOAT {idx+1} [COMPOUNDER]",
                font_size=12,
                stroke_color="#22c55e",
                text_align="left",
                seed=next_seed(),
            )
        )
        wrapped_m = "\n".join(textwrap.wrap(moat, width=38))
        elements.append(
            _make_excalidraw_text(
                f"{cid}_body",
                x=col_x[1] + 15,
                y=y + 40,
                width=col_width - 30,
                height=65,
                text=wrapped_m,
                font_size=13,
                stroke_color="#f8fafc",
                text_align="left",
                vertical_align="top",
                seed=next_seed(),
            )
        )

    # Column 3: Risk Vectors (#ef4444 stroke, #1e293b fill)
    for idx, risk in enumerate(risks):
        y = y_starts[idx]
        cid = f"risk_card_{idx+1}"
        elements.append(
            _make_excalidraw_rect(
                cid,
                x=col_x[2],
                y=y,
                width=col_width,
                height=card_h,
                stroke_color="#ef4444",
                bg_color="#1e293b",
                stroke_width=2,
                seed=next_seed(),
            )
        )
        elements.append(
            _make_excalidraw_text(
                f"{cid}_tag",
                x=col_x[2] + 15,
                y=y + 12,
                width=col_width - 30,
                height=18,
                text=f"RISK FACTOR {idx+1} [HEADWIND]",
                font_size=12,
                stroke_color="#ef4444",
                text_align="left",
                seed=next_seed(),
            )
        )
        wrapped_r = "\n".join(textwrap.wrap(risk, width=38))
        elements.append(
            _make_excalidraw_text(
                f"{cid}_body",
                x=col_x[2] + 15,
                y=y + 40,
                width=col_width - 30,
                height=65,
                text=wrapped_r,
                font_size=13,
                stroke_color="#f8fafc",
                text_align="left",
                vertical_align="top",
                seed=next_seed(),
            )
        )

    # 4. Connecting Arrows (Col 1 -> Col 2)
    for idx in range(3):
        mid_y = y_starts[idx] + (card_h / 2.0)
        elements.append(
            _make_excalidraw_arrow(
                f"arrow_p_to_m_{idx+1}",
                x=col_x[0] + col_width,
                y=mid_y,
                points=[[0, 0], [col_x[1] - (col_x[0] + col_width), 0]],
                stroke_color="#38bdf8",
                stroke_width=2,
                seed=next_seed(),
            )
        )

    # 5. Flywheel cycle loop in Col 2 (Moat 1 -> Moat 2 -> Moat 3 -> Loopback)
    elements.append(
        _make_excalidraw_arrow(
            "flywheel_1_to_2",
            x=col_x[1] + (col_width / 2.0),
            y=y_starts[0] + card_h,
            points=[[0, 0], [0, y_starts[1] - (y_starts[0] + card_h)]],
            stroke_color="#22c55e",
            stroke_width=2,
            seed=next_seed(),
        )
    )
    elements.append(
        _make_excalidraw_arrow(
            "flywheel_2_to_3",
            x=col_x[1] + (col_width / 2.0),
            y=y_starts[1] + card_h,
            points=[[0, 0], [0, y_starts[2] - (y_starts[1] + card_h)]],
            stroke_color="#22c55e",
            stroke_width=2,
            seed=next_seed(),
        )
    )
    elements.append(
        _make_excalidraw_arrow(
            "flywheel_loopback",
            x=col_x[1] + col_width,
            y=y_starts[2] + (card_h / 2.0),
            points=[
                [0, 0],
                [35, 0],
                [35, -(y_starts[2] - y_starts[0])],
                [0, -(y_starts[2] - y_starts[0])],
            ],
            stroke_color="#22c55e",
            stroke_style="dashed",
            stroke_width=2,
            seed=next_seed(),
        )
    )

    # 6. Risk Headwind Arrows (Col 3 -> Col 2)
    for idx in range(3):
        mid_y = y_starts[idx] + (card_h / 2.0)
        elements.append(
            _make_excalidraw_arrow(
                f"arrow_risk_{idx+1}",
                x=col_x[2],
                y=mid_y,
                points=[[0, 0], [-(col_x[2] - (col_x[1] + col_width) - 45), 0]],
                stroke_color="#ef4444",
                stroke_style="dashed",
                stroke_width=2,
                seed=next_seed(),
            )
        )

    # 7. Bottom Footer Strip
    elements.append(
        _make_excalidraw_rect(
            "footer_box",
            x=60,
            y=635,
            width=1160,
            height=50,
            stroke_color="#334155",
            bg_color="#1e293b",
            stroke_width=1,
            seed=next_seed(),
        )
    )
    elements.append(
        _make_excalidraw_text(
            "footer_text",
            x=80,
            y=648,
            width=1120,
            height=24,
            text=f"Moat Assessment: {moat_summary}",
            font_size=13,
            stroke_color="#94a3b8",
            text_align="center",
            seed=next_seed(),
        )
    )

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "viewBackgroundColor": "#0f172a",
            "gridSize": 20,
        },
        "files": {},
    }


def _render_moat_png(
    symbol: str,
    company_name: str,
    profile: Dict[str, Any],
    png_path: Path,
) -> Path:
    """
    Renders a high-resolution 200 DPI vector PNG chart mirroring the Excalidraw moat architecture.
    Completely deterministic, offline-capable, and styled with institutional dark-mode aesthetics.
    """
    png_path.parent.mkdir(parents=True, exist_ok=True)

    moats = _extract_items(profile.get("thesis_moats"), DEFAULT_MOATS)
    risks = _extract_items(profile.get("thesis_risks"), DEFAULT_RISKS)
    pillars = _extract_items(
        profile.get("core_pillars") or profile.get("pillars"),
        DEFAULT_PILLARS,
    )
    moat_summary = str(profile.get("moat") or "Durable economic moat defended by high switching costs, network effects, and scale.").strip()

    fig, ax = plt.subplots(figsize=(14.2, 8.8), dpi=200, facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 14.2)
    ax.set_ylim(0, 8.8)
    ax.axis("off")

    # 1. Header Banner
    header_box = FancyBboxPatch(
        (0.6, 7.55),
        13.0,
        0.95,
        boxstyle="round,pad=0.04,rounding_size=0.12",
        facecolor="#1e293b",
        edgecolor="#334155",
        linewidth=1.5,
        zorder=2,
    )
    ax.add_patch(header_box)
    ax.text(
        7.1,
        8.15,
        f"{company_name} ({symbol}) — Strategic Moats & Flywheel Architecture",
        ha="center",
        va="center",
        fontsize=14,
        fontweight="bold",
        color="#f8fafc",
        zorder=3,
    )
    ax.text(
        7.1,
        7.8,
        "Institutional Business Architecture, Ecosystem Lock-in & Risk Vector Model",
        ha="center",
        va="center",
        fontsize=10,
        color="#94a3b8",
        zorder=3,
    )

    # 2. Column Positions
    col_x = [0.6, 5.3, 10.0]
    col_w = 3.6
    badges = [
        ("CORE BUSINESS ENGINE", "#38bdf8", "#0f2942"),
        ("ECONOMIC MOATS & FLYWHEEL", "#22c55e", "#052e16"),
        ("RISK VECTORS & HEADWINDS", "#ef4444", "#3f1219"),
    ]

    for idx, (label, border_c, bg_c) in enumerate(badges):
        x = col_x[idx]
        badge_box = FancyBboxPatch(
            (x, 6.95),
            col_w,
            0.42,
            boxstyle="round,pad=0.03,rounding_size=0.08",
            facecolor=bg_c,
            edgecolor=border_c,
            linewidth=1.4,
            zorder=2,
        )
        ax.add_patch(badge_box)
        ax.text(
            x + (col_w / 2.0),
            7.16,
            label,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color=border_c,
            zorder=3,
        )

    # 3. Cards Data & Y Positions
    y_starts = [5.1, 3.3, 1.5]
    card_h = 1.55

    cols_data = [
        (col_x[0], pillars, "PILLAR", "#38bdf8"),
        (col_x[1], moats, "MOAT", "#22c55e"),
        (col_x[2], risks, "RISK FACTOR", "#ef4444"),
    ]

    for x, items, prefix, border_c in cols_data:
        for idx, item in enumerate(items):
            y = y_starts[idx]
            card = FancyBboxPatch(
                (x, y),
                col_w,
                card_h,
                boxstyle="round,pad=0.04,rounding_size=0.1",
                facecolor="#1e293b",
                edgecolor=border_c,
                linewidth=1.8,
                zorder=2,
            )
            ax.add_patch(card)

            # Card Header Tag
            ax.text(
                x + 0.2,
                y + card_h - 0.28,
                f"{prefix} {idx+1}",
                ha="left",
                va="center",
                fontsize=9.5,
                fontweight="bold",
                color=border_c,
                zorder=3,
            )

            # Card Body Text (Cleanly word-wrapped)
            wrapped_text = "\n".join(textwrap.wrap(item, width=34))
            ax.text(
                x + 0.2,
                y + card_h - 0.55,
                wrapped_text,
                ha="left",
                va="top",
                fontsize=9.5,
                color="#f8fafc",
                fontweight="medium",
                linespacing=1.35,
                zorder=3,
            )

    # 4. Connecting Arrows (Col 1 -> Col 2)
    for idx in range(3):
        mid_y = y_starts[idx] + (card_h / 2.0)
        arrow = FancyArrowPatch(
            (col_x[0] + col_w + 0.05, mid_y),
            (col_x[1] - 0.05, mid_y),
            arrowstyle="->,head_width=0.25,head_length=0.3",
            color="#38bdf8",
            linewidth=2.0,
            zorder=4,
        )
        ax.add_patch(arrow)

    # 5. Flywheel cycle in Col 2 (Moat 1 -> Moat 2 -> Moat 3 -> Loopback)
    ax.add_patch(
        FancyArrowPatch(
            (col_x[1] + (col_w / 2.0), y_starts[0] - 0.02),
            (col_x[1] + (col_w / 2.0), y_starts[1] + card_h + 0.02),
            arrowstyle="->,head_width=0.22,head_length=0.25",
            color="#22c55e",
            linewidth=2.0,
            zorder=4,
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (col_x[1] + (col_w / 2.0), y_starts[1] - 0.02),
            (col_x[1] + (col_w / 2.0), y_starts[2] + card_h + 0.02),
            arrowstyle="->,head_width=0.22,head_length=0.25",
            color="#22c55e",
            linewidth=2.0,
            zorder=4,
        )
    )
    # Loopback curved arrow along right flank of Moats
    ax.add_patch(
        FancyArrowPatch(
            (col_x[1] + col_w + 0.08, y_starts[2] + (card_h / 2.0)),
            (col_x[1] + col_w + 0.08, y_starts[0] + (card_h / 2.0)),
            arrowstyle="->,head_width=0.22,head_length=0.28",
            connectionstyle="arc3,rad=-0.38",
            color="#22c55e",
            linewidth=1.8,
            linestyle="--",
            zorder=4,
        )
    )
    ax.text(
        col_x[1] + col_w + 0.55,
        y_starts[1] + (card_h / 2.0),
        "Compound Flywheel Loop",
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
        color="#22c55e",
        rotation=-90,
        zorder=4,
    )

    # 6. Risk Headwinds (Col 3 -> Col 2 with dashed red arrows)
    for idx in range(3):
        mid_y = y_starts[idx] + (card_h / 2.0)
        ax.add_patch(
            FancyArrowPatch(
                (col_x[2] - 0.05, mid_y),
                (col_x[1] + col_w + 0.65, mid_y),
                arrowstyle="->,head_width=0.2,head_length=0.25",
                color="#ef4444",
                linewidth=1.6,
                linestyle=":",
                zorder=4,
            )
        )

    # 7. Bottom Footer Strip
    footer_box = FancyBboxPatch(
        (0.6, 0.4),
        13.0,
        0.75,
        boxstyle="round,pad=0.04,rounding_size=0.1",
        facecolor="#1e293b",
        edgecolor="#334155",
        linewidth=1.2,
        zorder=2,
    )
    ax.add_patch(footer_box)
    wrapped_footer = "\n".join(textwrap.wrap(f"Moat Assessment: {moat_summary}", width=115))
    ax.text(
        7.1,
        0.77,
        wrapped_footer,
        ha="center",
        va="center",
        fontsize=9.5,
        color="#94a3b8",
        linespacing=1.3,
        zorder=3,
    )

    plt.savefig(
        png_path,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        dpi=200,
    )
    plt.close(fig)
    return png_path


def generate_moat_excalidraw_diagram(
    symbol: str,
    company_name: str,
    profile: Dict[str, Any],
    output_base_path: Path,
) -> Tuple[Path, Path]:
    """
    Generates both:
    1. Valid Excalidraw v2 diagram file (.excalidraw) for interactive visual editing.
    2. High-resolution dark-mode vector rendering (.png) for direct GitHub markdown embedding.

    Returns:
        Tuple[Path, Path]: (excalidraw_path, png_path)
    """
    output_base_path = Path(output_base_path)
    output_base_path.parent.mkdir(parents=True, exist_ok=True)

    excalidraw_path = output_base_path.with_suffix(".excalidraw")
    png_path = output_base_path.with_suffix(".png")

    # 1. Build and save Excalidraw v2 document
    doc = build_moat_excalidraw_document(symbol, company_name, profile)
    with open(excalidraw_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)

    # 2. Render and save 200 DPI vector PNG
    _render_moat_png(symbol, company_name, profile, png_path)

    return excalidraw_path, png_path
