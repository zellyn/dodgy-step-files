"""A079 — Visibility / colour ignored for sub-shapes by XCAFPrs_AISObject.

Catalog claim: an XCAF document carries a sub-shape that is invisible or
semi-transparent. The viewer object derived from the document ignores
the sub-shape-level visibility / transparency.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 2 faces in
one shell, each with its own STYLED_ITEM where one carries a
SURFACE_STYLE_TRANSPARENT entity (transparency=0.5).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A079",
             defect="sub-shape STYLED_ITEM with SURFACE_STYLE_TRANSPARENT")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

faces = []
for k in range(2):
    x = k * 2.0
    p0 = f.cartesian_point((x, 0.0, 0.0))
    p1 = f.cartesian_point((x + 1.0, 0.0, 0.0))
    p2 = f.cartesian_point((x + 1.0, 1.0, 0.0))
    p3 = f.cartesian_point((x, 1.0, 0.0))
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
    faces.append(f.advanced_face([f.face_outer_bound(loop)], plane))

shell = f.open_shell(faces)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Face 0: opaque red.
colour0 = f._emit_raw("COLOUR_RGB('opaque_red',0.8,0.0,0.0)")
fasc0 = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour0.eid})")
fas0 = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc0.eid}))")
ssfa0 = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas0.eid})")
sss0 = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa0.eid}))")
ssu0 = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss0.eid})")
psa0 = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu0.eid}))")
f._emit_raw(f"STYLED_ITEM('opaque_face',(#{psa0.eid}),#{faces[0].eid})")

# Face 1: semi-transparent blue (transparency=0.5). The defect.
colour1 = f._emit_raw("COLOUR_RGB('transparent_blue',0.0,0.0,0.8)")
transparent = f._emit_raw(f"SURFACE_STYLE_TRANSPARENT(0.5)")
sss1 = f._emit_raw(
    f"SURFACE_SIDE_STYLE('semi_transparent',(#{transparent.eid}))"
)
ssu1 = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss1.eid})")
psa1 = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu1.eid}))")
f._emit_raw(f"STYLED_ITEM('transparent_face',(#{psa1.eid}),#{faces[1].eid})")
