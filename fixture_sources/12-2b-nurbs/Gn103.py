"""Gn103 — ShapeAnalysis_Curve.FillBndBox bspline-bezier-mixed.

Catalog claim: Composite curve mixing a degree-3 B-spline segment (requires
4 samples) with a degree-2 Bezier segment (requires 3 samples). FillBndBox
dispatches per-segment but applies B-spline sample count to the Bezier
component, undersampling the Bezier's curvature extrema.

STEP mechanism (literal):
  - COMPOSITE_CURVE with 2 segments:
    Segment 1: B_SPLINE_CURVE_WITH_KNOTS degree 3, 4 CPs (0,0,0)→(3,0,0).
      n=4, p=3 → n+p+1=8. mults (4,4) knots (0.0,1.0) sum=8 ✓.
    Segment 2: BEZIER_CURVE degree 2, 3 CPs (3,0,0)→(5,2,0)→(7,0,0).
      Bezier encoded as B_SPLINE_CURVE_WITH_KNOTS degree 2, mults (3,3)
      knots (0.0,1.0) sum=6 ✓; CPs form arc with curvature peak at mid-param.
    Segments connect at (3,0,0). FillBndBox applies degree-3 sample count
    (4 samples) to segment 2 (degree-2 Bezier), missing peak at t≈0.5.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: mixed-degree composite curve causes OCC shape processing
    to fail (bad bounding box → reject) → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: COMPOSITE_CURVE 2-segment; seg1 B-spline degree-3,
    seg2 Bezier degree-2; FillBndBox misapplies sample count to Bezier;
    IS defect edge SURFACE_CURVE.curve_3d; bounding-box error → shape_null=True.
  - C-1 DRIVER: mixed-degree composite → bounding-box undercount → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn103",
    defect=(
        "COMPOSITE_CURVE 2-segment; "
        "seg1 B_SPLINE_CURVE_WITH_KNOTS degree=3 4-pole mults (4,4) knots (0.0,1.0) sum=8 ✓; "
        "seg2 Bezier degree=2 3-pole mults (3,3) knots (0.0,1.0) sum=6 ✓; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "FillBndBox applies degree-3 sample count to Bezier → misses curvature peak → shape_null=True"
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

# ── CATALOG MECHANISM: COMPOSITE_CURVE with B-spline + Bezier segments ────────
# Segment 1: degree-3 B-spline, 4 CPs — gentle S-curve (0,0,0)→(3,0,0)
s1_cp0 = f.cartesian_point((0.0, 0.0, 0.0))
s1_cp1 = f.cartesian_point((1.0, 0.5, 0.0))
s1_cp2 = f.cartesian_point((2.0,-0.5, 0.0))
s1_cp3 = f.cartesian_point((3.0, 0.0, 0.0))
seg1_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn103_seg1',3,"
    f"(#{s1_cp0.eid},#{s1_cp1.eid},#{s1_cp2.eid},#{s1_cp3.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,4),(0.0,1.0),.UNSPECIFIED.)"
)

# Segment 2: degree-2 Bezier arc (3,0,0)→(5,2,0)→(7,0,0) — arc with upward bulge
# Encoded as B_SPLINE_CURVE_WITH_KNOTS degree 2, mults (3,3) sum=6 ✓
s2_cp0 = f.cartesian_point((3.0, 0.0, 0.0))
s2_cp1 = f.cartesian_point((5.0, 2.0, 0.0))  # curvature peak at t≈0.5
s2_cp2 = f.cartesian_point((7.0, 0.0, 0.0))
seg2_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn103_seg2_bezier',2,"
    f"(#{s2_cp0.eid},#{s2_cp1.eid},#{s2_cp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

ccs1 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#{seg1_curve.eid})")
ccs2 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#{seg2_curve.eid})")

mech_3d = f._emit_raw(
    f"COMPOSITE_CURVE('gn103_composite',"
    f"(#{ccs1.eid},#{ccs2.eid}),.F.)"
)

# pcurve: 2D line companion spanning the defect edge
pp_s = f.cartesian_point((0.0, 0.0))
d2   = f.direction((1.0, 0.0))
v2   = f.vector(d2, 7.0)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn103_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn103_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn103_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((7.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn103_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 7.5, -0.5, 0.0))
p_c = f.cartesian_point(( 7.5,  2.5, 0.0))
p_d = f.cartesian_point((-0.5,  2.5, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

def mk_line_edge(vs_, ve_, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3_ = f.vector(d3e, length)
    l3  = f.line(p3e, v3_)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2_ = f.vector(d2e, length)
    l2_ = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs_.eid},#{ve_.eid},#{sc_.eid},.T.)")

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.0), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 8.0)
e_right = mk_line_edge(v_b, v_c, ( 7.5,-0.5,0.0), (0.,1.,0.), ( 7.5,-0.5), (0.,1.), 3.0)
e_top   = mk_line_edge(v_c, v_d, ( 7.5, 2.5,0.0), (-1.,0.,0.),( 7.5, 2.5), (-1.,0.), 8.0)
e_left  = mk_line_edge(v_d, v_a, (-0.5, 2.5,0.0), (0.,-1.,0.),(-0.5, 2.5), (0.,-1.), 3.0)

outer_loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
inner_loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
])

outer_bound = f.face_outer_bound(outer_loop)
inner_bound = f._emit_raw(f"FACE_BOUND('inner_bound',#{inner_loop.eid},.T.)")

face  = f.advanced_face([outer_bound, inner_bound], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
