"""A035 — Product with both sub-assemblies and direct shape.

Catalog claim: a PRODUCT_DEFINITION is simultaneously an assembly parent
(referenced by 2 NAUOs as the relating party) AND a leaf node with its
own direct geometry (SHAPE_DEFINITION_REPRESENTATION + shape rep).
2 NAUO + 2 MAPPED_ITEM required.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A035",
             defect="root PD acts as both assembly parent (2 NAUO) and leaf with direct geometry (2 MAPPED_ITEM)")

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
# This is the HYBRID product that has BOTH direct shape AND sub-assembly children.
f.add_product_chain(sbsm)

sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")

# Sub-component A.
prod_a = f._emit_raw(f"PRODUCT('PartA','PartA','',(#{sub_pdc.eid}))")
pdf_a = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{prod_a.eid})")
pdef_a = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{pdf_a.eid},#9003)")

# Sub-component B.
prod_b = f._emit_raw(f"PRODUCT('PartB','PartB','',(#{sub_pdc.eid}))")
pdf_b = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{prod_b.eid})")
pdef_b = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{pdf_b.eid},#9003)")

# 2 NAUOs — root (#9004) acts as parent for both A and B.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','comp_a','',#9004,#{pdef_a.eid},$)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('2','comp_b','',#9004,#{pdef_b.eid},$)"
)

# Sub-shape representations for the MAPPED_ITEMs.
rep_map_a = f._emit_raw(f"REPRESENTATION_MAP(#{plc.eid},#9010)")
rep_map_b = f._emit_raw(f"REPRESENTATION_MAP(#{plc.eid},#9010)")

# 2 MAPPED_ITEMs attached to the root assembly's direct shape_rep.
plc_a = f._emit_raw("AXIS2_PLACEMENT_3D('inst_a_plc',#1,#3,#4)")
plc_b = f._emit_raw("AXIS2_PLACEMENT_3D('inst_b_plc',#1,#3,#4)")
f._emit_raw(f"MAPPED_ITEM('mi_a',#{rep_map_a.eid},#{plc_a.eid})")
f._emit_raw(f"MAPPED_ITEM('mi_b',#{rep_map_b.eid},#{plc_b.eid})")
