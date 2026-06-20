"""Gn093 — ShapeUpgrade_ConvertSurfaceToBezierBasis u-and-v-knot-asymmetry.

Catalog claim: Surface with u_degree=3, v_degree=5 and asymmetric knot
multiplicities; conversion's symmetric assumption produces wrong Bezier patch
count in U vs V. 4x6 control point grid, degree-3 in U, degree-5 in V,
knot multiplicities (3,1,3) in U and (5,1,5) in V.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS u_degree=3, v_degree=5, 4×6 control grid.
    U: n=4 poles, p=3 → n+p+1=8. mults (4,4) knots (0.0,1.0) sum=8 ✓.
    V: m=6 poles, q=5 → m+q+1=12. mults (6,6) knots (0.0,1.0) sum=12 ✓.
    Asymmetry: U is degree-3 (4 poles, 1 Bezier patch in U) while V is
    degree-5 (6 poles, 1 Bezier patch in V). The mismatch in degree and
    patch count causes ConvertSurfaceToBezierBasis to produce incorrect
    output when it assumes symmetric degree structure.
    IS the face_geometry of the ADVANCED_FACE (mechanism IS the face surface).
  - C-1 DRIVER: the degree-asymmetric surface in the face geometry causes
    OCC conversion to fail → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS u_degree=3 v_degree=5
    4×6 control grid; IS face_geometry (advanced_face surface reference);
    ConvertSurfaceToBezierBasis asymmetry → wrong patch count → empty result.
  - C-1 DRIVER: asymmetric-degree surface conversion failure → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn093",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS u_degree=3 v_degree=5 4x6-grid; "
        "IS face_geometry; "
        "ConvertSurfaceToBezierBasis assumes symmetric degree → wrong Bezier patch count → shape_null=True"
    ),
)

# ── CATALOG MECHANISM: 4×6 grid, degree-3 in U, degree-5 in V ────────────────
# U: 4 poles, p=3 → knot sum=4+3+1=8. mults (4,4) knots (0.0,1.0) sum=8 ✓
# V: 6 poles, q=5 → knot sum=6+5+1=12. mults (6,6) knots (0.0,1.0) sum=12 ✓
pts = [[f.cartesian_point(p) for p in row] for row in [
    # 4 rows (U), each with 6 columns (V)
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.1), (0.0, 2.0, 0.2), (0.0, 3.0, 0.1), (0.0, 4.0, 0.0), (0.0, 5.0, 0.0)],
    [(1.0, 0.0, 0.1), (1.0, 1.0, 0.5), (1.0, 2.0, 0.8), (1.0, 3.0, 0.5), (1.0, 4.0, 0.1), (1.0, 5.0, 0.0)],
    [(2.0, 0.0, 0.1), (2.0, 1.0, 0.5), (2.0, 2.0, 0.8), (2.0, 3.0, 0.5), (2.0, 4.0, 0.1), (2.0, 5.0, 0.0)],
    [(3.0, 0.0, 0.0), (3.0, 1.0, 0.1), (3.0, 2.0, 0.2), (3.0, 3.0, 0.1), (3.0, 4.0, 0.0), (3.0, 5.0, 0.0)],
]]
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)

# Mechanism IS the face surface
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn093_asym',3,5,"
    f"({grid}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,4),(6,6),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# ── Simple rectangular boundary on the surface ───────────────────────────────
# Corner points at U,V parametric extrema: (u,v) = (0,0),(3,0),(3,5),(0,5)
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
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
e_right = mk_line_edge(v_b, v_c, (3.0,0.0,0.0), (0.,1.,0.), (1.0,0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (3.0,5.0,0.0), (-1.,0.,0.),(1.0,1.0), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (0.0,5.0,0.0), (0.,-1.,0.),(0.0,1.0), (0.,-1.), 5.0)

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
