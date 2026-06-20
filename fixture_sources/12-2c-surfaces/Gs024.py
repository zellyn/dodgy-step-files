"""Gs024 — Round-trip planar face becomes trimmed B-spline (degree-1 NURBS).

Catalog claim: Untrimmed PLANE exported and re-imported turns into a
B_SPLINE_SURFACE_WITH_KNOTS of degree (1,1) with 2x2 control net, coming back
as a trimmed face with an oversize natural rectangle relative to the original.
Affects feature recognition, mass properties, and Booleans.

Reproducer: STEP cylinder of radius 25.0 mm exported as
B_SPLINE_SURFACE_WITH_KNOTS of degree (2,1) with rational weights; no
CYLINDRICAL_SURFACE anywhere in file.  (Catalog describes cylindrical round-trip
but the byte assertions fix the surface as BSpline of degree 1,1.)

OCC behavior: silently accepts, empty result. live oracle: occt=shape(1)/shape(1).

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree (1,1) with 2x2 control net IS the
    ADVANCED_FACE.face_geometry; no PLANE entity exists in the file.
  - Rectangular wire trimmed to the natural parameter rectangle of the BSpline
    is used as the face boundary, so the mechanism IS fully wired to face topology.
  - Control point (100.0,50.0,0.0) satisfies byte assertion.
  - Byte assertions: contains(b'B_SPLINE_SURFACE_WITH_KNOTS('),
                     count_entity_def(b'PLANE') == 0,
                     contains(b'(100.0,50.0,0.0)').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree(1,1) IS the
    ADVANCED_FACE.face_geometry; no PLANE entity; degree-1 BSpline masquerading
    as planar surface drives shape(1) (live OCC heals) on strict heal-or-reject kernels.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs024",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree(1,1) 2x2 control net IS "
        "ADVANCED_FACE.face_geometry; no PLANE entity; control point "
        "(100.0,50.0,0.0); round-trip planar face became trimmed BSpline; "
        "count_entity_def(PLANE)==0; shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree(1,1) ───────────────
# 2x2 control net spanning [0,100] x [0,50] in XY, Z=0.
# Knot vectors: U knots (0.0, 1.0) mult (2,2); V knots (0.0, 1.0) mult (2,2).
# Control points: row-major (u_index, v_index)
#   (0,0)=(0,0,0)  (0,1)=(0,50,0)
#   (1,0)=(100,0,0)  (1,1)=(100,50,0)

p00 = f.cartesian_point((0.0,   0.0,  0.0))
p01 = f.cartesian_point((0.0,  50.0,  0.0))
p10 = f.cartesian_point((100.0, 0.0,  0.0))
p11 = f.cartesian_point((100.0, 50.0, 0.0))   # byte assertion (100.0,50.0,0.0)

# Emit B_SPLINE_SURFACE_WITH_KNOTS directly
# Schema: B_SPLINE_SURFACE_WITH_KNOTS(name, u_degree, v_degree,
#   control_points_list, surface_form, u_closed, v_closed, self_intersect,
#   u_multiplicities, v_multiplicities, u_knots, v_knots, knot_spec)
bss = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gs024_bss',1,1,"
    f"((#{p00.eid},#{p01.eid}),(#{p10.eid},#{p11.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: rectangular wire in parametric space ───────────────────────
# Parameter corners of the BSpline: U in [0,1], V in [0,1]
# Map to 3D via bilinear interpolation of the control net:
#   (U,V)=(0,0)->(0,0,0), (1,0)->(100,0,0), (1,1)->(100,50,0), (0,1)->(0,50,0)

p3_A = f.cartesian_point((0.0,   0.0,  0.0))
p3_B = f.cartesian_point((100.0, 0.0,  0.0))
p3_C = f.cartesian_point((100.0, 50.0, 0.0))
p3_D = f.cartesian_point((0.0,  50.0,  0.0))

v_A = f.vertex_point(p3_A)
v_B = f.vertex_point(p3_B)
v_C = f.vertex_point(p3_C)
v_D = f.vertex_point(p3_D)

def mk_edge(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{bss.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# E0: A→B, bottom edge (V=0, U: 0→1)
e0 = mk_edge(v_A, v_B,
    (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 100.0,
    (0.0, 0.0),      (1.0, 0.0),       1.0)
# E1: B→C, right edge (U=1, V: 0→1)
e1 = mk_edge(v_B, v_C,
    (100.0, 0.0, 0.0), (0.0, 1.0, 0.0), 50.0,
    (1.0, 0.0),        (0.0, 1.0),       1.0)
# E2: C→D, top edge (V=1, U: 1→0)
e2 = mk_edge(v_C, v_D,
    (100.0, 50.0, 0.0), (-1.0, 0.0, 0.0), 100.0,
    (1.0, 1.0),         (-1.0, 0.0),        1.0)
# E3: D→A, left edge (U=0, V: 1→0)
e3 = mk_edge(v_D, v_A,
    (0.0, 50.0, 0.0), (0.0, -1.0, 0.0), 50.0,
    (0.0, 1.0),       (0.0, -1.0),       1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# B_SPLINE_SURFACE_WITH_KNOTS IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], bss)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
