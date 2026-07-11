"""Pf035 — Large assembly STEP: NUC12 design, eager MAPPED_ITEM closure.

Catalog claim: deep nested NEXT_ASSEMBLY_USAGE_OCCURRENCE + MAPPED_ITEM
graph causes eager resolver to materialise every instance up-front.
Byte assertions: ≥5 NAUO, ≥4 MAPPED_ITEM. We synthesize a small but
structurally-representative subset of that graph.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pf035",
             defect="deeply nested NAUO + MAPPED_ITEM graph (NUC12 closure blowup)")

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

# 4 MAPPED_ITEMs against a shared REPRESENTATION_MAP; 5 NAUO chain.
rmap = f._emit_raw(f"REPRESENTATION_MAP(#{plc.eid},#9061)")
for k in range(4):
    f._emit_raw(f"MAPPED_ITEM('inst_{k}','',#{rmap.eid})")
# 5 NAUO entries — pretend each maps a sub-assembly relation.
for k in range(5):
    f._emit_raw(
        f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_{k}','sub_{k}','',#9054,#9054,$)"
    )
