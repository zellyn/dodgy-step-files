"""A028 — Reference loss when defeaturing / simplifying for CAE.

Catalog claim: a SHAPE_ASPECT carries a face reference ('load_face_orphan')
that becomes orphaned when the face is suppressed during defeaturing.
Bytes 'SHAPE_ASPECT' and 'load_face_orphan' must appear.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A028",
             defect="SHAPE_ASPECT('load_face_orphan') referencing a face suppressed in CAE defeaturing")

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

# SHAPE_ASPECT for the face that carries the downstream load reference.
face_aspect = f._emit_raw(
    f"SHAPE_ASPECT('load_face_orphan','pressure face',#9054,.T.)"
)
# The associated property holds the Ansys face-pressure load identifier.
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('load_face_orphan','face pressure ref',#{face_aspect.eid})"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},"
    f"REPRESENTATION('load_ref',(DESCRIPTIVE_REPRESENTATION_ITEM('pressure','10.5_MPa')),#9060))"
)
# SHAPE_ASPECT_RELATIONSHIP linking the face aspect to the product shape.
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#9054)")
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('load_face_orphan','face_to_product',"
    f"#{face_aspect.eid},#{face_aspect.eid})"
)
