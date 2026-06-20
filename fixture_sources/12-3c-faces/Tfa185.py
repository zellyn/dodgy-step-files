"""Tfa185 — ShapeFix_Face.FixAddNaturalBound surface-with-discontinuity

Catalog claim: Face on plane with C0 discontinuity in parameter domain (split
at u=5.0). Inner boundary wire spans discontinuity. FixAddNaturalBound attempts
to bridge discontinuity but produces wrong boundary topology. Tests parameter-
domain discontinuity handling in natural boundary reconstruction.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE on a B-SPLINE surface that has
a knot at u=5.0 creating a C0 (position-continuous only) seam. The surface
spans u: 0→10, v: 0→10, with a knot multiplicity=3 at u=5 enforcing a crease.
An inner hole wire is positioned to straddle the u=5 seam: its left edge is at
u=3, right edge at u=7, crossing the discontinuity. FixAddNaturalBound must
reconstruct the natural boundary around the seam; its bridging logic mispicks
the split-point topology. Defect IS on live face traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa185",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on B-SPLINE surface (degree 1, u:0-10, v:0-10) "
        "with C0 crease at u=5 (knot multiplicity=2 at interior knot); "
        "inner hole wire straddles u=5 discontinuity (x: 3-7, y: 3-7); "
        "FixAddNaturalBound bridges discontinuity but selects wrong topology; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── B-spline surface: bilinear with knot multiplicity=2 at u=5 ─────────────
# Degree 1 in both u and v. u knots: [0,5,10] with mults [2,2,2] → 6 poles.
# v knots: [0,10] with mults [2,2] → 2 poles per row.
# 6×2 control point grid:
# u=0:  (0, 0,0), (0,10,0)
# u=5a: (5, 0,0), (5,10,0)   <- first copy of u=5 (lower half)
# u=5b: (5, 0,0.5),(5,10,0.5) <- second copy of u=5 (upper half, slight Z jump = C0 kink)
# u=10: (10,0,0), (10,10,0)
# Wait: degree-1 bilinear with mult=2 at interior knot means we need degree+mult-1=2 poles
# at the seam. With degree=1: knot mults [2,2,2] → n_poles = sum(mults)-degree-1 = 6-1-1=4.
# So we have 4 control points in u: u=0, u=5(a), u=5(b), u=10.
# The C0 seam is achieved by the two u=5 poles having different Z values.

cpts = []
# Row u=0: two v poles
cpts.append([
    f.cartesian_point((0.0, 0.0,  0.0)),
    f.cartesian_point((0.0, 10.0, 0.0)),
])
# Row u=5a (C0 seam, lower side)
cpts.append([
    f.cartesian_point((5.0, 0.0,  0.0)),
    f.cartesian_point((5.0, 10.0, 0.0)),
])
# Row u=5b (C0 seam, upper side — slight Z offset to create discontinuity)
cpts.append([
    f.cartesian_point((5.0, 0.0,  0.3)),   # z=0.3: C0 kink
    f.cartesian_point((5.0, 10.0, 0.3)),
])
# Row u=10
cpts.append([
    f.cartesian_point((10.0, 0.0,  0.0)),
    f.cartesian_point((10.0, 10.0, 0.0)),
])

# Build B_SPLINE_SURFACE_WITH_KNOTS via raw emit
# u: degree=1, 4 poles, knots=[0,5,5,10] mults=[2,2,2] — wait that's 3 knots for degree=1
# with 4 poles: sum(mults) = n+degree+1 = 4+1+1=6. Mults [2,2,2] sums to 6. ✓
# v: degree=1, 2 poles, knots=[0,10] mults=[2,2] sums to 4=2+1+1. ✓

def cp_ref_grid(rows):
    row_strs = []
    for row in rows:
        row_strs.append("(" + ",".join(f"#{p.eid}" for p in row) + ")")
    return "(" + ",".join(row_strs) + ")"

cp_grid = cp_ref_grid(cpts)

bsurf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('',"
    f"1,1,"               # u_degree, v_degree
    f"{cp_grid},"         # control_points_list
    f".UNSPECIFIED.,"     # surface_form
    f".F.,.F.,"           # u_closed, v_closed
    f".F.,"               # self_intersect
    f"(2,2,2),"           # u_multiplicities  (mults at u=0,5,10)
    f"(0.0,5.0,10.0),"   # u_knots
    f"(2,2),"             # v_multiplicities (mults at v=0,10)
    f"(0.0,10.0),"        # v_knots
    f".UNSPECIFIED.)"     # knot_spec
)

# ── Outer boundary: 10×10 rectangle CCW ────────────────────────────────────
op0 = f.cartesian_point(( 0.0,  0.0, 0.0))
op1 = f.cartesian_point((10.0,  0.0, 0.0))
op2 = f.cartesian_point((10.0, 10.0, 0.0))
op3 = f.cartesian_point(( 0.0, 10.0, 0.0))

ov0 = f.vertex_point(op0); ov1 = f.vertex_point(op1)
ov2 = f.vertex_point(op2); ov3 = f.vertex_point(op3)

def _line_edge(p1, v1, p2, v2):
    dx = p2.args[1][0] - p1.args[1][0]
    dy = p2.args[1][1] - p1.args[1][1]
    dz = p2.args[1][2] - p1.args[1][2]
    length = _math.sqrt(dx*dx + dy*dy + dz*dz)
    d = f.direction((dx/length, dy/length, dz/length))
    return f.edge_curve(v1, v2, f.line(p1, f.vector(d, length)))

oe_b = _line_edge(op0, ov0, op1, ov1)
oe_r = _line_edge(op1, ov1, op2, ov2)
oe_t = _line_edge(op2, ov2, op3, ov3)
oe_l = _line_edge(op3, ov3, op0, ov0)

outer_loop = f.edge_loop([
    f.oriented_edge(oe_b, True), f.oriented_edge(oe_r, True),
    f.oriented_edge(oe_t, True), f.oriented_edge(oe_l, True),
])
outer_fob = f.face_outer_bound(outer_loop)

# ── Inner hole wire: 4×4 rectangle straddling the u=5 seam (x: 3-7, y: 3-7) ─
ip0 = f.cartesian_point((3.0, 3.0, 0.0))
ip1 = f.cartesian_point((7.0, 3.0, 0.0))
ip2 = f.cartesian_point((7.0, 7.0, 0.0))
ip3 = f.cartesian_point((3.0, 7.0, 0.0))

iv0 = f.vertex_point(ip0); iv1 = f.vertex_point(ip1)
iv2 = f.vertex_point(ip2); iv3 = f.vertex_point(ip3)

ie_b = _line_edge(ip0, iv0, ip1, iv1)
ie_r = _line_edge(ip1, iv1, ip2, iv2)
ie_t = _line_edge(ip2, iv2, ip3, iv3)
ie_l = _line_edge(ip3, iv3, ip0, iv0)

inner_loop = f.edge_loop([
    f.oriented_edge(ie_b, True), f.oriented_edge(ie_r, True),
    f.oriented_edge(ie_t, True), f.oriented_edge(ie_l, True),
])
inner_fb = f.face_bound(inner_loop, False)

face = f.advanced_face([outer_fob, inner_fb], bsurf)

shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa185.stp")
