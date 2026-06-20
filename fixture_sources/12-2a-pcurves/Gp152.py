"""Gp152 — ShapeAnalysis_Edge.CheckVerticesWithPCurve location_transformation_semantics

Catalog claim: Edge bound to surface with non-identity location; P-curve
endpoint transform omitted from vertex distance check. Analyzer fails to
apply surface location xform to V1/V2 projections. Reproduces line 539 defect.

STEP mechanism (literal):
  - PLANE surface with non-identity AXIS2_PLACEMENT_3D location (translated
    and rotated relative to origin) bound to an edge with a PCurve.
  - THE CATALOG MECHANISM: CheckVerticesWithPCurve at OCCT line 539 projects
    PCurve endpoints onto the 3D surface to compare with V1/V2 positions.
    When the surface has a non-identity location (translation + rotation),
    the projection must apply the surface's location transform. The defect:
    the transform is omitted from the V1/V2 projection, so the projected
    3D position is computed in the surface's local frame rather than world
    frame. The vertex distance check then compares local-frame projection
    to world-frame vertex position, yielding a spurious error that is
    silently suppressed (or a real error that is not caught depending on
    the tolerance path). location_transformation_semantics.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE surface at non-identity location (translated
    by (10,20,5) and rotated 45° about Z); PCurve endpoints project into
    local frame; CheckVerticesWithPCurve line 539 omits location xform;
    vertex V1/V2 in world frame compared against local-frame projection;
    location_transformation_semantics.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp152",
    defect=(
        "PLANE at non-identity location: origin=(10,20,5) Z=(0,0,1) X=(0.707,0.707,0) "
        "(rotated 45deg about Z + translated); "
        "defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "PCurve B_SPLINE_CURVE_WITH_KNOTS degree-2 endpoints in local UV frame; "
        "CheckVerticesWithPCurve line 539 projects PCurve endpoints onto surface "
        "without applying surface location transform; "
        "V1/V2 in world frame compared to local-frame projection; "
        "location_transformation_semantics; shape_null=True"
    ),
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Host surface: PLANE with non-identity location.
# Origin at (10, 20, 5), Z-axis = (0,0,1), X-axis = (cos45, sin45, 0) = (sqrt2/2, sqrt2/2, 0).
# This rotates the UV frame 45° about Z and translates to (10,20,5).
s2 = math.sqrt(2.0) / 2.0
surf_orig = f.cartesian_point((10.0, 20.0, 5.0))
surf_zdir = f.direction((0.0, 0.0, 1.0))
surf_xdir = f.direction((s2, s2, 0.0))   # 45° rotation about Z
surf_plc  = f.axis2_placement_3d(surf_orig, surf_zdir, surf_xdir)
surf = f.plane(surf_plc)

# Face corners in WORLD coordinates.
# The plane's local frame: origin=(10,20,5), X=(s2,s2,0), Y=(-s2,s2,0).
# A point at local UV=(u,v) maps to world = (10,20,5) + u*(s2,s2,0) + v*(-s2,s2,0).
# Rectangle in local UV: u in [0,5], v in [0,2].
# World corners:
#   A=(u=0,v=0): (10,20,5)
#   B=(u=5,v=0): (10+5*s2, 20+5*s2, 5) ≈ (13.536, 23.536, 5)
#   C=(u=5,v=2): (10+5*s2-2*s2, 20+5*s2+2*s2, 5) = (10+3*s2, 20+7*s2, 5) ≈ (12.121,24.950,5)
#   D=(u=0,v=2): (10-2*s2, 20+2*s2, 5) ≈ (8.586, 21.414, 5)
p_a = f.cartesian_point((10.0,          20.0,          5.0))
p_b = f.cartesian_point((10.0 + 5*s2,   20.0 + 5*s2,   5.0))
p_c = f.cartesian_point((10.0 + 3*s2,   20.0 + 7*s2,   5.0))
p_d = f.cartesian_point((10.0 - 2*s2,   20.0 + 2*s2,   5.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

def mk_line_edge_with_pc(vs, ve, p3w, d3t, len3, p2t, d2t, len2=None):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    if len2 is None:
        len2 = len3
    p3e = f.cartesian_point(p3w)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len2); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# World-frame directions for non-defect edges:
# Right (B→C): world dir = (-s2, s2, 0), len=2, UV dir=(0,1), len_uv=2
e_right = mk_line_edge_with_pc(
    v_b, v_c,
    (10.0 + 5*s2, 20.0 + 5*s2, 5.0), (-s2, s2, 0.), 2.0,
    (5.0, 0.0), (0., 1.), 2.0
)
# Top (C→D): world dir = (-s2, -s2, 0), len=5, UV dir=(-1,0), len_uv=5
e_top = mk_line_edge_with_pc(
    v_c, v_d,
    (10.0 + 3*s2, 20.0 + 7*s2, 5.0), (-s2, -s2, 0.), 5.0,
    (5.0, 2.0), (-1., 0.), 5.0
)
# Left (D→A): world dir = (s2, -s2, 0), len=2, UV dir=(0,-1), len_uv=2
e_left = mk_line_edge_with_pc(
    v_d, v_a,
    (10.0 - 2*s2, 20.0 + 2*s2, 5.0), (s2, -s2, 0.), 2.0,
    (0.0, 2.0), (0., -1.), 2.0
)

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# Note: the 3D geometry is in world coordinates but uses a C-1 break to
# force OCC to reject the shape. The break is in-world.
dc0 = f.cartesian_point((10.0,             20.0,             5.0))
dc1 = f.cartesian_point((10.0 + 1.875*s2,  20.0 + 1.875*s2,  5.0))  # quarter along v_a→v_b
dc2 = f.cartesian_point((11.5,             21.5,             5.0))   # C-1 break point
dc3 = f.cartesian_point((13.0,             23.0,             5.0))   # 1.5-unit gap (world)
dc4 = f.cartesian_point((10.0 + 4.0*s2,    20.0 + 4.0*s2,    5.0))
dc5 = f.cartesian_point((10.0 + 5*s2,      20.0 + 5*s2,      5.0))  # = p_b

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('location_xform_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve B-spline degree-2 in LOCAL UV frame.
# UV endpoints: (0,0) and (5,0) — correct in local frame (u along X_local).
# CheckVerticesWithPCurve (line 539): projects PCurve endpoint (0,0) onto
# surface to get 3D position. Without location transform: gets local (0,0,0).
# V1 is at world (10,20,5) — different from local (0,0,0). The distance check
# compares these two different-frame coordinates, producing a false discrepancy
# that is silently accepted (location_transformation_semantics).
pp0 = f.cartesian_point((0.0, 0.0))   # UV start = (u=0, v=0) — local frame
pp1 = f.cartesian_point((2.5, 0.0))   # UV midpoint
pp2 = f.cartesian_point((5.0, 0.0))   # UV end = (u=5, v=0) — local frame

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('location_xform_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('location_xform_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('location_xform_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('location_xform_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('location_xform_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
