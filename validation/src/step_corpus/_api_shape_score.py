"""Score catalog entries for OCCT-API-shaped phrasing.

The LGPL+searchability audit is one job: rephrase entries whose descriptions
read like OCCT documentation into bug-reporter language. This module scores
every entry by counting OCCT-API tokens (class names, method names, file
paths) that leak into title / description / expected_kernel_behavior /
notes (exactly the fields a bug reporter would search).

Tokens in `sources` and `reproducer` fields are intentionally NOT counted:
- `sources` is allowed (and required) to cite OCCT path:line as evidence
- `reproducer` legitimately uses Part-21 entity names like
  `MANIFOLD_SOLID_BREP`, which are STEP-spec vocabulary, not OCCT-internal

CLI
---

    # show the 30 worst offenders
    uv run python -m step_corpus._api_shape_score --top 30

    # dump the full ranking as JSON for an audit pass
    uv run python -m step_corpus._api_shape_score --json > /tmp/api-shape-ranking.json

The hits-list per entry tells the audit pass which exact tokens to rephrase.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

from step_corpus import catalog

# OCCT identifiers we care about. Hand-curated from the OCCT module
# manifest; expand as needed. Match style is a word-boundary scan: we want
# `ShapeFix_Shape` but NOT `shape` and NOT `fix`.
_OCCT_CLASS_PREFIXES = (
    "ShapeFix",
    "ShapeAnalysis",
    "ShapeUpgrade",
    "ShapeBuild",
    "ShapeExtend",
    "ShapeProcess",
    "ShapeConstruct",
    "STEPControl",
    "STEPCAFControl",
    "RWStep",
    "StepToTopoDS",
    "TopoDSToStep",
    "BRepCheck",
    "BRepLib",
    "BRepBuilderAPI",
    "BRepFilletAPI",
    "BRepOffsetAPI",
    "BRepBndLib",
    "BRepGProp",
    "BRepAdaptor",
    "BRepAlgoAPI",
    "BRepClass3d",
    "BRepExtrema",
    "BRepMesh",
    "BRepProj",
    "BRepTools",
    "BOPAlgo",
    "BOPTools",
    "GeomLib",
    "GeomAdaptor",
    "Geom2dAdaptor",
    "GCPnts",
    "BRepOffset_MakeOffset",
    "BRepFill",
    "BRepPrimAPI",
    "BRepSweep",
    "BRepGProp_Face",
    "TopExp",
    "TopoDS",
    "TopTools",
    "TopAbs",
    "Message_Messenger",
    "Message_Printer",
    "Standard_",
)

# Tokens that aren't class prefixes but are still OCCT-internal vocabulary
# leaking into descriptions. These are the most search-hostile because they
# look like English but are actually method-name fragments.
_OCCT_METHOD_TOKENS = frozenset(
    """
    FixAddPCurve FixSplitFace FixVertexPosition FixSmallAreaWire FixWireGap2d
    FixWireGap3d FixGap2d FixGap3d FixSelfIntersection FixSeam FixSameParameter
    FixDegenerated FixMissingSeam FixOrientation FixIntersectingWires
    FixShape FixWire FixFace FixShell FixEdgeProjection FixPCurves
    UnifySameDomain BuildCurve3d BuildPCurveForEdgeOnPlane UpdateEdgeTol
    UpdateTolerances UpdateInnerTolerances OrientClosedSolid ContinuityOfFaces
    EncodeRegularity EnsureNormalConsistency UpdateDeflection FuseEdges
    FindValidRange ExtendFace SplitClosedFaces SplitContinuity
    SplitPeriodicSurface ProjectCurveOnSurface CheckSameUV
    """.split()
)

# Build one combined regex for class-prefix matches.
_CLASS_RE = re.compile(
    r"\b(" + "|".join(re.escape(p) for p in _OCCT_CLASS_PREFIXES) + r")[A-Za-z_][A-Za-z0-9_]*\b"
)
_METHOD_RE = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in _OCCT_METHOD_TOKENS) + r")\b"
)
# OCCT path mentions like `src/ModelingAlgorithms/...`, only flagged if
# they appear in description / notes (sources field is allowed to cite).
_PATH_RE = re.compile(r"\bsrc/[A-Za-z0-9_/]+\.(?:cxx|hxx|cpp|h)\b")


# Fields scored. `sources` and `reproducer` are excluded by design (see
# module docstring).
_SCORED_FIELDS = ("title", "description", "expected_kernel_behavior", "notes")


def _scan(text: str) -> list[str]:
    if not text:
        return []
    hits: list[str] = []
    hits.extend(m.group(0) for m in _CLASS_RE.finditer(text))
    hits.extend(m.group(0) for m in _METHOD_RE.finditer(text))
    hits.extend(m.group(0) for m in _PATH_RE.finditer(text))
    return hits


def score_entry(entry: dict[str, Any]) -> tuple[int, dict[str, list[str]]]:
    """Return (total_hits, per_field_hits) for one entry."""
    per_field: dict[str, list[str]] = {}
    total = 0
    for field in _SCORED_FIELDS:
        text = entry.get(field) or ""
        if isinstance(text, list):
            text = " ".join(str(t) for t in text)
        hits = _scan(str(text))
        if hits:
            per_field[field] = hits
            total += len(hits)
    return total, per_field


def rank_catalog(path: str | None = None) -> list[dict[str, Any]]:
    """Return entries sorted descending by API-token hits.

    Each row carries: id, title, score, per-field hits dict.
    """
    rows = []
    for entry in catalog.iter_canonical(path):
        score, per_field = score_entry(entry)
        rows.append(
            {
                "id": entry["id"],
                "title": entry["title"],
                "section": entry["section"],
                "score": score,
                "hits": per_field,
            }
        )
    rows.sort(key=lambda r: (-r["score"], r["id"]))
    return rows


def _format_row(row: dict[str, Any]) -> str:
    title = row["title"]
    if len(title) > 70:
        title = title[:67] + "..."
    line = f"  {row['score']:>3} {row['id']:<8} [{row['section']}] {title}"
    if row["hits"]:
        sample = []
        for field, hits in row["hits"].items():
            sample.append(f"{field}:{','.join(sorted(set(hits))[:3])}")
        line += "\n        " + "  ".join(sample)
    return line


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._api_shape_score")
    p.add_argument("--top", type=int, default=20, help="show the N worst offenders")
    p.add_argument("--json", action="store_true", help="dump full ranking as JSON")
    p.add_argument("--threshold", type=int, default=1, help="minimum hits to include")
    args = p.parse_args(argv)

    rows = rank_catalog()
    if args.json:
        json.dump([r for r in rows if r["score"] >= args.threshold], sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    total = sum(1 for r in rows if r["score"] > 0)
    grand = sum(r["score"] for r in rows)
    print(
        f"OCCT-API-shape ranking: {total}/{len(rows)} entries hit; "
        f"{grand} total token-hits across catalog\n"
    )
    print(f"Top {args.top}:")
    for row in rows[: args.top]:
        if row["score"] < args.threshold:
            break
        print(_format_row(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
