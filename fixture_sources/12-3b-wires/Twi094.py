"""Twi094 — Wire endpoint first/last edge skipped during wire build.

Catalog claim: An open (non-closed) wire's first or last edge is silently dropped
by a wire-build step that was written assuming the wire is closed (so the "first"
edge's predecessor is the "last" edge). When the wire is open, that wraparound
logic skips the first or last edge. Typical fixture: an EDGE_LOOP listing four
edges over vertices V13->V15->V17->V19->V21, with an additional VERTEX_POINT V11
at the origin defined but never referenced by any ORIENTED_EDGE; the missing
first edge leaves an orphan vertex and an open wire.

Reproducer recipe: A five-vertex open polyline wire where one endpoint
VERTEX_POINT is defined but no ORIENTED_EDGE references it (orphan vertex),
yielding a four-edge wire missing the first or last edge. The EDGE_LOOP is
labelled 'four_edges_first_dropped'. The orphan vertex is labelled
'V0_dropped_endpoint'. There are exactly 4 EDGE_CURVEs.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP. OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'V0_dropped_endpoint')
  - contains(b'four_edges_first_dropped')
  - count_entity_def(b'EDGE_CURVE') == 4

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi094",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'four_edges_first_dropped'; "
        "exactly FOUR EDGE_CURVEs forming an open polyline chain; "
        "five vertices: V13(0,1,0)→V15(1,1,0)→V17(2,1,0)→V19(3,1,0)→V21(4,1,0); "
        "orphan VERTEX_POINT 'V0_dropped_endpoint' at (0,0,0) defined but never "
        "referenced by any ORIENTED_EDGE — represents the dropped first-edge endpoint; "
        "wire-builder wraparound logic (for closed wires) skips the first edge "
        "when the wire is open — V0 was the lost start vertex; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; V0 is orphan"
    ),
)

# ── Orphan VERTEX_POINT: defined but never referenced by any ORIENTED_EDGE ───
# Byte assertion: contains(b'V0_dropped_endpoint') — name on orphan vertex
v_orphan = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)), name="V0_dropped_endpoint")

# ── Chain vertices V13→V15→V17→V19→V21 along Y=1 ────────────────────────────
v13 = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))
v15 = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))
v17 = f.vertex_point(f.cartesian_point((2.0, 1.0, 0.0)))
v19 = f.vertex_point(f.cartesian_point((3.0, 1.0, 0.0)))
v21 = f.vertex_point(f.cartesian_point((4.0, 1.0, 0.0)))

# ── Four EDGE_CURVEs: V13→V15, V15→V17, V17→V19, V19→V21 ────────────────────
e1 = f.edge_curve(v13, v15,
                  f.line(f.cartesian_point((0.0, 1.0, 0.0)),
                         f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
e2 = f.edge_curve(v15, v17,
                  f.line(f.cartesian_point((1.0, 1.0, 0.0)),
                         f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
e3 = f.edge_curve(v17, v19,
                  f.line(f.cartesian_point((2.0, 1.0, 0.0)),
                         f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
e4 = f.edge_curve(v19, v21,
                  f.line(f.cartesian_point((3.0, 1.0, 0.0)),
                         f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))

oe1 = f.oriented_edge(e1, True)
oe2 = f.oriented_edge(e2, True)
oe3 = f.oriented_edge(e3, True)
oe4 = f.oriented_edge(e4, True)

# ── EDGE_LOOP 'four_edges_first_dropped' — byte assertion ────────────────────
# Byte assertion: count_entity_def(b'EDGE_CURVE') == 4 — exactly four edges
loop = f._emit_raw(
    f"EDGE_LOOP('four_edges_first_dropped',"
    f"(#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi094.stp")
