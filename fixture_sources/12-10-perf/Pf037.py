"""Pf037 — Two-pass loader: dangling forward-ref subgraph silently truncated.

Catalog claim (BRL-CAD step-g): an EDGE_CURVE references a forward
ID (#999) that doesn't resolve. The two-pass loader's first pass marks
the subgraph reachable but the second pass silently drops it on the
dangling reference rather than reporting it.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pf037",
             defect="EDGE_CURVE with dangling #999 forward reference (silent truncation)")

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
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
loop = f.edge_loop([f.oriented_edge(e0, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# The defect: EDGE_CURVE with dangling forward-ref to #999.
f._emit_raw("EDGE_CURVE('dangling_subgraph',#10,#11,#999,.T.)")
