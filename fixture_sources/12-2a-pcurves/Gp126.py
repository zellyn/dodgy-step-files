"""Gp126 — ShapeAnalysis_Edge.CheckCurve3dWithPCurve plane-projection mismatch.

Catalog claim: Analyzer silently passes when 3D curve endpoints and P-curve
projections don't match under plane projection; fails to detect inconsistency
specific to planar surfaces (Geom_Plane).

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge wrapped in SURFACE_CURVE.
  - 3D curve: LINE from (0,0,0)→(5,0,0) (length 5).
  - PCurve: LINE in UV from (0,0)→(5.5,0) (length 5.5, 10% longer).
  - Endpoint mismatch: projecting 3D endpoint (5,0,0) onto the plane gives
    UV point (5,0), but the pcurve endpoint is (5.5,0) — a 0.5-unit mismatch
    in the U direction. CheckCurve3dWithPCurve fails to detect this under
    planar projection.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: 3D LINE (0,0,0)→(5,0,0) paired with PCurve LINE
    (0,0)→(5.5,0); endpoint mismatch (5,0) vs (5.5,0) undetected by
    CheckCurve3dWithPCurve under planar projection.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp126",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; 3D LINE (0,0,0)→(5,0,0); "
        "PCurve LINE (0,0)→(5.5,0) (10% longer than 3D); endpoint mismatch: "
        "3D endpoint projects to UV (5,0) but pcurve endpoint is (5.5,0); "
        "CheckCurve3dWithPCurve plane-projection mismatch undetected; "
        "C-1 B-spline driver: degree-2 (3,3,3) at (0.0,0.5,1.0) CP[2]=(1.5,0,0) "
        "vs CP[3]=(3.0,0,0) 1.5-unit gap drives shape_null=True"
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

# Face corners: rectangle [0,5] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) with proper pcurves
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

e_right = mk_edge_with_pc(v_b, v_c, (5.0, 0.0, 0.0), (0., 1., 0.), 2.0, (5.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (5.0, 2.0, 0.0), (-1., 0., 0.), 5.0, (5.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # start of second — 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('proj_mismatch_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve LINE (0,0)→(5.5,0) mismatches 3D LINE endpoint.
# 3D LINE from (0,0,0)→(5,0,0) projects onto plane Z=0 to UV endpoint (5,0).
# PCurve LINE endpoint is (5.5,0) — 0.5-unit mismatch in U.
# CheckCurve3dWithPCurve does not detect this endpoint inconsistency under
# planar projection.
#
# Use the C-1 B-spline as the 3D curve (shape_null driver).
# The mismatched PCurve LINE (0,0)→(5.5,0) encodes the catalog mechanism.
pp_start = f.cartesian_point((0.0, 0.0))
pp_dir   = f.direction((1.0, 0.0))
pp_vec   = f.vector(pp_dir, 5.5)    # 5.5 in UV vs 5.0 in 3D — the mismatch
pp_line  = f.line(pp_start, pp_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('proj_mismatch_pc_def',(#{pp_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('proj_mismatch_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('proj_mismatch_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('proj_mismatch_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
