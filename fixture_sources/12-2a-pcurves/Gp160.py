"""Gp160 — ShapeAnalysis_Surface.ProjectDegenerated singularity-tolerance-threshold

Catalog claim: Singularity tolerance exceeds requested precision; tolerance
filter passes high-tolerance singularities. Degenerate points project onto cone
apex with unvalidated precision consistency. Cone with gradient approach toward
u=0 singularity.

STEP mechanism (literal):
  - CONICAL_SURFACE (half-angle 45 deg, radius 0 at apex) face with a defect
    edge whose pcurve approaches the cone apex singularity along a gradient
    (multiple sample points at increasing proximity to u=0, v=0).
  - THE CATALOG MECHANISM (singularity-tolerance-threshold): ProjectDegenerated
    tests each sample point against a singularity tolerance to determine if it
    should be counted as degenerate. The tolerance used by the filter exceeds
    the precision requested by the caller. Points that are near but not exactly
    at the singularity (i.e., within singularity tolerance but outside requested
    precision) are passed through the filter as degenerate even though the
    precision consistency has not been validated. For a cone approaching the apex
    at u=0: sample points at gradient v values (decreasing v) are accepted as
    singular by the loose tolerance filter; the precision mismatch leaves the
    degenerate projection unvalidated; singularity-tolerance-threshold axis.
    OCC heals the shape and produces shape(1)/shape(1).
  - 3D curve: a clean LINE approaching the cone apex from slightly off-apex.
    Geometry is valid and loadable.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: CONICAL_SURFACE half_angle=45deg, radius=0; pcurve
    LINE approaches apex (u=0, v=0) from v=0.5 to v=0.02 (gradient approach,
    not reaching exact apex); singularity tolerance filter passes near-apex
    samples as degenerate without precision validation; singularity-tolerance-
    threshold axis; OCC heals silently.
  - NO C-1 DRIVER: Archetype B — geometry is clean and loadable.

Distinction from Gp157 (lazy-singularity-init): Gp157's defect is that
ComputeSingularities is never called (singularity table empty); Gp160's defect
is that singularities ARE registered but the tolerance used to filter them is
too loose relative to requested precision — the singularity table is populated
but the threshold mismatch causes incorrect acceptance.

Distinction from Gp158 (whole-edge-degenerate): Gp158 places the ENTIRE pcurve
on the u=0 singularity; Gp160 approaches the apex by gradient (v decreasing)
from a non-degenerate start, so only later samples hit the tolerance filter.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp160",
    defect=(
        "CONICAL_SURFACE half_angle=45deg radius=0 (apex at origin); "
        "defect edge: SURFACE_CURVE; "
        "3D LINE from (0.5,0,0.5) gradient-approaching apex (0,0,0) (clean, loadable); "
        "PCurve LINE in UV along u=0 from v=0.5 to v=0.02: gradient approach to apex; "
        "ProjectDegenerated singularity tolerance filter accepts near-apex samples "
        "v=0.02..0.5 as degenerate without precision validation; "
        "tolerance exceeds requested precision; consistency unvalidated; "
        "singularity-tolerance-threshold axis; OCC heals; shape(1)/shape(1)"
    ),
)

# CONICAL_SURFACE: half-angle=45deg (pi/4), radius=0 at apex (origin).
# OCC cone with radius=0: apex at origin, axis=Z, u=azimuth (0..2pi), v=height.
# 3D point: (v*tan(alpha)*cos(u), v*tan(alpha)*sin(u), v) with alpha=pi/4.
# tan(pi/4)=1, so 3D point = (v*cos(u), v*sin(u), v).
HALF_ANGLE = math.pi / 4.0   # 45 degrees
tan_a = math.tan(HALF_ANGLE)  # 1.0

orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
cone  = f._emit_raw(
    f"CONICAL_SURFACE('cone_tol_threshold',#{plc.eid},0.0,{HALF_ANGLE})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

def cone_pt(u_rad, v_h):
    """3D point on 45-deg cone with apex at origin, radius=0."""
    return (v_h * tan_a * math.cos(u_rad), v_h * tan_a * math.sin(u_rad), v_h)

# Patch: u in [0, pi/2], v in [0.02, 0.5].
# Defect edge: along u=0, v from 0.5 down to 0.02 (gradient approach to apex).
# The v range keeps the edge above the exact apex; sample points near but not at apex.
V_FAR  = 0.5    # v start: well away from apex
V_NEAR = 0.02   # v end:   close to apex (singularity tolerance catches this)

A3 = cone_pt(0.0,         V_FAR)   # (0.5, 0, 0.5)  — left side, far from apex
B3 = cone_pt(math.pi/2.0, V_FAR)   # (0, 0.5, 0.5)  — right side, far from apex
C3 = cone_pt(math.pi/2.0, V_NEAR)  # (0, 0.02, 0.02)— right side, near apex
D3 = cone_pt(0.0,         V_NEAR)  # (0.02, 0, 0.02)— left side, near apex

p_A = f.cartesian_point(A3); v_A = f.vertex_point(p_A)
p_B = f.cartesian_point(B3); v_B = f.vertex_point(p_B)
p_C = f.cartesian_point(C3); v_C = f.vertex_point(p_C)
p_D = f.cartesian_point(D3); v_D = f.vertex_point(p_D)

def mk_line_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, len2):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve on cone."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2e = f.vector(d2e, len2); l2 = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{cone.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Edge A→B: far ring (v=V_FAR, u from 0 to pi/2).
chord_AB = tuple(B3[i] - A3[i] for i in range(3))
len_AB   = math.sqrt(sum(x*x for x in chord_AB))
d_AB     = tuple(x / len_AB for x in chord_AB)
e_AB = mk_line_edge_with_pc(
    v_A, v_B,
    A3, d_AB, len_AB,
    (0.0, V_FAR), (1.0, 0.0), math.pi / 2.0
)

# Edge B→C: right side (u=pi/2, v from V_FAR down to V_NEAR).
chord_BC = tuple(C3[i] - B3[i] for i in range(3))
len_BC   = math.sqrt(sum(x*x for x in chord_BC))
d_BC     = tuple(x / len_BC for x in chord_BC)
e_BC = mk_line_edge_with_pc(
    v_B, v_C,
    B3, d_BC, len_BC,
    (math.pi / 2.0, V_FAR), (0.0, -1.0), V_FAR - V_NEAR
)

# Edge C→D: near-apex ring (v=V_NEAR, u from pi/2 down to 0).
chord_CD = tuple(D3[i] - C3[i] for i in range(3))
len_CD   = math.sqrt(sum(x*x for x in chord_CD))
d_CD     = tuple(x / len_CD for x in chord_CD)
e_CD = mk_line_edge_with_pc(
    v_C, v_D,
    C3, d_CD, len_CD,
    (math.pi / 2.0, V_NEAR), (-1.0, 0.0), math.pi / 2.0
)

# ── DEFECT EDGE D→A — left side (u=0, v from V_NEAR to V_FAR) ───────────────
#
# THE CATALOG MECHANISM: PCurve LINE along u=0, v from V_NEAR (≈apex) to V_FAR.
# The pcurve traverses from near-apex outward. ProjectDegenerated samples this
# pcurve; at the near-apex end (v=V_NEAR=0.02), the singularity tolerance filter
# accepts the samples as degenerate. The tolerance used exceeds the requested
# precision, so near-apex points at v=0.02 are treated as singular even though
# they are V_NEAR units away from the true apex. The precision consistency of
# these near-apex projections is never validated; singularity-tolerance-threshold
# axis. OCC heals the mixed result → shape(1)/shape(1).
# NO C-1 break: Archetype B.
chord_DA = tuple(A3[i] - D3[i] for i in range(3))
len_DA   = math.sqrt(sum(x*x for x in chord_DA))
d_DA     = tuple(x / len_DA for x in chord_DA)

line_3d_orig_DA = f.cartesian_point(D3)
line_3d_dir_DA  = f.direction(d_DA)
line_3d_vec_DA  = f.vector(line_3d_dir_DA, len_DA)
line_3d_DA      = f.line(line_3d_orig_DA, line_3d_vec_DA)

# PCurve: LINE along u=0, from (0.0, V_NEAR) increasing v to (0.0, V_FAR).
pc_start_DA = f.cartesian_point((0.0, V_NEAR))
pc_dir_DA   = f.direction((0.0, 1.0))    # increasing v (apex → far)
pc_vec_DA   = f.vector(pc_dir_DA, V_FAR - V_NEAR)
pc_line_DA  = f.line(pc_start_DA, pc_vec_DA)

defrep_DA = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('sing_tol_thresh_pc_def',(#{pc_line_DA.eid}),#{prc.eid})"
)
pcurve_DA = f._emit_raw(f"PCURVE('sing_tol_thresh_pc',#{cone.eid},#{defrep_DA.eid})")
sc_DA = f._emit_raw(
    f"SURFACE_CURVE('sing_tol_thresh_sc',#{line_3d_DA.eid},(#{pcurve_DA.eid}),.PCURVE_S1.)"
)
e_DA = f._emit_raw(
    f"EDGE_CURVE('sing_tol_thresh_edge',#{v_D.eid},#{v_A.eid},#{sc_DA.eid},.T.)"
)

# Loop: A→B (fwd), B→C (fwd), C→D (fwd), D→A (fwd/defect)
loop = f.edge_loop([
    f.oriented_edge(e_AB, True),
    f.oriented_edge(e_BC, True),
    f.oriented_edge(e_CD, True),
    f.oriented_edge(e_DA, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
