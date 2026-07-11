"""A073 — Expand Compounds loses sub-shape locations.

Catalog claim: an 'expand compounds' operation flattens nested compounds
into single-level XCAF; sub-shapes that carry local AXIS2_PLACEMENT_3D
locations have those locations dropped, so flattened parts pile up at
the world origin.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: a nested
compound — 3 sub-shapes each with a distinct AXIS2_PLACEMENT_3D
location at (2,0,0), (4,0,0), (6,0,0).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A073",
             defect="nested compound with 3 sub-shapes at distinct locations")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# Build base face.
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
base_face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([base_face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# REPRESENTATION_MAP wrapping the base shape, then 3 MAPPED_ITEMs at
# distinct AXIS2_PLACEMENT_3D locations — the nested-compound pattern
# whose locations Expand Compounds drops.
rep_map = f._emit_raw(f"REPRESENTATION_MAP(#{plc.eid},#9060)")
for k, offset in enumerate([(2.0, 0.0, 0.0), (4.0, 0.0, 0.0), (6.0, 0.0, 0.0)]):
    p_inst = f.cartesian_point(offset)
    plc_inst = f.axis2_placement_3d(p_inst, zdir, xdir)
    f._emit_raw(
        f"MAPPED_ITEM('subshape_{k}_at_x={offset[0]}',#{rep_map.eid},#{plc_inst.eid})"
    )
