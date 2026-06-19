"""Pf001 — Multi-GB Creo AP242 assembly: unbounded receiver memory growth.

Catalog claim: nested NEXT_ASSEMBLY_USAGE_OCCURRENCE chains with thousands
of MANIFOLD_SOLID_BREP children. Receiver-side allocators (Inventor,
AutoCAD, Navisworks) grow unbounded and OOM.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 30-deep NAUO
chain (each child PRODUCT contains 1 simple cube MANIFOLD_SOLID_BREP)
so the file structurally exhibits the deep-nesting pattern.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pf001",
             defect="30-deep nested NAUO chain with simple brep children")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Build a simple "unit cube body" as the shared child geometry.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

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

# The root PRODUCT chain is added by add_product_chain.
# Now nest 30 child PRODUCT chains, each linked via NAUO to the previous.
prev_pdef_eid = 9004   # PRODUCT_DEFINITION for root from add_product_chain
DEPTH = 30
for k in range(DEPTH):
    child_prod = f._emit_raw(
        f"PRODUCT('CHILD_{k}','child_{k}','',(#9000))"
    )
    child_pdf = f._emit_raw(
        f"PRODUCT_DEFINITION_FORMATION('','',#{child_prod.eid})"
    )
    child_pdef = f._emit_raw(
        f"PRODUCT_DEFINITION('design','',#{child_pdf.eid},#9003)"
    )
    # Link parent → child via NAUO.
    f._emit_raw(
        f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('{k}','child_{k}','',"
        f"#{prev_pdef_eid},#{child_pdef.eid},$)"
    )
    prev_pdef_eid = child_pdef.eid
