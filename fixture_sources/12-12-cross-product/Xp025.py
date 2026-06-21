"""Xp025 — Onshape→SolidWorks: assembly children snap to origin (placements lost)."""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Xp025",
             defect='Onshape-to-SolidWorks assembly children snap to origin (identity ITEM_DEFINED_TRANSFORMATION)')

# Build normal geometry for the shape (a square face)
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
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

# Defect: assembly with two children using identity ITEM_DEFINED_TRANSFORMATION
# Both NAUOs reference the same identity IDT (children snap to world origin)
# Child 1 intended position: (50, 0, 0)
# Child 2 intended position: (0, 75, 0)
# But the IDT is identity for both → they render at origin
child1_prod = f._emit_raw(
    "PRODUCT('SubA','SubA (intended at 50,0,0)','',())"
)
child2_prod = f._emit_raw(
    "PRODUCT('SubB','SubB (intended at 0,75,0)','',())"
)
# Identity placement — both children reference this same placement
id_plc0 = f._emit_raw("AXIS2_PLACEMENT_3D('identity',#1,#2,#3)")
id_idt   = f._emit_raw(f"ITEM_DEFINED_TRANSFORMATION('identity_xform','',#{id_plc0.eid},#{id_plc0.eid})")

# Two NAUOs both referencing the same identity IDT
nauo1 = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo1','','',#9003,#{child1_prod.eid},$)"
)
nauo2 = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo2','','',#9003,#{child2_prod.eid},$)"
)
f._emit_raw(
    "/* xp025 defect: both NAUOs reference identity IDT — "
    "children render at world origin instead of intended positions */"
)
