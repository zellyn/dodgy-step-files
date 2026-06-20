"""Gp138 — ShapeFix_IntersectionTool.SplitEdge2.pcurve-endpoint-detection

Catalog claim: SplitEdge2 determines fragment assignment by comparing PCurve
endpoints to the midpoint parameter. Without endpoint detection, parameter cuts
are applied to the wrong fragments.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect arc edge wrapped in SURFACE_CURVE.
  - THE CATALOG MECHANISM: The PCurve on the surface has its orientation
    reversed relative to the 3D curve. The arc's PCurve start (in UV) is at
    the same position as the 3D arc's end, and vice versa. SplitEdge2 uses
    PCurve endpoint detection (comparing PCurve endpoint to midpoint parameter)
    to determine correct fragment assignment. Without this check, a parameter
    cut would be applied to the wrong half of the arc, inverting the split.
    With endpoint detection: fragments correctly identified. OCC heals and
    produces shape(1)/shape(1).
  - 3D curve: a clean TRIMMED_CURVE arc. Geometry is valid and loadable.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: PCurve endpoint reversed relative to 3D arc; midpoint
    parameter comparison in SplitEdge2 needed to correctly assign fragments;
    OCC heals silently.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp138",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; 3D arc CIRCLE trimmed u=0..pi/2 "
        "(A=(1,0,0) to B=(0,1,0)); "
        "PCurve B_SPLINE_CURVE_WITH_KNOTS degree-2 UV endpoints reversed: "
        "PCurve starts at UV=(1.5707963,0) and ends at UV=(0,0) — reversed vs 3D; "
        "SplitEdge2 midpoint-parameter endpoint detection needed for correct "
        "fragment assignment; without detection: parameter cut applied to wrong "
        "fragment; OCC heals via endpoint detection; shape(1)/shape(1)"
    ),
)

# Host surface: planar Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners: triangle-like patch with one arc edge A=(1,0,0), B=(0,1,0),
# plus two straight edges closing the loop back to origin C=(0,0,0).
p_A = f.cartesian_point((1.0, 0.0, 0.0))
p_B = f.cartesian_point((0.0, 1.0, 0.0))
p_C = f.cartesian_point((0.0, 0.0, 0.0))
v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)

def mk_line_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# B→C: straight line from (0,1,0) to (0,0,0)
e_BC = mk_line_edge_with_pc(
    v_B, v_C,
    (0.0, 1.0, 0.0), (0., -1., 0.), 1.0,
    (0.0, 1.0), (0., -1.)
)
# C→A: straight line from (0,0,0) to (1,0,0)
e_CA = mk_line_edge_with_pc(
    v_C, v_A,
    (0.0, 0.0, 0.0), (1., 0., 0.), 1.0,
    (0.0, 0.0), (1., 0.)
)

# ── DEFECT EDGE — arc A→B (quarter circle at Z=0) ─────────────────────────────
#
# THE CATALOG MECHANISM: 3D arc goes A=(1,0,0) → B=(0,1,0) (u=0..pi/2).
# PCurve B-spline is endpoint-reversed: UV starts at (pi/2, 0) and ends at
# (0, 0). SplitEdge2 detects the reversal by comparing PCurve endpoints to the
# midpoint parameter, enabling correct fragment assignment.
# NO C-1 break: OCC heals, expected shape(1)/shape(1).

# 3D arc: CIRCLE radius=1 on Z=0 plane, trimmed u=0..pi/2
arc_ctr = f.cartesian_point((0.0, 0.0, 0.0))
arc_ax  = f.axis2_placement_3d(arc_ctr, zdir, xdir)
arc_circ = f._emit_raw(f"CIRCLE('arc_circ',#{arc_ax.eid},1.0)")
arc_trim = f._emit_raw(
    f"TRIMMED_CURVE('arc_trim',#{arc_circ.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({math.pi/2.0})),.T.,.PARAMETER.)"
)

# PCurve B-spline: reversed endpoints relative to 3D arc.
# 3D goes from u=0 (x=1,y=0) to u=pi/2 (x=0,y=1).
# PCurve in UV: starts at (pi/2, 0) and ends at (0, 0) — flipped U order.
# This is the structural trigger: endpoint detection in SplitEdge2 must
# compare PCurve endpoint to midpoint param to identify the correct fragment.
rp0 = f.cartesian_point((math.pi / 2.0, 0.0))   # UV start (reversed)
rp1 = f.cartesian_point((math.pi / 4.0, 0.0))   # UV midpoint
rp2 = f.cartesian_point((0.0, 0.0))              # UV end (reversed)

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('splitedge2_endpoint_pc',2,"
    f"(#{rp0.eid},#{rp1.eid},#{rp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('splitedge2_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('splitedge2_pc',#{surf.eid},#{defrep.eid})")
sc_arc = f._emit_raw(
    f"SURFACE_CURVE('splitedge2_sc',#{arc_trim.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_arc = f._emit_raw(
    f"EDGE_CURVE('splitedge2_edge',#{v_A.eid},#{v_B.eid},#{sc_arc.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_arc, True),
    f.oriented_edge(e_BC,  True),
    f.oriented_edge(e_CA,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
