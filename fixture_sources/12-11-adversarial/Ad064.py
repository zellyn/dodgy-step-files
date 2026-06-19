"""Ad064 — Underscore inside string truncated by name-parsing consumer.

Catalog claim: consumer uses `_` as field delimiter on quoted-string
content of MANIFOLD_SURFACE_SHAPE_REPRESENTATION name; everything after
first `_` lost.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: sliver
planar face + a MANIFOLD_SURFACE_SHAPE_REPRESENTATION explicitly named
'component1_1|dipole1' to trigger the truncation.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Ad064",
             defect="MSSR name containing underscore-delimiter trigger")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Sliver face — aspect ratio 1e6.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 1.0e-5, 0.0))
p3 = f.cartesian_point((0.0, 1.0e-5, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(p0, (1.0, 0.0, 0.0), 10.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0e-5, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 10.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0e-5, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Add an EXPLICITLY-NAMED MANIFOLD_SURFACE_SHAPE_REPRESENTATION with the
# underscore-delimiter trigger string. The default MSSR from
# add_product_chain has an empty name; this extra one carries the
# trigger. Both can coexist in the file.
f._emit_raw(
    f"MANIFOLD_SURFACE_SHAPE_REPRESENTATION('component1_1|dipole1',"
    f"(#{sbsm.eid}),#9010)"
)
