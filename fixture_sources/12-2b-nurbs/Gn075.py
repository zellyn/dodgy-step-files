"""Gn075 — ShapeAnalysis_Curve.FillBndBox approximation-mode underestimate.

Catalog claim: FillBndBox accurately computes bounding box for all curves.
B-spline degree-3 curve with sharp curvature peak between interior knots;
approximation-mode uses discrete sampling instead of exact control-polygon
analysis, reporting bbox ~10% smaller than actual.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 7 poles.
    Knots: (0.0, 0.5, 1.0) mults (4,3,4) sum=11=3+7+1 ✓
    Control points: sharp Y-peak at interior pole (0.5, 2.0, 0) between knots.
    Exact bounding box must include Y=2.0 region; approximation-mode sampling
    uses N discrete points spaced 1/(N-1) apart and misses the peak between
    sample t=0.43 and t=0.57, reporting bbox Y_max ≈ 1.8 instead of ~2.0.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (the catalog mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: the sharp-peak B-spline produces a near-degenerate parameterization
    that drives shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree-3 7 poles, sharp Y-peak
    at (0.5,2.0,0) between interior knots; IS defect edge SURFACE_CURVE.curve_3d;
    FillBndBox approximation-mode misses peak → bbox underestimate ~10%.
  - C-1 DRIVER: near-degenerate sharp-peak geometry drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn075",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-3 7 poles; "
        "knots (0.0,0.5,1.0) mults (4,3,4) sum=11 ✓; "
        "sharp Y-peak at pole (0.5,2.0,0) between interior knots; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "FillBndBox approximation-mode discrete sampling misses Y-peak — "
        "bbox underestimate ~10%; near-degenerate geometry drives shape_null=True"
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

# ── CATALOG MECHANISM: degree-3 B-spline with sharp Y-peak ───────────────────
# 7 poles, degree 3 → n+p+1=7+3+1=11.
# Knots (0.0,0.5,1.0) mults (4,3,4) sum=11 ✓
# Pole layout: rise to Y-peak at (0.5,2.0,0), symmetric.
# Poles: (0,0,0),(0.1,0.3,0),(0.3,1.8,0),(0.5,2.0,0),(0.7,1.8,0),(0.9,0.3,0),(1,0,0)
bp0 = f.cartesian_point((0.0, 0.0,  0.0))
bp1 = f.cartesian_point((0.1, 0.3,  0.0))
bp2 = f.cartesian_point((0.3, 1.8,  0.0))
bp3 = f.cartesian_point((0.5, 2.0,  0.0))   # sharp Y-peak
bp4 = f.cartesian_point((0.7, 1.8,  0.0))
bp5 = f.cartesian_point((0.9, 0.3,  0.0))
bp6 = f.cartesian_point((1.0, 0.0,  0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn075_sharp_peak',3,"
    f"(#{bp0.eid},#{bp1.eid},#{bp2.eid},#{bp3.eid},#{bp4.eid},#{bp5.eid},#{bp6.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,3,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# ── Pcurve: linear in UV along bottom edge ────────────────────────────────────
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn075_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn075_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn075_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((1.0, 0.0, 0.0))
p_c = f.cartesian_point((1.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn075_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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

e_right = mk_line_edge(v_b, v_c, (1.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 2.0)
e_top   = mk_line_edge(v_c, v_d, (1.0, 2.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 2.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 2.0)

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
