"""Xp004 — PMI annotation × tessellation-vs-BRep mix in a single AP242 file."""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(catalog_id="Xp004",
             defect='PMI annotation x tessellation-vs-BRep mix in a single AP242 file',
             schema="AP242")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, p1, v0, v1)
e1 = line_edge(p1, p2, v1, v2)
e2 = line_edge(p2, p3, v2, v3)
e3 = line_edge(p3, p0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Defect 1: TESSELLATED_FACE mixed into tessellated_shape_representation
# together with an ADVANCED_FACE — forbidden in AP242 Ed.1
coords_list = f._emit_raw("COORDINATES_LIST('tess_coords',3,((0.0,0.0,0.0),(1.0,0.0,0.0),(1.0,1.0,0.0)))")
tess_face = f._emit_raw(f"TRIANGULATED_FACE('tess_face',#{coords_list.eid},(),(),(0.,(1.,1.)),(3,((1,2,3))))")

# Defect 2: PMI dimensional_size referencing BRep face via shape_aspect
# shape_aspect → face; geometric_item_specific_usage links it
shape_asp = f._emit_raw(f"SHAPE_ASPECT('diameter_aspect','',#9055,.T.)")
dim_size = f._emit_raw(f"DIMENSIONAL_SIZE(#{shape_asp.eid},'diameter')")
gisu = f._emit_raw(f"GEOMETRIC_ITEM_SPECIFIC_USAGE(#{shape_asp.eid},#{face.eid})")

# Defect 3: draughting_model with items list missing required mapped_item
draughting_model = f._emit_raw("DRAUGHTING_MODEL('saved_view',(),$)")
