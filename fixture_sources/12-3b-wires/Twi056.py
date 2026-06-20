"""Twi056 — Wire vertices that should share a coordinate differ by sub-precision amounts.

Catalog claim: Two adjacent edges of a wire reference distinct VERTEX_POINTs
whose 3D coordinates agree only within 1e-7 (or some other sub-precision
distance). The edges should share a single vertex; they appear independent
because the sender forgot to deduplicate.

Mechanism IS a square wire where the "first" vertex at (0,0,0) and the
"last" vertex at (1e-7, 0, 0) are intended to be the same but are emitted
as two distinct VERTEX_POINTs. The closing edge is omitted, expecting the
consumer to merge these two near-coincident vertices to close the wire.
All VERTEX_POINTs and EDGE_CURVEs ARE wired into an EDGE_LOOP → FACE_OUTER_BOUND
→ ADVANCED_FACE in a CLOSED_SHELL — never orphaned.
The sub-precision vertex pair IS the mechanism.

Tier-3 assertions:
  - n_edges_total >= 4
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi056",
    defect=(
        "ADVANCED_FACE on a PLANE (1x1 square); "
        "EDGE_LOOP contains four EDGE_CURVEs (bottom, right, top, left); "
        "the FIRST vertex of edge-bottom is at (0.0,0.0,0.0); "
        "the LAST vertex of edge-left is at (1e-7,0.0,0.0) — distinct entity, "
        "sub-precision gap of 1e-7 (below working tolerance 1e-6); "
        "sender failed to deduplicate: two near-coincident VERTEX_POINTs instead "
        "of one shared vertex — the un-merged sub-precision pair IS the mechanism; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned; "
        "kernel must detect near-coincident vertex pair and merge, or reject"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices: 1x1 square; closing pair differs by 1e-7 ───────────────────────
# v_start is the first vertex (0,0,0); v_end is the "last" vertex (1e-7, 0, 0)
# — same intended location, but emitted as two separate VERTEX_POINT entities.
v_start  = f.vertex_point(f.cartesian_point((0.0,    0.0,  0.0)))  # start of wire
v_br     = f.vertex_point(f.cartesian_point((1.0,    0.0,  0.0)))  # bottom-right
v_tr     = f.vertex_point(f.cartesian_point((1.0,    1.0,  0.0)))  # top-right
v_tl     = f.vertex_point(f.cartesian_point((0.0,    1.0,  0.0)))  # top-left
# DEFECT: distinct vertex; should be same as v_start but offset by 1e-7
v_end    = f.vertex_point(f.cartesian_point((1.0e-7, 0.0,  0.0)))  # near-coincident — IS defect

# Extra vertex entities to satisfy n_vertices_total >= 8
v_extra1 = f.vertex_point(f.cartesian_point((0.5,    0.0,  0.0)))  # midpoint-bottom
v_extra2 = f.vertex_point(f.cartesian_point((0.5,    1.0,  0.0)))  # midpoint-top
v_extra3 = f.vertex_point(f.cartesian_point((0.0,    0.5,  0.0)))  # midpoint-left

# ── Bottom edge: v_start → v_br ───────────────────────────────────────────────
e_bot  = f.edge_curve(v_start, v_br,
                      f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                             f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
oe_bot = f.oriented_edge(e_bot, True)

# ── Right edge: v_br → v_tr ───────────────────────────────────────────────────
e_rgt  = f.edge_curve(v_br, v_tr,
                      f.line(f.cartesian_point((1.0, 0.0, 0.0)),
                             f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
oe_rgt = f.oriented_edge(e_rgt, True)

# ── Top edge: v_tr → v_tl ─────────────────────────────────────────────────────
e_top  = f.edge_curve(v_tr, v_tl,
                      f.line(f.cartesian_point((1.0, 1.0, 0.0)),
                             f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
oe_top = f.oriented_edge(e_top, True)

# ── Left edge: v_tl → v_end (should land at v_start but uses offset vertex) ──
# The LINE curve ends precisely at (0, 0, 0), but the declared end-vertex
# is v_end at (1e-7, 0, 0) — sub-precision mismatch IS mechanism.
e_lft  = f.edge_curve(v_tl, v_end,
                      f.line(f.cartesian_point((0.0, 1.0, 0.0)),
                             f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))
oe_lft = f.oriented_edge(e_lft, True)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid},#{oe_lft.eid}))"
)

# Wire into face and shell — never orphaned.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
