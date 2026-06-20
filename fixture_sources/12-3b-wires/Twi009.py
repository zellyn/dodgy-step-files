"""Twi009 — Common vertex shared between two distinct wires (STEP-invalid).

Catalog claim: STEP requires that each wire of a face own its own distinct
VERTEX_POINTs. The sender produces a face whose outer wire and inner wire
reference the same VERTEX_POINT instance; legal in some kernel-internal BRep
representations, but invalid in STEP and ambiguous to receivers expecting
per-wire vertex ownership.

Mechanism IS the shared VERTEX_POINT between two EDGE_LOOPs: the outer
FACE_OUTER_BOUND and the inner FACE_BOUND both reference EDGE_LOOPs that
include oriented edges sharing a single VERTEX_POINT entity (#v_shared).
Outer loop: unit square. Inner loop: small square with one corner at #v_shared.
Both loops ARE wired into one ADVANCED_FACE in an OPEN_SHELL; never orphaned.
Kernel must split the shared vertex into per-wire copies or reject as malformed.

Tier-3 assertions:
  - n_edges_total >= 7
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi009",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP for a unit-square outer wire; "
        "FACE_BOUND references an EDGE_LOOP for a small inner square (hole); "
        "one VERTEX_POINT entity (#v_shared at (0.5,0.5,0)) IS referenced by "
        "both the outer wire's edge and the inner wire's edge; "
        "STEP requires per-wire distinct VERTEX_POINTs — sharing IS the defect; "
        "kernel must split shared vertex into per-wire copies or reject as malformed"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Shared vertex: IS the defect mechanism ────────────────────────────────────
# This single VERTEX_POINT entity is referenced by edges in BOTH wires.
p_shared = f.cartesian_point((0.5, 0.5, 0.0))
v_shared  = f.vertex_point(p_shared)       # shared across outer and inner loop

# ── Outer wire: unit square (0,0)→(2,0)→(2,2)→(0,2)→(0,0) ──────────────────
# One edge of the outer wire uses v_shared as its end vertex.
def mk_line_edge(px, py, qx, qy, va, vb):
    import math
    pa = f.cartesian_point((px, py, 0.0))
    dx, dy = qx - px, qy - py
    mag = math.hypot(dx, dy)
    d   = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, 1.0)
    ln  = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

# Outer square corners (2×2 for clear separation from inner square)
vO0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vO1 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))
vO2 = f.vertex_point(f.cartesian_point((2.0, 2.0, 0.0)))
# vO3 is intentionally v_shared: corner (0,2) is not at (0.5,0.5), so we
# place the shared vertex not at an outer corner but as a mid-route vertex
# in an extra edge that bridges (0,2)→(0.5,0.5)→(0,0).
# Simpler: outer square corners are normal; one outer EDGE_CURVE ends at v_shared
# as the explicit end vertex of the edge (0,2)→(0.5,0.5), and a second outer
# edge (0.5,0.5)→(0,0) completes the square — 5 outer edges total.
vO3 = f.vertex_point(f.cartesian_point((0.0, 2.0, 0.0)))

eO0 = mk_line_edge(0.0, 0.0, 2.0, 0.0, vO0, vO1)      # bottom
eO1 = mk_line_edge(2.0, 0.0, 2.0, 2.0, vO1, vO2)      # right
eO2 = mk_line_edge(2.0, 2.0, 0.0, 2.0, vO2, vO3)      # top
eO3 = mk_line_edge(0.0, 2.0, 0.5, 0.5, vO3, v_shared) # left-a: ends at SHARED vertex
eO4 = mk_line_edge(0.5, 0.5, 0.0, 0.0, v_shared, vO0) # left-b: starts at SHARED vertex

outer_loop = f.edge_loop([
    f.oriented_edge(eO0, True),
    f.oriented_edge(eO1, True),
    f.oriented_edge(eO2, True),
    f.oriented_edge(eO3, True),
    f.oriented_edge(eO4, True),
])

# ── Inner wire: small square (0.3,0.3)→(0.7,0.3)→(0.7,0.7)→(0.5,0.5)→(0.3,0.7)→(0.3,0.3)
# One corner of the inner wire IS v_shared (the same entity).
vI0 = f.vertex_point(f.cartesian_point((0.3, 0.3, 0.0)))
vI1 = f.vertex_point(f.cartesian_point((0.7, 0.3, 0.0)))
vI2 = f.vertex_point(f.cartesian_point((0.7, 0.7, 0.0)))
# vI3 = v_shared at (0.5, 0.5, 0.0) — IS the shared entity
vI4 = f.vertex_point(f.cartesian_point((0.3, 0.7, 0.0)))

eI0 = mk_line_edge(0.3, 0.3, 0.7, 0.3, vI0, vI1)
eI1 = mk_line_edge(0.7, 0.3, 0.7, 0.7, vI1, vI2)
eI2 = mk_line_edge(0.7, 0.7, 0.5, 0.5, vI2, v_shared)  # ends at SHARED vertex
eI3 = mk_line_edge(0.5, 0.5, 0.3, 0.7, v_shared, vI4)  # starts at SHARED vertex
eI4 = mk_line_edge(0.3, 0.7, 0.3, 0.3, vI4, vI0)

inner_loop = f.edge_loop([
    f.oriented_edge(eI0, True),
    f.oriented_edge(eI1, True),
    f.oriented_edge(eI2, True),
    f.oriented_edge(eI3, True),
    f.oriented_edge(eI4, True),
])

# ── Wire both loops into one ADVANCED_FACE ────────────────────────────────────
fob   = f.face_outer_bound(outer_loop)
fb    = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid},#{fb.eid}),#{plane.eid},.T.)")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
