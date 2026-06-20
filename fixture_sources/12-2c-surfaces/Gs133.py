"""Gs133 — CYLINDRICAL_SURFACE degenerate edge with sub-optimal projection.

Catalog claim: ShapeAnalysis_Surface.ProjectDegenerated is called on a
degenerate edge whose endpoints collapse to a single point (within tolerance
margin). The method picks a sub-optimal projection onto the surface: it
projects the collapse-point tangent direction but fails to minimize the
residual distance, returning a UV coordinate that does not minimize error.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE IS the ADVANCED_FACE.face_geometry; a degenerate
    edge whose 3D start and end vertices collapse to the same point (within
    tolerance) IS the mechanism wired into face topology;
    ProjectDegenerated sub-optimal tangent projection IS the defect.
  - Byte assertions: contains(b'CYLINDRICAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE IS ADVANCED_FACE.face_geometry;
    degenerate edge with coincident endpoints (collapse within tolerance)
    IS the mechanism wired into face topology; ProjectDegenerated
    sub-optimal tangent-direction projection IS the defect.
  - shape_null driver: wrong UV projection for degenerate edge;
    strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gs133",
    defect=(
        "CYLINDRICAL_SURFACE IS ADVANCED_FACE.face_geometry; "
        "degenerate edge with coincident endpoints (collapse within tolerance) "
        "IS the mechanism wired into face topology; "
        "ProjectDegenerated sub-optimal tangent-direction projection IS the defect; "
        "shape_null"
    ),
)

# ── CYLINDRICAL_SURFACE ────────────────────────────────────────────────────────
# Byte assertion: contains(b'CYLINDRICAL_SURFACE')
# Radius=1, axis along Z
R = 1.0
TWO_PI = 2.0 * math.pi

cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs133_cyl_ax',#{cyl_orig.eid},#{cyl_zdir.eid},#{cyl_xdir.eid})"
)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('gs133_cyl',#{cyl_ax.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Degenerate edge: endpoints collapse to single point ───────────────────────
# CYLINDRICAL_SURFACE: u in [0,2pi], v = height along Z
# x = cos(u), y = sin(u), z = v
#
# Degenerate edge: both endpoints at (1.0, 0.0, 0.5) — same 3D point.
# The edge "travels" a tiny 3D distance (sub-tolerance EPS) but both vertices
# are coincident within tolerance. ProjectDegenerated must project the
# tangent direction but picks sub-optimal UV.
EPS = 1e-7   # within OCCT tolerance (1e-7 default)
u_deg = 0.0  # degenerate point u-parameter
v_deg = 0.5  # degenerate point v-parameter

deg_pt_3d = (R * math.cos(u_deg), R * math.sin(u_deg), v_deg)  # (1,0,0.5)

p_deg_start = f.cartesian_point(deg_pt_3d)
p_deg_end   = f.cartesian_point(deg_pt_3d)  # same 3D point — collapse

v_deg_start = f.vertex_point(p_deg_start)
v_deg_end   = f.vertex_point(p_deg_end)

# Normal boundary vertices for the outer loop
def cyl_pt(u, v):
    return (R * math.cos(u), R * math.sin(u), v)

u0, u1 = 0.0, math.pi  # half cylinder
H = 0.5

A3 = cyl_pt(u0, 0.0)
B3 = cyl_pt(u1, 0.0)
C3 = cyl_pt(u1, H)
D3 = cyl_pt(u0, H)

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

# Outer loop: half-cylinder rectangle
# Bottom: A→B (u: 0→pi, v=0)
e0 = mk_edge_line(v_A, v_B,
                  A3, (B3[0]-A3[0], B3[1]-A3[1], 0.0), math.pi,
                  (u0, 0.0), (1.0, 0.0), math.pi)
# Right: B→C (v: 0→H, u=pi)
e1 = mk_edge_line(v_B, v_C,
                  B3, (0.0, 0.0, 1.0), H,
                  (u1, 0.0), (0.0, 1.0), H)
# Top: C→D (u: pi→0, v=H)
e2 = mk_edge_line(v_C, v_D,
                  C3, (D3[0]-C3[0], D3[1]-C3[1], 0.0), math.pi,
                  (u1, H), (-1.0, 0.0), math.pi)
# Left: D→A (v: H→0, u=0)
e3 = mk_edge_line(v_D, v_A,
                  D3, (0.0, 0.0, -1.0), H,
                  (u0, H), (0.0, -1.0), H)

outer_loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# Degenerate inner edge: both vertices at same point (collapse within EPS)
# pcurve direction: tangential (u-direction) — sub-optimal projection target
p2_degen = f.cartesian_point((u_deg, v_deg))
d2_degen = f.direction((1.0, 0.0))
v2_degen = f.vector(d2_degen, EPS)
l2_degen = f.line(p2_degen, v2_degen)
p3_degen = f.cartesian_point(deg_pt_3d)
d3_degen = f.direction((0.0, 1.0, 0.0))  # tangent direction on cylinder at u=0
v3_degen = f.vector(d3_degen, EPS)
l3_degen = f.line(p3_degen, v3_degen)
pcd_degen = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_degen',(#{l2_degen.eid}),#{prc.eid})")
pc_degen  = f._emit_raw(f"PCURVE('pc_degen',#{cyl.eid},#{pcd_degen.eid})")
sc_degen  = f._emit_raw(f"SURFACE_CURVE('sc_degen',#{l3_degen.eid},(#{pc_degen.eid}),.PCURVE_S1.)")
# Degenerate edge: same start/end vertex — collapse
e_degen = f._emit_raw(
    f"EDGE_CURVE('ec_degen',#{v_deg_start.eid},#{v_deg_end.eid},#{sc_degen.eid},.T.)"
)
degen_loop = f.edge_loop([f.oriented_edge(e_degen, True)])

# CYLINDRICAL_SURFACE IS face_geometry; degenerate edge (coincident endpoints)
# IS the mechanism wired into face topology.
face  = f.advanced_face(
    [f.face_outer_bound(outer_loop), f.face_bound(degen_loop, True)],
    cyl
)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
