"""Gn052 — ShapeUpgrade_ConvertSurfaceToBezierBasis knot-multiplicity C0 boundary.

Catalog claim: B-spline surface (degree 3×3) with interior V-knot at 0.5 where
multiplicity equals degree (4,3,4 pattern), creating C0 continuity.
Converter re-inserts at this boundary despite already full multiplicity;
spurious subdivisions follow.

OCC behavior: silently accepts, empty result. Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree 3×3.
    U knots: (0.0, 1.0) mults (4,4) sum=8=3+4+1 ✓ (single span).
    V knots: (0.0, 0.5, 1.0) mults (4,3,4) — interior knot at 0.5 with
    multiplicity 3 (= degree 3): creates C0 boundary between patches.
    Control net: 4 rows (U) × 7 cols (V): 4+4-1=7 for two degree-3 spans ✓.
    This IS the face geometry; ShapeUpgrade_ConvertSurfaceToBezierBasis
    receives this face's surface and re-inserts at the already-full C0 boundary.
  - C-1 DRIVER: bottom EDGE_CURVE B-spline with 1.5-unit gap at t=0.5
    drives shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree 3×3 V-knot mults
    (4,3,4) — interior mult=3=degree at V=0.5 creates C0 boundary;
    IS the ADVANCED_FACE.face_geometry; converter re-inserts spuriously.
  - C-1 DRIVER: bottom edge B-spline 1.5-unit gap at t=0.5 drives shape_null.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn052",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree 3x3; "
        "U knots (0.0,1.0) mults (4,4) sum=8 ✓; "
        "V knots (0.0,0.5,1.0) mults (4,3,4) — interior mult=3=degree at V=0.5: "
        "C0 boundary; IS face_geometry for ShapeUpgrade_ConvertSurfaceToBezierBasis "
        "which re-inserts at already-full-multiplicity boundary causing spurious splits; "
        "C-1 break in bottom edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree 3×3, 4×7 control net ──────────────────
# U: 1 span, V: 2 spans sharing a C0 boundary at V=0.5
# U-knots (0.0,1.0) mults (4,4): sum=8=3+4+1 ✓
# V-knots (0.0,0.5,1.0) mults (4,3,4): sum=11=3+7+1 ✓ (7 V-CPs)
# Grid: X in [0,3] (4 CPs), Y in [0,6] (7 CPs)

rows = []
for i in range(4):
    row = []
    x = i * 1.0
    for j in range(7):
        y = j * 1.0
        z = 0.05 * i * j   # slight bow
        row.append(f.cartesian_point((x, y, z)))
    rows.append(row)

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = "(" + ",".join(row_ids(r) for r in rows) + ")"

surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn052_c0_surf',3,3,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,4),(4,3,4),"
    f"(0.0,1.0),(0.0,0.5,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── C-1 DRIVER: bottom edge B-spline with 1.5-unit gap at t=0.5 ─────────────
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((3.5,  0.0, 0.0))
dc5 = f.cartesian_point((3.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn052_c1_break',2,"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('gn052_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn052_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn052_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn052_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 6.0, 0.0))
p_d = f.cartesian_point((0.0, 6.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn052_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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

e_right = mk_line_edge(v_b, v_c, (3.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 6.0)
e_top   = mk_line_edge(v_c, v_d, (3.0, 6.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 6.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 6.0)

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
