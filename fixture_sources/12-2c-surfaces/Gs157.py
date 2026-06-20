"""Gs157 — GetSurfaceType misidentification via precision.

Catalog claim: ShapeAnalysis_Geom::GetSurfaceType uses fixed classification
thresholds independent of model scale. CONICAL_SURFACE near-cylindrical cases
(very small half-angle) are misclassified as cylindrical, triggering wrong
healing path.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CONICAL_SURFACE (semi-angle 0.001 rad, near-cylindrical) IS the
    ADVANCED_FACE.face_geometry; face boundary edge pcurves referencing the
    near-cylindrical cone IS the mechanism wired into face topology;
    GetSurfaceType fixed-threshold misclassification of near-cylindrical
    CONICAL_SURFACE IS the defect.
  - Byte assertions: contains(b'CONICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CONICAL_SURFACE (half-angle 0.001 rad) IS
    ADVANCED_FACE.face_geometry; face boundary edge pcurves on near-cylindrical
    cone IS the mechanism wired into face topology; GetSurfaceType
    precision-threshold misclassification IS the defect.
  - shape_null driver: wrong surface type returned; wrong healing path invoked;
    strict kernels reject inconsistent result; empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs157",
    defect=(
        "CONICAL_SURFACE (half-angle 0.001 rad, near-cylindrical) IS "
        "ADVANCED_FACE.face_geometry; face boundary edge pcurves on "
        "near-cylindrical cone IS the mechanism wired into face topology; "
        "GetSurfaceType fixed-threshold misclassification of near-cylindrical "
        "CONICAL_SURFACE IS the defect; shape_null"
    ),
)

# ── CONICAL_SURFACE: very small semi-angle (near-cylindrical) ─────────────────
# Byte assertion: contains(b'CONICAL_SURFACE')
# half-angle = 0.001 rad ≈ 0.057°; radius at apex = 1.0.
# GetSurfaceType uses a fixed angular tolerance; 0.001 rad falls below the
# threshold → misclassified as CYLINDRICAL, wrong healing path triggered.
HALF_ANGLE = 0.001   # radians — near-cylindrical, triggers misclassification
RADIUS_BASE = 1.0
V_TOP = 1.0          # cone height used for face patch

cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs157_cone_ax',#{cone_orig.eid},#{cone_zdir.eid},#{cone_xdir.eid})"
)
# CONICAL_SURFACE(name, placement, radius, half-angle)
cone = f._emit_raw(
    f"CONICAL_SURFACE('gs157_cone',#{cone_ax.eid},{RADIUS_BASE},{HALF_ANGLE})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary on the near-cylindrical cone ───────────────────────────────
# Cone parametrization: x = (r + v*tan(a))*cos(u), y = (r + v*tan(a))*sin(u),
# z = v, where r = RADIUS_BASE, a = HALF_ANGLE.
# u in [0, pi/2], v in [0, V_TOP].
U_RIGHT = math.pi / 2.0
tan_a = math.tan(HALF_ANGLE)

def cone_pt(u, v):
    r = RADIUS_BASE + v * tan_a
    return (r * math.cos(u), r * math.sin(u), v)

A3 = cone_pt(0.0, 0.0)
B3 = cone_pt(U_RIGHT, 0.0)
C3 = cone_pt(U_RIGHT, V_TOP)
D3 = cone_pt(0.0, V_TOP)

p_A = f.cartesian_point(A3)
p_B = f.cartesian_point(B3)
p_C = f.cartesian_point(C3)
p_D = f.cartesian_point(D3)

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
    pc  = f._emit_raw(f"PCURVE('pc',#{cone.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

arc_len_bot = RADIUS_BASE * U_RIGHT
arc_len_top = (RADIUS_BASE + V_TOP * tan_a) * U_RIGHT
slant_len   = math.sqrt(V_TOP**2 + (V_TOP * tan_a)**2)

# Bottom: A→B, u=0→pi/2 at v=0
e0 = mk_edge_line(v_A, v_B,
                  A3, (B3[0]-A3[0], B3[1]-A3[1], 0.0), arc_len_bot,
                  (0.0, 0.0), (1.0, 0.0), U_RIGHT)
# Right: B→C, v=0→V_TOP at u=pi/2
e1 = mk_edge_line(v_B, v_C,
                  B3, (C3[0]-B3[0], C3[1]-B3[1], 1.0), slant_len,
                  (U_RIGHT, 0.0), (0.0, 1.0), V_TOP)
# Top: C→D, u=pi/2→0 at v=V_TOP
e2 = mk_edge_line(v_C, v_D,
                  C3, (D3[0]-C3[0], D3[1]-C3[1], 0.0), arc_len_top,
                  (U_RIGHT, V_TOP), (-1.0, 0.0), U_RIGHT)
# Left: D→A, v=V_TOP→0 at u=0
e3 = mk_edge_line(v_D, v_A,
                  D3, (A3[0]-D3[0], A3[1]-D3[1], -1.0), slant_len,
                  (0.0, V_TOP), (0.0, -1.0), V_TOP)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CONICAL_SURFACE (near-cylindrical, half-angle 0.001 rad) IS the face_geometry;
# face boundary edge pcurves on the near-cylindrical cone IS the mechanism wired
# into face topology — exercises GetSurfaceType fixed-threshold misclassification.
face  = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
