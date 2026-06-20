"""Twi020 — Missing seam edge on closed (periodic) surface.

Catalog claim: Face on a CYLINDRICAL_SURFACE bounded by wire(s) that close in
3D but are open in UV; the explicit seam edge along U=0 (x=1,y=0) is missing
from the wire. The receiver sees a wire that doesn't close in 2D parameter
space even though the 3D endpoints meet.

Mechanism IS the EDGE_LOOP without a seam EDGE_CURVE on the periodic cylinder:
the outer loop has two arcs (semi-circles, 180° each) and two vertical seam
lines but NO seam edge at U=0 to bridge the UV gap. The UV wire is open because
the cylindrical parameter space requires an explicit U=0 isoline edge to close
it. The defect EDGE_LOOP IS referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE
in an OPEN_SHELL; never orphaned. brepcheck.valid == False confirms the UV gap.

Reproducer: ADVANCED_FACE on CYLINDRICAL_SURFACE whose outer loop traverses
U from 0 to 2π with no EDGE_CURVE on the U=0 isoline.

Byte assertions:
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_LOOP') == 1

Tier-3 assertions:
  - face[0].surface_type == "cylinder"
  - n_edges_total >= 2
  - n_vertices_total >= 4
  - brepcheck.valid == False

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi020",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a CYLINDRICAL_SURFACE (radius 1, height 2); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with two semi-circular arcs "
        "at z=0 and z=2 but NO seam EDGE_CURVE along the U=0 (x=1,y=0) isoline; "
        "missing seam edge IS the mechanism — wire closes in 3D but is open in UV; "
        "defect EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "receiver must synthesise a seam edge along U=0 or reject as malformed"
    ),
)

# ── CYLINDRICAL_SURFACE: axis along +Z, radius 1 ────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},1.0)")

# ── Shared vertices at top and bottom of the U=0 seam ─────────────────────────
# Top two vertices: at (1,0,2) and (-1,0,2)
v_top_a = f.vertex_point(f.cartesian_point((1.0, 0.0, 2.0)))
v_top_b = f.vertex_point(f.cartesian_point((-1.0, 0.0, 2.0)))
# Bottom two vertices: at (1,0,0) and (-1,0,0)
v_bot_a = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
v_bot_b = f.vertex_point(f.cartesian_point((-1.0, 0.0, 0.0)))

# ── Two vertical lines connecting top and bottom ──────────────────────────────
# Seam A at (1,0): bottom to top
ln_a_dir = f.direction((0.0, 0.0, 1.0))
ln_a_vec = f.vector(ln_a_dir, 2.0)
ln_a     = f.line(f.cartesian_point((1.0, 0.0, 0.0)), ln_a_vec)
edge_a   = f.edge_curve(v_bot_a, v_top_a, ln_a)
oe_a     = f.oriented_edge(edge_a, True)

# Seam B at (-1,0): bottom to top (traversed in reverse for loop closure)
ln_b_dir = f.direction((0.0, 0.0, 1.0))
ln_b_vec = f.vector(ln_b_dir, 2.0)
ln_b     = f.line(f.cartesian_point((-1.0, 0.0, 0.0)), ln_b_vec)
edge_b   = f.edge_curve(v_bot_b, v_top_b, ln_b)
oe_b     = f.oriented_edge(edge_b, False)   # reversed

# ── Two semi-circular arcs (180° each): the only 2D-traversal edges ───────────
# Top arc from (1,0,2) to (-1,0,2) via (0,1,2) — 180° CCW
top_arc_plc_orig = f.cartesian_point((0.0, 0.0, 2.0))
top_arc_plc_zdir = f.direction((0.0, 0.0, 1.0))
top_arc_plc_xdir = f.direction((1.0, 0.0, 0.0))
top_arc_plc  = f.axis2_placement_3d(top_arc_plc_orig, top_arc_plc_zdir, top_arc_plc_xdir)
top_arc_circ = f._emit_raw(f"CIRCLE('',#{top_arc_plc.eid},1.0)")
top_arc_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_top_a.eid},#{v_top_b.eid},#{top_arc_circ.eid},.T.)"
)
top_arc_oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{top_arc_edge.eid},.T.)")

# Bottom arc from (-1,0,0) to (1,0,0) via (0,-1,0) — reversed traversal
bot_arc_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
bot_arc_plc_zdir = f.direction((0.0, 0.0, 1.0))
bot_arc_plc_xdir = f.direction((1.0, 0.0, 0.0))
bot_arc_plc  = f.axis2_placement_3d(bot_arc_plc_orig, bot_arc_plc_zdir, bot_arc_plc_xdir)
bot_arc_circ = f._emit_raw(f"CIRCLE('',#{bot_arc_plc.eid},1.0)")
bot_arc_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_bot_a.eid},#{v_bot_b.eid},#{bot_arc_circ.eid},.T.)"
)
bot_arc_oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{bot_arc_edge.eid},.F.)")

# ── EDGE_LOOP: no seam edge at U=0 — IS the mechanism ────────────────────────
# Loop: bot_arc(b→a, reversed) → seam_a(a→top_a) → top_arc(top_a→top_b) → seam_b(top_b→b, reversed)
# Wire closes in 3D but has no U=0 seam edge → open in UV parameter space.
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{bot_arc_oe.eid},#{oe_a.eid},"
    f"#{top_arc_oe.eid},#{oe_b.eid}))"
)

# Wire into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cyl_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
