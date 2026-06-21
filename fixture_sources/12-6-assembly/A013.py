"""A013 — STEP assembly reader returns success even when external-reference files are missing.

Catalog claim: APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT paths don't
exist on disk; OCCT silently fails resolution but Transfer() returns
success. The bytes 'APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT' and
'part_3.stp' must appear.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A013",
             defect="APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT referencing non-existent part_3.stp")

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

# DOCUMENT referencing non-existent part_3.stp.
doc_file = f._emit_raw(
    "DOCUMENT_FILE('part_3.stp','part_3.stp','STEP file','file://./part_3.stp')"
)
doc = f._emit_raw(
    f"DOCUMENT('part_3','DDP component 3','technical drawing',#{doc_file.eid})"
)
ext_source = f._emit_raw(
    f"EXTERNAL_SOURCE(IDENTIFICATION_ITEM('part_3','part_3.stp'))"
)
ext_id = f._emit_raw(
    f"EXTERNAL_IDENTIFICATION_ASSIGNMENT('face47','face reference',#{ext_source.eid})"
)
# APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT — the defect entity.
f._emit_raw(
    f"APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT(#{ext_id.eid},(APPLIED_SHAPE_ASPECT_ROLE($)))"
)
