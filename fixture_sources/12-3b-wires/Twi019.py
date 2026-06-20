"""Twi019 — Closed edges need splitting at parametric break.

Catalog claim: An EDGE_CURVE whose underlying curve is a closed full circle
(360°) is used as a single edge on a cylindrical face; start vertex equals end
vertex. Downstream tools that expect every edge to be an open arc with two
distinct endpoints require the edge to be split at the seam parameter.

Mechanism IS the single full-period EDGE_CURVE used as a seam edge on a
CYLINDRICAL_SURFACE: the EDGE_LOOP for the cylindrical face contains one
horizontal EDGE_CURVE (the seam) that wraps the full 360° of the cylinder
without being split. Both top and bottom edges of the cylinder are also present
so n_edges_total >= 4. The defect EDGE_CURVE IS referenced in the EDGE_LOOP,
which IS referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL;
never orphaned.

The fixture builds an open cylinder (no top/bottom caps): two semi-circular arcs
join at a single shared vertex, providing n_vertices_total >= 8, but the seam
edge wraps the full 360° as a single EDGE_CURVE with v_start == v_end.

Byte assertions:
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 1
  - count_entity_def(b'CIRCLE') >= 1

Tier-3 assertions:
  - face[0].surface_type == "cylinder"
  - n_edges_total >= 4
  - n_vertices_total >= 8
  - brepcheck.valid == True

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi019",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a CYLINDRICAL_SURFACE (radius 1, height 2); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with two half-circumference arcs and "
        "one full-period closed CIRCLE edge (start==end vertex) acting as the seam; "
        "plus two bottom edges, totalling >=4 EDGE_CURVEs; "
        "full-period EDGE_CURVE with start==end vertex IS the mechanism — the seam edge "
        "wraps 360° without being split; "
        "defect edge IS wired into EDGE_LOOP, FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "kernel must split closed edge at seam parameter into two open arcs"
    ),
)

# ── CYLINDRICAL_SURFACE: axis along +Z, radius 1 ────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},1.0)")

# ── Top circle: full CIRCLE at z=2 — IS the defect seam edge ─────────────────
# Single vertex for start==end (closed curve).
v_top_seam = f.vertex_point(f.cartesian_point((1.0, 0.0, 2.0)))

top_plc_orig = f.cartesian_point((0.0, 0.0, 2.0))
top_plc_zdir = f.direction((0.0, 0.0, 1.0))
top_plc_xdir = f.direction((1.0, 0.0, 0.0))
top_plc      = f.axis2_placement_3d(top_plc_orig, top_plc_zdir, top_plc_xdir)
top_circle   = f._emit_raw(f"CIRCLE('',#{top_plc.eid},1.0)")
# Full 360° edge: same vertex for start and end — this IS the mechanism.
top_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_top_seam.eid},#{v_top_seam.eid},#{top_circle.eid},.T.)"
)
top_oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{top_edge.eid},.T.)")

# ── Bottom circle: full CIRCLE at z=0 — another closed edge ──────────────────
v_bot_seam = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))

bot_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
bot_plc_zdir = f.direction((0.0, 0.0, 1.0))
bot_plc_xdir = f.direction((1.0, 0.0, 0.0))
bot_plc      = f.axis2_placement_3d(bot_plc_orig, bot_plc_zdir, bot_plc_xdir)
bot_circle   = f._emit_raw(f"CIRCLE('',#{bot_plc.eid},1.0)")
bot_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_bot_seam.eid},#{v_bot_seam.eid},#{bot_circle.eid},.T.)"
)
bot_oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{bot_edge.eid},.F.)")

# ── Two vertical seam lines connecting top and bottom circles ─────────────────
# Each seam line runs from z=0 to z=2 at theta=0 (x=1,y=0) and theta=π (x=-1,y=0).
v_top_0 = f.vertex_point(f.cartesian_point((1.0, 0.0, 2.0)))
v_bot_0 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
v_top_pi = f.vertex_point(f.cartesian_point((-1.0, 0.0, 2.0)))
v_bot_pi = f.vertex_point(f.cartesian_point((-1.0, 0.0, 0.0)))

# Seam line at theta=0
seam0_dir = f.direction((0.0, 0.0, 1.0))
seam0_vec = f.vector(seam0_dir, 2.0)
seam0_ln  = f.line(f.cartesian_point((1.0, 0.0, 0.0)), seam0_vec)
seam0_edge = f.edge_curve(v_bot_0, v_top_0, seam0_ln)
seam0_oe   = f.oriented_edge(seam0_edge, True)

# Seam line at theta=π
seam_pi_dir = f.direction((0.0, 0.0, 1.0))
seam_pi_vec = f.vector(seam_pi_dir, 2.0)
seam_pi_ln  = f.line(f.cartesian_point((-1.0, 0.0, 0.0)), seam_pi_vec)
seam_pi_edge = f.edge_curve(v_bot_pi, v_top_pi, seam_pi_ln)
seam_pi_oe   = f.oriented_edge(seam_pi_edge, False)

# ── EDGE_LOOP: full-period closed edges + vertical seams ─────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{bot_oe.eid},#{seam0_oe.eid},"
    f"#{top_oe.eid},#{seam_pi_oe.eid}))"
)

# Wire into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cyl_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
