"""Gn073 — ShapeAnalysis_Curve.FillBndBox composite-curve segment switch.

Catalog claim: A COMPOSITE_CURVE with three B-spline segments where the
inter-segment boundary at (1, 1.2) contains a local extremum is not detected
because FillBndBox samples each segment independently and omits joint analysis.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - COMPOSITE_CURVE with three degree-2 B-spline segments.
    Segment 1: (0,0,0)→(0.5,1.2,0)→(1.0,1.2,0) — ends at y=1.2.
    Segment 2: (1.0,1.2,0)→(1.5,1.5,0)→(2.0,0.8,0) — peaks at y≈1.5 near (1.5,1.5,0).
    Segment 3: (2.0,0.8,0)→(2.5,0.4,0)→(3.0,0.0,0) — descends to y=0.
    FillBndBox samples each segment independently; the y≈1.5 extremum near the
    seg1→seg2 handoff is missed because sampling stops before the joint.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (the catalog mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: the composite curve's degenerate joint at seg boundary combined
    with segment handoff miss drives shape_null=True via topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: COMPOSITE_CURVE 3 degree-2 B-spline segments with
    extremum at segment boundary; IS defect edge SURFACE_CURVE.curve_3d;
    FillBndBox omits inter-segment joint analysis — local maximum missed.
  - C-1 DRIVER: degenerate joint handling at segment boundary drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn073",
    defect=(
        "COMPOSITE_CURVE 3 degree-2 B-spline segments; "
        "seg1 ends at y=1.2; seg2 peaks at y=1.5 near seg1→seg2 boundary; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "FillBndBox samples each segment independently — misses inter-segment extremum; "
        "segment boundary topology failure drives shape_null=True"
    ),
)

# ── Flat plane for the face ──────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: COMPOSITE_CURVE with 3 degree-2 B-spline segments ─────
# Segment 1: (0,0,0) → (0.5,1.2,0) → (1.0,1.2,0)
s1p0 = f.cartesian_point((0.0, 0.0,  0.0))
s1p1 = f.cartesian_point((0.5, 1.2,  0.0))
s1p2 = f.cartesian_point((1.0, 1.2,  0.0))
seg1_bsp = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn073_seg1',2,"
    f"(#{s1p0.eid},#{s1p1.eid},#{s1p2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

# Segment 2: (1.0,1.2,0) → (1.5,1.5,0) → (2.0,0.8,0)  — peak at y≈1.5 near boundary
s2p0 = f.cartesian_point((1.0, 1.2,  0.0))
s2p1 = f.cartesian_point((1.5, 1.5,  0.0))
s2p2 = f.cartesian_point((2.0, 0.8,  0.0))
seg2_bsp = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn073_seg2',2,"
    f"(#{s2p0.eid},#{s2p1.eid},#{s2p2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

# Segment 3: (2.0,0.8,0) → (2.5,0.4,0) → (3.0,0.0,0)
s3p0 = f.cartesian_point((2.0, 0.8,  0.0))
s3p1 = f.cartesian_point((2.5, 0.4,  0.0))
s3p2 = f.cartesian_point((3.0, 0.0,  0.0))
seg3_bsp = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn073_seg3',2,"
    f"(#{s3p0.eid},#{s3p1.eid},#{s3p2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

ccs1 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{seg1_bsp.eid})")
ccs2 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{seg2_bsp.eid})")
ccs3 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{seg3_bsp.eid})")

composite_3d = f._emit_raw(
    f"COMPOSITE_CURVE('gn073_comp',(#{ccs1.eid},#{ccs2.eid},#{ccs3.eid}),.F.)"
)

# ── Pcurve: linear in UV along bottom edge ────────────────────────────────────
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn073_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn073_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn073_sc',#{composite_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 1.5, 0.0))
p_d = f.cartesian_point((0.0, 1.5, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn073_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, length)
    l2e = f.line(p2e, v2e)
    pcd2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc2  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd2.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc2.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (3.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 1.5)
e_top   = mk_line_edge(v_c, v_d, (3.0, 1.5, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 1.5, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 1.5)

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
