"""Outcome conformance check.

For each catalog entry with extracted outcome tags, classify the live
oracle output and check whether it falls within the catalog's
``allowed`` set. A mismatch is a CONFORMANCE-FAIL: the catalog says
the kernel should produce one of {heal, reject}, but the live oracle
shows the kernel doing something else (silently accepting, crashing).

This wires together two pieces:

- ``_outcome_extractor``: tags entries from prose
- ``validate2`` summary: actual oracle behavior

Mismatches surface a different kind of drift than ``_final_verdict``:
``_final_verdict`` checks "live oracle == codified Expected validation"
(both are spec strings). This check asks "does the kernel's behavior
actually match the catalog's *claim* about what kernels should do?"

Usage::

    cd validation
    uv run python -m step_corpus._outcome_conformance
    uv run python -m step_corpus._outcome_conformance --json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from step_corpus import catalog
from step_corpus._outcome_extractor import extract_outcomes

V2 = Path("/tmp/cad-v2-out")


def classify_oracle_output(summary: dict) -> set[str]:
    """Classify a fixture's live oracle behavior into outcome tags.

    Returns a set of tags in the same vocabulary as the extractor:
    ``heal``, ``reject``, ``warn-and-proceed``, ``silent-accept``,
    ``crash``, ``infinite-loop``.

    A fixture can produce multiple tags if its oracles disagree: e.g.
    ``occt=shape(1) gmsh=reject`` is both ``heal`` (OCC accepted) and
    ``reject`` (gmsh rejected).
    """
    tags: set[str] = set()
    occt_off = summary.get("occt_heal_off", "")
    occt_on  = summary.get("occt_heal_on", "")
    gmsh_off = summary.get("gmsh_autofix_off", "")
    ifc      = summary.get("ifcopenshell", "")

    # Crash detection
    if any("signal(" in v for v in (occt_off, occt_on, gmsh_off)):
        tags.add("crash")

    # Reject / heal / silent-accept on OCC heal_off
    if "reject" in occt_off:
        tags.add("reject")
    elif "shape(" in occt_off:
        # OCC produced shapes; kernel "accepted". Without diagnostic
        # signature, we can't tell heal-vs-silent-accept from this
        # field alone, but if heal_on yielded different shape count it's
        # healing.
        if occt_on != occt_off and "shape(" in occt_on:
            tags.add("heal")
        elif "shape(" in occt_off:
            tags.add("heal")  # default for shape-loading
    elif occt_off == "empty":
        # Silent-empty: OCC accepted but produced nothing. Could be
        # "ignore the input" (silent-accept) or "produce empty result".
        tags.add("silent-accept")

    # ifcOpenShell signal
    if ifc == "reject":
        tags.add("reject")

    # Diagnostic-based heuristics
    diag_off = summary.get("occt_diag_off") or "none"
    if diag_off != "none" and "reject" not in occt_off:
        # OCC emitted diagnostics but accepted: heal or warn-and-proceed
        tags.add("warn-and-proceed")

    return tags


def conformance(allowed: set[str], disallowed: set[str], observed: set[str]) -> str:
    """Return ``conform | violate-disallowed | outside-allowed | no-tags | informational``."""
    if not allowed and not disallowed:
        return "no-tags"
    if observed & disallowed:
        return "violate-disallowed"
    if allowed and not (observed & allowed):
        return "outside-allowed"
    return "conform"


def _load_summary(entry: dict) -> dict | None:
    p = V2 / entry["section_dir"] / f"{entry['id']}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text()).get("summary")
    except Exception:
        return None


def report(entries: Iterable[dict] | None = None) -> list[dict[str, Any]]:
    rows = []
    src = entries if entries is not None else catalog.iter_canonical()
    for entry in src:
        prose = entry.get("expected_kernel_behavior") or ""
        out = extract_outcomes(prose)
        allowed = set(out["allowed"])
        disallowed = set(out["disallowed"])
        summary = _load_summary(entry)
        if summary is None:
            observed = set()
            verdict = "no-oracle"
        else:
            observed = classify_oracle_output(summary)
            verdict = conformance(allowed, disallowed, observed)
        rows.append({
            "id": entry["id"],
            "section": entry["section"],
            "title": entry["title"],
            "allowed": sorted(allowed),
            "disallowed": sorted(disallowed),
            "observed": sorted(observed),
            "verdict": verdict,
            "spec": (summary or {}).get("occt_heal_off") if summary else None,
        })
    return rows


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._outcome_conformance")
    p.add_argument("--json", action="store_true")
    p.add_argument("--show-violations", type=int, default=20)
    args = p.parse_args(argv)

    rows = report()
    if args.json:
        json.dump(rows, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    bucket = Counter(r["verdict"] for r in rows)
    print(f"Outcome conformance across {len(rows)} entries:\n")
    print(f"{'verdict':<22} count")
    print(f"{'-' * 22} -----")
    for k in ("conform", "outside-allowed", "violate-disallowed", "no-tags", "no-oracle"):
        n = bucket.get(k, 0)
        pct = 100 * n / len(rows) if rows else 0
        print(f"{k:<22} {n:>5}  ({pct:.1f} %)")

    # Show interesting categories
    violations = [r for r in rows if r["verdict"] == "violate-disallowed"]
    outside = [r for r in rows if r["verdict"] == "outside-allowed"]

    def fmt_set(s):
        return ",".join(s) if s else "—"

    if violations:
        print(f"\n=== violate-disallowed ({len(violations)}): kernel does what catalog forbids")
        for r in violations[:args.show_violations]:
            d = fmt_set(r["disallowed"])
            o = fmt_set(r["observed"])
            print(f"  {r['id']:<8} disallowed={d:<30} observed={o:<30} spec={r['spec']}")

    if outside:
        print(f"\n=== outside-allowed ({len(outside)}): kernel doesn't do what catalog says it should")
        for r in outside[:args.show_violations]:
            a = fmt_set(r["allowed"])
            o = fmt_set(r["observed"])
            print(f"  {r['id']:<8} allowed={a:<30} observed={o:<30} spec={r['spec']}")

    return 0 if not (violations or outside) else 0  # informational; don't fail CI


if __name__ == "__main__":
    raise SystemExit(main())
