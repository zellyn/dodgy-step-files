"""A033 — product_definition_with_associated_documents name dropped.

Catalog claim: PRODUCT_DEFINITION_WITH_ASSOCIATED_DOCUMENTS carries its
own name attribute that OCCT did not pick up. APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT
must also appear.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A033",
             defect="PRODUCT_DEFINITION_WITH_ASSOCIATED_DOCUMENTS + APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT (name dropped)")

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

# Document associated with the product.
doc_file = f._emit_raw(
    "DOCUMENT_FILE('BOM_ref.pdf','BOM_ref.pdf','PDF','file://./BOM_ref.pdf')"
)
doc = f._emit_raw(
    f"DOCUMENT('BOM_REF_001','PLM document','specification',#{doc_file.eid})"
)

sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('PLM_Part_XYZ','PLM_Part_XYZ','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")

# PRODUCT_DEFINITION_WITH_ASSOCIATED_DOCUMENTS instead of plain PD — the defect.
pdwad = f._emit_raw(
    f"PRODUCT_DEFINITION_WITH_ASSOCIATED_DOCUMENTS('PLM_Part_XYZ','named product def',"
    f"#{sub_pdf.eid},#9053,(#{doc.eid}))"
)
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pdwad.eid})")
mssr = f._emit_raw(f"MANIFOLD_SURFACE_SHAPE_REPRESENTATION('pdwad_rep',(#{plc.eid}),#9060)")
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{mssr.eid})")

# External ID assignment for the document — the bytes that must appear.
ext_source = f._emit_raw(
    "EXTERNAL_SOURCE(IDENTIFICATION_ITEM('BOM_REF_001','BOM_ref.pdf'))"
)
ext_id = f._emit_raw(
    f"EXTERNAL_IDENTIFICATION_ASSIGNMENT('PLM_Part_XYZ','PLM doc-id',#{ext_source.eid})"
)
f._emit_raw(
    f"APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT(#{ext_id.eid},(APPLIED_SHAPE_ASPECT_ROLE($)))"
)
