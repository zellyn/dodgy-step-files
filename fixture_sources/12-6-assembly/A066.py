"""A066 — UpdateAssemblies produces wrong compounds for located roots.

Catalog claim: assembly tree where root has translation (100,0,0) and
one child has translation (50,0,0). After UpdateAssemblies the leaf
appears at (200,0,0) instead of (150,0,0) — the location is applied
twice. ITEM_DEFINED_TRANSFORMATION with 'root_loc' label must appear.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A066",
             defect="NAUO + ITEM_DEFINED_TRANSFORMATION(root_loc) + child_loc — double-apply bug")

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

# Assembly representations.
root_origin = f._emit_raw("CARTESIAN_POINT('root_origin',(100.0,0.0,0.0))")
root_z = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
root_x = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
root_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('root_loc',#{root_origin.eid},#{root_z.eid},#{root_x.eid})"
)
root_sr = f._emit_raw(f"SHAPE_REPRESENTATION('root_rep',(#{root_plc.eid}),#9010)")

child_origin = f._emit_raw("CARTESIAN_POINT('child_origin',(50.0,0.0,0.0))")
child_z = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
child_x = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
child_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('child_loc',#{child_origin.eid},#{child_z.eid},#{child_x.eid})"
)
child_sr = f._emit_raw(f"SHAPE_REPRESENTATION('child_rep',(#{child_plc.eid}),#9010)")

# ITEM_DEFINED_TRANSFORMATION named root_loc — the double-apply trigger.
idt = f._emit_raw(
    f"ITEM_DEFINED_TRANSFORMATION('root_loc','root translation',#{root_plc.eid},#{child_plc.eid})"
)

# SRR with the root_loc transform.
f._emit_raw(
    f"SHAPE_REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION('srr','root_to_child',"
    f"#{root_sr.eid},#{child_sr.eid},#{idt.eid})"
)

sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('Child','Child','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9003)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','child','',#9004,#{sub_pdef.eid},$)"
)
