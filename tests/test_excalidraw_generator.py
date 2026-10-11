import json
from pathlib import Path
import pytest

from stock_analyzer.engine.excalidraw_generator import (
    build_moat_excalidraw_document,
    generate_moat_excalidraw_diagram,
)


def test_generate_moat_excalidraw_diagram_full_profile(tmp_path: Path):
    profile = {
        "overview": "Amazon.com, Inc. is a global leader in e-commerce and cloud computing.",
        "thesis_moats": [
            "AWS Cloud Lock-in & Enterprise Switching Costs",
            "Global Logistics & Fulfillment Infrastructure",
            "Prime Ecosystem & Advertising Flywheel",
        ],
        "thesis_risks": [
            "Heavy AI Capex Cycles Compressing Free Cash Flow",
            "Antitrust Scrutiny on E-Commerce Marketplace Practices",
            "Hyperscaler Cloud Pricing Pressure & Margin Headwinds",
        ],
        "moat": "Deep ecosystem integration and logistics scale.",
    }
    out_file = tmp_path / "business_moat_diagram.excalidraw"
    excal_path, png_path = generate_moat_excalidraw_diagram(
        "AMZN", "Amazon.com, Inc.", profile, out_file
    )

    assert excal_path.exists()
    assert png_path.exists()
    assert excal_path.name == "business_moat_diagram.excalidraw"
    assert png_path.name == "business_moat_diagram.png"
    assert excal_path.stat().st_size > 500
    assert png_path.stat().st_size > 10000

    with open(excal_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["type"] == "excalidraw"
    assert data["version"] == 2
    assert data["source"] == "https://excalidraw.com"
    assert data["appState"]["viewBackgroundColor"] == "#0f172a"
    assert "elements" in data
    assert len(data["elements"]) > 0

    # Ensure elements contain moats, risks, and pillars
    element_texts = [el.get("text", "") for el in data["elements"] if el.get("type") == "text"]
    full_text = " ".join(element_texts)
    assert "AMZN" in full_text
    assert "AWS Cloud Lock-in" in full_text
    assert "Heavy AI Capex" in full_text


def test_generate_moat_excalidraw_diagram_empty_profile(tmp_path: Path):
    out_file = tmp_path / "empty_profile_diagram"
    excal_path, png_path = generate_moat_excalidraw_diagram(
        "XYZ", "Generic Corp", {}, out_file
    )

    assert excal_path.exists()
    assert png_path.exists()
    assert excal_path.suffix == ".excalidraw"
    assert png_path.suffix == ".png"
    assert excal_path.stat().st_size > 500
    assert png_path.stat().st_size > 5000

    with open(excal_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["type"] == "excalidraw"
    assert len(data["elements"]) > 0


def test_generate_moat_excalidraw_diagram_partial_profile(tmp_path: Path):
    profile = {
        "thesis_moats": ["Single Moat Feature"],
        "thesis_risks": ["Single Risk Factor"],
    }
    out_file = tmp_path / "partial_diagram.png"
    excal_path, png_path = generate_moat_excalidraw_diagram(
        "TEST", "Test LLC", profile, out_file
    )

    assert excal_path.exists()
    assert png_path.exists()
    with open(excal_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["type"] == "excalidraw"
    element_texts = [el.get("text", "") for el in data["elements"] if el.get("type") == "text"]
    full_text = " ".join(element_texts)
    assert "Single Moat Feature" in full_text
    assert "Single Risk Factor" in full_text


def test_build_moat_excalidraw_document_structure():
    doc = build_moat_excalidraw_document(
        "AAPL",
        "Apple Inc.",
        {
            "thesis_moats": ["iOS Ecosystem Lock-in"],
            "thesis_risks": ["Supply Chain Tariffs"],
        },
    )
    assert doc["type"] == "excalidraw"
    assert doc["version"] == 2
    assert isinstance(doc["elements"], list)
    assert len(doc["elements"]) > 0

    rects = [el for el in doc["elements"] if el.get("type") == "rectangle"]
    assert len(rects) > 0
    assert any(el.get("backgroundColor") == "#1e293b" for el in rects)
    assert any(el.get("strokeColor") == "#38bdf8" for el in rects)
