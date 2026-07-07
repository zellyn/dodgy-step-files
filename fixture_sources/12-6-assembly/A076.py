"""A076 — General attributes (AP242 GENERAL_PROPERTY) dropped on import.

Catalog claim: AP242 STEP file carries GENERAL_PROPERTY entities for
key/value metadata; a reader silently discards them. The file must:
  - declare AP242 schema
  - contain at least 2 GENERAL_PROPERTY entity defs
  - contain GENERAL_PROPERTY_ASSOCIATION
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A076",
             defect="GENERAL_PROPERTY('density'/'material') in AP242 file — reader silently discards",
             schema="AP242")

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

# Two GENERAL_PROPERTY entities — dropped by defective AP242 reader.
gp_density = f._emit_raw("GENERAL_PROPERTY('density','7.85',#9054)")
gp_material = f._emit_raw("GENERAL_PROPERTY('material','STEEL',#9054)")

# GENERAL_PROPERTY_ASSOCIATION links the properties to the product definition.
gpa = f._emit_raw(
    f"GENERAL_PROPERTY_ASSOCIATION('mat_props','',(#{gp_density.eid},#{gp_material.eid}),#9054)"
)
