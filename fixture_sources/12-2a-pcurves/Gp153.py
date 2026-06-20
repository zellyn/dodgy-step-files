"""Gp153 — ShapeAnalysis_Edge.CheckCurve3dWithPCurve planar_surface_bypass

Catalog claim: 3D line and 2D P-curve endpoints mismatch on planar surface;
consistency check skipped for plane geometry. Analyzer silently passes despite
V2 at (3,1,0) != P-curve projection. Reproduces line 384 defect.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge wrapped in SURFACE_CURVE.
  - THE CATALOG MECHANISM (planar_surface_bypass): CheckCurve3dWithPCurve at
    line 384 checks surface type before sampling. For PLANE surfaces, the check
    is bypassed entirely: planar surface geometry is considered trivially
    consistent without sampling. The defect edge has a 3D LINE from A=(0,0,0)
    to B=(3,0,0) but the PCurve LINE in UV ends at V=(3,1) — mismatched Y
    component means V2_projected != V2_3D by 1 unit. The consistency check is
    never reached because the PLANE bypass fires first. OCC chokes on the
    resulting topological inconsistency → shape_null=True.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE surface type triggers bypass at line 384;
    3D LINE endpoint at (3,0,0); PCurve LINE endpoint at UV=(3,1) — V-component
    mismatch; CheckCurve3dWithPCurve sampling skipped for plane;
    planar_surface_bypass axis.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp153",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "PCurve LINE in UV from (0,0) direction (1,0.333) — endpoint at UV=(3,1); "
        "3D endpoint at (3,0,0) but PCurve projects to (3,1,0) — 1-unit V mismatch; "
        "CheckCurve3dWithPCurve (line 384) skips sampling on PLANE surface type; "
        "planar_surface_bypass: consistency check omitted; OCC chokes; "
        "shape_null=True"
    ),
)

# Host surface: PLANE Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners: rectangle [0,3] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge_with_pc(v_b, v_c, (3.0, 0.0, 0.0), (0., 1., 0.), 2.0, (3.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (3.0, 2.0, 0.0), (-1., 0., 0.), 3.0, (3.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((2.5,  0.0, 0.0))
dc5 = f.cartesian_point((3.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('planar_bypass_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve LINE with V-component mismatch.
# PCurve goes from UV=(0,0) in direction (1, 0.333...) with length 3.
# At t=1: UV = (0,0) + 3*(1, 0.333) = (3, 1).
# 3D end vertex v_b is at (3,0,0) but PCurve endpoint projects to (3,1,0).
# CheckCurve3dWithPCurve (line 384): PLANE surface type → bypass fires,
# sampling skipped entirely. The 1-unit V mismatch at V2 is never detected.
import math
# direction (3,1) normalised magnitude = sqrt(10); we use scaled vector length 3
pcurve_dir_len = math.sqrt(10.0)
pc_start = f.cartesian_point((0.0, 0.0))
pc_dir   = f.direction((3.0 / pcurve_dir_len, 1.0 / pcurve_dir_len))
pc_vec   = f.vector(pc_dir, pcurve_dir_len)   # reaches (3,1) at t=1
pc_line  = f.line(pc_start, pc_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('planar_bypass_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('planar_bypass_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('planar_bypass_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('planar_bypass_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
