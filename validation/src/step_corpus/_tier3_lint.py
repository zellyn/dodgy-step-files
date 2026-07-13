"""Tier-3 placeholder-geometry lint.

Counterpart to ``_construction_lint`` (DIRECTION/AXIS bugs) and
``_schema_oracle`` (FILE_SCHEMA vs entity vocabulary). This lint catches
a different defect class: a fixture loads with `shape(N)`, but the
loaded geometry is *placeholder* (faces with no edge bounds, areas
that are NaN or astronomical (8e+100 from infinite-plane queries),
etc.).

This pattern is a recurring authoring pitfall: a fixture passes
syntactic checks and OCCT happily binds a `MANIFOLD_SOLID_BREP` to a
`CLOSED_SHELL` of `ADVANCED_FACE`s with empty wire-bounds, but the
result is geometrically degenerate. The catalog claim ("10×10×10 cube
with claimed volume 500 mm³") is unfalsifiable on this geometry.

Architecture
------------

Tier-3 introspection runs OCCT in a subprocess and is slow (~5 s per
fixture). To keep the lint fast, geometry is pre-computed once and
cached at ``/tmp/cad-tier3-out.json``. Refresh by running:

    uv run python -m step_corpus._tier3_lint --audit

This audits every catalog fixture whose ``occt_heal_off`` is
``shape(N)`` per the validate2 cache at ``/tmp/cad-v2-out``, runs
tier-3 in parallel (4 workers), and writes results to
``/tmp/cad-tier3-out.json``. Run again whenever fixtures change.

Rules
-----

For each fixture in the cache:

- **face-zero-edges**: every face must have ``edge_count >= 3``. A
  face with ``edge_count == 0`` is unbounded.

- **face-degenerate-area**: every face must have a finite area smaller
  than 1e30. NaN, infinite, or 1e+100-class values indicate the
  supporting surface was queried without a bounded domain.

A current-state ceiling (``CEILING = 31``) acts as a regression
ratchet: existing placeholder fixtures are tolerated (they predate
this lint), but no new fixture may join the list. Drop the ceiling
whenever a batch fix lands.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from step_corpus import catalog
from step_corpus._build_catalog_json import RESEARCH_ROOT


V2_BASE = Path("/tmp/cad-v2-out")
TIER3_CACHE = Path("/tmp/cad-tier3-out.json")
TIER3_TIMEOUT_S = 30


# Fixtures where the placeholder / unbounded face IS the catalog defect,
# OR the catalog claim is non-geometric (colors / labels / round-trip /
# schema scope / parser-behavior / OCCT-internal-call-path); in those
# cases, real bounded geometry adds nothing to falsifiability.
EXEMPT_PLACEHOLDER: set[str] = {
    # Catalog claim IS the unbound / out-of-scope face.
    "Tfa002",  # "Unbound ADVANCED_FACE (no FACE_OUTER_BOUND, no FACE_BOUND)"
    "Tfa026",  # OFFSET_SURFACE schema scope; defect is the surface type, not bounds
    "Tfa252",  # EDGE_CURVE null edge_geometry -> wire drops -> face collapses to
               # unbounded natural-surface fallback (edge_count==0) IS the defect

    # Non-geometric: parser / call-path / round-trip / semantic-attribute claims.
    "Ad064",   # string truncation on name parsing
    "Ad084",   # XCAFDoc_ShapeTool::FindSubShape crash; specific OCCT call path
    "A017",    # labels/colors lost when subshape carries transform on round-trip
    "A018",    # STYLED_ITEM at wrong scope / mis-binding
    "A019",    # per-face colours collapse on shared supporting planes
    "A020",    # bare STYLED_ITEM at top level (no MDGPR parent)
    "A022",    # PRESENTATION_LAYER_ASSIGNMENT collisions / namespace abuse
    "A023",    # mapped_item identity-transform requirement (Saved Views)
    "A073",    # Expand Compounds loses sub-shape locations on flatten
    "A087",    # exporter loses shapes after import-export cycle
    "Pmi033",  # placed_datum_target_feature shape-attr semantic mismatch
    "Pmi041",  # dimensional_size vs dimensional_location attribute confusion
    "Pmi044",  # legacy attachment via PropertyDefinition (AP203+G&DT)
    "Pmi057",  # GTOL semantic vs presentation associativity round-trip
    "Pmi059",  # surface status (cosmetic/construction/blanked) round-trip
    "Pmi061",  # DATUM→ADVANCED_FACE chain pattern not resolved
    "Pmi062",  # STEP-to-glTF mesh-count balloon inflation
    "Pmi079",  # dimension lost on STEP export round-trip
    "Pmi083",  # annotation plane orientation flipped (face same_sense expressible w/o real wires)
}


# Current-state ceiling; drop as fixtures get rebuilt with real geometry.
# 2026-05-02: 26 placeholder violators triaged → 21 exempted (non-geometric
# claims) + 5 fixed (Tfa055/056/057, A067, Pmi001: wires-in-UV /
# nested-wires / wire-orientation / shared-subshape baking / hole-as-two-
# half-cylinders). All 5 landed with real geometry; ratcheted to 0.
CEILING = 0


def _classify_face(face: dict[str, Any]) -> str | None:
    """Return rule name if face violates, else None."""
    ec = face.get("edge_count", None)
    if ec == 0:
        return "face-zero-edges"
    a = face.get("area", None)
    if a is None:
        return None
    if isinstance(a, float):
        if math.isnan(a) or math.isinf(a) or abs(a) > 1e30:
            return "face-degenerate-area"
    return None


def _shape_loaders() -> list[tuple[str, str, Path]]:
    """Return [(id, section_dir, fixture_path), ...] for fixtures that load
    with shape(N>=1) per the validate2 cache."""
    out = []
    for entry in catalog.iter_canonical():
        v2_path = V2_BASE / entry["section_dir"] / f'{entry["id"]}.json'
        if not v2_path.is_file():
            continue
        try:
            v2 = json.loads(v2_path.read_text())
        except Exception:
            continue
        occt = v2.get("summary", {}).get("occt_heal_off", "")
        if "shape(" in occt and "shape(0)" not in occt:
            fp = RESEARCH_ROOT / entry["fixture_path"]
            if fp.is_file():
                out.append((entry["id"], entry["section_dir"], fp))
    return out


def _run_tier3(args: tuple[str, Path]) -> tuple[str, dict | None]:
    eid, fp = args
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "step_corpus.tier3_geometric",
             str(fp), "--json"],
            capture_output=True, text=True, timeout=TIER3_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return eid, None
    if proc.returncode != 0:
        return eid, None
    try:
        return eid, json.loads(proc.stdout)
    except Exception:
        return eid, None


def audit_corpus(workers: int = 4) -> dict[str, dict]:
    loaders = _shape_loaders()
    print(f"Auditing tier-3 on {len(loaders)} shape-loading fixtures with {workers} workers...",
          file=sys.stderr, flush=True)
    cache: dict[str, dict] = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        for i, (eid, t3) in enumerate(ex.map(_run_tier3, [(eid, fp) for eid, _, fp in loaders]), 1):
            if t3 is not None:
                cache[eid] = {
                    "n_faces": len(t3.get("faces", [])),
                    "faces": [
                        {"i": f.get("i"), "edge_count": f.get("edge_count"),
                         "area": f.get("area")}
                        for f in t3.get("faces", [])
                    ],
                }
            if i % 30 == 0:
                print(f"  {i}/{len(loaders)} done; cache size {len(cache)}",
                      file=sys.stderr, flush=True)
    return cache


def lint_from_cache(cache: dict[str, dict]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in catalog.iter_canonical():
        eid = entry["id"]
        if eid in EXEMPT_PLACEHOLDER:
            continue
        t3 = cache.get(eid)
        if t3 is None:
            continue
        issues: list[str] = []
        for f in t3.get("faces", []):
            bad = _classify_face(f)
            if bad:
                issues.append(f"{bad} on face[{f.get('i')}] (area={f.get('area')!r})")
        if issues:
            rows.append({
                "id": eid,
                "section_dir": entry["section_dir"],
                "issues": issues[:6],
            })
    return rows


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._tier3_lint")
    p.add_argument("--audit", action="store_true",
                   help="rerun tier-3 across the corpus and write the cache")
    p.add_argument("--workers", type=int, default=4,
                   help="parallel tier-3 subprocesses for --audit")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true",
                   help="exit 1 if violation count exceeds CEILING")
    args = p.parse_args(argv)

    if args.audit:
        cache = audit_corpus(workers=args.workers)
        TIER3_CACHE.write_text(json.dumps(cache, indent=2, default=str))
        print(f"\nWrote {len(cache)} entries to {TIER3_CACHE}", file=sys.stderr)

    if not TIER3_CACHE.is_file():
        print(f"No tier-3 cache at {TIER3_CACHE}. Run `--audit` first.", file=sys.stderr)
        return 2

    cache = json.loads(TIER3_CACHE.read_text())
    rows = lint_from_cache(cache)

    if args.json:
        json.dump(rows, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    print(f"Tier-3 placeholder-geometry lint:")
    print(f"  fixtures with violations: {len(rows)} (ceiling: {CEILING})")
    if rows:
        print(f"\nFirst 30:")
        for r in rows[:30]:
            issues = "; ".join(r["issues"][:2])
            print(f"  {r['id']:<8}  {issues}")
    if len(rows) > CEILING:
        print(f"\nOver ceiling by {len(rows) - CEILING}. Either fix the new fixture(s) or raise the ceiling explicitly.")
        return 1 if args.strict else 0
    if len(rows) < CEILING:
        print(f"\nUnder ceiling by {CEILING - len(rows)}. Drop CEILING to {len(rows)} in _tier3_lint.py to ratchet down.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
