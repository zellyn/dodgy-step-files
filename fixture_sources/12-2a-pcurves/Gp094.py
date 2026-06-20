"""Gp094 — ShapeAnalysis_Edge.CheckOverlapping curves-tangent-at-endpoint.

Catalog claim: Two edges meeting tangentially at shared endpoint;
CheckOverlapping's interior-intersection test ignores boundary tangency.
Fixture has LINE+B_SPLINE_CURVE edges meeting at common vertex with tangent
alignment.

STEP mechanism (literal):
  - PLANE face with two adjacent edges sharing a vertex at (2, 0, 0).
  - Edge 1 (bottom-left): LINE from (0,0,0) to (2,0,0). Direction: (1,0,0).
  - Edge 2 (bottom-right): B_SPLINE_CURVE degree-2 from (2,0,0) to (4,0,0).
    Control points chosen so the tangent at the start (t=0) is (1,0,0) —
    matching the LINE direction. The two curves share both position AND tangent
    at their shared vertex (2,0,0).
  - THE CATALOG MECHANISM: CheckOverlapping scans interior parameter samples
    for curve-curve intersection. The LINE and B-spline are tangent at the
    boundary point (2,0,0) but have no interior overlap. The boundary tangency
    makes them look like "about to overlap" candidates; the algorithm treats
    this as an overlap candidate but resolves correctly to no interior overlap.
  - Geometry is clean: both curves lie on the Z=0 plane, face loads correctly.

NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp094",
    defect=(
        "PLANE Z=0; two edges share vertex at (2,0,0): LINE (0,0,0)→(2,0,0) "
        "direction (1,0,0) and B_SPLINE_CURVE (2,0,0)→(4,0,0) with tangent "
        "(1,0,0) at t=0; tangent alignment at shared endpoint triggers "
        "CheckOverlapping's interior-intersection overlap candidate; resolves "
        "correctly (no interior overlap); shape(1)/shape(1)"
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

# Vertices: rectangle [0,4] x [0,2], with midpoint at (2,0,0) on the bottom
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_m = f.cartesian_point((2.0, 0.0, 0.0))   # shared tangency vertex
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a)
v_m = f.vertex_point(p_m)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

# Helper: build clean SURFACE_CURVE edge with pcurve on plane
def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Context edges (right side, top, left) with clean pcurves
e_right = mk_edge_with_pc(v_b, v_c, (4.0, 0.0, 0.0), (0., 1., 0.), 2.0, (4.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (4.0, 2.0, 0.0), (-1., 0., 0.), 4.0, (4.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGES — bottom split into two tangent segments ─────────────────────

# Edge 1: LINE from (0,0,0) to (2,0,0). Clean with pcurve.
e_bot_left = mk_edge_with_pc(
    v_a, v_m,
    (0.0, 0.0, 0.0), (1., 0., 0.), 2.0,
    (0.0, 0.0),      (1., 0.),
)

# Edge 2 (THE CATALOG MECHANISM): B_SPLINE_CURVE from (2,0,0) to (4,0,0).
# Degree 2, 3 control points: CP[0]=(2,0,0), CP[1]=(3,0,0), CP[2]=(4,0,0).
# Tangent at t=0: CP[1]-CP[0] = (1,0,0) — matches the LINE direction at (2,0,0).
# This means the LINE and B-spline are tangent at their shared vertex.
# Interior of B-spline is strictly to the right of (2,0,0) — no interior overlap.
bc0 = f.cartesian_point((2.0, 0.0, 0.0))
bc1 = f.cartesian_point((3.0, 0.0, 0.0))  # tangent direction (1,0,0) at t=0
bc2 = f.cartesian_point((4.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('tangent_bspline',2,"
    f"(#{bc0.eid},#{bc1.eid},#{bc2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

# PCurve: matching B-spline in UV space (on Z=0 plane UV=(x,y))
pc0 = f.cartesian_point((2.0, 0.0))
pc1 = f.cartesian_point((3.0, 0.0))
pc2 = f.cartesian_point((4.0, 0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('tangent_bspline_pc',2,"
    f"(#{pc0.eid},#{pc1.eid},#{pc2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_right_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('bot_right_pc',#{surf.eid},#{defrep.eid})")
sc_bot_right = f._emit_raw(
    f"SURFACE_CURVE('bot_right_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot_right = f._emit_raw(
    f"EDGE_CURVE('tangent_bspline_edge',#{v_m.eid},#{v_b.eid},#{sc_bot_right.eid},.T.)"
)

# Loop: bot_left + bot_right + right + top + left
loop = f.edge_loop([
    f.oriented_edge(e_bot_left,  True),
    f.oriented_edge(e_bot_right, True),
    f.oriented_edge(e_right,     True),
    f.oriented_edge(e_top,       True),
    f.oriented_edge(e_left,      True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
