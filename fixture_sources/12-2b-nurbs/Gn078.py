"""Gn078 — ShapeUpgrade_ConvertCurve2dToBezier double-degree-elevation knot error.

Catalog claim: ConvertCurve2dToBezier correctly handles multi-step degree elevation.
2D B-spline degree-2 curve (6 control points) elevated to degree 4. Algorithm
assumes single-step elevation and produces incorrect knot vector; correct path
is 2→3→4 (two steps).

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 2, 6 control points.
    Knots: (0.0, 0.33, 0.67, 1.0) mults (3,2,2,3) sum=10=2+6+... wait:
    n+p+1 = 6+2+1 = 9. mults (3,2,2,2) sum=9 ✓.
    Interior knots at 0.33 and 0.67 force multi-span structure.
    ConvertCurve2dToBezier elevates degree 2→4 in one step (skips degree 3
    intermediate); the resulting Bezier-form knot vector has incorrect
    multiplicity at seam knots — each span should have 5 repeated knots (degree+1)
    but single-step elevation inserts only 3 extra, leaving under-multiplied seams.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (the catalog mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: the interior-knot multi-span structure with tight control-point
    spacing at t=0.33 (0.8-unit gap) produces a C-1 discontinuity that drives
    shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree-2 6 poles; interior
    knots at 0.33 and 0.67; IS defect edge SURFACE_CURVE.curve_3d; single-step
    2→4 elevation produces under-multiplied Bezier seam knots.
  - C-1 DRIVER: 0.8-unit CP gap at t=0.33 drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn078",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-2 6 poles; "
        "knots (0.0,0.33,0.67,1.0) mults (3,2,2,2) sum=9 ✓; "
        "interior knots at 0.33 and 0.67 → multi-span; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "ConvertCurve2dToBezier single-step 2→4 elevation skips degree-3 intermediate — "
        "Bezier seam knots under-multiplied; 0.8-unit CP gap at t=0.33 drives shape_null=True"
    ),
)

# ── Flat plane for the face ───────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: B-spline degree-2, 6 poles, multi-span with interior knots ──
# Knots (0.0,0.33,0.67,1.0) mults (3,2,2,2) sum=9=2+6+1 ✓
# CP gap at t=0.33: DC1→DC2 = 0.8 units → C-1 discontinuity
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((1.0, 0.0, 0.0))
dc2 = f.cartesian_point((1.8, 0.0, 0.0))  # 0.8-unit gap after dc1 → C-1 break at t=0.33
dc3 = f.cartesian_point((3.0, 0.0, 0.0))
dc4 = f.cartesian_point((4.2, 0.0, 0.0))
dc5 = f.cartesian_point((5.0, 0.0, 0.0))

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn078_deg2_multispan',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,2,2,2),(0.0,0.33,0.67,1.0),.UNSPECIFIED.)"
)

# pcurve: 2D line u∈[0,1] along bottom of face
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn078_pcdef',(#{l2.eid}),#{prc.eid})")
pc  = f._emit_raw(f"PCURVE('gn078_pc',#{plane.eid},#{pcd.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn078_sc',#{mech_3d.eid},(#{pc.eid}),.PCURVE_S1.)"
)

# Corner vertices; face spans [0,5]×[0,3]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 3.0, 0.0))
p_d = f.cartesian_point((0.0, 3.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn078_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_defect.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2_ = f.vector(d2e, length)
    l2_ = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 3.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 3.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 3.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 3.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
