"""Gn168 — Interior C0 Discontinuity (Tangent Jump).

Catalog claim: 2D B-spline with C0 (positional) but not C1 (tangent) at u=0.5.
BRepLib::SameParameter invokes Geom2dConvert::C0BSplineToC1 healing.
Falsifiable: pcurve is degree-2 B-spline with interior knot at t=0.5 mult=2
(C0 but not C1); SameParameter triggers C0BSplineToC1 healing path;
combined with 3D curve C-1 break → shape_null=True.

STEP mechanism (literal):
  - Defect PCURVE: degree-2 B-spline in 2D with interior knot at u=0.5 mult=2
    (C0 continuity only; tangent jump at u=0.5).
    n=4, p=2 → n+p+1=7. mults (3,2,2) knots (0.0,0.5,1.0) sum=7 ✓.
    Poles: (0,0)→(0.4,0.2)→(0.6,0.2)→(1,0) — tangent direction flips at u=0.5.
    IS the defect edge PCURVE (mechanism IS defect edge pcurve).
  - C-1 DRIVER: defect edge 3D curve is degree-2 B-spline with 1.5-unit CP
    gap at t=0.5 → C-1 positional break → OCC rejects → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: pcurve B_SPLINE_CURVE_WITH_KNOTS degree=2; interior
    knot t=0.5 mult=2 → C0 tangent jump; BRepLib::SameParameter invokes
    Geom2dConvert::C0BSplineToC1; IS defect edge pcurve.
  - C-1 DRIVER: defect edge 3D curve degree-2 B-spline, 1.5-unit CP gap at
    t=0.5 → shape_null=True (live oracle: empty/empty).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn168",
    defect=(
        "Defect PCURVE: B_SPLINE_CURVE_WITH_KNOTS degree=2 in 2D; "
        "interior knot t=0.5 mult=2 → C0 only (tangent jump); "
        "n=4, p=2, n+p+1=7; mults (3,2,2) knots (0.0,0.5,1.0) sum=7 ✓; "
        "IS defect edge pcurve; BRepLib::SameParameter → Geom2dConvert::C0BSplineToC1; "
        "C-1 DRIVER: defect edge 3D curve degree-2 B-spline 1.5-unit CP gap at t=0.5 "
        "→ shape_null=True (live oracle: empty/empty)"
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

# ── CATALOG MECHANISM: C0-only pcurve (tangent jump at u=0.5) ─────────────────
# Degree-2 B-spline in 2D; n=4, p=2 → n+p+1=7.
# mults (3,2,2) knots (0.0,0.5,1.0) sum=7 ✓ → C0 at u=0.5 (tangent jump).
# Poles arranged so tangent flips at u=0.5.
pc2d_p0 = f.cartesian_point((0.0, 0.0))
pc2d_p1 = f.cartesian_point((0.4, 0.3))
pc2d_p2 = f.cartesian_point((0.6, 0.3))   # tangent flip: slope changes sign
pc2d_p3 = f.cartesian_point((1.0, 0.0))

defect_pcurve_2d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn168_c0_pcurve',2,"
    f"(#{pc2d_p0.eid},#{pc2d_p1.eid},#{pc2d_p2.eid},#{pc2d_p3.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,2,2),(0.0,0.5,1.0),.UNSPECIFIED.)"
)
defect_pcdef = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn168_pcdef',(#{defect_pcurve_2d.eid}),#{prc.eid})"
)
defect_pc = f._emit_raw(f"PCURVE('gn168_pc',#{plane.eid},#{defect_pcdef.eid})")

# ── C-1 DRIVER: defect edge 3D curve — degree-2 B-spline with 1.5-unit gap ───
# n=4, p=2 → n+p+1=7. mults (3,1,3) knots (0.0,0.5,1.0) sum=7 ✓
# CP gap: cpb=(0.25,0,0) → cpc=(1.75,0,0) → 1.5-unit positional break at t=0.5
cpa = f.cartesian_point((0.0,  0.0, 0.0))
cpb = f.cartesian_point((0.25, 0.0, 0.0))
cpc = f.cartesian_point((1.75, 0.0, 0.0))
cpd = f.cartesian_point((2.0,  0.0, 0.0))

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn168_c1break',2,"
    f"(#{cpa.eid},#{cpb.eid},#{cpc.eid},#{cpd.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,1,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn168_sc',#{mech_3d.eid},(#{defect_pc.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((2.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)
e_defect = f._emit_raw(
    f"EDGE_CURVE('gn168_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
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
