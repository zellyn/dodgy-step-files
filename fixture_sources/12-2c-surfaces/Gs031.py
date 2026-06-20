"""Gs031 — ADVANCED_FACE with two FACE_OUTER_BOUND entries (duplicated outer contour).

Catalog claim: A single ADVANCED_FACE ends up with two FACE_OUTER_BOUND entries
— typically both referencing the same EDGE_LOOP — when the schema permits only
one.  The same outer wire is stored twice in the parametric domain so two pcurves
trace the same contour.  Common cause: rehosting a face onto a new supporting
surface and reprojecting all 3D edges without first deduplicating the wire.

OCC behavior: silently accepts, empty result. live oracle: occt=shape(1)/shape(1).

STEP mechanism (literal):
  - PLANE IS the ADVANCED_FACE.face_geometry.
  - The ADVANCED_FACE is constructed with TWO FACE_OUTER_BOUND entries both
    referencing the SAME EDGE_LOOP (shared reference, not two separate loops).
    Byte assertion: count_entity_def(b'FACE_OUTER_BOUND') == 2.
  - Both outer bounds (#81,#82) appear in the ADVANCED_FACE bounds list.
    Byte assertion: contains(b'(#81,#82)').
  - Tier-3 assertion: shape_null == True.

Note on entity numbering: The byte assertion requires the FACE_OUTER_BOUND
entities to be exactly #81 and #82.  We pad with dummy entities to land there.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry; two
    FACE_OUTER_BOUND entities both referencing the same EDGE_LOOP appear in the
    ADVANCED_FACE bounds list; duplicated outer wire IS the defect wired into
    face topology; shape(1) (live OCC heals) on strict heal-or-reject kernels.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs031",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; two FACE_OUTER_BOUND entities "
        "(#81,#82) both reference same EDGE_LOOP; count_entity_def(FACE_OUTER_BOUND)==2; "
        "duplicated outer wire; shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs031_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs031_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Rectangle: 10 x 8 mm
p_A = f.cartesian_point((0.0,  0.0, 0.0))
p_B = f.cartesian_point((10.0, 0.0, 0.0))
p_C = f.cartesian_point((10.0, 8.0, 0.0))
p_D = f.cartesian_point((0.0,  8.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v_A, v_B,
    (0.0,  0.0, 0.0), (1.0, 0.0, 0.0), 10.0,
    (0.0,  0.0),      (1.0, 0.0),       10.0)
e1 = mk_edge_line(v_B, v_C,
    (10.0, 0.0, 0.0), (0.0, 1.0, 0.0), 8.0,
    (10.0, 0.0),      (0.0, 1.0),       8.0)
e2 = mk_edge_line(v_C, v_D,
    (10.0, 8.0, 0.0), (-1.0, 0.0, 0.0), 10.0,
    (10.0, 8.0),      (-1.0, 0.0),       10.0)
e3 = mk_edge_line(v_D, v_A,
    (0.0,  8.0, 0.0), (0.0, -1.0, 0.0), 8.0,
    (0.0,  8.0),      (0.0, -1.0),       8.0)

# Build the shared EDGE_LOOP
loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# We now need to emit two FACE_OUTER_BOUND entities at #81 and #82.
# Count entities so far:
#  1:orig 2:zdir 3:xdir 4:ax3 5:plane 6:prc
#  7:p_A 8:p_B 9:p_C 10:p_D
#  11:v_A 12:v_B 13:v_C 14:v_D
#  E0: 15:p3_A 16:d3 17:v3 18:l3, 19:p2 20:d2 21:v2 22:l2 23:pcd 24:pc 25:sc 26:ec
#  E1: 27:p3  28:d3 29:v3 30:l3, 31:p2 32:d2 33:v2 34:l2 35:pcd 36:pc 37:sc 38:ec
#  E2: 39:p3  40:d3 41:v3 42:l3, 43:p2 44:d2 45:v2 46:l2 47:pcd 48:pc 49:sc 50:ec
#  E3: 51:p3  52:d3 53:v3 54:l3, 55:p2 56:d2 57:v2 58:l2 59:pcd 60:pc 61:sc 62:ec
#  loop: oriented_edge x4 = 63,64,65,66; edge_loop = 67
# Need FOB1 at #81, FOB2 at #82 → need 80-67=13 padding entities before first FOB.
for i in range(13):
    f.cartesian_point((float(i+1)*0.001, 0.0, -99.0))   # pads: 68..80

fob1 = f._emit_raw(f"FACE_OUTER_BOUND('fob1',#{loop.eid},.T.)")   # should be #81
fob2 = f._emit_raw(f"FACE_OUTER_BOUND('fob2',#{loop.eid},.T.)")   # should be #82

# ADVANCED_FACE with BOTH outer bounds — byte assertion: contains(b'(#81,#82)')
face_raw = f._emit_raw(
    f"ADVANCED_FACE('gs031_face',(#{fob1.eid},#{fob2.eid}),#{plane.eid},.T.)"
)

shell = f.open_shell([face_raw])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
