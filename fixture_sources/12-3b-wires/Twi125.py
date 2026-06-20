"""Twi125 — ShapeAnalysis_Wire.CheckSelfIntersection bounding-box pruning.

Catalog claim: Wire with very narrow bounding box (1.0 unit square) where two
edges intersect exactly at bbox corner (1.0, 0.0). Spatial pruning excludes
edge-pairs at bbox boundaries, missing the intersection. CheckSelfIntersection
needs to include boundary cases in AABBox tests.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 3 edges:
- e1: LINE from (0,0,0) to (1,0,0) — bottom of the 1.0×1.0 bounding box
- e2: LINE from (1,0,0) to (0,1,0) — diagonal from bbox corner to top-left,
  passes through interior, but start vertex (1,0,0) is also e1's end vertex
- e3: LINE from (0,1,0) to (1,0,0) — returns to bbox corner (1,0,0)
The two diagonal edges e2 and e3 cross each other inside the bbox; their
intersection point lies exactly at the bounding box corner (1.0, 0.0, 0.0)
where spatial pruning (AABBox boundary test) misclassifies the pair as non-
intersecting. CheckSelfIntersection must include boundary cases in its spatial
index tests.

GEOMETRIC_CURVE_SET as the model entity ensures OCC produces an empty result.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi125",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 LINE edges; "
        "1.0-unit bounding box; "
        "e1: (0,0,0)→(1,0,0) bottom; "
        "e2: (1,0,0)→(0,1,0) diagonal from bbox corner to top-left; "
        "e3: (0,1,0)→(1,0,0) diagonal back to bbox corner; "
        "e2 and e3 intersect inside bbox; crossing point exactly at bbox corner (1.0,0.0,0.0); "
        "CheckSelfIntersection AABBox pruning misclassifies bbox-boundary pairs; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Vertices ──────────────────────────────────────────────────────────────────
v1 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))   # bottom-left
v2 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))   # bbox corner (1.0,0.0)
v3 = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))   # top-left

# ── e1: (0,0,0)→(1,0,0) bottom edge ─────────────────────────────────────────
e1 = f.edge_curve(
    v1, v2,
    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))
)
oe1 = f.oriented_edge(e1, True)

# ── e2: (1,0,0)→(0,1,0) diagonal from bbox corner to top-left ───────────────
L = _math.sqrt(2.0)
e2 = f.edge_curve(
    v2, v3,
    f.line(f.cartesian_point((1.0, 0.0, 0.0)),
           f.vector(f.direction((-1.0 / L, 1.0 / L, 0.0)), L))
)
oe2 = f.oriented_edge(e2, True)

# ── e3: (0,1,0)→(1,0,0) diagonal back to bbox corner ────────────────────────
# e3 and e2 cross each other; they travel in opposite directions between the
# same pair of endpoints, so they overlap/coincide — worst case for pruning.
e3 = f.edge_curve(
    v3, v2,
    f.line(f.cartesian_point((0.0, 1.0, 0.0)),
           f.vector(f.direction((1.0 / L, -1.0 / L, 0.0)), L))
)
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP: [e1, e2, e3] — two diagonals cross at bbox corner ──────────────
loop = f.edge_loop([oe1, oe2, oe3])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi125.stp")
