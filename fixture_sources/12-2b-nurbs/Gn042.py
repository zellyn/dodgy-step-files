"""Gn042 — ShapeUpgrade_ConvertSurfaceToBezierBasis double-knot thin patch.

Catalog claim: A B-spline surface with a double interior U-knot (multiplicity=2)
yields degenerate Bezier patches after knot insertion via
ShapeUpgrade_ConvertSurfaceToBezierBasis; the extent filter fails to remove
the collapsed patches, leaving a degenerate shell.

OCC behavior: silently accepts or rejects; shape_null=True expected. Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree 3×1, interior U-knot at u=0.5 with
    multiplicity=2. After Bezier conversion (which inserts knots to full
    multiplicity), the patch at u=[0.5,0.5] has zero parametric width and
    degenerates. The extent-size filter should discard this patch but fails.
  - C-1 break in 3D edge curve (1.5-unit gap at t=0.5) drives shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree 3x1, interior U-knot
    at 0.5 mult=2; after Bezier conversion the patch u=[0.5,0.5] collapses to
    zero width; extent filter fails to remove degenerate patch; output shell
    contains degenerate face.
  - C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 drives shape_null.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn042",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree 3x1: interior U-knot at u=0.5 "
        "with multiplicity=2; ShapeUpgrade_ConvertSurfaceToBezierBasis inserts "
        "knots to full multiplicity; patch at u=[0.5,0.5] collapses to zero "
        "parametric width (degenerate Bezier patch); extent filter fails to "
        "remove degenerate patch; output shell contains degenerate face; "
        "C-1 break in 3D edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: double-knot B-spline surface ──────────────────
# Degree 3 in U, degree 1 in V.
# U: 6 control points per row; interior U-knot at 0.5 with mult=2.
#   U-knots: (0.0, 0.5, 1.0) mults (4, 2, 4) => sum=10 = degree+6+1=10 ✓
# V: 2 control points per col.
#   V-knots: (0.0, 1.0) mults (2, 2) => sum=4 = degree+2+1=4 ✓ (degree=1)
# Control net: 6 rows × 2 cols.

r0 = [f.cartesian_point((float(i * 1.2), 0.0, float(i % 2))) for i in range(6)]
r1 = [f.cartesian_point((float(i * 1.2), 5.0, float(i % 2))) for i in range(6)]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)})"

# THE DEFECT: interior U-knot mult=2 at u=0.5 (multiplicity < degree, not C0,
# but double knot triggers thin-patch degeneration in Bezier conversion).
double_knot_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('double_knot_surf',3,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,2,4),(2,2),"
    f"(0.0,0.5,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 ─────────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.25, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit C-1 gap
dc4 = f.cartesian_point((4.75, 0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn042_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn042_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn042_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn042_pc_ent',#{double_knot_surf.eid},#{defrep.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('gn042_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn042_edge',#{v_a.eid},#{v_b.eid},#{sc.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, length)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{double_knot_surf.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 5.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], double_knot_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
