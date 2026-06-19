"""A019 — Per-face STYLED_ITEM colours collapse to single hue when multiple
ADVANCED_FACEs share one supporting PLANE.

Catalog claim: three distinct ADVANCED_FACEs all share the same
supporting PLANE but each has its own distinct STYLED_ITEM / COLOUR_RGB.
XCAF risks merging the faces (since they overlap geometrically) and
collapsing the per-face colour binding.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 3 distinct
quad ADVANCED_FACEs that share the SAME plane entity, each with its own
STYLED_ITEM → COLOUR_RGB binding.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A019",
             defect="3 faces sharing one PLANE, each with own STYLED_ITEM/COLOUR")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
# SHARED plane entity — all three faces reference this same #PLANE.
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

FACES_AND_COLOR = [
    ("red",   (0.8, 0.1, 0.1), 0.0),
    ("green", (0.1, 0.8, 0.1), 1.5),
    ("blue",  (0.1, 0.1, 0.8), 3.0),
]
faces = []
for name, color, x_offset in FACES_AND_COLOR:
    p0 = f.cartesian_point((x_offset, 0.0, 0.0))
    p1 = f.cartesian_point((x_offset + 1.0, 0.0, 0.0))
    p2 = f.cartesian_point((x_offset + 1.0, 1.0, 0.0))
    p3 = f.cartesian_point((x_offset, 1.0, 0.0))
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
    faces.append((name, color, f.advanced_face([f.face_outer_bound(loop)], plane)))

shell = f.open_shell([face for _, _, face in faces])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Each face gets its own STYLED_ITEM color chain.
for name, color, face in faces:
    r, g, b = color
    colour = f._emit_raw(f"COLOUR_RGB('{name}',{r},{g},{b})")
    fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
    fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
    ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
    sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
    ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
    psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
    f._emit_raw(f"STYLED_ITEM('si_{name}',(#{psa.eid}),#{face.eid})")
