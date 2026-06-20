"""Gn085 — ShapeUpgrade_ConvertSurfaceToBezierBasis cylinder-conversion.

Catalog claim: Cylinder converted to Bezier patches; conversion doesn't propagate
rational weights from cylinder's analytic form — resulting patches have all weights=1.0
instead of sqrt(2)/2 for the 45-degree control points.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree u=2, v=1, 3x2 net (quarter-cylinder).
    U: n_u=3, degree 2 → n+p+1=3+2+1=6. Knots (0.0,1.0) mults (3,3) sum=6 ✓.
    V: n_v=2, degree 1 → n+p+1=2+1+1=4. Knots (0.0,1.0) mults (2,2) sum=4 ✓.
    Control points: rational quarter-circle arc with weights [1.0, sqrt(2)/2, 1.0]
    for u but stored as uniform weights (all 1.0) — exactly the conversion error.
    IS the ADVANCED_FACE.face_geometry (the catalog mechanism IS the face surface).
  - C-1 DRIVER: bottom edge B-spline with 1.5-unit CP gap at t=0.5 drives
    shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS u_degree=2 v_degree=1 3×2 net;
    quarter-cylinder arc CP geometry with all weights=1.0 (missing sqrt(2)/2);
    U knots (0.0,1.0) mults (3,3); IS the ADVANCED_FACE.face_geometry;
    ConvertSurfaceToBezierBasis fails to restore rational weights → geometry error.
  - C-1 DRIVER: bottom edge B-spline 1.5-unit CP gap drives shape_null=True.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gn085",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS u_degree=2 v_degree=1 3x2 net; "
        "quarter-cylinder CPs radius=1.0 with uniform weights=1.0 (should be sqrt(2)/2 at mid); "
        "U knots (0.0,1.0) mults (3,3) sum=6 ✓; "
        "V knots (0.0,1.0) mults (2,2) sum=4 ✓; "
        "IS the ADVANCED_FACE.face_geometry; "
        "ConvertSurfaceToBezierBasis doesn't propagate rational weights → wrong geometry; "
        "C-1 break in bottom edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree u=2 v=1, 3×2 control net ───────────────
# Quarter-cylinder arc: (1,0,z) → (1/sqrt(2), 1/sqrt(2), z) → (0,1,z)
# All weights 1.0 — the defect (should be 1.0, sqrt(2)/2, 1.0 for rational arc)
# U: n_u=3, degree 2 → n+p+1=6. knots (0.0,1.0) mults (3,3) sum=6 ✓
# V: n_v=2, degree 1 → n+p+1=4. knots (0.0,1.0) mults (2,2) sum=4 ✓
# Control points: row 0 at z=0, row 1 at z=1 (cylinder height=1)
# Quarter-circle arc CPs: (1,0), (1,1), (0,1) [mid-point at 45-deg needs weight sqrt(2)/2]

cp_coords = [
    # (x, y, z)
    (1.0, 0.0, 0.0),                      # u=0, v=0: start of arc, bottom
    (1.0, 1.0, 0.0),                      # u=1, v=0: 45-deg control point (weight error)
    (0.0, 1.0, 0.0),                      # u=2, v=0: end of arc, bottom
    (1.0, 0.0, 1.0),                      # u=0, v=1: start of arc, top
    (1.0, 1.0, 1.0),                      # u=1, v=1: 45-deg control point (weight error)
    (0.0, 1.0, 1.0),                      # u=2, v=1: end of arc, top
]

cps = [f.cartesian_point(c) for c in cp_coords]

# Net is 3 columns (u) × 2 rows (v): rows are v=0 and v=1
row0_ids = f"(#{cps[0].eid},#{cps[1].eid},#{cps[2].eid})"
row1_ids = f"(#{cps[3].eid},#{cps[4].eid},#{cps[5].eid})"
cp_net = f"({row0_ids},{row1_ids})"

surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn085_cyl_surf',2,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(2,2),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── C-1 DRIVER: bottom edge B-spline with 1.5-unit gap at t=0.5 ──────────────
# Bottom arc of cylinder: x=1→0 along quarter circle (approximated as B-spline)
dc0 = f.cartesian_point((1.0, 0.0, 0.0))
dc1 = f.cartesian_point((0.8, 0.2, 0.0))
dc2 = f.cartesian_point((0.5, 0.5, 0.0))
dc3 = f.cartesian_point((2.0, 0.5, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((0.2, 0.8, 0.0))
dc5 = f.cartesian_point((0.0, 1.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn085_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.17, 0.0))
pp2 = f.cartesian_point((0.33, 0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.67, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn085_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn085_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn085_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn085_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# Vertices at arc endpoints: start=(1,0,0), end=(0,1,0)
# Top arc at z=1: end=(0,1,1), back=(1,0,1)
p_a = f.cartesian_point((1.0, 0.0, 0.0))   # arc start bottom
p_b = f.cartesian_point((0.0, 1.0, 0.0))   # arc end bottom
p_c = f.cartesian_point((0.0, 1.0, 1.0))   # arc end top
p_d = f.cartesian_point((1.0, 0.0, 1.0))   # arc start top
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn085_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
    pc_  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

# Right edge: b→c (v direction at u=1.0, i.e., u=1 in param)
e_right = mk_line_edge(v_b, v_c, (0.0, 1.0, 0.0), (0.,0.,1.), (1.0, 0.0), (0.,1.), 1.0)
# Top arc: c→d (u direction at v=1.0)
e_top   = mk_line_edge(v_c, v_d, (0.0, 1.0, 1.0), (1.,-1.,0.), (1.0, 1.0), (-1.,0.), 1.0)
# Left edge: d→a (v direction at u=0.0)
e_left  = mk_line_edge(v_d, v_a, (1.0, 0.0, 1.0), (0.,0.,-1.), (0.0, 1.0), (0.,-1.), 1.0)

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
