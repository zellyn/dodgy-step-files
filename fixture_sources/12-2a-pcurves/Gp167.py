"""Gp167 — ProjectDegenerated.partial-edge-collapse

Catalog claim: Spherical surface with half-edge pcurve near pole (singularity),
tail normal. Tests collapse of degenerate segment endpoint to singularity
parameter. OCC cannot heal; produces empty/empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius=1) face with a defect edge whose pcurve starts
    exactly at the north pole (v=pi/2) and transitions to a normal equatorial
    region. The first half of the pcurve maps to a single degenerate point
    (pole); the second half is normal.
  - THE CATALOG MECHANISM (partial-edge-collapse, empty variant): The first half
    of the defect edge pcurve collapses entirely to the pole singularity (v=pi/2).
    ProjectDegenerated must detect that the degenerate segment endpoint coincides
    with the pole parameter and propagate this into the continuity state. When
    combined with a C-1 break in the 3D B-spline, OCC cannot reconcile the
    partial collapse with the 3D geometry discontinuity; shape_null=True.
  - C-1 DRIVER: degree-2 B-spline 3D curve with positional break at t=0.5 (knot
    mult=3, 1.5-unit CP gap) forces shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE radius=1; pcurve starts at north pole
    (v=pi/2, metric fully collapsed), transitions to equator (v=0, metric full);
    degenerate segment endpoint maps to pole singularity parameter;
    partial-edge-collapse axis; combined with C-1 break, OCC cannot heal;
    shape_null=True.
  - C-1 DRIVER: degree-2 B-spline 3D positional break forces shape_null=True.

Distinction from Gp159 (partial-edge-collapse, shape(1)/load==ok):
  Gp159 uses a clean 3D LINE with pcurve starting near (not at) the pole;
  OCC heals the partial collapse. Gp167 starts the pcurve exactly at the pole
  (v=pi/2) AND uses a C-1-broken 3D B-spline, combining full pole collapse with
  invalid 3D geometry so OCC cannot heal.

Distinction from Gp166 (whole-edge-degenerate): Gp166 collapses the ENTIRE
pcurve; Gp167 collapses only the first half (pole → equator transition).
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp167",
    defect=(
        "SPHERICAL_SURFACE radius=1; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2] vs CP[3] 1.5-unit gap) drives shape_null; "
        "PCurve LINE in UV from (pi/4, pi/2) to (pi/4, 0.0): "
        "first half at north pole (v=pi/2, metric fully collapsed), "
        "second half toward equator; degenerate endpoint at pole singularity; "
        "ProjectDegenerated partial collapse unrecoverable with C-1 break; "
        "partial-edge-collapse axis; shape_null=True"
    ),
)

# SPHERICAL_SURFACE radius=1.
# OCC sphere: u=longitude (0..2pi), v=latitude (-pi/2..pi/2).
# North pole at v=pi/2; equator at v=0.
# 3D point: (cos(v)*cos(u), cos(v)*sin(u), sin(v)).
orig   = f.cartesian_point((0.0, 0.0, 0.0))
zdir   = f.direction((0.0, 0.0, 1.0))
xdir   = f.direction((1.0, 0.0, 0.0))
plc    = f.axis2_placement_3d(orig, zdir, xdir)
sphere = f._emit_raw(f"SPHERICAL_SURFACE('unit_sphere_partial_collapse_empty',#{plc.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

def sph_pt(u, v):
    """3D point on unit sphere: u=longitude, v=latitude."""
    return (math.cos(v) * math.cos(u), math.cos(v) * math.sin(u), math.sin(v))

# Defect edge: u=pi/4 meridian, v from V_POLE (pi/2, the exact north pole) to V_EQ (0).
U_MER  = math.pi / 4.0    # meridian longitude
V_POLE = math.pi / 2.0    # exact north pole (metric fully collapsed)
V_EQ   = 0.0              # equator

# Face patch: 4 corners.
A3 = sph_pt(0.0,   V_EQ)    # equator, u=0
B3 = sph_pt(U_MER, V_EQ)    # equator, u=pi/4
C3 = sph_pt(U_MER, V_POLE)  # north pole on meridian (= (0,0,1) regardless of u)
D3 = sph_pt(0.0,   V_POLE)  # north pole, u=0 (same 3D point as C3)

p_A = f.cartesian_point(A3); v_A = f.vertex_point(p_A)
p_B = f.cartesian_point(B3); v_B = f.vertex_point(p_B)
p_C = f.cartesian_point(C3); v_C = f.vertex_point(p_C)
p_D = f.cartesian_point(D3); v_D = f.vertex_point(p_D)

def mk_line_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, len2):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve on sphere."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2e = f.vector(d2e, len2); l2 = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{sphere.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Edge A→B: equator (v=0, u from 0 to pi/4).
chord_AB = tuple(B3[i] - A3[i] for i in range(3))
len_AB   = math.sqrt(sum(x*x for x in chord_AB))
d_AB     = tuple(x / len_AB for x in chord_AB)
e_AB = mk_line_edge_with_pc(
    v_A, v_B, A3, d_AB, len_AB,
    (0.0, V_EQ), (1.0, 0.0), U_MER
)

# Edge A→D: left meridian (u=0, v from 0 to pi/2).
chord_AD = tuple(D3[i] - A3[i] for i in range(3))
len_AD   = math.sqrt(sum(x*x for x in chord_AD))
d_AD     = tuple(x / len_AD for x in chord_AD)
e_AD = mk_line_edge_with_pc(
    v_A, v_D, A3, d_AD, len_AD,
    (0.0, V_EQ), (0.0, 1.0), V_POLE - V_EQ
)

# Edge D→C: near-pole top (v=pi/2, u from 0 to pi/4 — degenerate arc at pole).
chord_DC = tuple(C3[i] - D3[i] for i in range(3))
len_DC   = math.sqrt(sum(x*x for x in chord_DC))
if len_DC < 1e-12:
    # Pole arc: C3==D3==(0,0,1). Use a tiny nonzero chord in a valid direction.
    d_DC = (1.0, 0.0, 0.0)
    len_DC = 1e-6
else:
    d_DC = tuple(x / len_DC for x in chord_DC)
e_DC = mk_line_edge_with_pc(
    v_D, v_C, D3, d_DC, len_DC,
    (0.0, V_POLE), (1.0, 0.0), U_MER
)

# ── DEFECT EDGE C→B — right meridian: exact pole to equator ──────────────────
#
# THE CATALOG MECHANISM: PCurve LINE at u=U_MER, v from V_POLE (=pi/2, exact
# north pole, metric fully collapsed) down to V_EQ (=0, equator, metric normal).
# The degenerate segment endpoint coincides with the pole singularity parameter.
# ProjectDegenerated must recognise that the FIRST half of the pcurve maps to
# the pole singularity and propagate collapse state to the continuity data.
# With a simultaneous C-1 break in the 3D B-spline, OCC cannot reconcile the
# degenerate endpoint with the 3D geometry discontinuity; shape_null=True.
#
# C-1 DRIVER: 6-CP degree-2 B-spline with positional break at t=0.5.
# Control points from C3 (pole, =(0,0,1)) to B3 (equator).
chord_CB = tuple(B3[i] - C3[i] for i in range(3))
len_CB   = math.sqrt(sum(x*x for x in chord_CB))
d_unit   = tuple(x / len_CB for x in chord_CB)
mid3     = tuple(C3[i] + 0.5 * chord_CB[i] for i in range(3))
gap3     = tuple(mid3[i] + 1.5 * d_unit[i] for i in range(3))
q25_3    = tuple(C3[i] + 0.25 * chord_CB[i] for i in range(3))
q75_3    = tuple(C3[i] + 0.75 * chord_CB[i] for i in range(3))

dc0 = f.cartesian_point(C3)
dc1 = f.cartesian_point(q25_3)
dc2 = f.cartesian_point(mid3)
dc3 = f.cartesian_point(gap3)       # 1.5-unit positional gap = C-1 break
dc4 = f.cartesian_point(q75_3)
dc5 = f.cartesian_point(B3)

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('partial_collapse_empty_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# PCurve LINE at u=U_MER, v from V_POLE down to V_EQ.
pc_start = f.cartesian_point((U_MER, V_POLE))
pc_dir   = f.direction((0.0, -1.0))   # decreasing v (pole → equator)
pc_vec   = f.vector(pc_dir, V_POLE - V_EQ)
pc_line  = f.line(pc_start, pc_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('partial_collapse_empty_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('partial_collapse_empty_pc',#{sphere.eid},#{defrep.eid})")
sc_CB = f._emit_raw(
    f"SURFACE_CURVE('partial_collapse_empty_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_CB = f._emit_raw(
    f"EDGE_CURVE('partial_collapse_empty_edge',#{v_C.eid},#{v_B.eid},#{sc_CB.eid},.T.)"
)

# Loop: A→B (fwd), B→C (rev of C→B defect), C→D (rev of D→C), D→A (rev of A→D)
loop = f.edge_loop([
    f.oriented_edge(e_AB, True),
    f.oriented_edge(e_CB, False),   # C→B reversed → B→C
    f.oriented_edge(e_DC, False),   # D→C reversed → C→D
    f.oriented_edge(e_AD, False),   # A→D reversed → D→A
])
face  = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
