"""Ad122 — pattern-mined fixture (see catalog for source).

This is part of B4 wave-1-extension issue-tracker mining. LGPL-clean:
synthesized from the defect *pattern*, no upstream bytes copied.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Ad122",
             defect='FreeCAD#25774: exported geometry damaged — duplicate same-ID entities')

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Damaged payload: the writer reuses ID slot #5 — originally `plane`
# (PLANE('',#4), the ADVANCED_FACE's underlying_surface at #36) — for a
# second, unrelated entity. A forward-reference resolver that binds the
# LAST definition it sees for a given id (as real STEP readers do) makes
# #36's surface reference resolve to this CARTESIAN_POINT instead of the
# PLANE, damaging the geometry exactly per FreeCAD#25774.
dup_point = f.cartesian_point((7.0, 7.0, 7.0), name="damaged_dup")
assert plane.eid == 5, "Ad122 defect assumes `plane` was allocated #5"
dup_point.eid = 5  # DEFECT: reuse #5 for a second, different entity
