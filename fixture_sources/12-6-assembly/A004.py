"""A004 — NEXT_ASSEMBLY_USAGE_OCCURRENCE references missing PRODUCT_DEFINITION.

Catalog claim: a NAUO whose related_product_definition slot points at
entity #99999 which doesn't exist in the file; the partner component
was lost or filtered out. Many readers report "successfully read" while
silently dropping the component.
Two NAUO rows: one valid, one dangling via #99999.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A004",
             defect="2 NAUO — second targets #99999 (dangling unresolved reference)")

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

# Valid sub-component (NAUO 1).
valid_prod = f._emit_raw(f"PRODUCT('Part_A','Part_A','',(#{sub_pdc.eid}))")
valid_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{valid_prod.eid})")
valid_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{valid_pdf.eid},#9003)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','part_a','',#9004,#{valid_pdef.eid},$)"
)

# Dangling NAUO — related product_definition is #99999 which does not exist.
f._emit_raw(
    "NEXT_ASSEMBLY_USAGE_OCCURRENCE('2','missing_part','',#9004,#99999,$)"
)
