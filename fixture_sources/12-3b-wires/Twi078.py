"""Twi078 — Wire-order analysis: reorder unordered edges (no reversal needed).

Catalog claim: Edges of a wire emitted in arbitrary order. The analyzer must
reconstruct head-to-tail order using 3D and 2D vertex matching with a starting
tolerance and report STATUS_DONE (reordered, no reversal needed).

Reproducer recipe: A wire whose four edges, when listed in order [3, 1, 4, 2],
form a valid square in head-to-tail traversal.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with label
'scrambled_3_1_4_2'. The EDGE_LOOP lists four LINE edges of a unit square in
permuted order [e3, e1, e4, e2]: e3 ends at v4, but the next declared edge e1
starts at v1 — head-to-tail vertex chain is broken. ShapeAnalysis_WireOrder
must reorder [3,1,4,2] back to [1,2,3,4] without reversal to recover closure.
OCC sees a GEOMETRIC_CURVE_SET (not a solid or surface model) and produces an
empty result.

Byte assertions:
  - contains(b'scrambled_3_1_4_2')
  - count_entity_def(b'EDGE_CURVE') == 4
  - count_entity_def(b'ORIENTED_EDGE') == 4

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi078",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'scrambled_3_1_4_2'; "
        "4 LINE edges of a unit square declared in permuted order [e3, e1, e4, e2]; "
        "head-to-tail vertex chain broken: e3 ends at v4=(0,1,0), "
        "next e1 starts at v1=(0,0,0) — gap; "
        "ShapeAnalysis_WireOrder::Perform must reorder [3,1,4,2]→[1,2,3,4] "
        "without reversal (STATUS_DONE, not STATUS_DONE2); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "all 4 EDGE_CURVEs and 4 ORIENTED_EDGEs ARE wired into the EDGE_LOOP; "
        "never orphaned"
    ),
)

# ── Four vertices of a unit square, labelled 1-4 ─────────────────────────────
v1 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))   # bottom-left
v2 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))   # bottom-right
v3 = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))   # top-right
v4 = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))   # top-left

# ── Four edges: e1 v1→v2, e2 v2→v3, e3 v3→v4, e4 v4→v1 ─────────────────────
# Natural order is [e1, e2, e3, e4]; scrambled order declared is [e3, e1, e4, e2].
e1 = f.edge_curve(
    v1, v2,
    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))
)
e2 = f.edge_curve(
    v2, v3,
    f.line(f.cartesian_point((1.0, 0.0, 0.0)),
           f.vector(f.direction((0.0, 1.0, 0.0)), 1.0))
)
e3 = f.edge_curve(
    v3, v4,
    f.line(f.cartesian_point((1.0, 1.0, 0.0)),
           f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0))
)
e4 = f.edge_curve(
    v4, v1,
    f.line(f.cartesian_point((0.0, 1.0, 0.0)),
           f.vector(f.direction((0.0, -1.0, 0.0)), 1.0))
)

# ── ORIENTED_EDGEs in scrambled order [3, 1, 4, 2] ───────────────────────────
oe3 = f.oriented_edge(e3, True)
oe1 = f.oriented_edge(e1, True)
oe4 = f.oriented_edge(e4, True)
oe2 = f.oriented_edge(e2, True)

# EDGE_LOOP with name 'scrambled_3_1_4_2' satisfies the byte assertion.
loop = f._emit_raw(
    f"EDGE_LOOP('scrambled_3_1_4_2',(#{oe3.eid},#{oe1.eid},#{oe4.eid},#{oe2.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi078.stp")
