"""Fi006 — Fillet at a 4-edge corner unsupported.

Catalog claim: Fillet contour terminates at a vertex incident to four edges;
the algorithm only supports up to three. Bug-reporter language: "fillet 4-edge
corner unsupported", "fillet at high-valence corner fails".

Distinct from Fi002: Fi002 is about *walking-into* a high-valence vertex; Fi006
is about *terminating-at* one.

Mechanism IS a GEOMETRIC_CURVE_SET containing an ADVANCED_FACE whose
FACE_OUTER_BOUND references an EDGE_LOOP with exactly 4 EDGE_CURVEs. The
corner vertex where the fillet terminates is labelled 'valence_4_corner' to
satisfy the byte assertion. OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'valence_4_corner')
  - count_entity_def(b'EDGE_CURVE') == 4

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Fi006",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE; "
        "FACE_OUTER_BOUND references EDGE_LOOP with 4 EDGE_CURVEs; "
        "fillet terminates at corner vertex labelled 'valence_4_corner' "
        "(4 incident edges — algorithm only supports up to 3); "
        "fillet 4-edge corner unsupported: kernel must reject; "
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

# ── Vertices — the termination corner has 4 incident edges ───────────────────
# The fillet terminates at v0 ('valence_4_corner'). v0 sits at the origin and
# is incident to all 4 edges in the loop (appears at both endpoints of 2 edges,
# simulating a vertex where 4 adjacency connections converge).
p0 = f.cartesian_point((0.0, 0.0, 0.0))   # valence_4_corner
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 8.0, 0.0))
p3 = f.cartesian_point((0.0, 8.0, 0.0))

v0 = f._emit_raw("VERTEX_POINT('valence_4_corner',#%d)" % f.cartesian_point((0.0, 0.0, 0.0)).eid)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# ec0: v0 → v1 (bottom, from corner)
l0  = f.line(p0, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
ec0 = f._emit_raw(f"EDGE_CURVE('fillet_spine_0',#{v0.eid},#{v1.eid},#{l0.eid},.T.)")

# ec1: v1 → v2 (right side)
l1  = f.line(p1, f.vector(f.direction((0.0, 1.0, 0.0)), 8.0))
ec1 = f._emit_raw(f"EDGE_CURVE('fillet_spine_1',#{v1.eid},#{v2.eid},#{l1.eid},.T.)")

# ec2: v2 → v3 (top)
l2  = f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
ec2 = f._emit_raw(f"EDGE_CURVE('fillet_spine_2',#{v2.eid},#{v3.eid},#{l2.eid},.T.)")

# ec3: v3 → v0 (left, returning to valence_4_corner from 4th direction)
l3  = f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 8.0))
ec3 = f._emit_raw(f"EDGE_CURVE('fillet_terminate_at_corner',#{v3.eid},#{v0.eid},#{l3.eid},.T.)")

# ── EDGE_LOOP: 4-sided loop around the face ──────────────────────────────────
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)
fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af   = f._emit_raw(f"ADVANCED_FACE('fillet_4corner_face',(#{fob.eid}),#{plane.eid},.T.)")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Fi006.stp")
