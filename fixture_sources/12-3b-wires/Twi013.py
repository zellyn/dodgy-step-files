"""Twi013 — Small / sliver / zero-length edges in wire (endpoints near-coincident).

Catalog claim: An EDGE_CURVE whose 3D length is below the kernel's working
tolerance; both endpoint vertices are nearly coincident. Often the remnant of a
translated tangency or an over-trimmed edge. The edge contributes nothing to the
topology but its presence in the host wire confuses traversal-order and
self-intersection logic.

Mechanism IS the near-zero-length EDGE_CURVE in the EDGE_LOOP: a 1×1 planar
face has a proper outer square but one edge in the loop is a degenerate sliver —
an EDGE_CURVE with both VERTEX_POINTs differing by only 1e-9 units (1 nm on a
1 m part, far below any kernel tolerance). The sliver edge IS referenced in the
EDGE_LOOP, which IS referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an
OPEN_SHELL; never orphaned. Kernel must drop the sliver edge and merge its
endpoints, or reject as malformed; must not let the sliver propagate into the
face outer bound.

Tier-3 assertions:
  - face[0].sliver_aspect_max_min > 1e6
  - face[0].surface_type == "plane"
  - n_edges_total >= 3

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi013",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with 4 ORIENTED_EDGEs; "
        "three edges form most of a 1×1 square; "
        "the fourth is a sliver EDGE_CURVE with both VERTEX_POINTs at (1,1,0) "
        "and (1+1e-9, 1, 0) — endpoint separation is 1e-9 (1 nm on 1 m part); "
        "near-zero-length sliver EDGE_CURVE IS the mechanism; "
        "kernel must drop sliver and merge endpoints or reject as malformed; "
        "sliver must not propagate into face outer bound"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Sliver length: 1e-9 m (far below any reasonable kernel tolerance) ─────────
SLIVER = 1e-9

def mk_line_edge(pa, pb, va, vb):
    dx = pb[0] - pa[0]; dy = pb[1] - pa[1]
    mag = math.hypot(dx, dy)
    if mag == 0.0:
        mag = 1.0  # fallback for degenerate direction
    d   = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, mag)
    ln  = f.line(f.cartesian_point(pa), vec)
    return f.edge_curve(va, vb, ln)

# ── Main 1×1 square vertices ──────────────────────────────────────────────────
v_00 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_10 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
v_11a = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))  # end of right edge
# Sliver: v_11a → v_11b; separation = 1e-9 in x
v_11b = f.vertex_point(f.cartesian_point((1.0 + SLIVER, 1.0, 0.0)))  # start of sliver end
v_01  = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))

# Three normal edges of the square
e_bot   = mk_line_edge((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), v_00, v_10)   # bottom
e_right = mk_line_edge((1.0, 0.0, 0.0), (1.0, 1.0, 0.0), v_10, v_11a)  # right
e_top   = mk_line_edge((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), v_01, v_00)   # left (reversed)

# ── Sliver edge: IS the mechanism — endpoints 1e-9 apart ─────────────────────
# From (1.0, 1.0, 0) to (1+1e-9, 1.0, 0): zero-area contribution.
e_sliver = mk_line_edge((1.0, 1.0, 0.0), (1.0 + SLIVER, 1.0, 0.0), v_11a, v_11b)

# The "closing" edge that returns from sliver end to (0,1) then completes square.
# To keep topology, add one more edge (v_11b → v_01) to close:
v_11b2 = f.vertex_point(f.cartesian_point((1.0 + SLIVER, 1.0, 0.0)))
e_close = mk_line_edge((1.0 + SLIVER, 1.0, 0.0), (0.0, 1.0, 0.0), v_11b, v_01)

# ── EDGE_LOOP with embedded sliver: IS the mechanism ─────────────────────────
loop = f.edge_loop([
    f.oriented_edge(e_bot,    True),    # (0,0)→(1,0)
    f.oriented_edge(e_right,  True),    # (1,0)→(1,1)
    f.oriented_edge(e_sliver, True),    # (1,1)→(1+1e-9,1) ← sliver (near-zero length)
    f.oriented_edge(e_close,  True),    # (1+1e-9,1)→(0,1)
    f.oriented_edge(e_top,    True),    # (0,1)→(0,0) — reversed to close
])

# Wire defect loop into face/shell topology — never orphan.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
