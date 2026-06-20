"""Gs154 — CheckSmall weak tolerance comparison spurious degenerate mark.

Catalog claim: ShapeAnalysis_WireVertex::CheckSmall() uses an undocumented
internal threshold independent of the schema-declared tolerance. Closely-spaced
vertices that fall within the declared schema tolerance are spuriously marked as
degenerate, triggering edge collapse in healing — removing valid edges from the
wire and breaking face boundary closure.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE (radius 1.0) IS the ADVANCED_FACE.face_geometry; face
    boundary EDGE_LOOP containing a very short edge (3D length 5e-4, within
    declared schema tolerance 1e-3) whose adjacent vertices are closely-spaced
    IS the mechanism wired into face topology; CheckSmall spurious-degenerate
    marking of within-tolerance vertices IS the defect.
  - Byte assertions: contains(b'CYLINDRICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE IS ADVANCED_FACE.face_geometry;
    short edge (length 5e-4 < schema tolerance 1e-3) in face boundary EDGE_LOOP
    IS the mechanism wired into face topology; CheckSmall internal-threshold
    spurious-degenerate mark on within-tolerance edge IS the defect.
  - shape_null driver: valid short edge spuriously collapsed; wire open;
    strict kernels reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs154",
    defect=(
        "CYLINDRICAL_SURFACE (radius 1.0) IS ADVANCED_FACE.face_geometry; "
        "face boundary EDGE_LOOP containing short edge (3D length 5e-4, within "
        "declared schema tolerance 1e-3) with closely-spaced adjacent vertices "
        "IS the mechanism wired into face topology; CheckSmall internal-"
        "threshold spurious-degenerate marking of within-tolerance edge IS the "
        "defect; shape_null"
    ),
)

# ── CYLINDRICAL_SURFACE: radius 1.0, axis along Z ──────────────────────────────
# Byte assertion: contains(b'CYLINDRICAL_SURFACE')
# CheckSmall examines vertex spacing using an internal threshold. An edge of
# length 5e-4 (within declared tolerance 1e-3) is spuriously flagged.
RADIUS = 1.0
TWO_PI = 2.0 * math.pi

cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs154_cyl_ax',#{cyl_orig.eid},#{cyl_zdir.eid},#{cyl_xdir.eid})"
)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('gs154_cyl',#{cyl_ax.eid},{RADIUS})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary with a very short edge (length 5e-4) ───────────────────────
# CYLINDRICAL_SURFACE: x = cos(u), y = sin(u), z = v.
# Face: u in [0, pi/2], v in [0, 1.0].
# One edge (bottom-left stub) spans u=0→epsilon where epsilon gives 3D
# arc-length = RADIUS * epsilon = 5e-4 → epsilon = 5e-4 (radius=1).
# This short edge is the mechanism: CheckSmall flags its vertices as degenerate.

EPS_U = 5e-4   # arc-length = 5e-4 (within schema tolerance 1e-3)
U_END = math.pi / 2.0
V_TOP = 1.0

def cyl_pt(u, v):
    return (RADIUS * math.cos(u), RADIUS * math.sin(u), v)

# Vertices: A at (u=0,v=0), B_stub at (u=EPS_U,v=0), C at (u=U_END,v=0),
#           D at (u=U_END,v=V_TOP), E at (u=0,v=V_TOP).
A3       = cyl_pt(0.0, 0.0)
B_stub3  = cyl_pt(EPS_U, 0.0)    # very close to A — CheckSmall flags this pair
C3       = cyl_pt(U_END, 0.0)
D3       = cyl_pt(U_END, V_TOP)
E3       = cyl_pt(0.0, V_TOP)

p_A      = f.cartesian_point(A3)
p_B_stub = f.cartesian_point(B_stub3)
p_C      = f.cartesian_point(C3)
p_D      = f.cartesian_point(D3)
p_E      = f.cartesian_point(E3)

v_A      = f.vertex_point(p_A)
v_B_stub = f.vertex_point(p_B_stub)
v_C      = f.vertex_point(p_C)
v_D      = f.vertex_point(p_D)
v_E      = f.vertex_point(p_E)

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

# Very short stub edge: A→B_stub, arc-length 5e-4 (within schema tolerance 1e-3)
# This IS the edge CheckSmall spuriously marks as degenerate.
e_stub = mk_edge_line(v_A, v_B_stub,
                      A3, (B_stub3[0] - A3[0], B_stub3[1] - A3[1], 0.0), EPS_U * RADIUS,
                      (0.0, 0.0), (1.0, 0.0), EPS_U)
# Rest of bottom arc: B_stub→C
e0 = mk_edge_line(v_B_stub, v_C,
                  B_stub3, (C3[0] - B_stub3[0], C3[1] - B_stub3[1], 0.0),
                  RADIUS * (U_END - EPS_U),
                  (EPS_U, 0.0), (1.0, 0.0), U_END - EPS_U)
# Right: C→D, v=0→V_TOP at u=U_END
e1 = mk_edge_line(v_C, v_D,
                  C3, (0.0, 0.0, 1.0), V_TOP,
                  (U_END, 0.0), (0.0, 1.0), V_TOP)
# Top: D→E, u=U_END→0 at v=V_TOP
e2 = mk_edge_line(v_D, v_E,
                  D3, (E3[0] - D3[0], E3[1] - D3[1], 0.0), RADIUS * U_END,
                  (U_END, V_TOP), (-1.0, 0.0), U_END)
# Left: E→A, v=V_TOP→0 at u=0
e3 = mk_edge_line(v_E, v_A,
                  E3, (0.0, 0.0, -1.0), V_TOP,
                  (0.0, V_TOP), (0.0, -1.0), V_TOP)

loop = f.edge_loop([
    f.oriented_edge(e_stub, True),   # short edge IS the mechanism
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CYLINDRICAL_SURFACE IS the face_geometry; face boundary EDGE_LOOP with
# short edge (arc-length 5e-4, within schema tolerance 1e-3) IS the mechanism
# wired into face topology — exercises CheckSmall spurious-degenerate-mark bug.
face  = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
