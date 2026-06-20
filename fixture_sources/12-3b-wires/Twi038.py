"""Twi038 — Scrambled EDGE_LOOP requiring only reorder: wire-only-reorder healing doesn't update the parent face.

Catalog claim: An EDGE_LOOP whose edge_list is ordered out of cyclic head-to-tail
(consecutive ORIENTED_EDGEs do not share endpoints) needs only a reorder, no edge
replacement. When a wire-healing pass performs only a wire reorder and no other
modification, the parent face is not replaced with the new (reordered) wire. The
pass reports success, but the output shape still references the unhealed wire.

Mechanism IS the EDGE_LOOP on a planar ADVANCED_FACE whose four ORIENTED_EDGEs
are listed in scrambled order — (#e_top, #e_bot, #e_rgt, #e_lft) — so consecutive
entries do not share endpoints. This EDGE_LOOP IS wired into a FACE_OUTER_BOUND
which IS referenced by an ADVANCED_FACE in a SHELL_BASED_SURFACE_MODEL; never
orphaned. The scrambled ordering IS the sole defect: a reorder-only healing pass
must propagate the corrected EDGE_LOOP back to the parent face.

Reproducer: Square planar face (2x2 at origin) with edges visited as
top→bottom→right→left instead of bottom→right→top→left.

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
    catalog_id="Twi038",
    defect=(
        "ADVANCED_FACE on a PLANE; four EDGE_CURVEs form a 2x2 square; "
        "EDGE_LOOP lists ORIENTED_EDGEs in scrambled cyclic order: "
        "top edge first, then bottom, then right, then left — "
        "so consecutive entries do not share endpoints; "
        "scrambled EDGE_LOOP IS the mechanism (needs only reorder, not replacement); "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND IS referenced by ADVANCED_FACE in shell; "
        "healing pass must reorder and propagate new wire to parent face"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices of a 2x2 square ─────────────────────────────────────────────────
v_bl = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))  # bottom-left
v_br = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))  # bottom-right
v_tr = f.vertex_point(f.cartesian_point((2.0, 2.0, 0.0)))  # top-right
v_tl = f.vertex_point(f.cartesian_point((0.0, 2.0, 0.0)))  # top-left

# ── Edges (each a LINE segment) ───────────────────────────────────────────────
# Bottom: v_bl → v_br
bot_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)), f.vector(f.direction((1.0, 0.0, 0.0)), 2.0))
e_bot = f.edge_curve(v_bl, v_br, bot_line)
oe_bot = f.oriented_edge(e_bot, True)

# Right: v_br → v_tr
rgt_line = f.line(f.cartesian_point((2.0, 0.0, 0.0)), f.vector(f.direction((0.0, 1.0, 0.0)), 2.0))
e_rgt = f.edge_curve(v_br, v_tr, rgt_line)
oe_rgt = f.oriented_edge(e_rgt, True)

# Top: v_tr → v_tl  (traversed right-to-left)
top_line = f.line(f.cartesian_point((2.0, 2.0, 0.0)), f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0))
e_top = f.edge_curve(v_tr, v_tl, top_line)
oe_top = f.oriented_edge(e_top, True)

# Left: v_tl → v_bl
lft_line = f.line(f.cartesian_point((0.0, 2.0, 0.0)), f.vector(f.direction((0.0, -1.0, 0.0)), 2.0))
e_lft = f.edge_curve(v_tl, v_bl, lft_line)
oe_lft = f.oriented_edge(e_lft, True)

# ── SCRAMBLED EDGE_LOOP: top, bot, rgt, lft — not head-to-tail ───────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_top.eid},#{oe_bot.eid},#{oe_rgt.eid},#{oe_lft.eid}))"
)

# Wire loop into face, face into shell — never orphaned.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
