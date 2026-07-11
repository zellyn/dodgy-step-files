"""A007 — SHAPE_REPRESENTATION_RELATIONSHIP with swapped/mixed rep_1/rep_2 axis placements.

Catalog claim: SRR with swapped axis-placements where one AXIS2_PLACEMENT_3D
is shared between assembly and component representations. The transform
labels 'swapped' to indicate the source/target axes were exchanged.
ITEM_DEFINED_TRANSFORMATION used with rep_1 and rep_2 axes swapped.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A007",
             defect="SRR with ITEM_DEFINED_TRANSFORMATION whose axes are swapped between rep_1 and rep_2")

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

# Assembly representation.
asm_orig = f._emit_raw("CARTESIAN_POINT('asm_origin',(0.0,0.0,0.0))")
asm_z = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
asm_x = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
asm_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('asm_placement',#{asm_orig.eid},#{asm_z.eid},#{asm_x.eid})"
)
asm_sr = f._emit_raw(f"SHAPE_REPRESENTATION('asm_rep',(#{asm_plc.eid}),#9060)")

# Component representation — placed at (10, 0, 0).
cmp_orig = f._emit_raw("CARTESIAN_POINT('cmp_origin',(10.0,0.0,0.0))")
cmp_z = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
cmp_x = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
cmp_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('cmp_placement',#{cmp_orig.eid},#{cmp_z.eid},#{cmp_x.eid})"
)
cmp_sr = f._emit_raw(f"SHAPE_REPRESENTATION('cmp_rep',(#{cmp_plc.eid}),#9060)")

# ITEM_DEFINED_TRANSFORMATION with swapped source/target — the defect.
# Correct would be (asm_plc → cmp_plc); here they are SWAPPED.
idt = f._emit_raw(
    f"ITEM_DEFINED_TRANSFORMATION('swapped','swapped axes',#{cmp_plc.eid},#{asm_plc.eid})"
)

# SHAPE_REPRESENTATION_RELATIONSHIP referencing the swapped transform.
f._emit_raw(
    f"SHAPE_REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION('srr','swapped_srr',"
    f"#{asm_sr.eid},#{cmp_sr.eid},#{idt.eid})"
)

# NAUO for the assembly presence lint.
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('Sub','Sub','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','sub','',#9054,#{sub_pdef.eid},$)"
)
