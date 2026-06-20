"""Gn100 — ShapeUpgrade_SplitSurface high-multiplicity-clamp.

Catalog claim: B-spline surface with U knot multiplicity vector (4,4,4),
degree 3, and only 3 control points (fully-clamped configuration:
multiplicity = degree + 1). SplitSurface attempts splitting at interior knot
positions but fails because the high multiplicity prevents proper subdivision,
producing empty or degenerate patches.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS u_degree=3, v_degree=1, 3×2 control grid.
    U: n=3, p=3 → n+p+1=7. Catalog says mults (4,4,4) sum=12 ≠ 7.
    For 3 CPs, p=3: sum must = 3+3+1=7. Only (4,3) or (7) works for 2 knots.
    mults (4,4,4) requires 3 distinct U-knot values and n+p+1=12 → n=8.
    Use n=8 CPs in U with mults (4,4,4) knots (0.0,0.5,1.0): 8+3+1=12 ✓.
    Interior knot at 0.5 with mult=4=degree+1: fully-clamped interior break.
    SplitSurface sees the interior high-mult knot and tries to split there,
    producing degenerate/empty patches since multiplicity already equals degree+1.
    IS the face_geometry of the ADVANCED_FACE (mechanism IS the face surface).
  - C-1 DRIVER: high-multiplicity interior knot defeats SplitSurface →
    empty patches → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS u_degree=3 v_degree=1
    8×2 control grid; U mults (4,4,4) → interior mult=4=degree+1 (clamped break);
    IS face_geometry; SplitSurface split attempt at mult=4 → empty patches → shape_null=True.
  - C-1 DRIVER: degenerate split at high-multiplicity interior knot → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn100",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS u_degree=3 v_degree=1 8x2-grid; "
        "U knots (0.0,0.5,1.0) mults (4,4,4) sum=12 ✓; interior mult=4=degree+1; "
        "IS face_geometry; "
        "SplitSurface split at high-mult knot → empty patches → shape_null=True"
    ),
)

# ── CATALOG MECHANISM: 8×2 grid, u_degree=3, mults (4,4,4) interior clamp ───
# U: n=8, p=3 → n+p+1=12. mults (4,4,4) knots (0.0,0.5,1.0) sum=12 ✓
# V: n=2, p=1 → n+p+1=4. mults (2,2) knots (0.0,1.0) sum=4 ✓
pts = [[f.cartesian_point(p) for p in row] for row in [
    # 8 rows (U), 2 columns (V)
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
    [(0.5, 0.0, 0.1), (0.5, 1.0, 0.1)],
    [(1.0, 0.0, 0.2), (1.0, 1.0, 0.2)],
    [(1.5, 0.0, 0.1), (1.5, 1.0, 0.1)],  # end of first clamped span
    [(1.5, 0.0, 0.1), (1.5, 1.0, 0.1)],  # start of second clamped span (high-mult break)
    [(2.0, 0.0, 0.2), (2.0, 1.0, 0.2)],
    [(2.5, 0.0, 0.1), (2.5, 1.0, 0.1)],
    [(3.0, 0.0, 0.0), (3.0, 1.0, 0.0)],
]]
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)

# Mechanism IS the face surface
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn100_highmult',3,1,"
    f"({grid}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,4,4),(2,2),"
    f"(0.0,0.5,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# ── Simple rectangular boundary on the surface ───────────────────────────────
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 1.0, 0.0))
p_d = f.cartesian_point((0.0, 1.0, 0.0))
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
e_right = mk_line_edge(v_b, v_c, (3.0,0.0,0.0), (0.,1.,0.), (1.0,0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, (3.0,1.0,0.0), (-1.,0.,0.),(1.0,1.0), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (0.0,1.0,0.0), (0.,-1.,0.),(0.0,1.0), (0.,-1.), 1.0)

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
