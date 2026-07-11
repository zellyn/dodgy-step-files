"""A014 — EXTERNAL_ANCHOR uniqueness (1:1 anchor<->entity) violated; orphan EER source.

Catalog claim: two EXTERNAL_ANCHOR instances both reference the same
entity #100 — a uniqueness violation. The bytes 'EXTERNAL_ANCHOR' must
appear. One NAUO is present for assembly-presence lint.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A014",
             defect="two EXTERNAL_ANCHOR records pointing at the same entity (uniqueness violated)")

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
# The target entity for the EXTERNAL_ANCHOR uniqueness violation.
# We use the sub_pdef as the anchor target (entity #100 pattern).
nauo = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','sub','',#9054,#{sub_pdef.eid},$)"
)

# Two EXTERNAL_ANCHOR instances both referencing the same sub_pdef — the violation.
f._emit_raw(
    f"EXTERNAL_ANCHOR('AAA',#{sub_pdef.eid})"
)
f._emit_raw(
    f"EXTERNAL_ANCHOR('BBB',#{sub_pdef.eid})"
)
