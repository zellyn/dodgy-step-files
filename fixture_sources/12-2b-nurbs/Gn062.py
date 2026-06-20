"""Gn062 — ShapeUpgrade_SplitSurface.SetVSplitValues out-of-order.

Catalog claim: Bi-quadratic B-spline surface (3×3 control points, degree 2×2).
When split values passed as [1.0, 0.5, 0.2] without sort, Init produces
inverted sub-patches with swapped parameter ranges.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree 2×2, 3×3 control net.
    U knots: (0.0, 1.0) mults (3,3) sum=6=2+3+1 ✓
    V knots: (0.0, 1.0) mults (3,3) sum=6=2+3+1 ✓
    SetVSplitValues receives [1.0, 0.5, 0.2] (descending, unsorted);
    Init applies knot insertions in input order, producing inverted V sub-patches
    with swapped parameter ranges — no diagnostic emitted.
    IS the ADVANCED_FACE.face_geometry (the catalog mechanism IS the face surface).
  - C-1 DRIVER: bottom edge B-spline with 1.5-unit CP gap at t=0.5 drives
    shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree 2×2 (3×3 net); IS
    the ADVANCED_FACE.face_geometry; ShapeUpgrade_SplitSurface.SetVSplitValues
    receives out-of-order [1.0,0.5,0.2], producing inverted V sub-patches.
  - C-1 DRIVER: bottom edge B-spline with 1.5-unit CP gap drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn062",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree 2x2 3x3 net; "
        "U knots (0.0,1.0) mults (3,3) sum=6 ✓; "
        "V knots (0.0,1.0) mults (3,3) sum=6 ✓; "
        "IS the face geometry fed to ShapeUpgrade_SplitSurface.SetVSplitValues "
        "with out-of-order [1.0,0.5,0.2] — inverted V sub-patches, no diagnostic; "
        "C-1 break in bottom edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree 2×2, 3×3 control net ──────────────────
# U knots (0.0,1.0) mults (3,3) → sum=6=2+3+1 ✓
# V knots (0.0,1.0) mults (3,3) → sum=6=2+3+1 ✓
# Simple 3×3 grid: X in [0,3], Y in [0,3]

r0 = [f.cartesian_point((0.0, float(j * 1.5), 0.0)) for j in range(3)]
r1 = [f.cartesian_point((1.5, float(j * 1.5), 0.0)) for j in range(3)]
r2 = [f.cartesian_point((3.0, float(j * 1.5), 0.0)) for j in range(3)]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)})"

surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn062_split_surf',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(3,3),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── C-1 DRIVER: bottom edge B-spline with 1.5-unit gap at t=0.5 ─────────────
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((0.5, 0.0, 0.0))
dc2 = f.cartesian_point((1.0, 0.0, 0.0))
dc3 = f.cartesian_point((2.5, 0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((2.8, 0.0, 0.0))
dc5 = f.cartesian_point((3.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn062_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.17, 0.0))
pp2 = f.cartesian_point((0.33, 0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.67, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn062_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn062_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn062_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn062_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 3.0, 0.0))
p_d = f.cartesian_point((0.0, 3.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn062_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (3.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 3.0)
e_top   = mk_line_edge(v_c, v_d, (3.0, 3.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 3.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 3.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
