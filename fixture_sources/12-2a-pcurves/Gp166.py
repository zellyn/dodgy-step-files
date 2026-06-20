"""Gp166 — ProjectDegenerated.whole-edge-degenerate

Catalog claim: Conical surface with entire pcurve collapsing to apex singularity.
Fixtures force redistribution of degenerate points along non-degenerate parametric
axis. OCC cannot heal; produces empty/empty.

STEP mechanism (literal):
  - CONICAL_SURFACE (half-angle 45 deg, radius 0 at apex) face with a defect
    edge whose entire pcurve lies exactly at u=0, v in [0, 1]. Every sample point
    collapses to the cone apex singularity.
  - THE CATALOG MECHANISM (whole-edge-degenerate, empty variant): The entire
    defect edge pcurve lies at u=0 (the apex singular line). Unlike Gp158, where
    OCC heals the inconsistency, here a C-1 break in the 3D B-spline provides a
    positional discontinuity that prevents healing: OCC encounters the collapsed
    pcurve AND an invalid 3D curve simultaneously, cannot reconcile them, and
    produces empty/empty.
  - C-1 DRIVER: degree-2 B-spline 3D curve with positional break at t=0.5 (knot
    mult=3, 1.5-unit CP gap) forces shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: CONICAL_SURFACE apex at u=0, v=0; entire PCurve at u=0,
    v in [0,1]; ALL pcurve samples collapse to singularity; redistribution of
    degenerate points fails; whole-edge-degenerate axis; combined with C-1 break,
    OCC cannot heal; shape_null=True.
  - C-1 DRIVER: degree-2 B-spline 3D positional break forces shape_null=True.

Distinction from Gp158 (whole-edge-degenerate, shape(1)/load==ok):
  Gp158 uses a clean 3D LINE so OCC can heal the degenerate pcurve.
  Gp166 uses a C-1-broken 3D B-spline that OCC cannot reconcile with the
  degenerate pcurve, yielding empty/empty (shape_null=True).

Distinction from Gp167 (partial-edge-collapse): Gp166 collapses the ENTIRE
pcurve to the singularity; Gp167 collapses only the first half.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp166",
    defect=(
        "CONICAL_SURFACE half_angle=45deg radius=0 (apex at origin); "
        "defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2] vs CP[3] 1.5-unit gap) drives shape_null; "
        "PCurve LINE entirely at u=0: from (0.0,0.0) to (0.0,1.0) — whole edge "
        "on cone apex singularity line; ProjectDegenerated: all sample points "
        "collapse to u=0 singularity; redistribution of degenerate points fails; "
        "whole-edge-degenerate axis; shape_null=True"
    ),
)

# CONICAL_SURFACE: half-angle=45deg (pi/4), radius=0 at apex.
# OCC cone: u=azimuth (0..2pi), v=height. tan(pi/4)=1.
# 3D point at (u,v): (v*cos(u), v*sin(u), v).
HALF_ANGLE = math.pi / 4.0
tan_a = math.tan(HALF_ANGLE)  # 1.0

orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
cone  = f._emit_raw(
    f"CONICAL_SURFACE('cone_whole_degen_empty',#{plc.eid},0.0,{HALF_ANGLE})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

def cone_pt(u_rad, v_h):
    return (v_h * tan_a * math.cos(u_rad), v_h * tan_a * math.sin(u_rad), v_h)

# Triangle patch: apex A=(0,0,0), B=(u=pi/2,v=1), D=(u=0,v=1).
apex_3d = (0.0, 0.0, 0.0)
B3 = cone_pt(math.pi / 2.0, 1.0)   # (0, 1, 1)
D3 = cone_pt(0.0,           1.0)   # (1, 0, 1)

p_apex = f.cartesian_point(apex_3d); v_apex = f.vertex_point(p_apex)
p_B    = f.cartesian_point(B3);      v_B    = f.vertex_point(p_B)
p_D    = f.cartesian_point(D3);      v_D    = f.vertex_point(p_D)

def mk_line_edge_with_pc(vs, ve, p3, d3, len3, p2, d2, len2):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2)
    d2e = f.direction(d2); v2e = f.vector(d2e, len2); l2 = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{cone.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Edge apex→B: along u=pi/2 from v=0 (apex) to v=1.
chord_AB = B3
len_AB   = math.sqrt(sum(x*x for x in chord_AB))
d_AB     = tuple(x / len_AB for x in chord_AB)
e_AB = mk_line_edge_with_pc(
    v_apex, v_B,
    apex_3d, d_AB, len_AB,
    (math.pi / 2.0, 0.0), (0.0, 1.0), 1.0
)

# Edge B→D: rim chord at v=1, u=pi/2→0.
chord_BD = tuple(D3[i] - B3[i] for i in range(3))
len_BD   = math.sqrt(sum(x*x for x in chord_BD))
d_BD     = tuple(x / len_BD for x in chord_BD)
e_BD = mk_line_edge_with_pc(
    v_B, v_D,
    B3, d_BD, len_BD,
    (math.pi / 2.0, 1.0), (-1.0, 0.0), math.pi / 2.0
)

# ── DEFECT EDGE D→apex — entire pcurve at u=0 singularity line ───────────────
#
# THE CATALOG MECHANISM: PCurve LINE at u=0, v from 1 down to 0 (toward apex).
# ALL pcurve points collapse to the u=0 singular line of the cone.
# ProjectDegenerated's redistribution of degenerate points is blocked by the
# simultaneous C-1 break in the 3D B-spline — OCC cannot reconcile degenerate
# pcurve with invalid 3D geometry; shape_null=True.
#
# C-1 DRIVER: 6-CP degree-2 B-spline with positional break at t=0.5.
chord_DA = tuple(apex_3d[i] - D3[i] for i in range(3))
len_DA   = math.sqrt(sum(x*x for x in chord_DA))
d_unit   = tuple(x / len_DA for x in chord_DA)
mid3     = tuple(D3[i] + 0.5 * chord_DA[i] for i in range(3))
gap3     = tuple(mid3[i] + 1.5 * d_unit[i] for i in range(3))
q25_3    = tuple(D3[i] + 0.25 * chord_DA[i] for i in range(3))
q75_3    = tuple(D3[i] + 0.75 * chord_DA[i] for i in range(3))

dc0 = f.cartesian_point(D3)
dc1 = f.cartesian_point(q25_3)
dc2 = f.cartesian_point(mid3)
dc3 = f.cartesian_point(gap3)       # 1.5-unit positional gap = C-1 break
dc4 = f.cartesian_point(q75_3)
dc5 = f.cartesian_point(apex_3d)

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('whole_degen_empty_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# PCurve: entirely at u=0, from (0.0, 1.0) down to (0.0, 0.0).
pc_start = f.cartesian_point((0.0, 1.0))
pc_dir   = f.direction((0.0, -1.0))   # decreasing v (toward apex)
pc_vec   = f.vector(pc_dir, 1.0)
pc_line  = f.line(pc_start, pc_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('whole_degen_empty_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('whole_degen_empty_pc',#{cone.eid},#{defrep.eid})")
sc_DA = f._emit_raw(
    f"SURFACE_CURVE('whole_degen_empty_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_DA = f._emit_raw(
    f"EDGE_CURVE('whole_degen_empty_edge',#{v_D.eid},#{v_apex.eid},#{sc_DA.eid},.T.)"
)

# Triangle: apex→B, B→D, D→apex(defect)
loop = f.edge_loop([
    f.oriented_edge(e_AB, True),
    f.oriented_edge(e_BD, True),
    f.oriented_edge(e_DA, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
