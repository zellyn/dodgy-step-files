"""A096 — STEPCAFControl_Writer skips identity-located instance when partner shapes have non-identity locations.

Catalog claim: assembly has 3 instances of the same part — one at identity
transform, two at non-identity. Writer's de-duplication wrongly skips the
identity-located instance. count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 2.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A096",
             defect="NAUO x3 (one identity + two placed) — writer drops identity-located instance, emitting only 2 of 3 instances")

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

# Sub-component product chain (the shared "part" that gets instanced 3 times).
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('Part','Part','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)")

# NAUO 1: instance at identity location (the one writer wrongly skips).
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','identity_instance','',#9054,#{sub_pdef.eid},$)"
)
# NAUO 2: instance at non-identity location (translated 10 mm along X).
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('2','placed_instance_a','',#9054,#{sub_pdef.eid},$)"
)
# NAUO 3: instance at non-identity location (translated 20 mm along X).
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('3','placed_instance_b','',#9054,#{sub_pdef.eid},$)"
)
