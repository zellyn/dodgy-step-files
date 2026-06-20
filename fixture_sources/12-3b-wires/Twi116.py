"""Twi116 — ShapeFix_Wire.FixConnected vertex-sharing mismatch.

Catalog claim: Wire with edges that should connect via a shared vertex but use
different VERTEX_POINT entities at identical coordinates (10.0, 0.0, 0.0): v2a
in edge1→edge2 transition, v2b in edge3 start. FixConnected should unify these
duplicate vertices into a single reference.

Reproducer recipe: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with three edges:
  - e1: LINE from (0,0,0)→(10,0,0), end vertex v2a=(10,0,0)
  - e2: LINE from (10,0,0)→(10,10,0), start vertex v2a=(10,0,0), end v3=(10,10,0)
  - e3: LINE from (10,0,0)→(0,0,0), start vertex v2b=(10,0,0) — DIFFERENT entity
         same coordinates as v2a, so FixConnected should unify them
The transition between e2 end and e3 start also breaks wire connectivity.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi116",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges; "
        "e1: LINE (0,0,0)→(10,0,0) end at vertex v2a=(10,0,0); "
        "e2: LINE (10,0,0)→(10,10,0) start at v2a=(10,0,0) end at v3=(10,10,0); "
        "e3: LINE (10,0,0)→(0,0,0) start at v2b=(10,0,0) — DIFFERENT VERTEX_POINT "
        "entity but same coordinates as v2a IS defect; "
        "FixConnected should unify v2a and v2b into single shared vertex reference; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Key coordinate: the duplicate vertex site ─────────────────────────────────
DUP_COORD = (10.0, 0.0, 0.0)   # Both v2a and v2b share this 3D position

P_start = (0.0,  0.0,  0.0)
P_v2a   = DUP_COORD             # v2a: e1 end / e2 start
P_v3    = (10.0, 10.0, 0.0)    # e2 end
P_v2b   = DUP_COORD             # v2b: e3 start (same coords, different entity!)

# Two separate VERTEX_POINT entities at identical 3D coordinates
v_start = f.vertex_point(f.cartesian_point(P_start))
v2a     = f.vertex_point(f.cartesian_point(P_v2a))   # used by e1 end, e2 start
v3      = f.vertex_point(f.cartesian_point(P_v3))
v2b     = f.vertex_point(f.cartesian_point(P_v2b))   # used by e3 start — IS duplicate


def _line(src, dst):
    dx, dy, dz = dst[0]-src[0], dst[1]-src[1], dst[2]-src[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    return f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag),
    )


# e1: (0,0,0) → (10,0,0), ends at v2a
e1  = f.edge_curve(v_start, v2a, _line(P_start, P_v2a))
oe1 = f.oriented_edge(e1, True)

# e2: (10,0,0) → (10,10,0), starts at v2a (same entity as e1 end — correct sharing)
e2  = f.edge_curve(v2a, v3, _line(P_v2a, P_v3))
oe2 = f.oriented_edge(e2, True)

# e3: (10,0,0) → (0,0,0), starts at v2b — SAME COORDS as v2a but DIFFERENT entity
e3  = f.edge_curve(v2b, v_start, _line(P_v2b, P_start))
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP: v2a/v2b mismatch means e2 and e3 don't share a vertex ─────────
loop = f.edge_loop([oe1, oe2, oe3])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi116.stp")
