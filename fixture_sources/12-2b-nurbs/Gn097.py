"""Gn097 — ShapeUpgrade_SplitSurface.Init duplicate-split-values.

Catalog claim: Call Init with duplicate split parameters [0.5, 0.5, 0.5];
dedup logic doesn't fully collapse, leaving phantom splits. Degree (2,2)
surface with interior knot at 0.5 on both axes; Init called with triplicate
U-split [0.5, 0.5, 0.5].

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS u_degree=2, v_degree=2, 3×3 control grid.
    U: n=3, p=2 → n+p+1=6. Knots (0.0,0.5,1.0) mults (3,0,3) — wait:
    for interior knot at 0.5 with multiplicity 1: mults (3,1,3) sum=7? No.
    n=3, p=2 → n+p+1=6. Valid: mults (3,3) sum=6 (no interior knot).
    For interior knot: n=4, p=2 → 4+2+1=7. mults (3,1,3) sum=7 ✓.
    Use 4×4 grid with interior knot at 0.5 on both axes.
    The interior knot at 0.5 corresponds to the split parameter Init will
    receive as a triplicate [0.5, 0.5, 0.5] — dedup logic leaves phantom splits.
    IS the face_geometry of the ADVANCED_FACE (mechanism IS the face surface).
  - C-1 DRIVER: phantom duplicate splits cause SplitSurface to produce
    invalid patches → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS u_degree=2 v_degree=2
    4×4 control grid; interior knot at U=0.5, V=0.5; IS face_geometry;
    Init([0.5,0.5,0.5]) dedup failure → phantom splits → shape_null=True.
  - C-1 DRIVER: phantom split parameters → degenerate surface patches → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn097",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS u_degree=2 v_degree=2 4x4-grid; "
        "interior knot at U=V=0.5; IS face_geometry; "
        "SplitSurface.Init([0.5,0.5,0.5]) dedup failure → phantom splits → shape_null=True"
    ),
)

# ── CATALOG MECHANISM: degree (2,2) surface, 4×4 grid, interior knot at 0.5 ──
# U: n=4, p=2 → n+p+1=7. mults (3,1,3) knots (0.0,0.5,1.0) sum=7 ✓
# V: n=4, p=2 → n+p+1=7. mults (3,1,3) knots (0.0,0.5,1.0) sum=7 ✓
pts = [[f.cartesian_point(p) for p in row] for row in [
    # 4 rows (U), each 4 columns (V)
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 2.0, 0.0), (0.0, 3.0, 0.0)],
    [(1.0, 0.0, 0.1), (1.0, 1.0, 0.3), (1.0, 2.0, 0.3), (1.0, 3.0, 0.1)],
    [(2.0, 0.0, 0.1), (2.0, 1.0, 0.3), (2.0, 2.0, 0.3), (2.0, 3.0, 0.1)],
    [(3.0, 0.0, 0.0), (3.0, 1.0, 0.0), (3.0, 2.0, 0.0), (3.0, 3.0, 0.0)],
]]
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)

# Mechanism IS the face surface
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn097_dupsplit',2,2,"
    f"({grid}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,1,3),(3,1,3),"
    f"(0.0,0.5,1.0),(0.0,0.5,1.0),"
    f".UNSPECIFIED.)"
)

# ── Simple rectangular boundary on the surface ───────────────────────────────
# Parametric corners (U,V): (0,0),(3,0),(3,3),(0,3) → world space approx
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 3.0, 0.0))
p_d = f.cartesian_point((0.0, 3.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

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
    pc_  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs_.eid},#{ve_.eid},#{sc_.eid},.T.)")

e_bot   = mk_line_edge(v_a, v_b, (0.0,0.0,0.0), (1.,0.,0.), (0.0,0.0), (1.,0.), 3.0)
e_right = mk_line_edge(v_b, v_c, (3.0,0.0,0.0), (0.,1.,0.), (1.0,0.0), (0.,1.), 3.0)
e_top   = mk_line_edge(v_c, v_d, (3.0,3.0,0.0), (-1.,0.,0.),(1.0,1.0), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (0.0,3.0,0.0), (0.,-1.,0.),(0.0,1.0), (0.,-1.), 3.0)

outer_loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])

# Mechanism IS the face surface (surf)
face  = f.advanced_face([f.face_outer_bound(outer_loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
