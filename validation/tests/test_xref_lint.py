"""Cross-reference lint regression.

Asserts the catalog markdown's `**See also**:` and `**Originally also
catalogued as**:` cross-references all resolve to existing entries.
A broken ref is a small but real navigation bug.
"""
from __future__ import annotations

from pathlib import Path

from step_corpus._build_catalog_json import CATALOG_MD
from step_corpus._xref_lint import find_broken_xrefs


def test_no_broken_cross_references() -> None:
    text = Path(CATALOG_MD).read_text(encoding="utf-8")
    broken = find_broken_xrefs(text)
    assert not broken, (
        f"{len(broken)} broken cross-references in catalog:\n"
        + "\n".join(
            f"  {r['referrer']} → {r['missing']} (in `{r['kind']}`)"
            for r in broken[:20]
        )
    )
