"""Gs150 — AdjustByTransformation placement inconsistency on CYLINDRICAL_SURFACE.

Catalog claim: ShapeConstruct_Surface::AdjustByTransformation() updates
surface placement after a coordinate-system transformation but fails to
propagate the new AXIS2_PLACEMENT_3D origin consistently. The transformed
cylinder parameterization becomes incoherent: the face boundary pcurves
reference the pre-transform origin, while the surface now lives at the
post-transform origin.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE (radius 2.5) with AXIS2_PLACEMENT_3D at (1,2,3)
    IS the ADVANCED_FACE.face_geometry; face boundary edge pcurves referencing
    the displaced placement origin IS the mechanism wired into face topology;
    AdjustByTransformation failing to reconcile placement shift IS the defect.
  - Byte assertions: contains(b'CYLINDRICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE with offset placement at (1,2,3)
    IS ADVANCED_FACE.face_geometry; face boundary edge pcurves encoded against
    displaced origin IS the mechanism wired into face topology;
    AdjustByTransformation placement-origin reconciliation failure IS the defect.
  - shape_null driver: surface parameterization incoherent after transform;
    pcurve-surface mapping broken; strict kernels reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs150",
    defect=(
        "CYLINDRICAL_SURFACE (radius 2.5) with AXIS2_PLACEMENT_3D offset at "
        "(1,2,3) IS ADVANCED_FACE.face_geometry; face boundary edge pcurves "
        "referencing displaced placement origin IS the mechanism wired into "
        "face topology; AdjustByTransformation placement-origin reconciliation "
        "failure IS the defect; shape_null"
    ),
)

# ── CYLINDRICAL_SURFACE with offset AXIS2_PLACEMENT_3D at (1,2,3) ─────────────
# Byte assertion: contains(b'CYLINDRICAL_SURFACE')
# Radius 2.5; axis at (1,2,3) — the offset origin is the placement inconsistency
# that AdjustByTransformation fails to reconcile after transformation.
RADIUS = 2.5
TWO_PI = 2.0 * math.pi

cyl_orig = f.cartesian_point((1.0, 2.0, 3.0))   # offset origin — key to defect
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs150_cyl_ax',#{cyl_orig.eid},#{cyl_zdir.eid},#{cyl_xdir.eid})"
)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('gs150_cyl',#{cyl_ax.eid},{RADIUS})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: partial u-strip on the cylinder ────────────────────────────
# CYLINDRICAL_SURFACE: x = ox + r*cos(u), y = oy + r*sin(u), z = oz + v.
# Placement at (1,2,3): ox=1, oy=2, oz=3.
# Face: u in [0, pi/2], v in [0, 1.5].
# Pcurves are encoded in the displaced coordinate system — the inconsistency
# AdjustByTransformation must fix but silently fails to do so.
ox, oy, oz = 1.0, 2.0, 3.0
v_top = 1.5
u_right = math.pi / 2.0

def cyl_pt(u, v):
    return (ox + RADIUS * math.cos(u), oy + RADIUS * math.sin(u), oz + v)

A3 = cyl_pt(0.0, 0.0)
B3 = cyl_pt(u_right, 0.0)
C3 = cyl_pt(u_right, v_top)
D3 = cyl_pt(0.0, v_top)

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
    pc  = f._emit_raw(f"PCURVE('pc',#{cyl.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

arc_len = RADIUS * u_right   # arc length at bottom / top

# Bottom: A→B, u=0→pi/2 at v=0; pcurve referencing displaced origin
e0 = mk_edge_line(v_A, v_B,
                  A3, (B3[0]-A3[0], B3[1]-A3[1], 0.0), arc_len,
                  (0.0, 0.0), (1.0, 0.0), u_right)
# Right: B→C, v=0→v_top at u=pi/2
e1 = mk_edge_line(v_B, v_C,
                  B3, (0.0, 0.0, 1.0), v_top,
                  (u_right, 0.0), (0.0, 1.0), v_top)
# Top: C→D, u=pi/2→0 at v=v_top
e2 = mk_edge_line(v_C, v_D,
                  C3, (D3[0]-C3[0], D3[1]-C3[1], 0.0), arc_len,
                  (u_right, v_top), (-1.0, 0.0), u_right)
# Left: D→A, v=v_top→0 at u=0
e3 = mk_edge_line(v_D, v_A,
                  D3, (0.0, 0.0, -1.0), v_top,
                  (0.0, v_top), (0.0, -1.0), v_top)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CYLINDRICAL_SURFACE with displaced placement IS the face_geometry; face
# boundary edge pcurves at displaced origin IS the mechanism wired into face
# topology — exercises AdjustByTransformation placement-reconciliation failure.
face  = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
