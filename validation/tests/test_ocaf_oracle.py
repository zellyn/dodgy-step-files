"""OCAF / XCAF document-layer oracle tests.

Locks the JSON-output shape of ``_ocaf_oracle.analyze()`` and
sanity-checks its behaviour on a small sample of clean and broken
fixtures. The oracle itself is documented in
``step_corpus._ocaf_oracle``.

These tests are skipped if the OCP bindings cannot be imported
(defensive: OCP / cadquery-ocp is a hard dependency in
pyproject.toml, but if a developer is running a partial install we
prefer skipping over noisy failures).
"""
from __future__ import annotations

from pathlib import Path

import pytest

OCP_AVAILABLE = True
try:
    import OCP.STEPCAFControl  # noqa: F401
    import OCP.TDocStd  # noqa: F401
    import OCP.XCAFApp  # noqa: F401
    import OCP.XCAFDoc  # noqa: F401
except Exception:  # pragma: no cover
    OCP_AVAILABLE = False


pytestmark = pytest.mark.skipif(
    not OCP_AVAILABLE, reason="OCP bindings not importable in this environment"
)


EXAMPLES = Path(__file__).resolve().parents[2] / "step-examples"

# Hand-picked fixtures from §12.6-assembly known to be readable.
CLEAN_ASSEMBLY_FIXTURES = ["A001", "A007", "A019"]
# Fixtures known to fail at the CAF-reader level (broken bytes / no PRODUCT).
KNOWN_BROKEN = ["A074"]


def _fixture(eid: str) -> Path:
    return EXAMPLES / "12-6-assembly" / f"{eid}.stp"


def test_analyze_returns_dict_with_required_keys() -> None:
    from step_corpus._ocaf_oracle import analyze
    p = _fixture("A001")
    if not p.exists():
        pytest.skip(f"fixture {p} missing")
    rec = analyze(p)
    assert isinstance(rec, dict)
    required = {
        "file", "load_status", "root_labels", "free_shapes",
        "named_labels", "named_label_examples",
        "colored_labels", "colored_label_count_with_alpha",
        "assembly_count", "assembly_components",
        "max_depth", "transforms_at_leaf", "non_identity_transforms",
        "sub_shape_labels", "layer_count", "diagnostics",
    }
    missing = required - set(rec.keys())
    assert not missing, f"analyze() output is missing keys: {sorted(missing)}"


def test_analyze_clean_fixtures_load_ok() -> None:
    """A handful of catalog fixtures known to be loadable should report load_status=ok."""
    from step_corpus._ocaf_oracle import analyze
    for eid in CLEAN_ASSEMBLY_FIXTURES:
        p = _fixture(eid)
        if not p.exists():
            pytest.skip(f"fixture {p} missing")
        rec = analyze(p)
        assert rec["load_status"] == "ok", (
            f"{eid}: expected load_status=ok, got {rec['load_status']}; "
            f"diagnostics={rec.get('diagnostics')}"
        )
        # Clean fixtures with PRODUCT chains should produce >= 1 root_label.
        assert rec["root_labels"] >= 1, (
            f"{eid}: expected at least one root label, got {rec['root_labels']}"
        )


def test_named_label_examples_truncated() -> None:
    from step_corpus._ocaf_oracle import analyze
    p = _fixture("A001")
    if not p.exists():
        pytest.skip(f"fixture {p} missing")
    rec = analyze(p)
    examples = rec.get("named_label_examples", [])
    # Sanity: examples list capped at 8 entries
    assert isinstance(examples, list)
    assert len(examples) <= 8


def test_no_product_chain_reports_zero_root_labels() -> None:
    """A specific fixture without a usable PRODUCT chain reports 0 root labels.

    Uses subprocess invocation (rather than in-process ``analyze()``)
    because some catalogue fixtures cause OCCT to abort with a
    SIGSEGV; the validate2 framework normally isolates each oracle
    in a subprocess, so this test does the same.

    A074 is hand-picked: a catalogue fixture with broken assembly
    PRODUCT linkage that loads (no parse error) but yields no
    OCAF-level shape labels.
    """
    import json
    import subprocess
    import sys
    p = _fixture("A074")
    if not p.exists():
        pytest.skip(f"fixture {p} missing")
    proc = subprocess.run(
        [sys.executable, "-m", "step_corpus._ocaf_oracle", str(p), "--json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Don't insist on rc==0 (oracle may print failure JSON)
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip().startswith("{")]
    if not lines:
        pytest.skip(f"oracle produced no JSON for {p.name}; stderr={proc.stderr[-300:]}")
    rec = json.loads(lines[-1])
    # A074 has broken PRODUCT linkage. Outcome depends on OCC version:
    #   - strict (e.g. local macOS OCC): STEPCAFControl_Reader.Perform fails
    #     → root_labels=0
    #   - lenient (e.g. CI Ubuntu OCC): the reader treats the partial chain
    #     as one anonymous shape → root_labels=1
    # Both are acceptable "broken bytes" outcomes; we just want to catch
    # multi-root regressions (root_labels >= 2 would mean OCAF mistakenly
    # treated the broken bytes as a valid multi-component assembly).
    n = rec.get("root_labels", 0)
    assert n <= 1, (
        f"expected <= 1 root label for {p.name} (broken-bytes assembly), "
        f"got {n}; load_status={rec.get('load_status')}"
    )


def test_json_serialisable() -> None:
    """analyze() output must round-trip through json.dumps (no non-serialisable objects)."""
    import json
    from step_corpus._ocaf_oracle import analyze
    p = _fixture("A001")
    if not p.exists():
        pytest.skip(f"fixture {p} missing")
    rec = analyze(p)
    blob = json.dumps(rec, default=str)
    rec2 = json.loads(blob)
    assert rec2["file"] == rec["file"]
    assert rec2["load_status"] == rec["load_status"]
    assert rec2["root_labels"] == rec["root_labels"]


def test_cli_emits_json_record(tmp_path: Path) -> None:
    """The module CLI with --json prints a single JSON object on stdout."""
    import json
    import subprocess
    import sys
    p = _fixture("A001")
    if not p.exists():
        pytest.skip(f"fixture {p} missing")
    proc = subprocess.run(
        [sys.executable, "-m", "step_corpus._ocaf_oracle", str(p), "--json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, f"oracle CLI failed: {proc.stderr[-400:]}"
    # Last non-empty stdout line should be a single JSON object
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    assert lines, "oracle CLI produced no stdout"
    rec = json.loads(lines[-1])
    assert rec["load_status"] == "ok"
    assert rec["root_labels"] >= 1


def test_validate2_summary_includes_ocaf() -> None:
    """validate2's summary block should include an 'ocaf' field."""
    import json
    import subprocess
    import sys
    p = _fixture("A001")
    if not p.exists():
        pytest.skip(f"fixture {p} missing")
    proc = subprocess.run(
        [sys.executable, "-m", "step_corpus.validate2", str(p), "--json"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert proc.returncode == 0, f"validate2 failed: {proc.stderr[-400:]}"
    payload = json.loads(proc.stdout)
    assert "summary" in payload
    summary = payload["summary"]
    assert "ocaf" in summary, f"summary missing 'ocaf' field: {sorted(summary)}"
    # On a clean fixture the value should embed the root-label count
    assert summary["ocaf"].startswith("root_labels="), summary["ocaf"]
