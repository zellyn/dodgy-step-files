"""A032 — Schema migration: enum-value reordering between AP242 Ed.2 and Ed.3.

Catalog claim: four enums reordered between Ed.2 and Ed.3; code comparing
by ordinal silently misinterprets values. GEOMETRIC_TOLERANCE_WITH_DATUM_REFERENCE
and GEOMETRIC_TOLERANCE_WITH_MODIFIERS must appear.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A032",
             defect="GEOMETRIC_TOLERANCE_WITH_DATUM_REFERENCE + GEOMETRIC_TOLERANCE_WITH_MODIFIERS (enum reorder trap)",
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

# NAUO for assembly presence.
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('Sub','Sub','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','sub','',#9054,#{sub_pdef.eid},$)"
)

# Geometric tolerance infrastructure.
shape_asp = f._emit_raw(
    f"SHAPE_ASPECT('tol_face','tolerance surface',#9054,.T.)"
)
datum_feat = f._emit_raw(
    f"DATUM_FEATURE('A_datum','',#9054,.T.)"
)
datum = f._emit_raw(
    f"DATUM('datum_A','',#{datum_feat.eid},.T.)"
)
datum_ref = f._emit_raw(
    f"DATUM_REFERENCE(.MAXIMUM.,.BASIC.,#{datum.eid})"
)

# GEOMETRIC_TOLERANCE_WITH_DATUM_REFERENCE — uses datum_reference_modifier_type enum.
gtdr = f._emit_raw(
    f"GEOMETRIC_TOLERANCE_WITH_DATUM_REFERENCE('flatness_tol','',LENGTH_MEASURE(0.05),"
    f"#{shape_asp.eid},(#{datum_ref.eid}))"
)

# GEOMETRIC_TOLERANCE_WITH_MODIFIERS — uses geometric_tolerance_modifier enum.
f._emit_raw(
    f"GEOMETRIC_TOLERANCE_WITH_MODIFIERS('flat_mod','',LENGTH_MEASURE(0.05),"
    f"#{shape_asp.eid},(.MAXIMUM_MATERIAL_REQUIREMENT.))"
)
