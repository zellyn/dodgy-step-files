"""Twi087 — Wire is non-manifold: a vertex is incident to >2 edges of the wire.

Catalog claim: A "wire" entity has a vertex shared by three or more edges,
branching the wire. The invariant — each interior vertex is shared by exactly
two edges — is violated. Bug-reporter language: "branching wire", "wire forks",
"non-manifold wire vertex".

Reproducer recipe: A wire built from three edges all sharing a common endpoint
vertex #V, forming a Y-shape rather than a path.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with label
'y_wire_branching'. Three LINE edges all share hub vertex vH=(0,0,0) as one
endpoint: e1(v1→vH), e2(vH→v2), e3(vH→v3). vH has degree 3 in the wire,
violating the manifold-wire invariant (each interior vertex must have exactly
2 incident edges). OCC's wire builder cannot close a branching wire.
GEOMETRIC_CURVE_SET as the model entity ensures OCC produces an empty result.

Byte assertions:
  - contains(b'y_wire_branching')
  - count_entity_def(b'EDGE_CURVE') == 3
  - count_entity_def(b'ORIENTED_EDGE') == 3

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi087",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'y_wire_branching'; "
        "3 LINE edges form a Y-shape: hub vertex vH=(0,0,0) is incident to all 3; "
        "e1 from v1=(1,1,0) to vH; e2 from vH to v2=(-1,1,0); e3 from vH to v3=(0,-1,0); "
        "vH degree-3 violates manifold-wire invariant (exactly 2 incident edges required); "
        "OCC wire builder cannot close a branching wire; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all 3 EDGE_CURVEs and 3 ORIENTED_EDGEs ARE wired into the EDGE_LOOP; "
        "never orphaned"
    ),
)

# ── Y-shape vertices: hub vH + three arms ────────────────────────────────────
vH = f.vertex_point(f.cartesian_point((0.0,  0.0, 0.0)))   # hub — degree-3
v1 = f.vertex_point(f.cartesian_point((1.0,  1.0, 0.0)))   # arm 1
v2 = f.vertex_point(f.cartesian_point((-1.0, 1.0, 0.0)))   # arm 2
v3 = f.vertex_point(f.cartesian_point((0.0, -1.0, 0.0)))   # arm 3

# Edge e1: v1(1,1,0) → vH(0,0,0)
L = _math.sqrt(2.0)
e1 = f.edge_curve(
    v1, vH,
    f.line(f.cartesian_point((1.0, 1.0, 0.0)),
           f.vector(f.direction((-1.0 / L, -1.0 / L, 0.0)), L))
)

# Edge e2: vH(0,0,0) → v2(-1,1,0)
e2 = f.edge_curve(
    vH, v2,
    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
           f.vector(f.direction((-1.0 / L, 1.0 / L, 0.0)), L))
)

# Edge e3: vH(0,0,0) → v3(0,-1,0)
e3 = f.edge_curve(
    vH, v3,
    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
           f.vector(f.direction((0.0, -1.0, 0.0)), 1.0))
)

oe1 = f.oriented_edge(e1, True)
oe2 = f.oriented_edge(e2, True)
oe3 = f.oriented_edge(e3, True)

# EDGE_LOOP with name 'y_wire_branching' satisfies the byte assertion.
loop = f._emit_raw(
    f"EDGE_LOOP('y_wire_branching',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi087.stp")
