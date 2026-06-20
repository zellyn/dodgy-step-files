"""Twi089 — Two collinear edges meeting at a degree-2 vertex should be fused into one edge.

Catalog claim: Two edges with collinear geometry share a vertex of degree 2,
and that vertex is not topologically necessary (no other face uses it). The
expected post-condition: fuse the two edges into one, removing the spurious vertex.

Reproducer recipe: A wire of two LINE-edges (0,0,0)→(1,0,0) and (1,0,0)→(2,0,0)
joined at #V (1,0,0), where #V is not used by any other wire/face. The midpoint
vertex is labelled 'mid_unused'. The EDGE_LOOP is labelled 'over_split_chain'.
There are exactly 2 EDGE_CURVEs.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP. OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'over_split_chain')
  - contains(b'mid_unused')
  - count_entity_def(b'EDGE_CURVE') == 2

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi089",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'over_split_chain'; "
        "exactly TWO EDGE_CURVEs, both collinear LINE segments along X axis; "
        "e1: (0,0,0)→(1,0,0); e2: (1,0,0)→(2,0,0); "
        "shared VERTEX_POINT 'mid_unused' at (1,0,0) — degree-2 vertex not used by any other face; "
        "the midpoint vertex is topologically redundant: BRepLib FuseEdges should merge e1+e2; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── VERTEX_POINTs ────────────────────────────────────────────────────────────
v_start = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
# Byte assertion: contains(b'mid_unused') — name on the redundant midpoint vertex
v_mid   = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)), name="mid_unused")
v_end   = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))

# ── Edge e1: (0,0,0) → (1,0,0) ────────────────────────────────────────────────
e1 = f.edge_curve(
    v_start, v_mid,
    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))
)
oe1 = f.oriented_edge(e1, True)

# ── Edge e2: (1,0,0) → (2,0,0) — collinear continuation ─────────────────────
e2 = f.edge_curve(
    v_mid, v_end,
    f.line(f.cartesian_point((1.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))
)
oe2 = f.oriented_edge(e2, True)

# ── EDGE_LOOP 'over_split_chain' — byte assertion ────────────────────────────
# Byte assertion: count_entity_def(b'EDGE_CURVE') == 2 — exactly two edges
loop = f._emit_raw(f"EDGE_LOOP('over_split_chain',(#{oe1.eid},#{oe2.eid}))")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi089.stp")
