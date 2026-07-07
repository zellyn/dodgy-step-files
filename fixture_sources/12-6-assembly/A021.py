"""A021 — CDORSI WR1 violated by per-component styling in Saved View.

Catalog claim: CONTEXT_DEPENDENT_OVER_RIDING_STYLED_ITEM whose style_context
mixes a MAPPED_ITEM with SHAPE_REPRESENTATION_RELATIONSHIPs — violating WR1.
count_entity_def(b'SHAPE_REPRESENTATION_RELATIONSHIP') == 2,
contains(b'COLOUR_RGB'), contains(b'MAPPED_ITEM').
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A021",
             defect="CDORSI WR1 violated — style_context mixes MAPPED_ITEM with REPRESENTATION_RELATIONSHIP (2 SRR + COLOUR_RGB + MAPPED_ITEM)")

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

# Sub-component product chain.
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('Comp','Comp','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)")

# Sub-shape representations for MAPPED_ITEM and SRRs.
sub_sr = f._emit_raw(f"SHAPE_REPRESENTATION('sub_rep',(#{plc.eid}),#9060)")
rep_map = f._emit_raw(f"REPRESENTATION_MAP(#{plc.eid},#{sub_sr.eid})")
mapped_item_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('mi_plc',#{orig.eid},#{zdir.eid},#{xdir.eid})"
)
mi = f._emit_raw(f"MAPPED_ITEM('comp_instance',#{rep_map.eid},#{mapped_item_plc.eid})")

# Two SHAPE_REPRESENTATION_RELATIONSHIPs (the WR1-violating context entries).
srr1 = f._emit_raw(
    f"SHAPE_REPRESENTATION_RELATIONSHIP('srr1','',#9060,#{sub_sr.eid})"
)
srr2 = f._emit_raw(
    f"SHAPE_REPRESENTATION_RELATIONSHIP('srr2','',#9060,#{sub_sr.eid})"
)

# COLOUR_RGB for the styling.
colour = f._emit_raw("COLOUR_RGB('comp_color',1.0,0.0,0.0)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
si = f._emit_raw(f"STYLED_ITEM('comp_style',(#{psa.eid}),#{face.eid})")

# CONTEXT_DEPENDENT_OVER_RIDING_STYLED_ITEM with mixed style_context:
# (MAPPED_ITEM + SHAPE_REPRESENTATION_RELATIONSHIP) — WR1 violation.
# The style_context must be a list containing both types — this is the defect.
f._emit_raw(
    f"CONTEXT_DEPENDENT_OVER_RIDING_STYLED_ITEM('cdorsi',(#{psa.eid}),#{face.eid},"
    f"(#{mi.eid},#{srr1.eid},#{srr2.eid}))"
)
