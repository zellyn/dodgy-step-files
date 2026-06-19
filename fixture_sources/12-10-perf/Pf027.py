"""Pf027 — Mixed-scale features produce millions of tiny faces post-tessellation.

Catalog claim: long large-scale primary surface (e.g. 1500 mm cylindrical
sleeve) interrupted by sub-mm fillet faces. Tessellator allocates uniform
mesh budget across all surfaces and runs out at the fillets, producing
tiny degenerate-Jacobian faces.

Previous fixture used 5 ADVANCED_FACEs all sharing the same empty
EDGE_LOOP placeholder. Regen: a 1500 mm CYLINDRICAL_SURFACE shaft + 20
real sub-mm fillet TOROIDAL_SURFACEs along its length, each with a real
small face boundary.
"""
from math import pi
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pf027",
             defect="1500mm shaft + 20 sub-mm fillet surfaces (mixed-scale tessellation)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)

# 1500 mm primary cylindrical shaft, radius 15 mm.
shaft = f._emit_raw(f"CYLINDRICAL_SURFACE('shaft_1500mm',#{plc.eid},15.0)")

# 20 sub-mm fillet tori distributed along the shaft length.
# Each fillet sits at z in [50, 1450] in increments of 70 mm.
# Minor radius 0.05 mm = 5e-2 mm — sub-tessellation scale.
NUM_FILLETS = 20

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# Shaft face: large outer boundary.
# Bottom + top circles + a seam line.
p_bot = f.cartesian_point((15.0, 0.0, 0.0))
p_top = f.cartesian_point((15.0, 0.0, 1500.0))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)
seam_dir = f.direction((0.0, 0.0, 1.0))
seam_vec = f.vector(seam_dir, 1500.0)
seam_line = f.line(p_bot, seam_vec)
seam_edge = f.edge_curve(v_bot, v_top, seam_line)

bot_plc = f.axis2_placement_3d(orig, zdir, xdir)
bot_circle = f._emit_raw(f"CIRCLE('bot',#{bot_plc.eid},15.0)")
bot_edge = f.edge_curve(v_bot, v_bot, bot_circle)
top_origin = f.cartesian_point((0.0, 0.0, 1500.0))
top_plc = f.axis2_placement_3d(top_origin, zdir, xdir)
top_circle = f._emit_raw(f"CIRCLE('top',#{top_plc.eid},15.0)")
top_edge = f.edge_curve(v_top, v_top, top_circle)

shaft_loop = f.edge_loop([
    f.oriented_edge(bot_edge, True),
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(top_edge, True),
    f.oriented_edge(seam_edge, False),
])
shaft_face = f.advanced_face([f.face_outer_bound(shaft_loop)], shaft)
faces = [shaft_face]

# 20 fillet surfaces — sub-mm torus axes along the shaft.
for k in range(NUM_FILLETS):
    z = 50.0 + k * 70.0
    fillet_center = f.cartesian_point((0.0, 0.0, z))
    fillet_plc = f.axis2_placement_3d(fillet_center, zdir, xdir)
    # Toroidal surface: major radius 15 (shaft radius), minor radius 0.05 (sub-mm).
    torus = f._emit_raw(
        f"TOROIDAL_SURFACE('fillet_{k}',#{fillet_plc.eid},15.0,0.05)"
    )
    # Minimal fillet boundary: a small circle at the torus equator.
    fillet_vp = f.cartesian_point((15.05, 0.0, z))
    fillet_v = f.vertex_point(fillet_vp)
    fillet_circ_plc = f.axis2_placement_3d(fillet_center, zdir, xdir)
    fillet_circ = f._emit_raw(f"CIRCLE('fillet_{k}_arc',#{fillet_circ_plc.eid},15.05)")
    fillet_edge = f.edge_curve(fillet_v, fillet_v, fillet_circ)
    fillet_loop = f.edge_loop([f.oriented_edge(fillet_edge, True)])
    faces.append(f.advanced_face([f.face_outer_bound(fillet_loop)], torus))

shell = f._emit_raw(
    f"OPEN_SHELL('mixed_scale_shell',({','.join(f'#{x.eid}' for x in faces)}))"
)
sbsm = f._emit_raw(
    f"SHELL_BASED_SURFACE_MODEL('mixed_scale_sbsm',(#{shell.eid}))"
)
f.add_product_chain(sbsm)
