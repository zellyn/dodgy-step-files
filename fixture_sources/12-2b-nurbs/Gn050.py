"""Gn050 — ShapeUpgrade_SplitSurface.SetUSplitValues empty parameter list.

Catalog claim: Valid B-spline surface (degree 2×2, 3×4 control net) fed to
SetUSplitValues with empty split parameter list. Code initializes without
diagnostic message and produces no surface splits. Lacks error signaling for
degenerate input.

OCC behavior: silently accepts, empty result. Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree 2×2, 3×4 control net.
    U knots: (0.0, 1.0) mults (3,3) sum=6=2+3+1 ✓
    V knots: (0.0, 0.33, 0.67, 1.0) mults (3,1,1,3) sum=8=2+4+1+1=8 ✓
    This is the surface that ShapeUpgrade_SplitSurface.SetUSplitValues receives
    with an empty parameter list — the catalog mechanism IS the face geometry.
  - C-1 break on the bottom EDGE_CURVE (degree-2 B-spline with 1.5-unit gap
    at t=0.5) drives shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree 2×2 (3×4 net);
    IS the ADVANCED_FACE.face_geometry; ShapeUpgrade_SplitSurface receives this
    face's surface and SetUSplitValues is called with an empty parameter list,
    producing no splits and no diagnostic.
  - C-1 DRIVER: bottom edge B-spline with 1.5-unit positional gap at t=0.5
    drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn050",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree 2x2 3x4 net; "
        "U knots (0.0,1.0) mults (3,3) sum=6 ✓; "
        "V knots (0.0,0.33,0.67,1.0) mults (3,1,1,3) sum=8 ✓; "
        "IS the face geometry fed to ShapeUpgrade_SplitSurface.SetUSplitValues "
        "with empty split parameter list — no splits, no diagnostic; "
        "C-1 break in bottom edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: degree 2×2, 3×4 control net ──────────────────
# U knots (0.0,1.0) mults (3,3) → sum=6=2+3+1 ✓
# V knots (0.0,0.33,0.67,1.0) mults (3,1,1,3) → sum=8=2+4+1+1 ✓
# Simple grid: X in [0,4], Y in [0,6] (3 rows × 4 cols)

r0 = [f.cartesian_point((0.0, float(j * 2), 0.0)) for j in range(4)]
r1 = [f.cartesian_point((2.0, float(j * 2), 0.0)) for j in range(4)]
r2 = [f.cartesian_point((4.0, float(j * 2), 0.0)) for j in range(4)]

def row_ids(row):
    return "(" + ",".join(f"#{p.eid}" for p in row) + ")"

cp_net = f"({row_ids(r0)},{row_ids(r1)},{row_ids(r2)})"

surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn050_split_surf',2,2,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(3,1,1,3),"
    f"(0.0,1.0),(0.0,0.33,0.67,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── C-1 DRIVER: bottom edge B-spline with 1.5-unit gap at t=0.5 ─────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.0,  0.0, 0.0))
dc2 = f.cartesian_point((2.0,  0.0, 0.0))
dc3 = f.cartesian_point((3.5,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.25, 0.0, 0.0))
dc5 = f.cartesian_point((4.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn050_c1_break',2,"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('gn050_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn050_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn050_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn050_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 6.0, 0.0))
p_d = f.cartesian_point((0.0, 6.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn050_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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

e_right = mk_line_edge(v_b, v_c, (4.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 6.0)
e_top   = mk_line_edge(v_c, v_d, (4.0, 6.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 4.0)
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
