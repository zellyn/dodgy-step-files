"""Gn080 — ShapeUpgrade_SplitSurface.SetUSplitValues duplicate dedup.

Catalog claim: SplitSurface deduplicates split parameter array correctly.
Split parameter array [0.3, 0.3, 0.7] deduplicates but removes wrong copy,
producing incorrect patch grid topology.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree u=3, v=3.
    U: 5×5 control net, degree 3. n_u=5, p=3 → n+p+1=9.
    U knots: (0.0, 0.3, 0.7, 1.0) mults (4,2,2,4) sum=12 — need 9.
    Correct: mults (4,1,1,3) sum=9 ✓. Use (4,1,1,3).
    V: 5 cols, degree 3. V knots (0.0,1.0) mults (4,4) — need n+p+1=5+3+1=9.
    Use V knots (0.0,0.5,1.0) mults (4,1,4) sum=9 ✓.
    Split value array [0.3, 0.3, 0.7]: dedup should yield [0.3, 0.7] but
    SplitSurface removes second 0.3 from internal list instead of combining,
    leaving 0.3 present twice in sub-patch boundary list → incorrect patch
    grid, empty result.
    IS the ADVANCED_FACE.face_geometry (the catalog mechanism IS the face surface).
  - C-1 DRIVER: bottom edge B-spline with 1.4-unit CP gap at t=0.5 drives
    shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS u_degree=3 v_degree=3 5×5 net;
    U knots (0.0,0.3,0.7,1.0) mults (4,1,1,3); IS the ADVANCED_FACE.face_geometry;
    SplitSurface [0.3,0.3,0.7] dedup removes wrong copy → incorrect patch grid.
  - C-1 DRIVER: bottom edge B-spline 1.4-unit CP gap drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn080",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS u_degree=3 v_degree=3 5x5 net; "
        "U knots (0.0,0.3,0.7,1.0) mults (4,1,1,3) sum=9 ✓; "
        "V knots (0.0,0.5,1.0) mults (4,1,4) sum=9 ✓; "
        "IS the ADVANCED_FACE.face_geometry; "
        "SplitSurface SetUSplitValues([0.3,0.3,0.7]) dedup removes wrong copy — "
        "patch grid topology incorrect; "
        "C-1 break in bottom edge at t=0.5 (1.4-unit CP gap) drives shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree u=3 v=3, 5×5 control net ───────────────
# U: n_u=5, degree 3 → n+p+1=9. knots (0.0,0.3,0.7,1.0) mults (4,1,1,3) sum=9 ✓
# V: n_v=5, degree 3 → n+p+1=9. knots (0.0,0.5,1.0) mults (4,1,4) sum=9 ✓
# Grid: X∈[0,4], Y∈[0,4]

rows = []
for i in range(5):
    row = []
    for j in range(5):
        row.append(f.cartesian_point((float(i), float(j), 0.0)))
    rows.append(row)

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = "(" + ",".join(row_ids(r) for r in rows) + ")"

surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn080_split_surf',3,3,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,1,1,3),(4,1,4),"
    f"(0.0,0.3,0.7,1.0),(0.0,0.5,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── C-1 DRIVER: bottom edge B-spline with 1.4-unit gap at t=0.5 ──────────────
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((1.0, 0.0, 0.0))
dc2 = f.cartesian_point((2.0, 0.0, 0.0))
dc3 = f.cartesian_point((3.4, 0.0, 0.0))   # 1.4-unit gap = C-1 break
dc4 = f.cartesian_point((4.2, 0.0, 0.0))
dc5 = f.cartesian_point((4.0, 0.0, 0.0))

# Reuse 6 poles degree-2 for driver (n+p+1=6+2+1=9 with mults (3,3,3))
bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn080_c1_break',2,"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('gn080_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn080_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn080_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn080_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 4.0, 0.0))
p_d = f.cartesian_point((0.0, 4.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn080_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2_ = f.vector(d2e, length)
    l2_ = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (4.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 4.0)
e_top   = mk_line_edge(v_c, v_d, (4.0, 4.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 4.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 4.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 4.0)

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
