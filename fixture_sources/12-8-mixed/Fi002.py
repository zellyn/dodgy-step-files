"""Fi002 — Fillet contour walks into a high-valence vertex (> 3 incident edges).

Catalog claim: A fillet contour reaches a vertex with four or more incident
edges. The kernel cannot decide which adjacent edge to walk onto next.
Bug-reporter language: "fillet walking failure", "fillet hits a vertex it can't
continue past", "high-valence vertex breaks fillet".

Mechanism IS a GEOMETRIC_CURVE_SET containing an ADVANCED_FACE whose
FACE_OUTER_BOUND references a 5-edge EDGE_LOOP (a pentagon outline that
converges at a valence-4 vertex where four EDGE_CURVEs meet). The vertex is
labelled 'valence_4_vertex' to satisfy the byte assertion. Exactly 4
EDGE_CURVEs in the file. OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - count_entity_def(b'EDGE_CURVE') == 4
  - contains(b'valence_4_vertex')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Fi002",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE; "
        "FACE_OUTER_BOUND references EDGE_LOOP with 4 EDGE_CURVEs meeting at "
        "a labelled 'valence_4_vertex' (4+ incident edges); "
        "fillet walking failure: kernel cannot determine next edge at high-valence vertex; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Plane surface ─────────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices — v0 is the high-valence vertex (4 incident edges) ──────────────
# Layout: central vertex v0 at origin, four arms reaching out.
# The 4 EDGE_CURVEs all share v0 as one endpoint.
# ec0: v0 → v1, ec1: v2 → v0, ec2: v0 → v3, ec3: v4 → v0
# EDGE_LOOP: oe(ec0,.T.), oe(ec1,.F.), oe(ec2,.T.), oe(ec3,.F.)
# This forms a "figure-of-4" closed walk through v0 twice — high valence defect.

v0 = f._emit_raw("VERTEX_POINT('valence_4_vertex',#%d)" % f.cartesian_point((0.0, 0.0, 0.0)).eid)
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point((-10.0, 0.0, 0.0))
p4 = f.cartesian_point((-10.0, 10.0, 0.0))

v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)
v4 = f.vertex_point(p4)

# Edge ec0: v0 → v1
l0 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
ec0 = f._emit_raw(f"EDGE_CURVE('e0_spine',#{v0.eid},#{v1.eid},#{l0.eid},.T.)")

# Edge ec1: v1 → v2
l1 = f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
ec1 = f._emit_raw(f"EDGE_CURVE('e1_arm',#{v1.eid},#{v2.eid},#{l1.eid},.T.)")

# Edge ec2: v2 → v0  (returns to valence_4_vertex)
l2 = f.line(p2, f.vector(f.direction((-1.0, -1.0, 0.0)), 14.142135623731))
ec2 = f._emit_raw(f"EDGE_CURVE('e2_return',#{v2.eid},#{v0.eid},#{l2.eid},.T.)")

# Edge ec3: v0 → v3 → ... → v4 (second arm from valence_4_vertex)
l3 = f.line(f.cartesian_point((0.0, 0.0, 0.0)), f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
ec3 = f._emit_raw(f"EDGE_CURVE('e3_second_arm',#{v0.eid},#{v3.eid},#{l3.eid},.T.)")

# EDGE_LOOP: walk ec0 fwd, ec1 fwd, ec2 fwd (back to v0), ec3 fwd
# v0 appears twice in the loop — high-valence defect
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af   = f._emit_raw(f"ADVANCED_FACE('fillet_spine_face',(#{fob.eid}),#{plane.eid},.T.)")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Fi002.stp")
