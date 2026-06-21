"""A010 — NAUO instance name lost on round-trip / re-export.

Catalog claim: STEP writer drops instance-level names when the parent
assembly itself has no name. Two NAUOs with distinct instance names
'LEFT_LEAF_INSTANCE' and 'RIGHT_LEAF_INSTANCE' appear; after round-trip
both are silently stripped.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A010",
             defect="2 NAUO with named instances LEFT_LEAF_INSTANCE and RIGHT_LEAF_INSTANCE")

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
# Root assembly product chain (note: assembled under an unnamed assembly).
f.add_product_chain(sbsm)

sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
# Shared leaf product — both instances reference the same PD.
leaf_prod = f._emit_raw(f"PRODUCT('Leaf','Leaf','',(#{sub_pdc.eid}))")
leaf_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{leaf_prod.eid})")
leaf_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{leaf_pdf.eid},#9003)")

# Two NAUOs with distinct instance names — names that must survive round-trip.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('L','LEFT_LEAF_INSTANCE','',"
    f"#9004,#{leaf_pdef.eid},$)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('R','RIGHT_LEAF_INSTANCE','',"
    f"#9004,#{leaf_pdef.eid},$)"
)
