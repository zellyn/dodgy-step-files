"""A069 — Material with zero density blocks STEP write.

Catalog claim: a material entity with MASS_DENSITY_MEASURE(0.0) causes
the writer to throw. Both 'MASS_DENSITY_MEASURE(0.0)' and
'PROPERTY_DEFINITION' must appear.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A069",
             defect="MASS_DENSITY_MEASURE(0.0) in PROPERTY_DEFINITION — writer rejects zero density")

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

# Material with MASS_DENSITY_MEASURE(0.0) — the writer-rejection trigger.
mat_unit = f._emit_raw(
    "(MASS_UNIT()NAMED_UNIT(*)SI_UNIT(.KILO.,.GRAM.))"
)
vol_unit = f._emit_raw(
    "(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))"
)
# MEASURE_WITH_UNIT carrying zero density.
density_mwu = f._emit_raw(
    f"MEASURE_WITH_UNIT(MASS_DENSITY_MEASURE(0.0),#{mat_unit.eid})"
)
mat_prop = f._emit_raw(
    f"PROPERTY_DEFINITION('density','material density',#9054)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{mat_prop.eid},"
    f"REPRESENTATION('mat_rep',(#{density_mwu.eid}),#9060))"
)
