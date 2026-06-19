
"""non-manifold edge (3 faces sharing one edge)"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Sw001", defect="non-manifold edge (3 faces sharing one edge)")

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

# 3 faces sharing the bottom edge (e0).
f2_p0 = f.cartesian_point((0.0, 0.0, 0.5))
f2_p1 = f.cartesian_point((1.0, 0.0, 0.5))
f2_v0 = f.vertex_point(f2_p0); f2_v1 = f.vertex_point(f2_p1)
f2_e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
f2_e1 = line_edge(p1, (0.0, 0.0, 1.0), 0.5, v1, f2_v1)
f2_e2 = line_edge(f2_p1, (-1.0, 0.0, 0.0), 1.0, f2_v1, f2_v0)
f2_e3 = line_edge(f2_p0, (0.0, 0.0, -1.0), 0.5, f2_v0, v0)
f2_loop = f.edge_loop([f.oriented_edge(f2_e0, True), f.oriented_edge(f2_e1, True),
                      f.oriented_edge(f2_e2, True), f.oriented_edge(f2_e3, True)])
plc2 = f.axis2_placement_3d(orig, f.direction((0.0, 1.0, 0.0)), xdir)
plane2 = f.plane(plc2)
face2 = f.advanced_face([f.face_outer_bound(f2_loop)], plane2)
face3 = f.advanced_face([f.face_outer_bound(f2_loop)], plane2)  # 3rd face sharing same loop
extra_shell_faces = [face2, face3]

all_faces = [face]
all_faces.extend(extra_shell_faces)
shell = f.open_shell(all_faces)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)


# Sw001 byte: 3 PLANEs total
plc3 = f.axis2_placement_3d(orig, f.direction((1.0, 0.0, 0.0)), zdir)
f.plane(plc3)
