"""A011 — Naming collision: same component referenced by colliding PRODUCT.name.

Catalog claim: STEP with N NAUO rows referencing one PRODUCT named 'Cap';
receivers keyed on label-as-primary-key raise ValueError or report
'Duplicate Definition of Block ignored'. The name 'Cap' must appear
at least 3 times in the byte stream.
3 NAUO rows + 3 PRODUCTs all named 'Cap'.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A011",
             defect="3 NAUO referencing 3 PRODUCTs all named 'Cap' (label collision)")

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

# 3 distinct PRODUCTs all named 'Cap' — the collision.
for i in range(1, 4):
    cap_prod = f._emit_raw(f"PRODUCT('Cap','Cap','',(#{sub_pdc.eid}))")
    cap_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{cap_prod.eid})")
    cap_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{cap_pdf.eid},#9053)")
    f._emit_raw(
        f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('{i}','cap{i}','',#9054,#{cap_pdef.eid},$)"
    )
