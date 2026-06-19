"""Pmi044 — DimensionalSize/GeometricTolerance via PROPERTY_DEFINITION (legacy AP203+G&DT).

Catalog claim: older AP242 / AP203+G&DT files attach the toleranced item
indirectly through a PROPERTY_DEFINITION chain rather than the modern
direct association.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: one face +
PROPERTY_DEFINITION + DIMENSIONAL_SIZE + GEOMETRIC_TOLERANCE chain in
the legacy form.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pmi044",
             defect="DIMENSIONAL_SIZE + GEOMETRIC_TOLERANCE via PROPERTY_DEFINITION (legacy)")

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

# Legacy AP203+G&DT chain.
shape_aspect = f._emit_raw(
    f"SHAPE_ASPECT('feature_aspect','',#9005,.T.)"
)
gen_prop = f._emit_raw(
    f"GENERAL_PROPERTY('hole_diameter','indirect via property_definition','')"
)
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('hole_diameter_prop','legacy AP203+GDT chain',"
    f"#{shape_aspect.eid})"
)
prop_def_rep = f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#9022)"
)
# DIMENSIONAL_SIZE reachable indirectly via the property chain above.
f._emit_raw(
    f"DIMENSIONAL_SIZE(#{shape_aspect.eid},'diameter','indirect via prop def')"
)
f._emit_raw(
    f"GEOMETRIC_TOLERANCE('cylindricity','indirect',#9009,#{shape_aspect.eid})"
)
