"""Construction-validity guards for fixture scaffolding.

The topology meta-quality analysis surfaced several fixtures with
*scaffold* bugs that mask the actual defect: non-unit ``DIRECTION``
ratios (Tfa050, Sw009, Twi082), parallel axis/refdir
(Hea008), and similar construction bugs. The catalog claim is about
something else, but the broken scaffold may make oracle behavior
ambiguous.

This lint catches them statically by regex on the fixture bytes.

Rules
-----

- **direction-non-unit**: every ``DIRECTION('',(<a>,<b>,<c>))`` must
  have ``a² + b² + c² = 1.0`` within 1 % tolerance. The spec doesn't
  strictly require unit length, but every kernel uses these as basis
  vectors and silently normalises. A fixture with a non-unit
  DIRECTION isn't testing what its catalog claim says.

- **axis-refdir-parallel**: in every ``AXIS2_PLACEMENT_3D``, the
  ``axis`` (Z) and ``ref_direction`` (X) must be linearly independent.
  Parallel basis vectors collapse the placement.

The rules are deliberately conservative; they only flag genuine spec
violations, not anything that *might* be intentional. Each rule's
exemption list excuses fixtures where the construction bug IS the
catalog defect.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

from step_corpus import catalog
from step_corpus._build_catalog_json import RESEARCH_ROOT


EXAMPLES = RESEARCH_ROOT / "step-examples"

# Match `#N=DIRECTION('...',(a,b,c));`. Allow whitespace inside the parens
# and signed decimal/exponent floats.
_RE_DIRECTION = re.compile(
    rb"#(\d+)\s*=\s*DIRECTION\s*\(\s*'[^']*'\s*,\s*\(\s*"
    rb"([-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)\s*,\s*"
    rb"([-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)\s*,\s*"
    rb"([-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)\s*\)\s*\)"
)
# Match `#N=AXIS2_PLACEMENT_3D('...',#A,#B,#C);` capturing the three IDs.
_RE_AXIS2 = re.compile(
    rb"#(\d+)\s*=\s*AXIS2_PLACEMENT_3D\s*\(\s*'[^']*'\s*,"
    rb"\s*#(\d+)\s*,\s*(?:#(\d+)|\$)\s*,\s*(?:#(\d+)|\$)"
)


# Exempt fixtures where the construction bug IS the documented defect.
EXEMPT_NON_UNIT_DIRECTION = {
    # Catalog claim is "non-unit DIRECTION encodes scale" or similar.
    "Gs036",   # "Negative-radius / zero-magnitude direction or vector"
    "Tsh051",  # Non-unit DIRECTION encoding implicit scale
    "In011",   # Extreme-magnitude IEEE-754 (1.0E+308) coordinates IS the defect
    "Ls003",   # Lower-case `e` exponent / non-conforming REAL printing IS the defect
    "M061",    # "Scaling-factor encoded as non-unit DIRECTION ratios" (explicitly cited)
    "M067",    # "AXIS2_PLACEMENT_3D with zero-vector DIRECTION ratios" (explicitly cited)
    "Os022",   # "non-unit DIRECTION breaks parameterization" (explicitly cited)
    "Gs053",   # MAPPED_ITEM with (2.0,1.0,1.0) non-uniform scale via non-unit DIRECTION
    "Xp016",   # "DIRECTION('',(0.,0.,0.))" zero-magnitude direction (explicitly cited)
}

EXEMPT_AXIS_REFDIR_PARALLEL = {
    # Catalog claim is "axis and ref_direction are parallel".
    "Gs036",   # "axis and ref_direction colinear" (explicitly cited)
    "M036",    # "Datum target axes nearly identical": near-parallel direction ratios
    "M067",    # zero-vector DIRECTION ratios → degenerate placement
    "Pmi019",  # "view-up parallel to view-direction" (explicitly cited)
    "Xp016",   # AXIS2_PLACEMENT_3D referencing zero-magnitude direction twice
}


def _parse_directions(body: bytes) -> dict[int, tuple[float, float, float]]:
    out: dict[int, tuple[float, float, float]] = {}
    for m in _RE_DIRECTION.finditer(body):
        try:
            rid = int(m.group(1))
            a, b, c = (float(m.group(i)) for i in (2, 3, 4))
        except ValueError:
            continue
        out[rid] = (a, b, c)
    return out


def _parse_axis2_refs(body: bytes) -> list[tuple[int, int | None, int | None]]:
    """Return [(axis2_id, axis_dir_id, refdir_id), ...]."""
    out = []
    for m in _RE_AXIS2.finditer(body):
        rid = int(m.group(1))
        axis_id = int(m.group(3)) if m.group(3) else None
        ref_id = int(m.group(4)) if m.group(4) else None
        out.append((rid, axis_id, ref_id))
    return out


def lint_one(entry: dict) -> list[str]:
    fixture = EXAMPLES / entry["fixture_path"].split("step-examples/")[-1]
    if not fixture.is_file():
        return []
    body = fixture.read_bytes()
    issues: list[str] = []

    eid = entry["id"]
    directions = _parse_directions(body)

    # Rule 1: non-unit DIRECTION
    if eid not in EXEMPT_NON_UNIT_DIRECTION:
        for rid, (a, b, c) in directions.items():
            norm = math.sqrt(a * a + b * b + c * c)
            if norm < 1e-12:
                issues.append(
                    f"#{rid}=DIRECTION has zero magnitude ({a}, {b}, {c})"
                )
            elif abs(norm - 1.0) > 0.01:
                issues.append(
                    f"#{rid}=DIRECTION ratios ({a}, {b}, {c}) have norm {norm:.4f}, "
                    f"expected 1.0 ± 1 %"
                )

    # Rule 2: parallel axis / ref_direction
    if eid not in EXEMPT_AXIS_REFDIR_PARALLEL:
        for axis2_id, axis_id, ref_id in _parse_axis2_refs(body):
            if axis_id is None or ref_id is None:
                continue
            axis = directions.get(axis_id)
            ref = directions.get(ref_id)
            if axis is None or ref is None:
                continue
            # Cross product magnitude: small ⇒ parallel.
            cx = axis[1] * ref[2] - axis[2] * ref[1]
            cy = axis[2] * ref[0] - axis[0] * ref[2]
            cz = axis[0] * ref[1] - axis[1] * ref[0]
            cross_mag = math.sqrt(cx * cx + cy * cy + cz * cz)
            # If both vectors are unit-length, |cross| = sin(angle).
            # Unit cross < 0.01 → angle < ~0.6° → effectively parallel.
            if cross_mag < 0.01:
                issues.append(
                    f"#{axis2_id}=AXIS2_PLACEMENT_3D has parallel axis (#{axis_id}) "
                    f"and ref_direction (#{ref_id}); cross magnitude {cross_mag:.4f}"
                )

    return issues


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._construction_lint")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true",
                   help="exit 1 on any violation")
    args = p.parse_args(argv)

    rows: list[dict] = []
    for entry in catalog.iter_canonical():
        for issue in lint_one(entry):
            rows.append({"id": entry["id"], "issue": issue})

    if args.json:
        json.dump(rows, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    by_id = Counter(r["id"] for r in rows)
    print(f"Construction-lint findings: {len(rows)} violations across {len(by_id)} fixtures\n")
    if rows:
        for r in rows[:30]:
            print(f"  {r['id']:<8}  {r['issue']}")
    return 1 if (args.strict and rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
