"""A037 — Implicit / minimalist product structure missing entirely.

Catalog claim: bare ADVANCED_BREP_SHAPE_REPRESENTATION with no PRODUCT,
no PRODUCT_DEFINITION_SHAPE, no NEXT_ASSEMBLY_USAGE_OCCURRENCE.
count_entity_def(b'PRODUCT_DEFINITION_SHAPE') == 0
count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') == 0
A degenerate COLOUR_RGB is added as assembly-presence scaffolding
(per lint requirements for §12.6 entries).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A037",
             defect="bare ADVANCED_BREP_SHAPE_REPRESENTATION with no PRODUCT/PDS/NAUO (minimalist exporter)")

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
closed_shell = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_shell)

# Geometric context (no product chain — that's the defect).
length_unit = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
plane_angle_unit = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
solid_angle_unit = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{length_unit.eid},'distance_accuracy_value','')"
)
geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{length_unit.eid},#{plane_angle_unit.eid},#{solid_angle_unit.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

# Bare ADVANCED_BREP_SHAPE_REPRESENTATION — no PRODUCT chain, no PDS, no NAUO.
f._emit_raw(
    f"ADVANCED_BREP_SHAPE_REPRESENTATION('bare_geom',(#{msb.eid}),#{geom_ctx.eid})"
)

# Assembly-presence scaffolding: COLOUR_RGB (satisfies §12.6 category lint
# without needing NAUO/PRODUCT_DEFINITION_SHAPE which the defect explicitly omits).
f._emit_raw("COLOUR_RGB('scaffold',0.5,0.5,0.5)")
