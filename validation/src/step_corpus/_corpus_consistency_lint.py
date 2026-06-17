"""Cross-checks between fixture files and catalog entries.

Catches orphans in either direction:
- Fixtures on disk with no matching `### ID —` entry in
  STEP_PROBLEM_CATALOG.md (e.g. Gs094-Gs138 range surfaced 2026-06-17).
- Catalog entries that reference a `Fixture path:` that doesn't exist
  on disk (truncated regeneration, deleted by mistake, etc).

Run: `uv run python -m step_corpus._corpus_consistency_lint`
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from step_corpus._build_catalog_json import RESEARCH_ROOT

EXAMPLES = RESEARCH_ROOT / "step-examples"
CATALOG = RESEARCH_ROOT / "STEP_PROBLEM_CATALOG.md"

# Maps fixture-id prefix → directory under step-examples/
PREFIX_DIR = {
    "Tsh": "12-3a-shells",
    "Twi": "12-3b-wires",
    "Tfa": "12-3c-faces",
    "N": "12-4-tolerance",
    "Gp": "12-2a-pcurves",
    "Gn": "12-2b-nurbs",
    "Gs": "12-2c-surfaces",
}


def _catalog_ids() -> set[str]:
    """Return all IDs declared with `### ID — ` (em-dash separator) in the catalog."""
    text = CATALOG.read_text()
    return set(re.findall(r"^### ([A-Za-z][a-z]*\d+) — ", text, re.M))


def _fixture_ids() -> set[str]:
    """Return all IDs found on disk under step-examples, excluding quarantine."""
    ids = set()
    for d in PREFIX_DIR.values():
        sub = EXAMPLES / d
        if not sub.is_dir():
            continue
        for f in sub.glob("*.stp"):
            m = re.match(r"^([A-Za-z][a-z]*\d+)\.stp$", f.name)
            if m:
                ids.add(m.group(1))
    return ids


def main(argv: list[str] | None = None) -> int:
    cat = _catalog_ids()
    fix = _fixture_ids()

    orphan_files = sorted(fix - cat)  # fixture on disk, no catalog entry
    orphan_entries = sorted(cat - fix)  # catalog entry, no fixture on disk

    if "--json" in (argv or sys.argv[1:]):
        json.dump({
            "orphan_files": orphan_files,
            "orphan_catalog_entries": orphan_entries,
            "n_orphan_files": len(orphan_files),
            "n_orphan_entries": len(orphan_entries),
        }, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 1 if (orphan_files or orphan_entries) else 0

    print(f"Orphan fixtures (file exists, no catalog entry): {len(orphan_files)}")
    for i, fid in enumerate(orphan_files[:30]):
        print(f"  {fid}")
    if len(orphan_files) > 30:
        print(f"  ... and {len(orphan_files) - 30} more")
    print()
    print(f"Orphan catalog entries (entry exists, no fixture): {len(orphan_entries)}")
    for i, fid in enumerate(orphan_entries[:30]):
        print(f"  {fid}")
    if len(orphan_entries) > 30:
        print(f"  ... and {len(orphan_entries) - 30} more")
    return 1 if (orphan_files or orphan_entries) else 0


if __name__ == "__main__":
    raise SystemExit(main())
