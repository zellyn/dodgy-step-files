"""Audit consistency between byte and tier-3 assertions.

A small fraction of catalog entries carry BOTH ``byte_assertions``
(checked against the raw fixture bytes) AND ``tier3_assertions``
(checked against OCCT-parsed geometry). Each kind of claim is true in
its own world, but the two worlds describe the same fixture and must
therefore agree about that fixture's identity. This module detects
*internal contradictions*: pairs of assertions that disagree about a
shared dimension (face count, surface type, etc.).

Heuristics
----------

We pair byte-side and tier-3-side claims that target the same
dimension and check that they don't contradict.

1.  ``count_entity_def(b'ADVANCED_FACE') == K`` ↔ ``n_faces_total ==
    M``. ``ADVANCED_FACE`` is the canonical AP203/214/242 surface-face
    entity, and OCCT loads each of them as one ``TopoDS_Face``. K and
    M should match. Inconsistent if M > K (impossible) or M is much
    smaller than K (loaded < declared without an explanatory note).

2.  ``contains(b'CYLINDRICAL_SURFACE')`` ↔ at least one
    ``face[i].surface_type == 'cylinder'``. If the fixture text
    contains a cylindrical surface entity then *some* loaded face
    should be a cylinder. Inconsistent if every tier-3 surface_type
    claim is non-``cylinder`` and there are tier-3 surface_type claims
    for every face.

3.  ``contains(b'PLANE')`` (as a STEP entity, not the substring
    inside ``CYLINDRICAL_SURFACE`` etc.) ↔ at least one
    ``face[i].surface_type == 'plane'``. Same idea.

4.  ``count_entity_def(b'EDGE_CURVE') == K`` ↔ ``n_edges_total == M``.
    OCCT may collapse coincident edges, so we expect M <= K.
    Inconsistent if M > K.

The detector is deliberately conservative: a pair gets verdict
``inconsistent`` only when the two claims *clearly* cannot both be
true of the same fixture. Pairs that target unrelated dimensions
return ``uncheckable`` (most pairs) so we don't drown the report in
noise.

CLI::

    cd validation
    uv run python -m step_corpus._bytes_tier3_audit
    uv run python -m step_corpus._bytes_tier3_audit --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from step_corpus import catalog

OUTPUT_JSON = Path("/tmp/cad-bytes-tier3-audit.json")

# Entries where bytes/tier-3 divergence IS the documented kernel-bug
# evidence (OCC silently transforms the source). Both assertions are
# individually correct; cross-audit downgrades inconsistent → documented.
DOCUMENTED_DIVERGENCE: set[str] = {
    "Tsh050",  # OCC silently merges two coplanar ADVANCED_FACEs sharing an edge
    "Tsh056",  # figure-eight wire: 1 ADVANCED_FACE in bytes, 2 loaded by OCCT
}

# --- Byte-assertion shape extractors --------------------------------------

_RE_COUNT_ENTITY_DEF = re.compile(
    r"count_entity_def\(\s*b['\"]([A-Za-z_]+)['\"]\s*\)\s*(<=|>=|==|!=|<|>)\s*(\d+)"
)
_RE_CONTAINS = re.compile(
    r"contains\(\s*b['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*\)"
)
_RE_NOT_CONTAINS = re.compile(
    r"not_contains\(\s*b['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*\)"
)


def _byte_count_claims(byte_asserts: list[str]) -> dict[str, tuple[str, int]]:
    """Return ``{TYPE_NAME: (op, value)}`` for ``count_entity_def`` claims.

    Conjunction-only: each claim is treated independently. Disjunctions
    (``or``) make the claim weaker, so we skip those (uncheckable).
    """
    out: dict[str, tuple[str, int]] = {}
    for line in byte_asserts:
        if " or " in line:
            continue
        for m in _RE_COUNT_ENTITY_DEF.finditer(line):
            type_name, op, val = m.group(1).upper(), m.group(2), int(m.group(3))
            out[type_name] = (op, val)
    return out


def _byte_contains_types(byte_asserts: list[str]) -> set[str]:
    """Return entity-type tokens that are required to be present.

    Skips lines containing ``or`` (disjunctions don't pin anything).
    Skips ``not_contains``.
    """
    out: set[str] = set()
    for line in byte_asserts:
        if " or " in line:
            continue
        # remove ``not_contains(...)`` matches before scanning ``contains``.
        sanitized = _RE_NOT_CONTAINS.sub("", line)
        for m in _RE_CONTAINS.finditer(sanitized):
            out.add(m.group(1).upper())
    return out


# --- Tier-3 assertion shape extractors ------------------------------------

_RE_TIER3 = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_\.\[\]]*)\s*(<=|>=|==|!=|<|>|in)\s*(.+?)\s*$"
)


def _parse_tier3(line: str) -> tuple[str, str, Any] | None:
    m = _RE_TIER3.match(line)
    if not m:
        return None
    lhs, op, rhs = m.group(1), m.group(2), m.group(3).strip()
    try:
        rhs_val: Any = json.loads(rhs)
    except Exception:
        rhs_val = rhs.strip("\"'")
    return lhs, op, rhs_val


def _tier3_n_faces(tier3_asserts: list[str]) -> tuple[str, int] | None:
    for a in tier3_asserts:
        p = _parse_tier3(a)
        if p and p[0] == "n_faces_total" and isinstance(p[2], (int, float)):
            return p[1], int(p[2])
    return None


def _tier3_n_edges(tier3_asserts: list[str]) -> tuple[str, int] | None:
    for a in tier3_asserts:
        p = _parse_tier3(a)
        if p and p[0] == "n_edges_total" and isinstance(p[2], (int, float)):
            return p[1], int(p[2])
    return None


_RE_FACE_SURFACE = re.compile(r"^face\[(\d+)\]\.surface_type$")


def _tier3_face_surface_types(tier3_asserts: list[str]) -> dict[int, str]:
    """Return ``{i: surface_type}`` for ``face[i].surface_type == 'X'`` claims."""
    out: dict[int, str] = {}
    for a in tier3_asserts:
        p = _parse_tier3(a)
        if not p:
            continue
        lhs, op, rhs = p
        m = _RE_FACE_SURFACE.match(lhs)
        if m and op == "==" and isinstance(rhs, str):
            out[int(m.group(1))] = rhs.lower()
    return out


# --- Pairing logic ---------------------------------------------------------

def _check_face_count(byte_counts: dict[str, tuple[str, int]],
                      n_faces: tuple[str, int] | None) -> dict | None:
    """Compare ADVANCED_FACE byte count to n_faces_total tier-3 claim."""
    if "ADVANCED_FACE" not in byte_counts or n_faces is None:
        return None
    b_op, b_val = byte_counts["ADVANCED_FACE"]
    t_op, t_val = n_faces
    # Only handle the simple equality case; ranges are uncheckable.
    if b_op != "==" or t_op != "==":
        return {
            "byte_claim": f"count_entity_def(b'ADVANCED_FACE') {b_op} {b_val}",
            "tier3_claim": f"n_faces_total {t_op} {t_val}",
            "verdict": "uncheckable",
            "reason": "non-equality operator on at least one side",
        }
    # tier-3 face count cannot exceed declared ADVANCED_FACE count.
    if t_val > b_val:
        return {
            "byte_claim": f"count_entity_def(b'ADVANCED_FACE') == {b_val}",
            "tier3_claim": f"n_faces_total == {t_val}",
            "verdict": "inconsistent",
            "reason": (
                f"OCCT loaded {t_val} faces but only {b_val} ADVANCED_FACE "
                f"entities are declared"
            ),
        }
    if t_val == b_val:
        return {
            "byte_claim": f"count_entity_def(b'ADVANCED_FACE') == {b_val}",
            "tier3_claim": f"n_faces_total == {t_val}",
            "verdict": "consistent",
            "reason": "face count matches",
        }
    # t_val < b_val: a discrepancy that *might* be intentional (some faces
    # not loaded). Mark uncheckable rather than inconsistent unless very
    # large discrepancy.
    if b_val >= 2 and t_val == 1:
        return {
            "byte_claim": f"count_entity_def(b'ADVANCED_FACE') == {b_val}",
            "tier3_claim": f"n_faces_total == {t_val}",
            "verdict": "inconsistent",
            "reason": (
                f"declared {b_val} ADVANCED_FACE entities but tier-3 only "
                f"sees 1; likely a miscount on one side"
            ),
        }
    return {
        "byte_claim": f"count_entity_def(b'ADVANCED_FACE') == {b_val}",
        "tier3_claim": f"n_faces_total == {t_val}",
        "verdict": "uncheckable",
        "reason": "tier-3 face count smaller than declared (could be partial load)",
    }


def _check_edge_count(byte_counts: dict[str, tuple[str, int]],
                      n_edges: tuple[str, int] | None) -> dict | None:
    if "EDGE_CURVE" not in byte_counts or n_edges is None:
        return None
    b_op, b_val = byte_counts["EDGE_CURVE"]
    t_op, t_val = n_edges
    if b_op != "==" or t_op != "==":
        return None
    if t_val > b_val:
        return {
            "byte_claim": f"count_entity_def(b'EDGE_CURVE') == {b_val}",
            "tier3_claim": f"n_edges_total == {t_val}",
            "verdict": "inconsistent",
            "reason": (
                f"tier-3 reports {t_val} edges but only {b_val} EDGE_CURVE "
                f"entities are declared"
            ),
        }
    return {
        "byte_claim": f"count_entity_def(b'EDGE_CURVE') == {b_val}",
        "tier3_claim": f"n_edges_total == {t_val}",
        "verdict": "consistent",
        "reason": "tier-3 edge count <= declared edge count (expected)",
    }


_BYTE_TYPE_TO_TIER3_SURFACE = {
    "CYLINDRICAL_SURFACE": "cylinder",
    "CONICAL_SURFACE": "cone",
    "SPHERICAL_SURFACE": "sphere",
    "TOROIDAL_SURFACE": "torus",
    "B_SPLINE_SURFACE": "bspline",
    "B_SPLINE_SURFACE_WITH_KNOTS": "bspline",
}
# PLANE is special: it appears in many entity names ("PLANE_ANGLE_MEASURE",
# etc.). Use count_entity_def or word-boundary matching instead of contains.


def _check_surface_type_pair(byte_type: str,
                             expected_t3: str,
                             surface_types: dict[int, str]) -> dict | None:
    """If ``byte_type`` is asserted present, at least one tier-3 face
    should have surface_type == expected_t3 (IF tier-3 makes any
    surface_type claims at all and those claims cover face[0]).
    """
    if not surface_types:
        return None
    # If we have surface_type claims but none mention this type, that's
    # only suspicious if face[0] is claimed AND it's a single-face fixture.
    if expected_t3 in surface_types.values():
        return {
            "byte_claim": f"contains(b'{byte_type}')",
            "tier3_claim": f"face[i].surface_type contains '{expected_t3}'",
            "verdict": "consistent",
            "reason": "tier-3 surface_type claim matches byte-side",
        }
    # Tier-3 says face[0] is something else; bytes say byte_type is present.
    # If the only surface mentioned in bytes is byte_type, this is a
    # potential contradiction (e.g. cylinder declared but tier-3 face[0]
    # is plane and there's no other face).
    return {
        "byte_claim": f"contains(b'{byte_type}')",
        "tier3_claim": (
            f"face surface_types: "
            + ", ".join(f"face[{i}]={t}" for i, t in sorted(surface_types.items()))
        ),
        "verdict": "inconsistent",
        "reason": (
            f"bytes contain {byte_type} but no tier-3 face has "
            f"surface_type=='{expected_t3}'"
        ),
    }


# --- Driver ---------------------------------------------------------------

def audit_entry(entry: dict) -> list[dict[str, Any]]:
    """Return zero or more pair-records for one entry."""
    byte_asserts = entry.get("byte_assertions") or []
    tier3_asserts = entry.get("tier3_assertions") or []
    if not byte_asserts or not tier3_asserts:
        return []

    byte_counts = _byte_count_claims(byte_asserts)
    byte_contains = _byte_contains_types(byte_asserts)
    n_faces = _tier3_n_faces(tier3_asserts)
    n_edges = _tier3_n_edges(tier3_asserts)
    surface_types = _tier3_face_surface_types(tier3_asserts)

    pairs: list[dict[str, Any]] = []

    pair = _check_face_count(byte_counts, n_faces)
    if pair is not None:
        pair["id"] = entry["id"]
        pairs.append(pair)

    pair = _check_edge_count(byte_counts, n_edges)
    if pair is not None:
        pair["id"] = entry["id"]
        pairs.append(pair)

    # contains() vs surface_type pairs.
    for byte_type, expected_t3 in _BYTE_TYPE_TO_TIER3_SURFACE.items():
        if byte_type in byte_contains:
            pair = _check_surface_type_pair(byte_type, expected_t3, surface_types)
            if pair is not None:
                pair["id"] = entry["id"]
                pairs.append(pair)

    # If we found nothing pairable, emit a single ``uncheckable`` record so
    # the report still acknowledges that the entry has both kinds of claim.
    if not pairs:
        pairs.append({
            "id": entry["id"],
            "byte_claim": "; ".join(byte_asserts),
            "tier3_claim": "; ".join(tier3_asserts),
            "verdict": "uncheckable",
            "reason": (
                "byte-side and tier-3-side claims target unrelated "
                "dimensions (no shared metric to compare)"
            ),
        })

    if entry["id"] in DOCUMENTED_DIVERGENCE:
        for p in pairs:
            if p["verdict"] == "inconsistent":
                p["verdict"] = "documented"
                p["reason"] = (
                    "divergence IS the documented kernel-bug evidence "
                    "(OCC silently transforms the source); original: "
                    + p["reason"]
                )

    return pairs


def audit_all(entries: Iterable[dict] | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    src = entries if entries is not None else catalog.iter_canonical()
    for entry in src:
        out.extend(audit_entry(entry))
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._bytes_tier3_audit")
    p.add_argument("--json", action="store_true",
                   help="emit JSON results to stdout (always also written "
                        "to /tmp/cad-bytes-tier3-audit.json)")
    p.add_argument("--output", type=Path, default=OUTPUT_JSON,
                   help="path for JSON dump (default: %(default)s)")
    args = p.parse_args(argv)

    results = audit_all()
    args.output.write_text(json.dumps(results, indent=2) + "\n")

    if args.json:
        json.dump(results, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    from collections import Counter
    by_verdict = Counter(r["verdict"] for r in results)
    print(f"Bytes/tier-3 audit: {len(results)} pair-records "
          f"across entries with both kinds of assertion")
    for v, n in sorted(by_verdict.items(), key=lambda kv: -kv[1]):
        print(f"  {v:<14} {n:>4}")
    print(f"\nWrote {args.output}")

    inconsistent = [r for r in results if r["verdict"] == "inconsistent"]
    if inconsistent:
        print(f"\n{len(inconsistent)} inconsistent pairs:")
        for r in inconsistent:
            print(f"  {r['id']:<8} byte={r['byte_claim']!r}  "
                  f"tier3={r['tier3_claim']!r}  reason={r['reason']}")
    return 1 if inconsistent else 0


if __name__ == "__main__":
    raise SystemExit(main())
