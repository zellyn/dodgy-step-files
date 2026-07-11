"""A016 — UDA on multi-level reference designator (MLRD) ignored.

Catalog claim: UDAs at the assembly-instance level can be attached to
NAUOs or to MLRDs (multi-level paths). The bytes 'AS1_TO_LBR' and
'LBR_TO_NUT' must appear. Two NAUO rows required.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A016",
             defect="2 NAUO + UDA on NAUO (AS1_TO_LBR) and MLRD path (LBR_TO_NUT)")

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

# L-Bracket-Assembly.
lbr_prod = f._emit_raw(f"PRODUCT('L-Bracket-Assembly','LBR','',(#{sub_pdc.eid}))")
lbr_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{lbr_prod.eid})")
lbr_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{lbr_pdf.eid},#9053)")

# Nut subcomponent within LBR.
nut_prod = f._emit_raw(f"PRODUCT('Nut','Nut','',(#{sub_pdc.eid}))")
nut_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{nut_prod.eid})")
nut_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{nut_pdf.eid},#9053)")

# NAUO 1: AS1 → LBR (named AS1_TO_LBR — UDA is on this NAUO).
nauo_lbr = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','AS1_TO_LBR','',#9054,#{lbr_pdef.eid},$)"
)
# NAUO 2: LBR → Nut (named LBR_TO_NUT — UDA is on the MLRD path through here).
nauo_nut = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('2','LBR_TO_NUT','',#{lbr_pdef.eid},#{nut_pdef.eid},$)"
)

# UDA on NAUO (first level) — attached to the NAUO directly.
uda_prop1 = f._emit_raw(
    f"PROPERTY_DEFINITION('AS1_TO_LBR','UDA on NAUO',#{nauo_lbr.eid})"
)
# UDA on MLRD path (multi-level) — attached via a path through the second NAUO.
uda_prop2 = f._emit_raw(
    f"PROPERTY_DEFINITION('LBR_TO_NUT','UDA on MLRD path',#{nauo_nut.eid})"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{uda_prop1.eid},"
    f"REPRESENTATION('UDA_rep_1',(DESCRIPTIVE_REPRESENTATION_ITEM('AS1_LBR_attr','mlrd_level_1')),#9060))"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{uda_prop2.eid},"
    f"REPRESENTATION('UDA_rep_2',(DESCRIPTIVE_REPRESENTATION_ITEM('LBR_NUT_attr','mlrd_level_2')),#9060))"
)
