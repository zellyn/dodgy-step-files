"""A023 — MAPPED_ITEM with non-identity transform requirement (Saved Views).

Catalog claim: a Saved View's MAPPED_ITEM mapping_source must be a
unit-identity AXIS2_PLACEMENT_3D. A file with non-identity transform
inadvertently moves the geometry only in that view.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: one base
face wrapped in a REPRESENTATION_MAP whose mapping_origin is at
P0=(10,0,0) — the NON-identity that should be identity.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A023",
             defect="REPRESENTATION_MAP mapping_origin at (10,0,0) instead of identity")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc_identity = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc_identity)

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

# Non-identity AXIS2_PLACEMENT_3D at (10,0,0) — the defect.
nonident_origin = f.cartesian_point((10.0, 0.0, 0.0))
plc_nonident = f.axis2_placement_3d(nonident_origin, zdir, xdir)
rep_map = f._emit_raw(
    f"REPRESENTATION_MAP(#{plc_nonident.eid},#9060)"   # non-identity mapping origin
)
# MAPPED_ITEM under this REPRESENTATION_MAP exercises the saved-view defect.
p_inst = f.cartesian_point((0.0, 0.0, 0.0))
plc_inst = f.axis2_placement_3d(p_inst, zdir, xdir)
f._emit_raw(
    f"MAPPED_ITEM('saved_view_inst',#{rep_map.eid},#{plc_inst.eid})"
)
