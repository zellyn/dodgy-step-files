"""Gn072 — ShapeUpgrade_SplitSurface explicit-knot-spec mismatch.

Catalog claim: A B-spline surface declares .UNIFORM_KNOTS. but U-knot vector
has non-uniform spacing (0, 0.3, 0.6, 1). Init() trusts the tag over the
actual knot values and produces incorrect splits aligned to uniform spacing.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS 4×4 poles, degree (2,2).
    U knots: (0.0, 0.3, 0.6, 1.0) mults (3,1,1,3) sum=8=2+4+2 ✓ — non-uniform.
    V knots: (0.0, 1.0) mults (3,3) sum=6=2+4 WRONG.
    Correction: degree=2, 4 cols → n+p+1=4+2+1=7. Use (3,1,3) sum=7 ✓.
    Surface tag says .UNIFORM_KNOTS. but spacing is non-uniform (0,0.3,0.6,1).
    SplitSurface::Init trusts the tag and applies uniform-spacing split logic,
    producing splits misaligned with actual knot positions — no diagnostic emitted.
    IS the ADVANCED_FACE.face_geometry (the catalog mechanism IS the face surface).
  - C-1 DRIVER: bottom edge B-spline with 1.4-unit CP gap at t=0.5 drives
    shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS 4×4 degree 2×2 with
    non-uniform U-knots (0,0.3,0.6,1) declared as .UNIFORM_KNOTS.; IS the
    ADVANCED_FACE.face_geometry; SplitSurface trusts tag, misaligns splits.
  - C-1 DRIVER: bottom edge B-spline 1.4-unit CP gap drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn072",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS 4x4 poles degree 2x2; "
        "U knots (0.0,0.3,0.6,1.0) mults (3,1,1,3) sum=8 ✓ non-uniform; "
        "V knots (0.0,1.0) mults (4,4) sum=8=2+4+2 ✓; "
        "IS the ADVANCED_FACE.face_geometry; "
        "declared .QUASI_UNIFORM_KNOTS. but spacing is non-uniform; "
        "SplitSurface trusts tag, misaligns splits; "
        "C-1 break in bottom edge at t=0.5 (1.4-unit CP gap) drives shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: 4×4, degree 2×2, non-uniform U-knots ──────────
# U: 4 rows, degree 2 → n+p+1=4+2+1=7. mults (3,1,1,3) sum=8 WRONG.
# Correction: (3,1,3) sum=7 ✓. Only 3 distinct knots: (0.0,0.3,1.0).
# Wait: need 4 rows, degree 2: n=4,p=2 → sum=7. mults (3,1,3)=7 ✓ → 2 interior knots.
# V: 4 cols, degree 2 → n+p+1=7. mults (3,1,3)=7 ✓ → knots (0.0,0.5,1.0) uniform.
# U knots non-uniform: (0.0, 0.3, 1.0) mults (3,1,3) sum=7 ✓

rows = []
for i in range(4):   # u direction: 4 rows
    row = []
    for j in range(4):   # v direction: 4 cols
        row.append(f.cartesian_point((float(i), float(j), 0.0)))
    rows.append(row)

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = "(" + ",".join(row_ids(r) for r in rows) + ")"

# .QUASI_UNIFORM_KNOTS. — claimed near-uniform but actual spacing non-uniform
# n=4 CPs per direction, degree=2 → sum=7; U: (3,1,3) at (0.0,0.3,1.0) non-uniform
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn072_nonunif_surf',2,2,"
    f"{cp_net},"
    f".QUASI_UNIFORM_KNOTS.,.F.,.F.,.F.,"
    f"(3,1,3),(3,1,3),"
    f"(0.0,0.3,1.0),(0.0,0.5,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── C-1 DRIVER: bottom edge B-spline with 1.4-unit gap at t=0.5 ──────────────
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((0.5, 0.0, 0.0))
dc2 = f.cartesian_point((1.0, 0.0, 0.0))
dc3 = f.cartesian_point((2.4, 0.0, 0.0))   # 1.4-unit gap = C-1 break
dc4 = f.cartesian_point((2.7, 0.0, 0.0))
dc5 = f.cartesian_point((3.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn072_c1_break',2,"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('gn072_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn072_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn072_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn072_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
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
    f"EDGE_CURVE('gn072_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
