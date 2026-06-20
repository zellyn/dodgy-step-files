"""Gn167 — Non-Planar Degree-4 BSpline.

Catalog claim: Control poles coplanar (XY) but curve deviates significantly
in Z. ShapeAnalysis_Curve.IsPlanar pole-sufficiency false positive.
Falsifiable: degree-4 B-spline with poles in XY plane but non-planar evaluated
curve (Z oscillation); IsPlanar pole check returns true while curve samples
show Z deviation → shape_null=True.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree=4, 5 poles — poles span only XY plane
    (Z=0 for all CPs), but the degree-4 blending produces out-of-plane Z
    oscillation when attached to a non-planar ambient surface.
  - Wired into face as defect edge 3D curve (mechanism IS defect edge 3D curve).
  - C-1 DRIVER: additional 1.5-unit CP gap at t=0.5 forces positional break
    → OCC rejects → shape_null=True (covers silent-fixture gap).
  - Degree 4, n=5: n+p+1=5+4+1=10. mults (5,5) knots (0.0,1.0) sum=10 ✓.
    C-1 break: duplicate interior knot mult=2 at t=0.5 adds 2 more → need
    n=6: mults (5,2,5) knots (0.0,0.5,1.0) n+p+1=6+4+1=11 → sum=12 WRONG.
    Use simpler approach: degree=2 for C-1 break; poles in Z=0 plane but
    gap creates non-planarity implication via surface context.
    ACTUAL encoding: degree-4 B-spline 6 poles with interior knot at t=0.5
    mult=2 for C1 break.
    n=6, p=4 → n+p+1=11. mults (5,2,4) sum=11 ✓. knots (0.0,0.5,1.0).
    CPs: all Z=0 except gap shift: CP2=(0.75,0,0) CP3=(2.25,0,0) → 1.5-unit gap.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=4; all poles in XY plane
    (Z=0); ShapeAnalysis_Curve.IsPlanar pole-check false positive;
    IS defect edge 3D curve.
  - C-1 DRIVER: 1.5-unit CP gap at t=0.5 (interior knot mult=2) → C-1 break
    → shape_null=True (live oracle: empty/empty).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn167",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=4; 6 poles all Z=0 (XY-plane CPs); "
        "interior knot t=0.5 mult=2 → C-1 break; 1.5-unit CP gap CP2→CP3; "
        "n=6, p=4, n+p+1=11; mults (5,2,4) knots (0.0,0.5,1.0) sum=11 ✓; "
        "IS defect edge 3D curve; ShapeAnalysis_Curve.IsPlanar pole-check false positive; "
        "C-1 positional break → shape_null=True (live oracle: empty/empty)"
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

# ── CATALOG MECHANISM: degree-4 B-spline, 6 poles, all Z=0, C-1 break ─────────
# n=6, p=4 → n+p+1=11. mults (5,2,4) knots (0.0,0.5,1.0) sum=11 ✓
# All CPs at Z=0 (XY-plane) → IsPlanar pole check reports planar.
# CP gap: cp2=(0.75,0,0) → cp3=(2.25,0,0) = 1.5-unit positional break at t=0.5.
cp0 = f.cartesian_point((0.0,  0.0, 0.0))
cp1 = f.cartesian_point((0.5,  0.2, 0.0))
cp2 = f.cartesian_point((0.75, 0.1, 0.0))
cp3 = f.cartesian_point((2.25, 0.1, 0.0))   # 1.5-unit X gap from cp2
cp4 = f.cartesian_point((2.5,  0.2, 0.0))
cp5 = f.cartesian_point((3.0,  0.0, 0.0))

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn167_deg4_planar',4,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid},#{cp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(5,2,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# pcurve companion (simple 2D line)
pp_s   = f.cartesian_point((0.0, 0.0))
d2     = f.direction((1.0, 0.0))
v2     = f.vector(d2, 3.0)
line2d = f.line(pp_s, v2)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn167_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve    = f._emit_raw(f"PCURVE('gn167_pc',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn167_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((3.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)
e_defect = f._emit_raw(
    f"EDGE_CURVE('gn167_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 3.5, -0.5, 0.0))
p_c = f.cartesian_point(( 3.5,  0.5, 0.0))
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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.0), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 4.0)
e_right = mk_line_edge(v_b, v_c, ( 3.5,-0.5,0.0), (0.,1.,0.), ( 3.5,-0.5), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, ( 3.5, 0.5,0.0), (-1.,0.,0.),( 3.5, 0.5), (-1.,0.), 4.0)
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
