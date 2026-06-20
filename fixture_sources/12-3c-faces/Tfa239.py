"""Tfa239 — ShapeFix_Face.FixSplitFace (line-2908)

Multi-wire face splitting; sub-face reconstruction via outer loop + inner hole
on rational B-spline surface.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a RATIONAL_B_SPLINE_SURFACE
(NURBS). The face has TWO wires: a large outer FACE_OUTER_BOUND forming a unit
square, and an inner FACE_BOUND forming a smaller hole rectangle. The
ShapeFix_Face::FixSplitFace() code path (line 2908) handles multi-wire faces
by splitting the outer face at each inner boundary, reconstructing the topology
as separate sub-faces. The rational B-spline surface provides the geometry on
which the sub-face parameter-space computations are performed; any slight bias
in the NURBS weights causes the inner-loop containment test to hit the
FixSplitFace sub-face reconstruction branch.

Byte assertions:
  - contains(b'RATIONAL_B_SPLINE_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa239",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on RATIONAL_B_SPLINE_SURFACE (NURBS); "
        "degree 1×1, 2×2 control grid, uniform knots; "
        "bilinear weights: corner=1.0, mid-edge=0.9 (slight bias); "
        "outer FACE_OUTER_BOUND: 2×2 square CCW; "
        "inner FACE_BOUND: 0.5×0.5 hole at center, CW (hole convention); "
        "ShapeFix_Face::FixSplitFace (line 2908): multi-wire split path; "
        "inner-loop containment test → sub-face reconstruction via outer+inner; "
        "rational B-spline weights introduce NURBS bias in containment check; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── RATIONAL B-SPLINE SURFACE: bilinear patch (degree 1×1, 2×2 grid) ─────────
# Slight weight variation (0.9 at mid) introduces NURBS bias for the
# inner-loop containment test, triggering the FixSplitFace branch.
# nu=2, nv=2, u_degree=1, v_degree=1
# sum(u_mults) = nu+u_degree+1 = 2+1+1 = 4 → [2,2]
# sum(v_mults) = nv+v_degree+1 = 2+1+1 = 4 → [2,2]

cp_grid = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 2.0, 0.0)],
    [(2.0, 0.0, 0.0), (2.0, 2.0, 0.0)],
]]
wt_grid = [
    [1.0, 0.9],
    [0.9, 1.0],
]
nurbs_surf = f.rational_b_spline_surface_with_knots(
    u_degree=1, v_degree=1,
    control_points_grid=cp_grid,
    weights_grid=wt_grid,
    u_multiplicities=[2, 2],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 1.0],
    surface_form="UNSPECIFIED",
    u_closed=False,
    v_closed=False,
    self_intersect=False,
)


def _make_line_edge(va, pa, vb, pb):
    dx = pb[0] - pa[0]
    dy = pb[1] - pa[1]
    dz = pb[2] - pa[2]
    length = _math.sqrt(dx*dx + dy*dy + dz*dz)
    d = f.direction((dx/length, dy/length, dz/length))
    return f.edge_curve(va, vb, f.line(f.cartesian_point(pa), f.vector(d, length)))


# ── Outer boundary: 2×2 square CCW ───────────────────────────────────────────
o_bl = (0.0, 0.0, 0.0)
o_br = (2.0, 0.0, 0.0)
o_tr = (2.0, 2.0, 0.0)
o_tl = (0.0, 2.0, 0.0)

ov_bl = f.vertex_point(f.cartesian_point(o_bl))
ov_br = f.vertex_point(f.cartesian_point(o_br))
ov_tr = f.vertex_point(f.cartesian_point(o_tr))
ov_tl = f.vertex_point(f.cartesian_point(o_tl))

oe_bot = _make_line_edge(ov_bl, o_bl, ov_br, o_br)
oe_rgt = _make_line_edge(ov_br, o_br, ov_tr, o_tr)
oe_top = _make_line_edge(ov_tr, o_tr, ov_tl, o_tl)
oe_lft = _make_line_edge(ov_tl, o_tl, ov_bl, o_bl)

outer_loop = f.edge_loop([
    f.oriented_edge(oe_bot, True),
    f.oriented_edge(oe_rgt, True),
    f.oriented_edge(oe_top, True),
    f.oriented_edge(oe_lft, True),
])
outer_bound = f.face_outer_bound(outer_loop)

# ── Inner hole: 0.5×0.5 square at center (0.75,0.75)-(1.25,1.25), CW ────────
# CW winding for inner hole (hole convention: opposite of outer CCW)
i_bl = (0.75, 0.75, 0.0)
i_tl = (0.75, 1.25, 0.0)
i_tr = (1.25, 1.25, 0.0)
i_br = (1.25, 0.75, 0.0)

iv_bl = f.vertex_point(f.cartesian_point(i_bl))
iv_tl = f.vertex_point(f.cartesian_point(i_tl))
iv_tr = f.vertex_point(f.cartesian_point(i_tr))
iv_br = f.vertex_point(f.cartesian_point(i_br))

# CW: bl→tl→tr→br→bl
ie_lft = _make_line_edge(iv_bl, i_bl, iv_tl, i_tl)
ie_top = _make_line_edge(iv_tl, i_tl, iv_tr, i_tr)
ie_rgt = _make_line_edge(iv_tr, i_tr, iv_br, i_br)
ie_bot = _make_line_edge(iv_br, i_br, iv_bl, i_bl)

inner_loop = f.edge_loop([
    f.oriented_edge(ie_lft, True),
    f.oriented_edge(ie_top, True),
    f.oriented_edge(ie_rgt, True),
    f.oriented_edge(ie_bot, True),
])
# FACE_BOUND (not FACE_OUTER_BOUND) for inner hole, orientation=False
inner_bound = f.face_bound(inner_loop, orientation=False)

# ── ADVANCED_FACE: outer + inner wire on NURBS surface ───────────────────────
face = f.advanced_face([outer_bound, inner_bound], nurbs_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa239.stp")
