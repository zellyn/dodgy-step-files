"""Gn057 — ShapeAnalysis_Curve.GetSamplePoints high-radius full-circle 360K cap.

Catalog claim: Full-circle CIRCLE entity with radius 1,000,000 meters.
GetSamplePoints caps at 360 samples; 1-degree resolution insufficient to detect
near-tangent intersections in high-curvature regions.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - CIRCLE entity with radius 1,000,000.0 placed at origin.
    Full-circle arc spans 0→2π. GetSamplePoints caps at 360 uniformly-spaced
    samples regardless of radius; at 1e6m radius each step spans ~17,453m of
    arc, making near-tangent intersection detection impossible.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE.
  - C-1 DRIVER: same entity — at 1e6m radius the 360-sample step produces a
    chord gap >> the geometric tolerance, driving shape_null=True via edge
    topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: CIRCLE radius=1,000,000.0; IS defect edge
    SURFACE_CURVE.curve_3d; GetSamplePoints uses fixed 360-sample cap,
    missing near-tangent intersections at this scale.
  - C-1 DRIVER: same entity — chord gap at 1e6m radius drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn057",
    defect=(
        "CIRCLE radius=1000000.0 full-circle arc; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "GetSamplePoints caps at 360 samples — 1-degree resolution at 1e6m radius "
        "spans ~17453m/step; near-tangent intersections undetectable at this density; "
        "chord gap >> geometric tolerance drives shape_null=True"
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

# ── CATALOG MECHANISM: CIRCLE radius=1,000,000m ───────────────────────────────
# Full-circle arc. At this radius GetSamplePoints 360-sample cap is far too
# coarse (each step ~17,453m arc length) to detect near-tangent intersections.
circle_orig = f.cartesian_point((0.0, 0.0, 0.0))
circle_norm = f.direction((0.0, 0.0, 1.0))
circle_xdir = f.direction((1.0, 0.0, 0.0))
circle_ax = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('circ_ax',#{circle_orig.eid},#{circle_norm.eid},#{circle_xdir.eid})"
)
circle = f._emit_raw(f"CIRCLE('gn057_circle',#{circle_ax.eid},1000000.0)")

# Pcurve: radial line in UV from (0,0) along U
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn057_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn057_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn057_sc',#{circle.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# Face corners: large square enclosing (radius used as scale reference)
R = 5.0  # face size in model units — circle is at 1e6 so edge references it
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((R,   0.0, 0.0))
p_c = f.cartesian_point((R,   R,   0.0))
p_d = f.cartesian_point((0.0, R,   0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn057_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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

e_right = mk_line_edge(v_b, v_c, (R, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), R)
e_top   = mk_line_edge(v_c, v_d, (R, R,   0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), R)
e_left  = mk_line_edge(v_d, v_a, (0.0, R, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), R)

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
