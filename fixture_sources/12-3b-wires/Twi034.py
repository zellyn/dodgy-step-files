"""Twi034 — EDGE_LOOP missing the closing edge (open near-closed wire).

Catalog claim: An EDGE_LOOP is missing the edge that would close it back to
its starting vertex; three ORIENTED_EDGEs form an L-shape (bottom, right, top,
with no closing left edge), so the wire never returns to its start vertex. The
fixer's default ClosedWireMode mis-matches the caller's expectation: a closed
wire missing one edge gets treated as intentionally open and never repaired.

Mechanism IS the EDGE_LOOP containing only three of the four required edges of
a rectangular face: bottom (v00→v10), right (v10→v11), top (v11→v01) — the
closing left edge (v01→v00) is absent. The three-edge EDGE_LOOP IS wired into
a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL; never orphaned.
Callers must explicitly set ClosedWireMode per topological context; healer
must respect it and insert or synthesise the missing closing edge.

Reproducer: Planar ADVANCED_FACE with outer wire of three edges; pass through
ShapeFix_Wire with ClosedWireMode=Standard_True.

Byte assertions:
  - count_entity_def(b'PLANE') == 1
  - count_entity_def(b'EDGE_LOOP') == 1

Tier-3 assertions:
  - n_edges_total >= 3
  - face[0].surface_type == "plane"
  - n_vertices_total >= 6

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi034",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, 2x2 square); "
        "FACE_OUTER_BOUND references an EDGE_LOOP containing only three ORIENTED_EDGEs: "
        "bottom edge (v00→v10), right edge (v10→v11), top edge (v11→v01); "
        "the closing left edge (v01→v00) is absent — "
        "wire ends at v01 but started at v00, never returns to start; "
        "three-edge open EDGE_LOOP on a rectangular face IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "healer with ClosedWireMode must insert the missing closing edge"
    ),
)

# ── PLANE: z=0, normal +Z ─────────────────────────────────────────────────────
plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_zdir = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_plc  = f.axis2_placement_3d(plane_orig, plane_zdir, plane_xdir)
plane_surf = f._emit_raw(f"PLANE('',#{plane_plc.eid})")

# ── Four corner vertices (three used in the open wire, v00 unreached at end) ──
v00 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))  # start vertex — never re-reached
v10 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))
v11 = f.vertex_point(f.cartesian_point((2.0, 2.0, 0.0)))
v01 = f.vertex_point(f.cartesian_point((0.0, 2.0, 0.0)))  # end vertex — wire stops here

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

# ── EDGE_LOOP: three edges only — missing left (closing) edge IS the mechanism ─
# Wire: v00→v10→v11→v01; never returns to v00. Open wire on closed face.
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid}))"
)

# Wire into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
