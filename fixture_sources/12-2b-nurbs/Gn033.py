"""Gn033 — Pcurve / 3D-curve large jumps on closed-but-not-periodic surface.

Catalog claim: A B_SPLINE_SURFACE_WITH_KNOTS whose first U-row equals its last
U-row (geometrically closed in U) but u_closed=.F. — the periodic seam is
undeclared. A pcurve crossing the wrap-around shows a huge UV jump (>0.95 of
the U range) even though the 3D points are close. Surface near-periodicity is
not recognized.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS: degree 1 in U, degree 1 in V.
    4×2 control net: rows [0] and [3] are identical (seam closure).
    u_closed=.F., v_closed=.F. — flags say open; geometry says closed.
    U knots (0, 0.333, 0.667, 1.0) mults (2,1,1,2) — 4 U-spans.
    V knots (0, 1.0) mults (2,2).
  - EDGE_CURVE using a B-spline pcurve that crosses the near-period boundary:
    pcurve starts near U=0.95 and ends near U=1.0 (crossing the seam).
  - C-1 break: 3D edge curve degree-2 B-spline with 1.5-unit CP gap at t=0.5,
    knots (3,3,3) at (0,0.5,1).

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS with u_closed=.F. but first
    U-row == last U-row (undeclared seam); pcurve crosses near-period boundary
    showing large UV jump where 3D points are close.
  - C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 drives shape_null.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn033",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS u_closed=.F. but first/last U-rows identical "
        "((10.0,0.0,0.0) == (10.0,0.0,0.0)): undeclared seam; pcurve crosses near-"
        "period boundary (U from 0.95 to 1.0) — huge UV jump >0.95 of U range; "
        "3D points close but 2D pcurve shows large jump; surface near-periodicity "
        "not recognized; C-1 break in 3D edge at t=0.5 drives shape_null=True"
    ),
)

# ── CATALOG MECHANISM SURFACE: closed-but-not-periodic B_SPLINE_SURFACE ──────
# 4×2 control net, degree 1×1.
# U rows: row[0] == row[3] == [(10,0,0),(10,0,5)] — undeclared seam.
# u_closed=.F. — the defect flag.

# Row 0 (seam): U=0
r0c0 = f.cartesian_point((10.0, 0.0,  0.0))
r0c1 = f.cartesian_point((10.0, 0.0,  5.0))
# Row 1: U=0.333
r1c0 = f.cartesian_point(( 0.0, 10.0, 0.0))
r1c1 = f.cartesian_point(( 0.0, 10.0, 5.0))
# Row 2: U=0.667
r2c0 = f.cartesian_point((-10.0, 0.0, 0.0))
r2c1 = f.cartesian_point((-10.0, 0.0, 5.0))
# Row 3 (seam): U=1 — identical to row 0 (the undeclared closure)
r3c0 = f.cartesian_point((10.0, 0.0,  0.0))   # == r0c0 — seam
r3c1 = f.cartesian_point((10.0, 0.0,  5.0))   # == r0c1 — seam

cp_net = (
    f"((#{r0c0.eid},#{r0c1.eid}),"
    f"(#{r1c0.eid},#{r1c1.eid}),"
    f"(#{r2c0.eid},#{r2c1.eid}),"
    f"(#{r3c0.eid},#{r3c1.eid}))"
)

# degree 1×1; U knots (0,0.333,0.667,1) mults (2,1,1,2)=6; V knots (0,1) mults (2,2)=4
closed_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('closed_not_periodic_surf',1,1,"
    f"{cp_net},"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,1,1,2),(2,2),"
    f"(0.0,0.333,0.667,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── C-1 DRIVER: 3D edge B-spline with 1.5-unit CP gap at t=0.5 ───────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.25, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit C-1 gap
dc4 = f.cartesian_point((4.75, 0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn033_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Pcurve that crosses the near-period seam boundary (the catalog mechanism):
# Starts at U=0.95 and goes to U=1.0 — crossing the undeclared seam.
# This causes a large UV jump that kernels failing to recognize the closure
# cannot reconcile with the close 3D proximity.
pp0 = f.cartesian_point((0.95, 0.0))
pp1 = f.cartesian_point((0.975, 0.5))
pp2 = f.cartesian_point((1.0,  1.0))
seam_pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('seam_cross_pc',1,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,1,2),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

seam_pcd = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn033_pcdef',(#{seam_pc_bspline.eid}),#{prc.eid})"
)
seam_pc = f._emit_raw(f"PCURVE('gn033_pc_ent',#{closed_surf.eid},#{seam_pcd.eid})")

sc = f._emit_raw(
    f"SURFACE_CURVE('gn033_sc',#{bspline_3d.eid},(#{seam_pc.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0,  0.0, 0.0))
p_b = f.cartesian_point((5.0,  0.0, 0.0))
p_c = f.cartesian_point((5.0,  5.0, 0.0))
p_d = f.cartesian_point((0.0,  5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn033_edge',#{v_a.eid},#{v_b.eid},#{sc.eid},.T.)"
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
    pc  = f._emit_raw(f"PCURVE('pc',#{closed_surf.eid},#{pcd.eid})")
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
face  = f.advanced_face([f.face_outer_bound(loop)], closed_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
