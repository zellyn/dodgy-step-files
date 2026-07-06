"""Structural-assertion regression test.

Catalog entries can carry one or more `**Structural assertion**:` lines of the
form ``struct == <CODE>``, verified by the non-kernel structural linter
(_structural_oracle) independent of any geometry kernel. This test runs the
linter against each such fixture and fails if the asserted code no longer holds.

Pair to ``test_byte_assertions.py`` / ``test_tier3_assertions.py``: same idea,
for the structural-defect (oracle-invisible) subset — inconsistent units,
degenerate axes, dangling refs, duplicate ids.
"""
from __future__ import annotations

import re

import pytest

from step_corpus import catalog
from step_corpus._structural_oracle import CODES, lint_file

_RESEARCH_ROOT = catalog._RESEARCH_ROOT
_ASSERT_RE = re.compile(r"struct\s*==\s*([A-Z_]+)")


def _entries_with_structural():
    out = []
    for e in catalog.iter_canonical():
        for a in e.get("structural_assertions") or []:
            m = _ASSERT_RE.search(a)
            if m:
                out.append((e["id"], e["fixture_path"], m.group(1), a))
    return out


def test_some_entries_carry_structural_assertions() -> None:
    entries = _entries_with_structural()
    assert len(entries) >= 3, (
        f"only {len(entries)} structural assertions registered; expected >=3"
    )


def test_structural_assertion_codes_are_known() -> None:
    for _id, _path, code, raw in _entries_with_structural():
        assert code in CODES, f"{_id}: unknown structural code {code!r} in {raw!r}"


def test_no_structural_assertion_failures() -> None:
    fails = []
    for fid, rel_path, code, raw in _entries_with_structural():
        p = _RESEARCH_ROOT / rel_path
        if not p.is_file():
            fails.append(f"  {fid:<8} [missing-fixture] {rel_path}")
            continue
        actual = lint_file(p)
        if actual != code:
            fails.append(f"  {fid:<8} expected struct=={code} but linter said {actual!r}")
    if fails:
        pytest.fail(f"{len(fails)} structural-assertion failures:\n" + "\n".join(fails))
