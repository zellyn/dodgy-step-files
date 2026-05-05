"""Auto-generate per-fixture detail pages.

For each catalog entry, write one markdown file aggregating:

- Catalog metadata (id, title, section, sources, sender)
- Description / reproducer / expected kernel behavior / notes
- Live oracle output (validate2 summary)
- Tier-3 geometric metrics (face count, edge count, face areas, sliver
  aspects, BRepCheck validity)
- Cross-oracle status (purepy-strict vs OCCT)
- Tier-3 machine-checkable assertions
- Forward adversarial verdict (if available)
- Reverse self-evidence rank (if available)
- Mutation sensitivity (if available)
- Cross-references (see_also)
- Link back to the .stp fixture

Output: ``validation/per-fixture/<section_dir>/<id>.md``. Written with a
front-matter block so they're easy to consume by static-site generators.

Usage::

    cd validation
    uv run python -m step_corpus._per_fixture_pages
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from step_corpus import catalog
from step_corpus._build_catalog_json import RESEARCH_ROOT
from step_corpus._outcome_extractor import extract_outcomes

V2 = Path("/tmp/cad-v2-out")
T3 = Path("/tmp/cad-v2-out-tier3")
PAGES_DIR = RESEARCH_ROOT / "validation" / "per-fixture"


def _read_oracle(entry: dict) -> dict | None:
    p = V2 / entry["section_dir"] / f"{entry['id']}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _read_tier3(entry: dict) -> dict | None:
    p = T3 / entry["section_dir"] / f"{entry['id']}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _adversarial_data() -> dict[str, str]:
    """Map id → forward-review verdict from the batch reports."""
    out: dict[str, str] = {}
    pat = re.compile(r"^\|\s*([A-Z][a-z]*\d+)\s*\|\s*([a-z\-]+)\s*\|")
    for stem in ("cad-adversarial-batch", "cad-v02-fwd-batch"):
        for n in (1, 2, 3):
            p = Path(f"/tmp/{stem}{n}.md")
            if not p.is_file():
                continue
            for line in p.read_text().splitlines():
                m = pat.match(line)
                if m:
                    v = m.group(2).strip()
                    if v == "does-not":
                        v = "does-not-demonstrate"
                    out[m.group(1)] = v
    return out


def _reverse_data() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in (Path("/tmp/cad-reverse-eval.json"),
                 Path("/tmp/cad-v02-reverse-eval.json")):
        if not path.is_file():
            continue
        try:
            rows = json.loads(path.read_text())
        except Exception:
            continue
        for r in rows:
            if isinstance(r, dict) and r.get("id"):
                out[r["id"]] = r
    return out


def _mutation_data() -> dict[str, dict]:
    p = Path("/tmp/cad-mutation-test.json")
    if not p.is_file():
        return {}
    try:
        return {r["id"]: r for r in json.loads(p.read_text()) if isinstance(r, dict)}
    except Exception:
        return {}


def _tier3_assertions(_md_text: str, _eid: str) -> list[str]:
    """Legacy. Assertions now live on the JSON entry directly. Kept
    for ABI compatibility; the page builder reads ``entry['tier3_assertions']``."""
    return []


def _cross_oracle_class(summary: dict) -> str:
    purepy = summary.get("part21_strict", "?")
    occt = summary.get("occt_heal_off", "?")
    purepy_accepts = purepy == "accept" or purepy.startswith("warn")
    if purepy.startswith("reject") and ("shape(" in occt or occt == "empty"):
        return "OCC silently heals — pure-Python rejects this"
    if purepy_accepts and "reject" in occt:
        return "OCC stricter than spec — pure-Python accepts"
    if purepy_accepts and "signal(" in occt:
        return "Spec-clean Part-21; OCC crashes (kernel-side bug)"
    return "Pure-Python and OCC agree"


def _format_oracle_table(summary: dict | None) -> str:
    if not summary:
        return "*(no live oracle data — run `_run_corpus` to populate)*"
    rows = ["| Oracle | Verdict |", "|---|---|"]
    for k in ("occt_heal_on", "occt_heal_off", "gmsh_autofix_on",
              "gmsh_autofix_off", "ifcopenshell", "part21_strict", "manifold"):
        rows.append(f"| `{k}` | `{summary.get(k, '?')}` |")
    # Diagnostic signatures (silent-empty disambiguator)
    for k in ("occt_diag_on", "occt_diag_off", "gmsh_diag"):
        v = summary.get(k)
        if v and v != "none":
            rows.append(f"| `{k}` | {v[:80]} |")
    return "\n".join(rows)


def _format_tier3(t3: dict | None) -> str:
    if not t3:
        return "*(tier-3 not run — fixture didn't load or wasn't introspected)*"
    lines = [
        f"- **load**: `{t3.get('load')}`",
        f"- **n_faces**: {len(t3.get('faces') or [])}",
        f"- **n_edges_total**: {t3.get('n_edges_total')}",
        f"- **n_vertices_total**: {t3.get('n_vertices_total')}",
        f"- **brepcheck.valid**: `{(t3.get('brepcheck') or {}).get('valid')}`",
    ]
    faces = t3.get("faces") or []
    if faces:
        lines.append("\nFace details (first 3):\n")
        lines.append("| i | type | area | sliver_aspect | edges |")
        lines.append("|---|---|---|---|---|")
        for f in faces[:3]:
            lines.append(
                f"| {f.get('i')} | {f.get('surface_type')} | {f.get('area')} | "
                f"{f.get('sliver_aspect_max_min')} | {f.get('edge_count')} |"
            )
    return "\n".join(lines)


def _build_page(entry: dict, md_text: str,
                fwd: dict[str, str], rev: dict[str, dict],
                mut: dict[str, dict]) -> str:
    eid = entry["id"]
    oracle = _read_oracle(entry)
    summary = (oracle or {}).get("summary") or {}
    t3 = _read_tier3(entry)
    asserts = entry.get("tier3_assertions") or []
    fwd_verdict = fwd.get(eid, "n/a")
    rev_row = rev.get(eid)
    mut_row = mut.get(eid)

    rel_fixture = entry["fixture_path"]
    cross = _cross_oracle_class(summary) if summary else "n/a"

    lines = [
        f"# {eid} — {entry['title']}\n",
        f"<!-- Auto-generated; edit `STEP_PROBLEM_CATALOG.md` instead. -->\n",
        f"**Section**: §{entry['section']} (`{entry['section_dir']}`)  ",
        f"**Fixture**: [`{rel_fixture}`](../../{rel_fixture})  ",
    ]
    if entry.get("sender"):
        lines.append(f"**Sender**: {entry['sender']}  ")
    lines.append("")

    if entry.get("sources"):
        lines.append("## Sources")
        for s in entry["sources"]:
            lines.append(f"- {s}")
        lines.append("")

    lines.append("## Description")
    lines.append("")
    lines.append(entry["description"])
    lines.append("")

    lines.append("## Reproducer recipe")
    lines.append("")
    lines.append(entry["reproducer"])
    lines.append("")

    lines.append("## Expected kernel behavior")
    lines.append("")
    lines.append(entry["expected_kernel_behavior"])
    lines.append("")

    outcomes = extract_outcomes(entry.get("expected_kernel_behavior") or "")
    if outcomes["allowed"] or outcomes["disallowed"]:
        lines.append("**Structured outcomes** (extracted from prose; for downstream auto-grading):")
        if outcomes["allowed"]:
            lines.append(f"- allowed: `{', '.join(outcomes['allowed'])}`")
        if outcomes["disallowed"]:
            lines.append(f"- disallowed: `{', '.join(outcomes['disallowed'])}`")
        lines.append("")

    if entry.get("notes"):
        lines.append("## Notes")
        lines.append("")
        lines.append(entry["notes"])
        lines.append("")

    lines.append("## Live oracle output")
    lines.append("")
    lines.append(_format_oracle_table(summary))
    lines.append("")
    lines.append(f"**Cross-oracle classification**: {cross}")
    lines.append("")

    lines.append("## Tier-3 geometric introspection")
    lines.append("")
    lines.append(_format_tier3(t3))
    lines.append("")

    if asserts:
        lines.append("## Tier-3 assertions (machine-checked)")
        lines.append("")
        for a in asserts:
            lines.append(f"- `{a}`")
        lines.append("")

    byte_asserts = entry.get("byte_assertions") or []
    if byte_asserts:
        lines.append("## Byte assertions (machine-checked)")
        lines.append("")
        for a in byte_asserts:
            lines.append(f"- `{a}`")
        lines.append("")

    # Structured signals
    extras = []
    pt = entry.get("provenance_tier")
    if pt and pt != "bytes-sufficient":
        extras.append(f"- **Provenance tier**: `{pt}` (defect not fully embodied in fixture bytes)")
    co = entry.get("cross_oracle_note")
    if co:
        extras.append(f"- **Cross-oracle**: {co}")
    ob = entry.get("occ_behavior_note")
    if ob:
        extras.append(f"- **OCC behavior**: {ob}")
    if extras:
        lines.append("## Provenance / kernel-behavior annotations")
        lines.append("")
        lines.extend(extras)
        lines.append("")

    lines.append("## Confidence signals")
    lines.append("")
    lines.append("| Signal | Result |")
    lines.append("|---|---|")
    lines.append(f"| Forward adversarial review | `{fwd_verdict}` |")
    if rev_row:
        rk = rev_row.get("rank")
        bk = rev_row.get("bucket")
        lines.append(f"| Reverse self-evidence | `{bk}` (rank {rk if rk is not None else 'n/a'}) |")
    else:
        lines.append("| Reverse self-evidence | `n/a` |")
    if mut_row:
        ms = mut_row.get("status")
        n = mut_row.get("n_attempts")
        lines.append(f"| Mutation sensitivity | `{ms}` ({n or '?'} attempts) |")
    else:
        lines.append("| Mutation sensitivity | not tested |")
    lines.append(f"| Expected validation | `{entry['expected_validation']}` |")
    lines.append("")

    if entry.get("see_also"):
        lines.append("## Cross-references")
        lines.append("")
        lines.append("**See also**: " + ", ".join(f"[{i}]({i}.md)" for i in entry["see_also"]))
        lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._per_fixture_pages")
    p.add_argument("--out-dir", type=Path, default=PAGES_DIR)
    args = p.parse_args(argv)

    md_text = (RESEARCH_ROOT / "STEP_PROBLEM_CATALOG.md").read_text(encoding="utf-8")
    fwd = _adversarial_data()
    rev = _reverse_data()
    mut = _mutation_data()

    counts = Counter()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for entry in catalog.iter_canonical():
        page = _build_page(entry, md_text, fwd, rev, mut)
        target = args.out_dir / entry["section_dir"] / f"{entry['id']}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")
        counts[entry["section_dir"]] += 1

    # Section index page
    index_lines = [
        "# STEP Defect Corpus — Per-Fixture Pages",
        "",
        f"Auto-generated detail pages for {sum(counts.values())} fixtures.",
        "",
        "## By section",
        "",
        "| Section | Count |",
        "|---|---:|",
    ]
    for sec in sorted(counts):
        index_lines.append(f"| [{sec}]({sec}/) | {counts[sec]} |")
    (args.out_dir / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    print(f"Wrote {sum(counts.values())} pages to {args.out_dir}")
    for sec, n in sorted(counts.items()):
        print(f"  {sec}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
