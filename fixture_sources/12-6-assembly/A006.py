"""A006 — Components collapse to (0,0,0) / placement transforms lost.

Catalog claim: NAUO chain with no resolvable SHAPE_REPRESENTATION_RELATIONSHIP
transform; receiver flattens to absolute coords using identity. Every
component lands at the origin because no SRR exists to carry the offsets.
Two NAUO rows are present; zero SHAPE_REPRESENTATION_RELATIONSHIP rows.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A006",
             defect="2 NAUO + zero SHAPE_REPRESENTATION_RELATIONSHIP (placement transforms absent)")

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

# Sub-component A (NAUO 1) — no SRR to carry its transform.
prod_a = f._emit_raw(f"PRODUCT('PartA','PartA','',(#{sub_pdc.eid}))")
pdf_a = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{prod_a.eid})")
pdef_a = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{pdf_a.eid},#9053)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','comp_a','',#9054,#{pdef_a.eid},$)"
)

# Sub-component B (NAUO 2) — no SRR to carry its transform.
prod_b = f._emit_raw(f"PRODUCT('PartB','PartB','',(#{sub_pdc.eid}))")
pdf_b = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{prod_b.eid})")
pdef_b = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{pdf_b.eid},#9053)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('2','comp_b','',#9054,#{pdef_b.eid},$)"
)
# NOTE: No SHAPE_REPRESENTATION_RELATIONSHIP emitted anywhere — that is the defect.
# Both components will collapse to (0,0,0) on import.
