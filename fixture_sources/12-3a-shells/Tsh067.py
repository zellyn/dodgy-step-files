
"""BREP_WITH_VOIDS where void extends past outer"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh067", defect="BREP_WITH_VOIDS where void extends past outer")

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

inner_origin = f.cartesian_point((100.0, 100.0, 100.0))
inner_plc = f.axis2_placement_3d(inner_origin, zdir, xdir)
inner_plane = f.plane(inner_plc)
ip0 = f.cartesian_point((100.0, 100.0, 100.0)); ip1 = f.cartesian_point((101.0, 100.0, 100.0))
ip2 = f.cartesian_point((101.0, 101.0, 100.0)); ip3 = f.cartesian_point((100.0, 101.0, 100.0))
iv0 = f.vertex_point(ip0); iv1 = f.vertex_point(ip1)
iv2 = f.vertex_point(ip2); iv3 = f.vertex_point(ip3)
ie0 = line_edge(ip0, (1.0, 0.0, 0.0), 1.0, iv0, iv1)
ie1 = line_edge(ip1, (0.0, 1.0, 0.0), 1.0, iv1, iv2)
ie2 = line_edge(ip2, (-1.0, 0.0, 0.0), 1.0, iv2, iv3)
ie3 = line_edge(ip3, (0.0, -1.0, 0.0), 1.0, iv3, iv0)
iloop = f.edge_loop([f.oriented_edge(ie0, True), f.oriented_edge(ie1, True),
                    f.oriented_edge(ie2, True), f.oriented_edge(ie3, True)])
inner_face = f.advanced_face([f.face_outer_bound(iloop)], inner_plane)
inner_shell = f._emit_raw(f"CLOSED_SHELL('inner_void_OUTSIDE_outer',(#{inner_face.eid}))")
outer_closed = f._emit_raw(f"CLOSED_SHELL('outer',(#{face.eid}))")
f._emit_raw(f"BREP_WITH_VOIDS('outer_with_voids',#{outer_closed.eid},(#{inner_shell.eid}))")


# Tsh067 byte: needs ORIENTED_CLOSED_SHELL
f._emit_raw(f"ORIENTED_CLOSED_SHELL('reverse_outer',*,#{outer_closed.eid},.F.)")
