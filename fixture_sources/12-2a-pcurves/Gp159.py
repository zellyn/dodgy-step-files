"""Gp159 — ShapeAnalysis_Surface.ProjectDegenerated partial-edge-collapse

Catalog claim: First half of pcurve near singularity not collapsed to parameter.
Mixed degenerate/non-degenerate segment fails healing signal propagation. Sphere
with pcurve starting at pole (u≈0.01), ending equator (u=0.5).

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius=1) face with a defect edge whose pcurve starts
    very close to the north pole (v≈π/2 - ε) and ends at the equator (v=0).
  - THE CATALOG MECHANISM (partial-edge-collapse): ProjectDegenerated samples
    the pcurve at multiple points. The first half of the pcurve lies in the
    near-pole region where the sphere metric is nearly collapsed; sample points
    there project onto a very small neighbourhood of the pole. The second half
    moves away from the pole toward the equator, where the metric is regular.
    ProjectDegenerated must signal the first segment as degenerate and the
    second as non-degenerate. The healing signal for the degenerate segment
    fails to propagate correctly because the partial collapse detection does
    not track the transition from degenerate to non-degenerate; partial-edge-
    collapse axis. OCC heals the mixed edge and produces shape(1)/shape(1).
  - 3D curve: a clean LINE from a near-pole point to the equator. Geometry is
    valid and loadable.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE; pcurve starts near north pole
    (v = pi/2 - 0.01) and ends at equator (v = 0.0) along u = pi/4 meridian;
    first pcurve segment near-degenerate, second non-degenerate; ProjectDegenerated
    partial collapse detection fails to propagate healing signal for first segment;
    partial-edge-collapse axis; OCC heals silently.
  - NO C-1 DRIVER: Archetype B — geometry is clean and loadable.

Distinction from Gp157 (lazy-singularity-init, cone apex) and Gp158
(whole-edge-degenerate, cone u=0 entire edge): Gp159 uses a SPHERE and
the critical structure is the MIX of degenerate + non-degenerate segments in
a single edge, not a uniformly degenerate or lazy-init failure.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp159",
    defect=(
        "SPHERICAL_SURFACE radius=1; defect edge: SURFACE_CURVE; "
        "3D LINE from near-pole (sin(pi/4)*cos(pi/2-0.01), sin(pi/4)*sin(pi/2-0.01), cos(pi/2-0.01)) "
        "to equator (cos(pi/4), sin(pi/4), 0) (clean, loadable); "
        "PCurve LINE in UV from (pi/4, pi/2-0.01) to (pi/4, 0.0): "
        "first half near north pole (v~pi/2, metric collapsed), second half toward equator; "
        "ProjectDegenerated partial collapse: degenerate-to-non-degenerate transition "
        "not tracked; healing signal for first segment fails to propagate; "
        "partial-edge-collapse axis; OCC heals; shape(1)/shape(1)"
    ),
)

# SPHERICAL_SURFACE radius=1.
# OCC sphere: u=longitude (0..2pi), v=latitude (-pi/2..pi/2).
# North pole at v=pi/2; equator at v=0.
# 3D point: (cos(v)*cos(u), cos(v)*sin(u), sin(v)).
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
sphere = f._emit_raw(f"SPHERICAL_SURFACE('unit_sphere_partial_degen',#{plc.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

def sph_pt(u, v):
    """3D point on unit sphere: u=longitude, v=latitude."""
    return (math.cos(v) * math.cos(u), math.cos(v) * math.sin(u), math.sin(v))

# Defect edge meridian: u=pi/4, v from v_pole to v_eq.
# v_pole = pi/2 - 0.01 (very close to north pole, metric nearly collapsed).
# v_eq   = 0.0         (equator, metric full).
U_MER   = math.pi / 4.0     # meridian longitude (u = 45 deg)
V_POLE  = math.pi / 2.0 - 0.01   # near north pole
V_EQ    = 0.0               # equator

# Face patch: 4 corners.
# A = (u=0,     v=V_EQ)  — equator, u=0
# B = (u=U_MER, v=V_EQ)  — equator, u=pi/4
# C = (u=U_MER, v=V_POLE)— near pole, u=pi/4  (one end of defect edge)
# D = (u=0,     v=V_POLE)— near pole, u=0
A3 = sph_pt(0.0,    V_EQ)
B3 = sph_pt(U_MER,  V_EQ)
C3 = sph_pt(U_MER,  V_POLE)
D3 = sph_pt(0.0,    V_POLE)

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

# Edge A→B: equator (v=V_EQ=0, u from 0 to pi/4).
chord_AB = tuple(B3[i] - A3[i] for i in range(3))
len_AB   = math.sqrt(sum(x*x for x in chord_AB))
d_AB     = tuple(x / len_AB for x in chord_AB)
e_AB = mk_line_edge_with_pc(
    v_A, v_B,
    A3, d_AB, len_AB,
    (0.0, V_EQ), (1.0, 0.0), U_MER
)

# Edge A→D: left meridian (u=0, v from V_EQ to V_POLE).
chord_AD = tuple(D3[i] - A3[i] for i in range(3))
len_AD   = math.sqrt(sum(x*x for x in chord_AD))
d_AD     = tuple(x / len_AD for x in chord_AD)
e_AD = mk_line_edge_with_pc(
    v_A, v_D,
    A3, d_AD, len_AD,
    (0.0, V_EQ), (0.0, 1.0), V_POLE - V_EQ
)

# Edge D→C: near-pole top (v=V_POLE, u from 0 to pi/4).
chord_DC = tuple(C3[i] - D3[i] for i in range(3))
len_DC   = math.sqrt(sum(x*x for x in chord_DC))
d_DC     = tuple(x / len_DC for x in chord_DC)
e_DC = mk_line_edge_with_pc(
    v_D, v_C,
    D3, d_DC, len_DC,
    (0.0, V_POLE), (1.0, 0.0), U_MER
)

# ── DEFECT EDGE C→B — right meridian: near-pole to equator ───────────────────
#
# THE CATALOG MECHANISM: PCurve LINE in UV at u=U_MER (fixed longitude),
# v from V_POLE (=pi/2-0.01, near pole) down to V_EQ (=0, equator).
# First half (v from V_POLE down to ~pi/4): sphere metric nearly collapsed near
# pole; ProjectDegenerated treats those samples as degenerate.
# Second half (v from ~pi/4 down to 0): metric normal; non-degenerate samples.
# The transition from degenerate to non-degenerate is not tracked; healing signal
# for the first half fails to propagate; partial-edge-collapse axis.
# 3D curve: clean LINE from C3 to B3.
# NO C-1 break: Archetype B.
chord_CB = tuple(B3[i] - C3[i] for i in range(3))
len_CB   = math.sqrt(sum(x*x for x in chord_CB))
d_CB     = tuple(x / len_CB for x in chord_CB)

line_3d_orig_CB = f.cartesian_point(C3)
line_3d_dir_CB  = f.direction(d_CB)
line_3d_vec_CB  = f.vector(line_3d_dir_CB, len_CB)
line_3d_CB      = f.line(line_3d_orig_CB, line_3d_vec_CB)

# PCurve LINE at u=U_MER, v from V_POLE down to V_EQ.
pc_start_CB = f.cartesian_point((U_MER, V_POLE))
pc_dir_CB   = f.direction((0.0, -1.0))   # decreasing v (pole → equator)
pc_vec_CB   = f.vector(pc_dir_CB, V_POLE - V_EQ)
pc_line_CB  = f.line(pc_start_CB, pc_vec_CB)

defrep_CB = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('partial_collapse_pc_def',(#{pc_line_CB.eid}),#{prc.eid})"
)
pcurve_CB = f._emit_raw(f"PCURVE('partial_collapse_pc',#{sphere.eid},#{defrep_CB.eid})")
sc_CB = f._emit_raw(
    f"SURFACE_CURVE('partial_collapse_sc',#{line_3d_CB.eid},(#{pcurve_CB.eid}),.PCURVE_S1.)"
)
e_CB = f._emit_raw(
    f"EDGE_CURVE('partial_collapse_edge',#{v_C.eid},#{v_B.eid},#{sc_CB.eid},.T.)"
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
