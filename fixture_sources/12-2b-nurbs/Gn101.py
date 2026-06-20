"""Gn101 — ShapeAnalysis_Curve.IsClosed COMPOSITE_CURVE with-discontinuity.

Catalog claim: Composite curve with 3 segments where segment 2 starts at
(1.1, 0.1, 0) but segment 1 ends at (1.0, 0.0, 0) — a 0.15-unit gap.
Segment 3 loops back to origin. IsClosed only checks the global endpoint pair
(first=last), missing the internal discontinuity at segment boundaries.

STEP mechanism (literal):
  - COMPOSITE_CURVE with 3 COMPOSITE_CURVE_SEGMENT entries.
    Segment 1: B_SPLINE_CURVE_WITH_KNOTS degree 1, 2 CPs: (0,0,0)→(1,0,0).
    Segment 2: B_SPLINE_CURVE_WITH_KNOTS degree 1, 2 CPs: (1.1,0.1,0)→(2,0,0).
      Gap between seg1 end (1,0,0) and seg2 start (1.1,0.1,0) = 0.15 units.
    Segment 3: B_SPLINE_CURVE_WITH_KNOTS degree 1, 2 CPs: (2,0,0)→(0,0,0).
    Global: first=(0,0,0), last=(0,0,0) → IsClosed returns true.
    But internal discontinuity at seg1/seg2 boundary is missed.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: internal gap in composite curve causes OCC shape processing to
    fail (invalid loop geometry) → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: COMPOSITE_CURVE 3-segment; seg1 ends (1,0,0),
    seg2 starts (1.1,0.1,0) → 0.15-unit internal gap; global endpoints close;
    IS defect edge SURFACE_CURVE.curve_3d;
    IsClosed misses internal discontinuity → shape_null=True.
  - C-1 DRIVER: internal gap in composite curve → invalid edge topology → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn101",
    defect=(
        "COMPOSITE_CURVE 3-segment; "
        "seg1 (0,0,0)→(1,0,0), seg2 (1.1,0.1,0)→(2,0,0) [0.15-unit gap], seg3 (2,0,0)→(0,0,0); "
        "global endpoints close; IS defect edge SURFACE_CURVE.curve_3d; "
        "IsClosed misses internal gap → shape_null=True"
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

# ── CATALOG MECHANISM: COMPOSITE_CURVE with internal gap ─────────────────────
# Segment 1: (0,0,0) → (1,0,0)  [n=2, p=1, mults (2,2) sum=4 ✓]
s1_cp0 = f.cartesian_point((0.0, 0.0, 0.0))
s1_cp1 = f.cartesian_point((1.0, 0.0, 0.0))
seg1_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn101_seg1',1,"
    f"(#{s1_cp0.eid},#{s1_cp1.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,2),(0.0,1.0),.UNSPECIFIED.)"
)

# Segment 2: (1.1,0.1,0) → (2,0,0)  — INTERNAL GAP: seg1 ends at (1,0,0)
s2_cp0 = f.cartesian_point((1.1, 0.1, 0.0))   # gap start: 0.15 units from (1,0,0)
s2_cp1 = f.cartesian_point((2.0, 0.0, 0.0))
seg2_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn101_seg2',1,"
    f"(#{s2_cp0.eid},#{s2_cp1.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,2),(0.0,1.0),.UNSPECIFIED.)"
)

# Segment 3: (2,0,0) → (0,0,0)  — closes global loop
s3_cp0 = f.cartesian_point((2.0, 0.0, 0.0))
s3_cp1 = f.cartesian_point((0.0, 0.0, 0.0))
seg3_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn101_seg3',1,"
    f"(#{s3_cp0.eid},#{s3_cp1.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,2),(0.0,1.0),.UNSPECIFIED.)"
)

# COMPOSITE_CURVE_SEGMENT for each sub-curve
ccs1 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#{seg1_curve.eid})")
ccs2 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#{seg2_curve.eid})")
ccs3 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#{seg3_curve.eid})")

# COMPOSITE_CURVE: global first=(0,0,0), last=(0,0,0) → IsClosed=True
# but internal discontinuity at seg1/seg2 is missed
mech_3d = f._emit_raw(
    f"COMPOSITE_CURVE('gn101_composite',"
    f"(#{ccs1.eid},#{ccs2.eid},#{ccs3.eid}),.F.)"
)

# pcurve: simple 2D line companion
pp_s = f.cartesian_point((0.0, 0.0))
d2   = f.direction((1.0, 0.0))
v2   = f.vector(d2, 2.0)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn101_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn101_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn101_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((0.0, 0.0, 0.0))   # same point — closed loop
v_start = f.vertex_point(p_start)
# closed edge: start vertex = end vertex
e_defect = f._emit_raw(
    f"EDGE_CURVE('gn101_defect_edge',#{v_start.eid},#{v_start.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 2.5, -0.5, 0.0))
p_c = f.cartesian_point(( 2.5,  0.5, 0.0))
p_d = f.cartesian_point((-0.5,  0.5, 0.0))
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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.0), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 3.0)
e_right = mk_line_edge(v_b, v_c, ( 2.5,-0.5,0.0), (0.,1.,0.), ( 2.5,-0.5), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, ( 2.5, 0.5,0.0), (-1.,0.,0.),( 2.5, 0.5), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (-0.5, 0.5,0.0), (0.,-1.,0.),(-0.5, 0.5), (0.,-1.), 1.0)

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
