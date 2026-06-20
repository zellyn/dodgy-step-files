"""Gn063 — ShapeAnalysis_Curve.GetSamplePoints rational pole density.

Catalog claim: 5-control-point NURBS with weight 150.0 at midpoint (u=0.5),
creating extreme cusp. Sample density doesn't scale with pole weight; uniform
grid misses the sharp feature pulled by high-weight pole.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - RATIONAL_B_SPLINE_CURVE (complex entity) degree-2, 5 control points.
    Weights: (1.0, 1.0, 150.0, 1.0, 1.0) — extreme weight at CP2.
    Knots: (0.0, 0.5, 1.0) mults (3,1,3) sum=7=2+5 ✓
    CP2=(0.5, 5.0, 0.0) pulled sharply by weight=150.0; rational blending
    creates an extreme cusp at u≈0.5 that the uniform GetSamplePoints grid
    completely misses (samples at 0, 0.1, 0.2, … 1.0 step over the peak).
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE.
  - C-1 DRIVER: same entity — weight=150 creates a near-singularity in the
    rational denominator at u=0.5 that drives shape_null=True via edge
    topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: RATIONAL_B_SPLINE_CURVE weights (1,1,150,1,1) at CP2;
    IS defect edge SURFACE_CURVE.curve_3d; GetSamplePoints uniform density
    misses extreme cusp pulled by weight-150 pole.
  - C-1 DRIVER: same entity — near-singular rational geometry drives
    shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn063",
    defect=(
        "RATIONAL_B_SPLINE_CURVE degree-2 5 poles; "
        "weights (1.0,1.0,150.0,1.0,1.0) extreme weight at CP2=(0.5,5.0,0.0); "
        "knots (0.0,0.5,1.0) mults (3,1,3) sum=7 ✓; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "GetSamplePoints uniform grid misses extreme cusp at u≈0.5 "
        "pulled by weight=150; near-singular rational geometry drives shape_null=True"
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

# ── CATALOG MECHANISM: RATIONAL B-SPLINE CURVE, weight=150 at midpoint ───────
# degree-2, 5 CPs. Interior knot at t=0.5 mult=1 (C1).
# CP2=(0.5,5.0,0.0) with weight=150 creates extreme cusp at u≈0.5.
# Uniform GetSamplePoints grid steps over the narrow cusp peak.
rc0 = f.cartesian_point((0.0,  0.0,  0.0))
rc1 = f.cartesian_point((0.25, 0.0,  0.0))
rc2 = f.cartesian_point((0.5,  5.0,  0.0))   # pulled by weight=150
rc3 = f.cartesian_point((0.75, 0.0,  0.0))
rc4 = f.cartesian_point((1.0,  0.0,  0.0))

# RATIONAL_B_SPLINE_CURVE complex entity: B_SPLINE_CURVE_WITH_KNOTS + RATIONAL_B_SPLINE_CURVE
rational_curve = f._emit_raw(
    f"(B_SPLINE_CURVE_WITH_KNOTS('gn063_rational_curve',2,"
    f"(#{rc0.eid},#{rc1.eid},#{rc2.eid},#{rc3.eid},#{rc4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,1,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
    f"RATIONAL_B_SPLINE_CURVE((1.0,1.0,150.0,1.0,1.0)))"
)

# Pcurve for the defect edge (linear in UV, U from 0→1, V=0)
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn063_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn063_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn063_sc',#{rational_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((1.0, 0.0, 0.0))
p_c = f.cartesian_point((1.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn063_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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

e_right = mk_line_edge(v_b, v_c, (1.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (1.0, 5.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 5.0)

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
