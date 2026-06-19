"""Wr053 — Toroidal-surface portion of fused solid corrupted on STEP round-trip.

Catalog claim: a fused solid containing a toroidal sub-surface (torus +
cylinder boolean) loses geometric fidelity through write+read. The torus
parameters (major + minor radius) round-trip cleanly via OCCT's writer
but the post-fuse face_outer_bound topology gets corrupted — specifically
the edge count and vertex count drift from the in-memory original.

Source: pattern-mined from OCCT/tests/bugs/step/bug32556 (LGPL-clean —
pattern only, no bytes copied). The OCCT regression: torus(5, 3) fused
with cylinder(radius 2, height 10) should produce a 12-edge / 7-vertex
result; OCCT-pre-fix produces a corrupted shape with non-matching counts.
We synthesize the *pre-corruption* fused-shape fixture for receivers to
exercise.

LGPL-clean: pattern-matched, no bytes copied.
"""
from math import pi
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Wr053",
             defect="fused torus + cylinder, write-side corruption")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc_torus = f.axis2_placement_3d(orig, zdir, xdir)

# Torus: major radius 5, minor radius 3.
torus = f._emit_raw(f"TOROIDAL_SURFACE('major5_minor3',#{plc_torus.eid},5.0,3.0)")

# Cylinder: radius 2, vertical axis offset to +5 X.
cyl_origin = f.cartesian_point((5.0, 0.0, -5.0))
plc_cyl = f.axis2_placement_3d(cyl_origin, zdir, xdir)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('r2_h10',#{plc_cyl.eid},2.0)")

# Minimal face on each surface so the fixture has the two surfaces visible
# to a writer that traverses the BRep. The fused-result-checking happens in
# the consumer; here we provide a clean torus + cylinder pair the writer
# round-trip must preserve.
v_t_start = f.vertex_point(f.cartesian_point((8.0, 0.0, 0.0)))
v_t_end = v_t_start
circ_t_plc = f.axis2_placement_3d(orig, zdir, xdir)
circ_t = f._emit_raw(f"CIRCLE('torus_outer_circle',#{circ_t_plc.eid},8.0)")
edge_t = f.edge_curve(v_t_start, v_t_end, circ_t)
loop_t = f.edge_loop([f.oriented_edge(edge_t, True)])
face_t = f.advanced_face([f.face_outer_bound(loop_t)], torus)

v_c_bot = f.vertex_point(f.cartesian_point((7.0, 0.0, -5.0)))
v_c_top = f.vertex_point(f.cartesian_point((7.0, 0.0, 5.0)))
seam_dir = f.direction((0.0, 0.0, 1.0))
seam_vec = f.vector(seam_dir, 10.0)
seam_line = f.line(f.cartesian_point((7.0, 0.0, -5.0)), seam_vec)
edge_seam = f.edge_curve(v_c_bot, v_c_top, seam_line)
bot_circ_plc = f.axis2_placement_3d(cyl_origin, zdir, xdir)
bot_circ = f._emit_raw(f"CIRCLE('cyl_bot_circ',#{bot_circ_plc.eid},2.0)")
edge_bot = f.edge_curve(v_c_bot, v_c_bot, bot_circ)
top_origin = f.cartesian_point((5.0, 0.0, 5.0))
top_circ_plc = f.axis2_placement_3d(top_origin, zdir, xdir)
top_circ = f._emit_raw(f"CIRCLE('cyl_top_circ',#{top_circ_plc.eid},2.0)")
edge_top = f.edge_curve(v_c_top, v_c_top, top_circ)
loop_c = f.edge_loop([
    f.oriented_edge(edge_bot, True),
    f.oriented_edge(edge_seam, True),
    f.oriented_edge(edge_top, True),
    f.oriented_edge(edge_seam, False),
])
face_c = f.advanced_face([f.face_outer_bound(loop_c)], cyl)

shell = f.open_shell([face_t, face_c])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
