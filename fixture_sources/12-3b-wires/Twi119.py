"""Twi119 — ShapeFix_Wire.FixSmall threshold-on-tolerance.

Catalog claim: Wire with "small" edge exactly at user-configured small-edge
threshold (1e-5). FixSmall uses non-strict comparison at one code site and strict
at another, causing inconsistent behavior. Floating-point equality test at
threshold boundary is undefined; edge may or may not be flagged for removal.

Reproducer recipe: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with three edges:
  - e1: LINE from (0,0,0) to (1,0,0) — normal edge, length 1.0
  - e2: LINE from (1,0,0) to (1,0,1e-5) — "small" edge exactly 1e-5 units long
  - e3: LINE from (1,0,1e-5) to (0,0,0) — closing edge (approximate)
The edge e2 has length exactly 1e-5, matching the FixSmall threshold exactly.
Due to FP equality inconsistency, the threshold check may or may not flag e2.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

SMALL_THRESHOLD = 1e-5  # exactly at FixSmall threshold — IS defect trigger

f = StepFile(
    catalog_id="Twi119",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges; "
        "e1: LINE (0,0,0)→(1,0,0) length 1.0 (normal); "
        "e2: LINE (1,0,0)→(1,0,1e-5) length 1e-5 exactly — at FixSmall threshold IS defect; "
        "e3: LINE (1,0,1e-5)→(0,0,0) closing edge; "
        "FixSmall non-strict vs strict comparison at threshold boundary "
        "causes inconsistent edge-removal behavior; "
        "FP equality test at 1e-5 boundary is undefined; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Vertices ───────────────────────────────────────────────────────────────────
P0 = (0.0, 0.0, 0.0)
P1 = (1.0, 0.0, 0.0)
P2 = (1.0, 0.0, SMALL_THRESHOLD)  # P2 is exactly 1e-5 above P1 in Z
P_back = (0.0, 0.0, 0.0)          # same as P0 — closing loop

v0 = f.vertex_point(f.cartesian_point(P0))
v1 = f.vertex_point(f.cartesian_point(P1))
v2 = f.vertex_point(f.cartesian_point(P2))
# v_back shares the same entity as v0 (wire closes to origin)


def _line(src, dst):
    dx, dy, dz = dst[0]-src[0], dst[1]-src[1], dst[2]-src[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    return f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag),
    )


# e1: normal edge, length 1.0
e1  = f.edge_curve(v0, v1, _line(P0, P1))
oe1 = f.oriented_edge(e1, True)

# e2: "small" edge exactly at threshold 1e-5 — IS defect
e2  = f.edge_curve(v1, v2, _line(P1, P2))
oe2 = f.oriented_edge(e2, True)

# e3: closing edge from P2 back to P0
e3  = f.edge_curve(v2, v0, _line(P2, P0))
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f.edge_loop([oe1, oe2, oe3])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi119.stp")
