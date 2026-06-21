"""A030 — Edition-mixed Part 21 file (header schema vs instance schema).

Catalog claim: FILE_SCHEMA declares AP214 (AUTOMOTIVE_DESIGN) but
payload contains AP242-only entities. NEXT_ASSEMBLY_USAGE_OCCURRENCE
and SHAPE_ASPECT must be present.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A030",
             defect="AP214 schema header + AP242-only entities (edition-mixed STEP file)")

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
# AP214 schema declared in header (default for StepFile).
f.add_product_chain(sbsm)

sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('Sub','Sub','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9003)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','sub','',#9004,#{sub_pdef.eid},$)"
)

# AP242-only entity in the payload (SHAPE_ASPECT with AP242 semantics).
# This is legal AP242 but the header declares AP214 — the edition mismatch.
shape_asp = f._emit_raw(
    f"SHAPE_ASPECT('ap242_aspect','AP242 Edition-3 hole feature',#{sub_pdef.eid},.T.)"
)
# ROUND_HOLE is an AP242-only entity — violates the declared AP214 schema.
# This triggers the schema-oracle AP242-in-AP214 detection.
f._emit_raw(
    f"ROUND_HOLE('rh1','',#{shape_asp.eid},.T.)"
)
