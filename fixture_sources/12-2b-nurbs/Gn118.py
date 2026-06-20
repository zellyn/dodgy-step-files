"""Gn118 — ShapeAnalysis_Curve.IsPlanar two-points-and-one-offset.

Catalog claim: Degenerate B-spline curve (degree 2, 3 points) where first two
poles are coincident and third is spatially offset. IsPlanar's degenerate-input
handler produces a verdict but computes a meaningless "plane" from insufficient
independent points.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 2, 3 CPs.
    n=3, p=2 → n+p+1=6. mults (3,3) knots (0.0,1.0) sum=6 ✓.
    cp0 == cp1 (coincident); cp2 is spatially offset at (2.0, 3.0, 1.5).
    Only two distinct spatial positions → only 1 independent vector.
    IsPlanar's plane-fitting needs 2 independent vectors from 3+ points;
    with cp0==cp1, it has only 1 unique direction (cp0→cp2). The degenerate
    handler picks a normal but the "plane" it computes is meaningless, and
    downstream shape analysis rejects the planarity determination.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: degenerate plane from coincident poles → IsPlanar meaningless
    verdict → shape analysis failure → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=2 3-pole;
    mults (3,3) knots (0.0,1.0) sum=6 ✓;
    cp0==(0,0,0) == cp1==(0,0,0); cp2==(2.0,3.0,1.5);
    only 1 independent direction → degenerate plane;
    IS defect edge SURFACE_CURVE.curve_3d;
    IsPlanar degenerate-input handler computes meaningless plane → shape_null=True.
  - C-1 DRIVER: coincident poles → degenerate planarity computation → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn118",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=2 3-pole; "
        "mults (3,3) knots (0.0,1.0) sum=6 ✓; "
        "cp0==(0,0,0) == cp1==(0,0,0) (coincident); cp2==(2.0,3.0,1.5) (offset); "
        "only 1 independent direction → degenerate IsPlanar input; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsPlanar degenerate-input handler computes meaningless plane → shape_null=True"
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

# ── CATALOG MECHANISM: degree-2 B-spline, 3 CPs, first two coincident ────────
# n=3, p=2 → n+p+1=6. mults (3,3) knots (0.0,1.0) sum=6 ✓.
# cp0 == cp1 (both at origin); cp2 at (2.0, 3.0, 1.5).
# The curve degenerates near t=0: it starts at the coincident point and ends
# at cp2. IsPlanar receives 3 pole positions but only 2 distinct positions
# → cannot construct 2 independent basis vectors for a plane normal.
cp0 = f.cartesian_point((0.0, 0.0, 0.0))   # coincident start
cp1 = f.cartesian_point((0.0, 0.0, 0.0))   # coincident (== cp0)
cp2 = f.cartesian_point((2.0, 3.0, 1.5))   # offset endpoint

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn118_degenerate_planar',2,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

# pcurve: 2D line companion
pp_s   = f.cartesian_point((0.0, 0.0))
d2     = f.direction((1.0, 0.0))
v2     = f.vector(d2, 3.0)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn118_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn118_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn118_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((2.0, 3.0, 1.5))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn118_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 3.5, -0.5, 0.0))
p_c = f.cartesian_point(( 3.5,  4.0, 0.0))
p_d = f.cartesian_point((-0.5,  4.0, 0.0))
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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.0), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 4.0)
e_right = mk_line_edge(v_b, v_c, ( 3.5,-0.5,0.0), (0.,1.,0.), ( 3.5,-0.5), (0.,1.), 4.5)
e_top   = mk_line_edge(v_c, v_d, ( 3.5, 4.0,0.0), (-1.,0.,0.),( 3.5, 4.0), (-1.,0.), 4.0)
e_left  = mk_line_edge(v_d, v_a, (-0.5, 4.0,0.0), (0.,-1.,0.),(-0.5, 4.0), (0.,-1.), 4.5)

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
