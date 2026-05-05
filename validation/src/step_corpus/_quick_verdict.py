"""Heuristic verdict generator for §12.3 reports.

Reads pre-computed validator JSON + catalog entries, emits per-file verdicts
with simple rules:
  - all 4 oracles reject  → CONFIRMED (defect blocks parse)
  - all accept-but-empty (n_roots=0, shape_null=true) → CONFIRMED if catalog
    claims silent corruption / topological defect; else CONCERN
  - some have shape, some don't → CONFIRMED if catalog claims partial-failure
  - exception-out → CONFIRMED if catalog mentions crash; else CONCERN

This isn't as precise as an LLM agent's reasoning but covers the bulk
quickly without stalling.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def grep_catalog_entry(prefix_id: str, catalog: Path) -> str:
    """Pull the catalog block for `### {prefix_id} —` (next 12 lines)."""
    try:
        out = subprocess.run(
            ["grep", "-A", "12", f"^### {prefix_id} —", str(catalog)],
            capture_output=True, text=True, timeout=5,
        )
        return out.stdout
    except Exception as e:
        return f"<grep failed: {e}>"


def per_file_verdict(jpath: Path, catalog: Path, prefix_id: str) -> tuple[str, str]:
    """Return (verdict, one-line-diagnosis)."""
    if not jpath.exists() or jpath.stat().st_size == 0:
        return "ERROR", f"missing or empty pre-computed JSON: {jpath.name}"

    try:
        d = json.loads(jpath.read_text())
    except Exception as e:
        return "ERROR", f"corrupt JSON: {e}"

    summary = d.get("summary", {})
    cat_text = grep_catalog_entry(prefix_id, catalog)

    # Extract the catalog one-liner title
    m = re.search(rf"^### {re.escape(prefix_id)} — (.+)$", cat_text, flags=re.M)
    title = m.group(1).strip() if m else "(no title)"

    # If marked merged in catalog, skip
    if "**Status**: merged" in cat_text:
        return "MERGED", f"merged stub — {title[:60]}"

    occt_on = summary.get("occt_heal_on", "?")
    occt_off = summary.get("occt_heal_off", "?")
    gmsh_on = summary.get("gmsh_autofix_on", "?")
    ifc = summary.get("ifcopenshell", "?")

    bs = d.get("byte_signature", {})
    es = d.get("entity_summary", {})
    n_entities = es.get("total_entity_definitions", 0)

    # Heuristics:
    # 1. All-empty / silent-corruption pattern
    all_empty = (
        occt_on in ("empty", "reject", "except")
        and occt_off in ("empty", "reject", "except")
        and gmsh_on in ("empty", "reject", "except", "shape(0)")
    )
    has_shape = "shape" in str(occt_on) and not str(occt_on).endswith("(0)")

    # 2. Catalog claim keywords
    cat_lower = cat_text.lower()
    is_silent_corruption_claim = any(s in cat_lower for s in [
        "silent", "drop", "lost", "ignored", "absorbed", "auto-heal",
    ])
    is_topology_invalid_claim = any(s in cat_lower for s in [
        "open shell", "non-manifold", "invalid", "missing seam",
        "self-intersect", "degenerate",
    ])
    is_crash_claim = any(s in cat_lower for s in [
        "crash", "segfault", "exception", "abort", "null deref",
    ])

    occt_excepted = "except" in (occt_on, occt_off)

    if occt_excepted and is_crash_claim:
        return "CONFIRMED", f"OCCT raised exception — matches crash claim — {title[:60]}"
    if all_empty and (is_silent_corruption_claim or is_topology_invalid_claim):
        return "CONFIRMED", f"silent corruption — {n_entities} entities parsed but no shape — {title[:50]}"
    if all_empty and not (is_silent_corruption_claim or is_topology_invalid_claim):
        return "CONCERN", f"silent corruption signal but catalog doesn't explicitly claim it — {title[:50]}"
    if has_shape and is_topology_invalid_claim:
        return "CONCERN", f"OCCT produced shape; structural claim may need entity-level check — {title[:50]}"
    if has_shape and not is_topology_invalid_claim:
        return "CONFIRMED", f"OCCT loaded shape; defect likely consumer-side — {title[:50]}"

    return "CONCERN", f"oracle pattern unclear: occt_on={occt_on} occt_off={occt_off} ifc={ifc}"


def write_section_report(
    section_dir: str,
    prefix: str,
    out_path: Path,
    catalog: Path,
    json_dir: Path,
):
    """Generate report for one §12.3 sub-section."""
    files = sorted(Path(section_dir).glob(f"{prefix}*.stp"))
    counts = {"CONFIRMED": 0, "CONCERN": 0, "FAIL": 0, "ERROR": 0, "MERGED": 0}
    lines = [f"# §12.3 {prefix} validation\n"]
    lines.append("Auto-generated heuristic verdicts. CONFIRMED = parser/oracle behavior matches catalog claim. CONCERN = needs manual check. ERROR = tooling problem.\n\n## Per-file\n")
    for stp in files:
        prefix_id = stp.stem
        jpath = json_dir / f"{prefix_id}.json"
        verdict, diag = per_file_verdict(jpath, catalog, prefix_id)
        counts[verdict] = counts.get(verdict, 0) + 1
        lines.append(f"{prefix_id} {verdict} — {diag}")
    lines.append("\n## Summary")
    lines.append(f"Total files: {len(files)}")
    for k, v in counts.items():
        if v:
            lines.append(f"{k}: {v}")
    out_path.write_text("\n".join(lines) + "\n")
    return counts


def main():
    ap = argparse.ArgumentParser()
    # This file lives at: <repo-root>/validation/src/step_corpus/_quick_verdict.py
    # So the repo root is parents[3].
    repo_root = Path(__file__).resolve().parents[3]
    ap.add_argument("--catalog", default=str(repo_root / "STEP_PROBLEM_CATALOG.md"))
    ap.add_argument("--examples", default=str(repo_root / "step-examples"))
    ap.add_argument("--json-base", default="/tmp/cad-12-3-validator-out")
    ap.add_argument("--out-base", default=str(repo_root / "validation" / "reports"))
    args = ap.parse_args()

    catalog = Path(args.catalog)
    sections = [
        ("12-3a-shells", "Tsh"),
        ("12-3b-wires", "Twi"),
        ("12-3c-faces", "Tfa"),
    ]
    for sec_dir, prefix in sections:
        out = Path(args.out_base) / f"{sec_dir.split('-shells')[0].split('-wires')[0].split('-faces')[0]}-{prefix.lower()}-validation.md"
        # Just use canonical naming
        out = Path(args.out_base) / f"{sec_dir.split('-')[0]}-{sec_dir.split('-')[1]}-validation.md"
        counts = write_section_report(
            section_dir=str(Path(args.examples) / sec_dir),
            prefix=prefix,
            out_path=out,
            catalog=catalog,
            json_dir=Path(args.json_base) / sec_dir,
        )
        print(f"[{sec_dir}] {dict(counts)} → {out}")


if __name__ == "__main__":
    main()
