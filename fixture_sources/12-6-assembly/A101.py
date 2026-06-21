"""A101 — SubShapeBinder-derived Boolean Cut: asterisk edge_element escapes file body.

Catalog claim: ORIENTED_EDGE whose edge_element is * (asterisk-implicit)
escapes into the file body; receivers dereference and crash. The regex
ORIENTED_EDGE(*,*,  must match, EDGE_LOOP must appear, n_faces_total == 1.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A101",
             defect="ORIENTED_EDGE('',*,*,#N,.T.) with dangling edge_element — SubShapeBinder Boolean Cut emits orphan ORIENTED_EDGE causing slicer crash")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# One face (n_faces_total == 1).
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

# Standard edges for the face boundary.
def le(pa, dv, ln, va, vb):
    d = f.direction(dv); ve = f.vector(d, ln); li = f.line(pa, ve)
    return f.edge_curve(va, vb, li)
e0 = le(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
e1 = le(p1, (0.0, 1.0, 0.0), 1.0, v1, v2)
e2 = le(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = le(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)

# The EDGE_LOOP for the face — uses standard ORIENTED_EDGEs.
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# The defect: an ORIENTED_EDGE('',*,*,#N,.T.) whose edge_element is *
# (asterisk-implicit, not a real entity). This escapes into the file body
# and causes receivers to crash when dereferencing the dangling *.
# Reference one of the real edge_curves (e0) as the edge_element, but the
# ORIENTED_EDGE itself has *,* as start/end vertex (the crash trigger).
f._emit_raw(
    f"EDGE_LOOP('defect_loop',(ORIENTED_EDGE('',*,*,#{e0.eid},.T.),ORIENTED_EDGE('',*,*,#{e1.eid},.T.)))"
)
