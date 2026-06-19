"""Wr049 — Writer-pathology fixture: Wr049 specific byte target."""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Wr049", defect="Wr049 post-pathology output")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0)); p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0)); p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
loop = f.edge_loop([f.oriented_edge(e0, True), f.oriented_edge(e1, True),
                   f.oriented_edge(e2, True), f.oriented_edge(e3, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
# Wr049: needs SPHERICAL_SURFACE + 2 CLOSED_SHELLs or SBSM
sphere_origin = f.cartesian_point((2.0, 0.0, 0.0))
sphere_plc = f.axis2_placement_3d(sphere_origin, zdir, xdir)
sphere = f._emit_raw(f"SPHERICAL_SURFACE(\\\"\\\",#{sphere_plc.eid},1.0)")
v_sa = f.vertex_point(f.cartesian_point((3.0, 0.0, 0.0)))
v_sb = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
arc_plc = f.axis2_placement_3d(sphere_origin, zdir, xdir)
arc = f._emit_raw(f"CIRCLE(\\\"\\\",#{arc_plc.eid},1.0)")
arc_edge = f.edge_curve(v_sa, v_sb, arc)
sphere_loop = f.edge_loop([f.oriented_edge(arc_edge, True)])
sphere_face = f.advanced_face([f.face_outer_bound(sphere_loop)], sphere)
extra_shell = f._emit_raw(f"CLOSED_SHELL(\\\"\\\",(#{sphere_face.eid}))")

