"""Xp006 — Schema-mismatch × forward-reference × unresolved entity."""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

# Defect: FILE_SCHEMA declares AP203 (CONFIG_CONTROL_DESIGN) but DATA
# contains AP242-only entities. Also an ADVANCED_FACE references #999
# which is never defined (unresolved forward reference).
# We override the schema string manually via _render_header.

f = StepFile(catalog_id="Xp006",
             defect='Schema-mismatch x forward-reference x unresolved entity')

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
# Valid face — geometry resolves normally
face = f.advanced_face([f.face_outer_bound(loop)], plane)

# Defect 2: ADVANCED_FACE with face_geometry = #999 (unresolved forward ref)
# We need a new EDGE_LOOP for the bad face's bound
loop2 = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
fob2 = f.face_outer_bound(loop2)
# #999 is never defined — dangling reference for face_geometry
bad_face = f._emit_raw(f"ADVANCED_FACE('bad_face',(#{fob2.eid}),#999,.T.)")

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Defect 1: AP242-only entities (COORDINATES_LIST + TRIANGULATED_FACE)
# emitted in DATA section under AP203 schema. This IS the schema-mismatch
# claim; Xp006 is on schema_oracle.EXEMPT_SCHEMA_MISMATCH so the resulting
# oracle violation is the documented bug (not a regression).
coords = f._emit_raw(
    "COORDINATES_LIST('',4,((0.0,0.0,0.0),(1.0,0.0,0.0),"
    "(0.5,1.0,0.0),(0.5,0.5,1.0)))"
)
f._emit_raw(
    f"TRIANGULATED_FACE('',#{coords.eid},$,$,(),"
    f"((1,2,3),(1,2,4),(2,3,4),(3,1,4)))"
)
f._emit_raw("/* xp006 defect-1: AP242-only entities present under AP203 schema */")
f._emit_raw("/* xp006 defect-3: FILE_SCHEMA CONFIG_CONTROL_DESIGN (AP203) declared */")

# Defect 3: Override FILE_SCHEMA to AP203
def _ap203_render_header():
    return (
        "HEADER;\n"
        f"FILE_DESCRIPTION(('{f.catalog_id}'),'2;1');\n"
        f"FILE_NAME('{f.catalog_id}.stp','{f.timestamp}',(''),(''),"
        f"'cad-research-suite','','');\n"
        "FILE_SCHEMA(('CONFIG_CONTROL_DESIGN { 1 0 10303 203 1 1 1 1 }'));\n"
        "ENDSEC;"
    )

f._render_header = _ap203_render_header  # type: ignore[method-assign]
