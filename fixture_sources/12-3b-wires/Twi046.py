"""Twi046 — Edge 3D curve evaluation does not match its declared end vertices.

Catalog claim: An EDGE_CURVE's 3D representation, evaluated at the edge's parameter
range, returns points that are not the same as the edge's start/end VERTEX_POINTs;
the curve goes somewhere else entirely. Senders that regenerated the curve without
coordinating with vertices, or copied the wrong curve handle, produce this.

Mechanism IS the EDGE_CURVE on a planar ADVANCED_FACE whose VERTEX_POINTs are at
(0,0,0) and (2,0,0) but whose 3D curve is a LINE in the +Z direction starting at
(0,0,0) — evaluating at the parameter range yields (0,0,0) to (0,0,1), which does
not reach the second vertex at (2,0,0). This EDGE_CURVE IS wired into an EDGE_LOOP
→ FACE_OUTER_BOUND → ADVANCED_FACE in a SHELL_BASED_SURFACE_MODEL; never orphaned.
The mismatch between curve evaluation and declared end-vertex IS the mechanism.

Reproducer: Square planar face (2x2) where one edge's LINE runs in the +Z direction
instead of +X, so the curve endpoint lands at (0,0,2) but the declared end vertex
is at (2,0,0).

Byte assertions:
  - count_entity_def(b'PLANE') == 1
  - count_entity_def(b'EDGE_LOOP') == 1

Tier-3 assertions:
  - n_edges_total >= 4
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi046",
    defect=(
        "ADVANCED_FACE on a PLANE (2x2 square); "
        "EDGE_LOOP contains four EDGE_CURVEs; "
        "the bottom edge's VERTEX_POINTs are at (0,0,0) and (2,0,0) "
        "but its 3D LINE runs in the +Z direction: origin (0,0,0), direction (0,0,1); "
        "curve evaluation reaches (0,0,2), not the declared end vertex (2,0,0); "
        "this curve-vertex mismatch IS the mechanism; "
        "the mismatched EDGE_CURVE IS wired into EDGE_LOOP → FACE_OUTER_BOUND → "
        "ADVANCED_FACE in shell — never orphaned; "
        "kernel must detect and either drop/rebuild the bad 3D curve or reject the edge"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices: 2x2 square ─────────────────────────────────────────────────────
v_bl = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))   # bottom-left
v_br = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))   # bottom-right
v_tr = f.vertex_point(f.cartesian_point((2.0, 2.0, 0.0)))   # top-right
v_tl = f.vertex_point(f.cartesian_point((0.0, 2.0, 0.0)))   # top-left

# ── Bottom edge: vertices at (0,0,0)→(2,0,0), but LINE runs in +Z — IS mechanism ──
bad_line_dir = f.direction((0.0, 0.0, 1.0))     # WRONG: should be (1,0,0)
bad_line_vec = f.vector(bad_line_dir, 2.0)
bad_line     = f.line(f.cartesian_point((0.0, 0.0, 0.0)), bad_line_vec)
e_bot        = f.edge_curve(v_bl, v_br, bad_line)   # declared v_br=(2,0,0) but curve→(0,0,2)
oe_bot       = f.oriented_edge(e_bot, True)

# ── Right edge: v_br → v_tr (correct) ────────────────────────────────────────
rgt_line = f.line(f.cartesian_point((2.0, 0.0, 0.0)),
                  f.vector(f.direction((0.0, 1.0, 0.0)), 2.0))
e_rgt  = f.edge_curve(v_br, v_tr, rgt_line)
oe_rgt = f.oriented_edge(e_rgt, True)

# ── Top edge: v_tr → v_tl (correct) ──────────────────────────────────────────
top_line = f.line(f.cartesian_point((2.0, 2.0, 0.0)),
                  f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0))
e_top  = f.edge_curve(v_tr, v_tl, top_line)
oe_top = f.oriented_edge(e_top, True)

# ── Left edge: v_tl → v_bl (correct) ─────────────────────────────────────────
lft_line = f.line(f.cartesian_point((0.0, 2.0, 0.0)),
                  f.vector(f.direction((0.0, -1.0, 0.0)), 2.0))
e_lft  = f.edge_curve(v_tl, v_bl, lft_line)
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
