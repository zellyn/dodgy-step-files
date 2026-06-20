"""Gn067 — ShapeUpgrade_SplitSurface degree mismatch.

Catalog claim: B-spline surface with u_degree=2, v_degree=4. SplitSurface
assumes equal degrees and reuses u_degree for v-split logic, causing knot
vector misalignment during split operations.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS u_degree=2, v_degree=4.
    Control net: 3 rows × 5 cols (u_size=3, v_size=5).
    U knots: (0.0, 1.0) mults (3,3) sum=6=2+3+1 ✓
    V knots: (0.0, 1.0) mults (5,5) sum=10=4+5+1 ✓
    SplitSurface mis-applies u_degree=2 to v-split knot insertion, producing
    a knot vector of length 3+3=6 instead of 5+5=10 — misalignment detected
    at evaluation time, no diagnostic emitted.
    IS the ADVANCED_FACE.face_geometry (catalog mechanism IS the face surface).
  - C-1 DRIVER: bottom edge B-spline with large pole gap at t=0.5 drives
    shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS u_degree=2 v_degree=4
    (3×5 net); IS the ADVANCED_FACE.face_geometry; SplitSurface reuses
    u_degree for v-split → knot vector misalignment.
  - C-1 DRIVER: bottom edge B-spline with 1.2-unit CP gap at t=0.5 drives
    shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn067",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS u_degree=2 v_degree=4 (3x5 net); "
        "U knots (0.0,1.0) mults (3,3) sum=6 ✓; "
        "V knots (0.0,1.0) mults (5,5) sum=10 ✓; "
        "IS the ADVANCED_FACE.face_geometry; "
        "SplitSurface reuses u_degree=2 for v-split logic — knot vector misalignment; "
        "C-1 break in bottom edge at t=0.5 (1.2-unit CP gap) drives shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: u_degree=2, v_degree=4, 3×5 control net ───────
# U: 3 rows, degree 2 → mults (3,3) sum=6 ✓
# V: 5 cols, degree 4 → mults (5,5) sum=10 ✓
# Grid: U ∈ [0,2], V ∈ [0,4]

rows = []
for i in range(3):        # u direction: 3 rows
    row = []
    for j in range(5):    # v direction: 5 cols
        row.append(f.cartesian_point((float(i), float(j), 0.0)))
    rows.append(row)

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = "(" + ",".join(row_ids(r) for r in rows) + ")"

surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn067_asym_surf',2,4,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(5,5),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── C-1 DRIVER: bottom edge B-spline with 1.2-unit gap at t=0.5 ──────────────
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((0.6, 0.0, 0.0))
dc2 = f.cartesian_point((1.2, 0.0, 0.0))   # before gap
dc3 = f.cartesian_point((2.4, 0.0, 0.0))   # 1.2-unit gap = C-1 break driver
dc4 = f.cartesian_point((3.2, 0.0, 0.0))
dc5 = f.cartesian_point((4.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn067_c1_break',2,"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('gn067_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn067_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn067_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn067_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn067_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
    pc2  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd2.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc2.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (4.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 2.0)
e_top   = mk_line_edge(v_c, v_d, (4.0, 2.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 4.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 2.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 2.0)

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
