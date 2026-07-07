"""A025 — Names with special / non-ASCII / encoded characters lost or corrupted.

Catalog claim: STEP name fields contain ISO 10303-21 control directives,
raw 8-bit characters, doubled apostrophes, backslashes. Four NAUOs required.
Four different name encoding patterns: X2 Unicode, doubled apostrophe,
backslash path, single-space.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A025",
             defect="4 NAUO with special-char PRODUCT names: X2-unicode, O''Brien, C:\\path, single-space")

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

# 4 products with different special-character name encodings.
# 1. X2 control-directive: Greek alpha U+03B1 → '\X2\03B1\X0\'.
p1_prod = f._emit_raw(
    r"PRODUCT('\X2\03B1\X0\','\X2\03B1\X0\','',(#" + str(sub_pdc.eid) + r"))"
)
p1_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{p1_prod.eid})")
p1_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{p1_pdf.eid},#9053)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','unicode_name','',#9054,#{p1_pdef.eid},$)"
)

# 2. Doubled apostrophe: O'Brien → 'O''Brien'.
p2_prod = f._emit_raw(
    "PRODUCT('O''Brien','O''Brien','',(#" + str(sub_pdc.eid) + "))"
)
p2_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{p2_prod.eid})")
p2_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{p2_pdf.eid},#9053)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('2','apostrophe_name','',#9054,#{p2_pdef.eid},$)"
)

# 3. Backslash Windows path.
p3_prod = f._emit_raw(
    "PRODUCT('C:\\\\path\\\\file','C:\\\\path\\\\file','',(#" + str(sub_pdc.eid) + "))"
)
p3_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{p3_prod.eid})")
p3_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{p3_pdf.eid},#9053)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('3','backslash_name','',#9054,#{p3_pdef.eid},$)"
)

# 4. Single space placeholder.
p4_prod = f._emit_raw(
    "PRODUCT(' ',' ','',(#" + str(sub_pdc.eid) + "))"
)
p4_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{p4_prod.eid})")
p4_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{p4_pdf.eid},#9053)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('4','space_name','',#9054,#{p4_pdef.eid},$)"
)
