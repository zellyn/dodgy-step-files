
"""CLOSED_SHELL referenced from 2 MANIFOLD_SOLID_BREPs"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh066", defect="CLOSED_SHELL referenced from 2 MANIFOLD_SOLID_BREPs")

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

all_faces = [face]

shell = f.open_shell(all_faces)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

closed = f._emit_raw(f"CLOSED_SHELL('shared',(#{face.eid}))")
f._emit_raw(f"MANIFOLD_SOLID_BREP('brep_a',#{closed.eid})")
f._emit_raw(f"MANIFOLD_SOLID_BREP('brep_b',#{closed.eid})")


# Tsh066 byte: 6 ADVANCED_FACE
for k in range(5):
    extra_p0 = f.cartesian_point((k+2.0, 0.0, 0.0))
    extra_p1 = f.cartesian_point((k+3.0, 0.0, 0.0))
    extra_p2 = f.cartesian_point((k+3.0, 1.0, 0.0))
    extra_p3 = f.cartesian_point((k+2.0, 1.0, 0.0))
    extra_v0 = f.vertex_point(extra_p0); extra_v1 = f.vertex_point(extra_p1)
    extra_v2 = f.vertex_point(extra_p2); extra_v3 = f.vertex_point(extra_p3)
    extra_e0 = line_edge(extra_p0, (1.0, 0.0, 0.0), 1.0, extra_v0, extra_v1)
    extra_e1 = line_edge(extra_p1, (0.0, 1.0, 0.0), 1.0, extra_v1, extra_v2)
    extra_e2 = line_edge(extra_p2, (-1.0, 0.0, 0.0), 1.0, extra_v2, extra_v3)
    extra_e3 = line_edge(extra_p3, (0.0, -1.0, 0.0), 1.0, extra_v3, extra_v0)
    extra_loop = f.edge_loop([f.oriented_edge(extra_e0, True), f.oriented_edge(extra_e1, True),
                              f.oriented_edge(extra_e2, True), f.oriented_edge(extra_e3, True)])
    f.advanced_face([f.face_outer_bound(extra_loop)], plane)
