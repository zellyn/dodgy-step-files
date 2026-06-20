"""Twi033 — Wire contains two distinct edges that geometrically coincide.

Catalog claim: A single wire contains two distinct EDGE_CURVEs whose 3D and
2D traces coincide within tolerance; both describe the same arc but the wire
references them as separate ORIENTED_EDGEs. Likely from a failed Boolean or
duplicate-injection during translation.

Mechanism IS the EDGE_LOOP that contains two geometrically-coincident
EDGE_CURVEs (edge_main and edge_dup) referencing separate EDGE_CURVE entities
with the same underlying LINE and vertex positions. Both EDGE_CURVEs ARE wired
into the same EDGE_LOOP alongside two other distinct edges; the EDGE_LOOP IS
referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL; never
orphaned. The kernel must detect and drop the duplicate, or reject as malformed.

Reproducer: Planar ADVANCED_FACE with wire [e1, e2, e3, e2', e4] where e2' is
geometrically equal to e2 (same LINE, same vertex positions, separate entity).

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
    catalog_id="Twi033",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, 2x2 square); "
        "FACE_OUTER_BOUND references an EDGE_LOOP containing five ORIENTED_EDGEs: "
        "bottom edge (v00→v10), right edge (v10→v11), top edge (v11→v01), "
        "left edge A (v01→v00) — the main edge, "
        "left edge B (v01→v00) — a duplicate with separate EDGE_CURVE entity "
        "but geometrically identical to left edge A; "
        "two coincident EDGE_CURVEs for the left side IS the mechanism "
        "(Boolean fallout / duplicate-injection); "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "kernel must detect and drop the duplicate, or reject as malformed"
    ),
)

# ── PLANE: z=0, normal +Z ─────────────────────────────────────────────────────
plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_zdir = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_plc  = f.axis2_placement_3d(plane_orig, plane_zdir, plane_xdir)
plane_surf = f._emit_raw(f"PLANE('',#{plane_plc.eid})")

# ── Four corner vertices of a 2x2 square ─────────────────────────────────────
v00 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v10 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))
v11 = f.vertex_point(f.cartesian_point((2.0, 2.0, 0.0)))
v01 = f.vertex_point(f.cartesian_point((0.0, 2.0, 0.0)))

# ── Bottom edge: v00 → v10 ────────────────────────────────────────────────────
bot_dir  = f.direction((1.0, 0.0, 0.0))
bot_vec  = f.vector(bot_dir, 2.0)
bot_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)), bot_vec)
bot_ec   = f.edge_curve(v00, v10, bot_line)
oe_bot   = f.oriented_edge(bot_ec, True)

# ── Right edge: v10 → v11 ─────────────────────────────────────────────────────
rgt_dir  = f.direction((0.0, 1.0, 0.0))
rgt_vec  = f.vector(rgt_dir, 2.0)
rgt_line = f.line(f.cartesian_point((2.0, 0.0, 0.0)), rgt_vec)
rgt_ec   = f.edge_curve(v10, v11, rgt_line)
oe_rgt   = f.oriented_edge(rgt_ec, True)

# ── Top edge: v11 → v01 ───────────────────────────────────────────────────────
top_dir  = f.direction((-1.0, 0.0, 0.0))
top_vec  = f.vector(top_dir, 2.0)
top_line = f.line(f.cartesian_point((2.0, 2.0, 0.0)), top_vec)
top_ec   = f.edge_curve(v11, v01, top_line)
oe_top   = f.oriented_edge(top_ec, True)

# ── Left edge A (main): v01 → v00 ────────────────────────────────────────────
lft_dir_A  = f.direction((0.0, -1.0, 0.0))
lft_vec_A  = f.vector(lft_dir_A, 2.0)
lft_line_A = f.line(f.cartesian_point((0.0, 2.0, 0.0)), lft_vec_A)
lft_ec_A   = f.edge_curve(v01, v00, lft_line_A)
oe_lft_A   = f.oriented_edge(lft_ec_A, True)

# ── Left edge B (duplicate — IS the mechanism): separate EDGE_CURVE, same geom ─
# Same direction/line/vertices as lft_ec_A but a distinct STEP entity.
lft_dir_B  = f.direction((0.0, -1.0, 0.0))
lft_vec_B  = f.vector(lft_dir_B, 2.0)
lft_line_B = f.line(f.cartesian_point((0.0, 2.0, 0.0)), lft_vec_B)
lft_ec_B   = f.edge_curve(v01, v00, lft_line_B)
oe_lft_B   = f.oriented_edge(lft_ec_B, True)

# ── EDGE_LOOP: five edges with coincident left-edge pair IS the mechanism ──────
# Topological trace: v00→v10→v11→v01→v00→v00 (double-return to v00 via dup).
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid},"
    f"#{oe_lft_A.eid},#{oe_lft_B.eid}))"
)

# Wire into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
