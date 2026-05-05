"""Regenerate per-section README index files under step-examples/12-*/.

Each section README starts with a short prose intro (preserved from
existing file) and then a fixtures table listing every entry in that
section with its catalog title.

Usage::

    uv run python -m step_corpus._regen_section_readmes
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from step_corpus import catalog
from step_corpus._build_catalog_json import RESEARCH_ROOT

SECTION_INTROS: dict[str, str] = {
    "12-12-cross-product": (
        "# §12.12 — Cross-product synthesized defects (`Xp*`-prefix)\n\n"
        "Fixtures combining 2-3 single-defect classes per file (encoding × wire,\n"
        "sliver × non-manifold, PMI × tess/BRep mix, etc.). They exercise\n"
        "ordering and interaction hazards when multiple defect types co-occur\n"
        "in the same file. Each entry's `**Builds on:**` field cites the single-\n"
        "defect entries it composes.\n\n"
        "See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.12)\n"
        "for canonical entries.\n"
    ),
}


def _intro_for(section_dir: str) -> str:
    """Return existing README intro (everything up to ## Fixtures), else
    the canonical intro for new sections."""
    rd = RESEARCH_ROOT / "step-examples" / section_dir / "README.md"
    if rd.is_file():
        text = rd.read_text(encoding="utf-8")
        m = re.search(r"^## Fixtures\b", text, re.MULTILINE)
        if m:
            return text[:m.start()].rstrip() + "\n"
        return text.rstrip() + "\n"
    return SECTION_INTROS.get(section_dir, f"# {section_dir}\n")


def _natural_sort_key(entry: dict) -> tuple:
    eid = entry["id"]
    m = re.match(r"^([A-Za-z]+)(\d+)$", eid)
    if m:
        return (m.group(1), int(m.group(2)))
    return (eid, 0)


def main() -> int:
    by_section: dict[str, list[dict]] = defaultdict(list)
    for entry in catalog.iter_canonical():
        by_section[entry["section_dir"]].append(entry)

    for section_dir, entries in by_section.items():
        entries.sort(key=_natural_sort_key)
        intro = _intro_for(section_dir)
        rows = ["| ID | Title |", "|---|---|"]
        for e in entries:
            # Escape pipes inside titles
            title = e["title"].replace("|", "\\|")
            rows.append(f"| [{e['id']}]({e['id']}.stp) | {title} |")
        body = intro + "\n## Fixtures\n\n" + "\n".join(rows) + "\n"
        target = RESEARCH_ROOT / "step-examples" / section_dir / "README.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        print(f"  wrote {section_dir}/README.md ({len(entries)} entries)")

    print(f"\nTotal: {sum(len(v) for v in by_section.values())} entries across {len(by_section)} sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
