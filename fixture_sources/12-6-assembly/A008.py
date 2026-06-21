"""A008 — AP242 Ed.2 widened SELECT for product_definition_relationship.related/relating.

Catalog claim: AP242e2 changed representation_relationship.rep_1/rep_2 and
product_definition_relationship.related/relating from direct references to
SELECT types. Code doing direct dot-access crashes against an Ed.2 file
whose related is a SELECT case wrapping a product_definition_occurrence.
Fixture must contain NEXT_ASSEMBLY_USAGE_OCCURRENCE and MAPPED_ITEM.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A008",
             defect="AP242e2 SELECT widened for related/relating — NAUO + MAPPED_ITEM in Ed.2 context",
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

sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
# Sub-component product.
sub_prod = f._emit_raw(f"PRODUCT('Sub','Sub','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9003)")

# AP242 Ed.2 PRODUCT_DEFINITION_OCCURRENCE wrapping the sub PD (SELECT widening).
pdo = f._emit_raw(
    f"PRODUCT_DEFINITION_OCCURRENCE('pdo_1','',#{sub_pdef.eid})"
)

# NAUO using the wrapping PDO as the related slot — Ed.2 SELECT form.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','sub_e2','',#9004,#{pdo.eid},$)"
)

# REPRESENTATION_MAP + MAPPED_ITEM for the sub-component.
sub_sr = f._emit_raw(f"SHAPE_REPRESENTATION('sub_rep',(#{plc.eid}),#9010)")
rep_map = f._emit_raw(f"REPRESENTATION_MAP(#{plc.eid},#{sub_sr.eid})")
f._emit_raw(f"MAPPED_ITEM('mi1',#{rep_map.eid},#{plc.eid})")
