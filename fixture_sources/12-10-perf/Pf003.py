"""Pf003 — 50-second read on a 20 MB STEP: forward-reference DATA section
forces multi-pass resolution (single-threaded).

Catalog claim: every ADVANCED_FACE in DATA references forward to later
EDGE_LOOP / EDGE_CURVE / VERTEX_POINT entities, forcing the reader to
perform many forward-resolve passes over the entity table.

The fixture encodes this by emitting the topology entities
(ADVANCED_FACE, FACE_OUTER_BOUND, EDGE_LOOP) *before* their referenced
lower-level entities (EDGE_CURVE, VERTEX_POINT, CARTESIAN_POINT, LINE)
using _emit_raw with pre-reserved forward IDs — the same forward-reference
pattern that causes the O(N²) multi-pass resolution cost.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 1
Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf003",
    defect=(
        "forward-reference DATA section: ADVANCED_FACE/EDGE_LOOP topology "
        "emitted before EDGE_CURVE/VERTEX_POINT/CARTESIAN_POINT geometry; "
        "forces multi-pass resolver in single-threaded reader; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# ---- Forward-reference block ----
# Plan: emit the topology first, then geometry at the IDs they forward-reference.
# We emit N_FACES quad-faces.  Layout of IDs for each face:
#   topology block (3 + 4*1 + 4 = 11 IDs per face):
#     ADVANCED_FACE, FACE_OUTER_BOUND, EDGE_LOOP,
#     ORIENTED_EDGE×4, EDGE_CURVE×4
#   geometry block (12 IDs per face):
#     PLANE, AXIS2_PLACEMENT_3D, CARTESIAN_POINT×3 (origin+dir base), DIRECTION×2
#     CARTESIAN_POINT×4 (corners), VERTEX_POINT×4 — but we share PLANE per face.
#
# To keep the forward-ref structure clean and predictable, emit ONE face
# where topology comes first, geometry second.

base = f._next_id  # start of our forward-ref block

# IDs for topology (emitted first):
face_id  = base + 0
fob_id   = base + 1
loop_id  = base + 2
oe0_id   = base + 3
oe1_id   = base + 4
oe2_id   = base + 5
oe3_id   = base + 6
ec0_id   = base + 7
ec1_id   = base + 8
ec2_id   = base + 9
ec3_id   = base + 10
# IDs for geometry (emitted second — forward-referenced from topology above):
plane_id = base + 11
plc_id   = base + 12
orig_id  = base + 13
zdir_id  = base + 14
xdir_id  = base + 15
p0_id    = base + 16
p1_id    = base + 17
p2_id    = base + 18
p3_id    = base + 19
v0_id    = base + 20
v1_id    = base + 21
v2_id    = base + 22
v3_id    = base + 23
e0d_id   = base + 24; e0v_id = base + 25; e0l_id = base + 26
e1d_id   = base + 27; e1v_id = base + 28; e1l_id = base + 29
e2d_id   = base + 30; e2v_id = base + 31; e2l_id = base + 32
e3d_id   = base + 33; e3v_id = base + 34; e3l_id = base + 35

# ---- Emit topology block (forward-refs to geometry IDs above) ----
f._emit_raw(f"ADVANCED_FACE('',(#{fob_id}),#{plane_id},.T.)")         # face_id
f._emit_raw(f"FACE_OUTER_BOUND('',#{loop_id},.T.)")                   # fob_id
f._emit_raw(
    f"EDGE_LOOP('',(#{oe0_id},#{oe1_id},#{oe2_id},#{oe3_id}))"
)                                                                       # loop_id
f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0_id},.T.)")                   # oe0_id
f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1_id},.T.)")                   # oe1_id
f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2_id},.T.)")                   # oe2_id
f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3_id},.T.)")                   # oe3_id
# EDGE_CURVEs forward-ref VERTEX_POINTs and LINEs (both in geometry block)
f._emit_raw(f"EDGE_CURVE('',#{v0_id},#{v1_id},#{e0l_id},.T.)")        # ec0_id
f._emit_raw(f"EDGE_CURVE('',#{v1_id},#{v2_id},#{e1l_id},.T.)")        # ec1_id
f._emit_raw(f"EDGE_CURVE('',#{v2_id},#{v3_id},#{e2l_id},.T.)")        # ec2_id
f._emit_raw(f"EDGE_CURVE('',#{v3_id},#{v0_id},#{e3l_id},.T.)")        # ec3_id

# ---- Emit geometry block (back-filled, IDs referenced above) ----
f._emit_raw(f"PLANE('',#{plc_id})")                                    # plane_id
f._emit_raw(f"AXIS2_PLACEMENT_3D('',#{orig_id},#{zdir_id},#{xdir_id})")  # plc_id
f._emit_raw(f"CARTESIAN_POINT('',(0.,0.,0.))")                         # orig_id
f._emit_raw(f"DIRECTION('',(0.,0.,1.))")                               # zdir_id
f._emit_raw(f"DIRECTION('',(1.,0.,0.))")                               # xdir_id
f._emit_raw(f"CARTESIAN_POINT('',(0.,0.,0.))")                         # p0_id
f._emit_raw(f"CARTESIAN_POINT('',(1.,0.,0.))")                         # p1_id
f._emit_raw(f"CARTESIAN_POINT('',(1.,1.,0.))")                         # p2_id
f._emit_raw(f"CARTESIAN_POINT('',(0.,1.,0.))")                         # p3_id
f._emit_raw(f"VERTEX_POINT('',#{p0_id})")                              # v0_id
f._emit_raw(f"VERTEX_POINT('',#{p1_id})")                              # v1_id
f._emit_raw(f"VERTEX_POINT('',#{p2_id})")                              # v2_id
f._emit_raw(f"VERTEX_POINT('',#{p3_id})")                              # v3_id
f._emit_raw(f"DIRECTION('',(1.,0.,0.))")                               # e0d_id
f._emit_raw(f"VECTOR('',#{e0d_id},1.)")                                # e0v_id
f._emit_raw(f"LINE('',#{p0_id},#{e0v_id})")                            # e0l_id
f._emit_raw(f"DIRECTION('',(0.,1.,0.))")                               # e1d_id
f._emit_raw(f"VECTOR('',#{e1d_id},1.)")                                # e1v_id
f._emit_raw(f"LINE('',#{p1_id},#{e1v_id})")                            # e1l_id
f._emit_raw(f"DIRECTION('',(-1.,0.,0.))")                              # e2d_id
f._emit_raw(f"VECTOR('',#{e2d_id},1.)")                                # e2v_id
f._emit_raw(f"LINE('',#{p2_id},#{e2v_id})")                            # e2l_id
f._emit_raw(f"DIRECTION('',(0.,-1.,0.))")                              # e3d_id
f._emit_raw(f"VECTOR('',#{e3d_id},1.)")                                # e3v_id
f._emit_raw(f"LINE('',#{p3_id},#{e3v_id})")                            # e3l_id

assert f._next_id == base + 36, (
    f"ID layout mismatch: expected {base+36}, got {f._next_id}"
)
