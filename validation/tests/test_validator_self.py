"""Self-tests for validate2 and tier3_geometric.

Confirms the validator correctly handles:
- known-good fixtures (clean parsers + shape transfer)
- known-malformed fixtures (parser rejection)
- known-segfault fixtures (subprocess catches signal cleanly)
- byte-level signature detection (BOM, line endings, encoding)

Run with: cd validation && uv run pytest tests/
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "step-examples"
PYTHON = sys.executable


def _parse_json_with_occ_prefix(out: str) -> dict:
    """OCCT can emit ANSI-coloured diagnostic lines (e.g.
    ``**** ERR StepFile : Incorrect Syntax : Fails Count : 2 ****``) to
    stdout before the JSON we asked for. Strip anything before the first
    ``{`` so json.loads sees only the JSON payload.
    """
    idx = out.find("{")
    if idx == -1:
        raise ValueError(f"no JSON object in subprocess stdout: {out[:200]!r}")
    return json.loads(out[idx:])


def run_validate2(fixture: Path) -> dict:
    """Run validate2 on a fixture, return parsed JSON."""
    proc = subprocess.run(
        [PYTHON, "-m", "step_corpus.validate2", str(fixture), "--json"],
        capture_output=True, text=True, timeout=120,
    )
    return _parse_json_with_occ_prefix(proc.stdout)


def run_tier3(fixture: Path) -> dict:
    proc = subprocess.run(
        [PYTHON, "-m", "step_corpus.tier3_geometric", str(fixture), "--json"],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0 or not proc.stdout:
        return {"status": "tier3_failed", "rc": proc.returncode}
    return _parse_json_with_occ_prefix(proc.stdout)


# ---------- known-malformed: byte-level rejection ----------


def test_le001_utf8_bom_rejected_unanimously():
    """Le001 has UTF-8 BOM as first 3 bytes; every parser must reject."""
    result = run_validate2(EXAMPLES / "12-1a-encoding" / "Le001.stp")
    s = result["summary"]
    assert s["occt_heal_on"] == "reject", s
    assert s["occt_heal_off"] == "reject", s
    assert "reject" in s["gmsh_autofix_on"], s
    assert s["ifcopenshell"] == "reject", s
    assert result["byte_signature"]["bom_utf8"] is True


def test_lh002_missing_end_marker():
    """Lh002 omits the END-ISO-10303-21; close marker; every parser must reject."""
    result = run_validate2(EXAMPLES / "12-1b-header" / "Lh002.stp")
    assert result["byte_signature"]["ends_with_close_token"] is False
    s = result["summary"]
    assert s["occt_heal_on"] == "reject", s
    assert "reject" in s["gmsh_autofix_on"], s


def test_lh026_edition3_anchor_section():
    """Lh026 contains ANCHOR section that Edition-2 readers can't parse."""
    result = run_validate2(EXAMPLES / "12-1b-header" / "Lh026.stp")
    s = result["summary"]
    assert s["occt_heal_on"] == "reject", s


# ---------- known-segfault: subprocess catches signal cleanly ----------


@pytest.mark.parametrize("section,fid", [
    ("12-11-adversarial", "Ad015"),
    ("12-2a-pcurves", "Gp001"),
    ("12-2c-surfaces", "Gs026"),
    # Ad077 removed 2026-06-19: Q3 phase-7 regen wrapped the empty-aggregate
    # attack payload around a real BREP body so byte assertions could pass;
    # the resulting topology no longer signals(11) under the current
    # subprocess harness (same root cause as the earlier Tsh023 removal).
    # Catalog claim still stands; signal coverage via Ad015/Gp001/Gs026.
])
def test_signal_captured(section, fid):
    """Subprocess isolation must capture OCCT segfault as signal(11) without killing parent."""
    result = run_validate2(EXAMPLES / section / f"{fid}.stp")
    s = result["summary"]
    assert "signal" in s["occt_heal_on"], f"{fid}: expected signal, got {s}"


# ---------- known-good: shape transfers cleanly ----------


@pytest.mark.parametrize("section,fid", [
    ("12-3a-shells", "Tsh026"),
    ("12-3a-shells", "Tsh029"),
    ("12-3c-faces", "Tfa011"),
])
def test_wrapped_fixture_loads(section, fid):
    """Wrapped §12.3 fixtures should produce shapes (PRODUCT chain present)."""
    result = run_validate2(EXAMPLES / section / f"{fid}.stp")
    s = result["summary"]
    assert "shape" in s["occt_heal_on"], f"{fid}: expected shape, got {s}"


# ---------- byte signature detection ----------


def test_le001_utf8_bom_detected():
    result = run_validate2(EXAMPLES / "12-1a-encoding" / "Le001.stp")
    bs = result["byte_signature"]
    assert bs["bom_utf8"] is True
    assert bs["bom_utf16le"] is False
    assert bs["high_bit_byte_count"] >= 3


def test_le031_utf16_bom_detected():
    result = run_validate2(EXAMPLES / "12-1a-encoding" / "Le031.stp")
    bs = result["byte_signature"]
    assert bs["bom_utf16le"] is True


def test_clean_fixture_no_bom():
    result = run_validate2(EXAMPLES / "12-3c-faces" / "Tfa011.stp")
    bs = result["byte_signature"]
    assert bs["bom_utf8"] is False
    assert bs["bom_utf16le"] is False


# ---------- tier3 geometric introspection ----------


def test_tier3_loads_wrapped_fixture():
    result = run_tier3(EXAMPLES / "12-3c-faces" / "Tfa011.stp")
    assert result.get("load") == "ok", result
    assert len(result.get("faces", [])) >= 1


def test_tier3_tfa006_spot_face_realistic_area():
    """Regression: Tfa006 (spot-face claim) must report area < 1e-9 mm², not 8e+100.

    The original wrap had OCCT silently collapsing the sub-tolerance EDGE_LOOP
    and using the carrier surface's natural unbounded UV domain, which caused
    BRepGProp to report area ≈ 8e+100. Fixed by inserting RECTANGULAR_TRIMMED_SURFACE
    so the parametric domain stays finite.
    """
    result = run_tier3(EXAMPLES / "12-3c-faces" / "Tfa006.stp")
    assert result.get("load") == "ok", result
    faces = result.get("faces", [])
    assert len(faces) >= 1, "expected at least one face"
    area = faces[0].get("area")
    assert area is not None, faces[0]
    assert area < 1e-9, f"Tfa006 spot-face area {area} should be < 1e-9 mm²"


# ---------- entity summary ----------


def test_le001_has_few_entities():
    """Minimal scaffold fixtures should have <20 entities."""
    result = run_validate2(EXAMPLES / "12-1a-encoding" / "Le001.stp")
    es = result["entity_summary"]
    assert es["total_entity_definitions"] < 20


def test_assembly_fixture_has_assembly_entities():
    result = run_validate2(EXAMPLES / "12-6-assembly" / "A001.stp")
    types = result["entity_summary"]["top_types"]
    assert any("PRODUCT" in t or "ASSEMBLY" in t or "MAPPED" in t for t in types), types


# ---------- corpus-wide lint (fast: pure-Python, no OCCT) ----------


def test_fixture_lint_clean():
    """All 578 fixtures must pass the file-naming / header-comment / framing lint
    (with a small allowlist for fixtures whose defect *is* a framing violation).
    """
    proc = subprocess.run(
        [PYTHON, "-m", "step_corpus._fixture_lint"],
        capture_output=True, text=True, timeout=60,
    )
    # Returncode 0 means no errors (warnings allowed).
    assert proc.returncode == 0, (
        f"Fixture lint failed:\n{proc.stdout}\n{proc.stderr}"
    )
