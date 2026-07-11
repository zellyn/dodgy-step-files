"""A029 — User-Defined Attribute (UDA) target-binding inconsistency.

Catalog claim: same UDA template bound differently across CAD systems —
to product, product_definition, NAUO, or SHAPE_ASPECT. Round-trip loses
the binding. A 'mat_aspect' SHAPE_ASPECT is the key identifier.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A029",
             defect="UDA bound to SHAPE_ASPECT('mat_aspect') instead of NAUO — target-binding mismatch")

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
sub_prod = f._emit_raw(f"PRODUCT('Sub','Sub','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','sub','',#9054,#{sub_pdef.eid},$)"
)

# NX-style UDA bound to SHAPE_ASPECT instead of NAUO — the binding mismatch.
mat_aspect = f._emit_raw(
    f"SHAPE_ASPECT('mat_aspect','material binding',#{sub_pdef.eid},.T.)"
)
uda_prop = f._emit_raw(
    f"PROPERTY_DEFINITION('mat_aspect','material UDA',#{mat_aspect.eid})"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{uda_prop.eid},"
    f"REPRESENTATION('mat_uda',(DESCRIPTIVE_REPRESENTATION_ITEM('material','Steel_1045')),#9060))"
)
