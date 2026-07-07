"""Xp040 — Solid Edge import of Creo Elements STEP: 'stuck' sub-assemblies."""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Xp040",
             defect='Solid Edge stuck sub-assemblies: two NAUOs share same ITEM_DEFINED_TRANSFORMATION')

# Normal geometry for the shape
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

# Defect: two NEXT_ASSEMBLY_USAGE_OCCURRENCEs sharing the same IDT
# Both children SubA and SubB are placed at the same AXIS2_PLACEMENT_3D
shared_plc = f._emit_raw("AXIS2_PLACEMENT_3D('shared_plc',#1,#2,#3)")
shared_idt = f._emit_raw(
    f"ITEM_DEFINED_TRANSFORMATION('shared_xform','',#{shared_plc.eid},#{shared_plc.eid})"
)

prodA = f._emit_raw("PRODUCT('SubA','SubA','',())")
prodB = f._emit_raw("PRODUCT('SubB','SubB','',())")

nauo1 = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_A','','',#9053,#{prodA.eid},$)"
)
nauo2 = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_B','','',#9053,#{prodB.eid},$)"
)

f._emit_raw(
    f"/* xp040 defect: NAUO #{nauo1.eid} and NAUO #{nauo2.eid} both reference "
    f"shared IDT #{shared_idt.eid} — Solid Edge cannot assign per-instance frames */"
)
