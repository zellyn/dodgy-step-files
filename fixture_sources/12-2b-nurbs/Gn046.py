"""Gn046 — ShapeAnalysis_Curve.IsPlanar near-coplanar at tolerance boundary.

Catalog claim: 4-point cubic B-spline where 3 control points are coplanar and
the 4th is offset by exactly 1.0E-7 (planarity tolerance). IsPlanar() returns
true at the tolerance boundary despite curve being technically non-planar.

OCC behavior: silently accepts or rejects; shape_null=True expected. Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 4 CPs (minimum clamped degree-3).
    Knots (0.0,1.0) mults (4,4) sum=8=3+4+1=8 ✓.
    Three CPs in XY plane: (0,0,0), (1,0,0), (2,0,0).
    Fourth CP offset: (3, 0, 1.0E-7) — exactly at planarity tolerance.
    IsPlanar() computes max CP distance to best-fit plane; at 1.0E-7 the
    comparison (distance <= tolerance) returns true due to floating-point
    boundary, misclassifying a non-planar curve as planar.
  - C-1 break in 3D edge curve (1.5-unit gap at t=0.5) drives shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree 3 4-CP; CP[3]=(3,0,1E-7)
    sits at exact planarity-tolerance distance from XY plane; IsPlanar() boundary
    comparison returns true (false positive) classifying non-planar curve as planar.
  - C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn046",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree 3 4-CP: "
        "knots (0.0,1.0) mults (4,4) sum=8=3+4+1 ✓; "
        "CPs (0,0,0),(1,0,0),(2,0,0),(3,0,1.0E-7); "
        "CP[3] Z-offset=1.0E-7 equals planarity tolerance; "
        "ShapeAnalysis_Curve.IsPlanar() boundary comparison (distance<=tol) "
        "returns true (false positive); non-planar curve misclassified as planar; "
        "C-1 break in 3D edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

# ── HOST SURFACE: flat plane ──────────────────────────────────────────────────
plane_origin = f.cartesian_point((0.0, 0.0, 0.0))
plane_normal = f.direction((0.0, 0.0, 1.0))
plane_ref    = f.direction((1.0, 0.0, 0.0))
plane_ax2 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('plane_ax',#{plane_origin.eid},#{plane_normal.eid},#{plane_ref.eid})"
)
surf = f._emit_raw(f"PLANE('flat_plane',#{plane_ax2.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: near-coplanar cubic B-spline ──────────────────────────
# Degree 3, 4 CPs (minimum clamped): knots (0.0,1.0) mults (4,4)
# 3 CPs in XY plane; CP[3] offset by 1E-7 in Z (exact planarity tolerance).
np0 = f.cartesian_point((0.0, 0.0, 0.0))
np1 = f.cartesian_point((1.0, 0.0, 0.0))
np2 = f.cartesian_point((2.0, 0.0, 0.0))
np3 = f.cartesian_point((3.0, 0.0, 1.0E-7))  # THE DEFECT: Z = 1e-7

near_planar_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn046_near_planar',3,"
    f"(#{np0.eid},#{np1.eid},#{np2.eid},#{np3.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,4),(0.0,1.0),.UNSPECIFIED.)"
)

# ── C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 ─────────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.25, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit C-1 gap
dc4 = f.cartesian_point((4.75, 0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn046_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn046_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn046_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn046_pc_ent',#{surf.eid},#{defrep.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('gn046_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn046_edge',#{v_a.eid},#{v_b.eid},#{sc.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, length)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (5.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 5.0, 0.0), (-1.,0.,0.), (5.0, 5.0), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 5.0), (0.,-1.), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
