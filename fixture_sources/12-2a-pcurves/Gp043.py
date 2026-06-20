"""Gp043 — B-spline PCURVE reversal stale-knot-domain bug (FixReversed2d).

Catalog claim: OCCT's `ShapeFix_Edge::FixReversed2d` reverses the parametric
direction of a PCURVE without re-computing its knot vector. For a B-spline
with asymmetric interior knots (e.g. degree-2, knot vector [0,0,0,0.2,1,1,1]),
forward evaluation maps interior knot u=0.2 onto 3D parameter 0.2; a reversed
evaluation requires the knot vector to be reflected to [0,0,0,0.8,1,1,1] for
the interior parameter to map correctly. The stale-knot bug leaves the
original knots intact while flipping the edge sense, causing parameter
misalignment when the edge is traversed in reverse.

Fixture (rebuilt 2026-06-19 per Sonnet rigor verify): degree-2 B-spline
pcurve with explicitly asymmetric interior knot (u=0.2 instead of mirror-
symmetric u=0.5), wrapped in EDGE_CURVE with same_sense=.F. The
non-symmetric knot vector + reversed sense is exactly the stale-knot
configuration FixReversed2d should detect and correct; OCC's heal path
silently accepts it. A stricter receiver would catch the parameter-mapping
inconsistency.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp043",
    defect=(
        "PLANE face; PCURVE degree-2 B-spline with asymmetric knots "
        "(0,0,0,0.2,1,1,1) wrapped in EDGE_CURVE same_sense=.F.; "
        "knot vector not reflected to (0,0,0,0.8,1,1,1) for the reversed "
        "edge — FixReversed2d stale-knot bug"
    ),
)

# Planar host surface
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face is a 1x1 rectangle.
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)


def straight_edge(va, vb, dir_tup, length, p_start):
    d = f.direction(dir_tup); vec = f.vector(d, length)
    ln = f.line(p_start, vec)
    return f.edge_curve(va, vb, ln)


# 3 of 4 sides are plain LINE edges (context — not the defect).
e_top = straight_edge(v11, v01, (-1.0, 0.0, 0.0), 1.0, p11)
e_left = straight_edge(v01, v00, (0.0, -1.0, 0.0), 1.0, p01)
e_right = straight_edge(v10, v11, (0.0, 1.0, 0.0), 1.0, p10)

# ──────────────────────────────────────────────────────────────────────────────
# DEFECT EDGE — bottom side, the stale-knot pcurve.
# ──────────────────────────────────────────────────────────────────────────────
# 3D LINE authored v10→v00 (right to left in 3D, magnitude 1.0).
d_bot = f.direction((-1.0, 0.0, 0.0))
vec_bot = f.vector(d_bot, 1.0)
line3d_bot = f.line(p10, vec_bot)

# PCURVE: degree-2 B-spline with non-symmetric interior knot at u=0.2.
# Control points (0,0)→(0.2,0)→(1,0) end-points match the LINE; interior
# control at (0.2,0) plus knot (0,0,0,0.2,1,1,1) breaks the linear ratio.
pc_p0 = f.cartesian_point((0.0, 0.0))
pc_p1 = f.cartesian_point((0.2, 0.0))
pc_p2 = f.cartesian_point((1.0, 0.0))
pc_basis_stale = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('stale_knots_forward_form',2,"
    f"(#{pc_p0.eid},#{pc_p1.eid},#{pc_p2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,1,3),(0.0,0.2,1.0),.UNSPECIFIED.)"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('stale_pcurve_def',(#{pc_basis_stale.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('stale_knots_pcurve',#{surf.eid},#{defrep.eid})")
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('reverse_stale',#{line3d_bot.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
# THE DEFECT: same_sense=.F. on EDGE_CURVE. Edge traversed v00→v10 (left→
# right in 3D) but the underlying 3D LINE and the pcurve are both authored
# v10→v00 (right→left). FixReversed2d should reflect the pcurve's knot
# vector (0,0,0,0.2,1,1,1) → (0,0,0,0.8,1,1,1) for correct parameter
# mapping under reversed sense; it doesn't. Sampling at t=0.5 on the
# stale pcurve evaluates to UV≈(0.6, 0) instead of the correct (0.5, 0)
# after reflection.
e_bot = f._emit_raw(
    f"EDGE_CURVE('reversed_edge_with_stale_pcurve',"
    f"#{v00.eid},#{v10.eid},#{surface_curve.eid},.F.)"
)

# Assemble the face: 4-edge outer loop traversed CCW in 3D.
loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_left, True),
])
fob = f.face_outer_bound(loop)
face = f._emit_raw(f"ADVANCED_FACE('face_with_reversed_edge',(#{fob.eid}),#{surf.eid},.T.)")
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
