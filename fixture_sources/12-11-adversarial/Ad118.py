"""Ad118 — Forward-compat: older-OCC STEP files rejected by newer build.

Catalog claim: a STEP file emitted by OCC4 declares FILE_SCHEMA
'CONFIG_CONTROL_DESIGN' (AP203 1994 schema); the current reader rejects
the schema string outright even though the entities are still
recognisable.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Ad118",
             defect="AP203 1994 schema (CONFIG_CONTROL_DESIGN) rejected by newer kernel")

# Override the FILE_SCHEMA to the deprecated AP203 1994 schema string.
def _render_header():
    return (
        "HEADER;\n"
        f"FILE_DESCRIPTION(('{f.catalog_id}'),'2;1');\n"
        f"FILE_NAME('{f.catalog_id}.stp','{f.timestamp}',(''),(''),"
        f"'cad-research-suite','','');\n"
        f"FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));\n"
        "ENDSEC;"
    )
f._render_header = _render_header  # type: ignore[method-assign]

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
shell = f._emit_raw(f"CLOSED_SHELL('outer',(#{face.eid}))")
# BREP_WITH_VOIDS — the entity flavour the older schema used but the
# newer schema retired.
f._emit_raw(f"BREP_WITH_VOIDS('old_brep',#{shell.eid},())")
