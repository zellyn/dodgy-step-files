"""A064 — Subshape names not transferred on STEP import.

Catalog claim: STYLED_ITEM and PRESENTATION_LAYER_ASSIGNMENT carry
human-readable names per face. STEP reader records names only at the
top PRODUCT_DEFINITION level, dropping per-subshape names.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: a solid
with 6 quad faces named "top", "bottom", "left", "right", "front",
"back", each carrying a STYLED_ITEM with a distinct COLOUR_RGB and a
PRESENTATION_LAYER_ASSIGNMENT giving the face its named layer.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A064",
             defect="6 named faces with STYLED_ITEM + PRESENTATION_LAYER_ASSIGNMENT")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# Build 6 named 1x1 quad faces.
FACES = [
    ("top",    (1.0, 0.0, 0.0)),
    ("bottom", (0.5, 0.5, 0.5)),
    ("left",   (0.0, 1.0, 0.0)),
    ("right",  (0.0, 0.0, 1.0)),
    ("front",  (1.0, 1.0, 0.0)),
    ("back",   (1.0, 0.0, 1.0)),
]
face_entities = []
for idx, (name, color) in enumerate(FACES):
    i = idx % 3
    j = idx // 3
    x = float(i)
    y = float(j)
    p0 = f.cartesian_point((x, y, 0.0))
    p1 = f.cartesian_point((x + 1.0, y, 0.0))
    p2 = f.cartesian_point((x + 1.0, y + 1.0, 0.0))
    p3 = f.cartesian_point((x, y + 1.0, 0.0))
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
    # Use _emit_raw so the face label is the human-readable name.
    fob = f._emit_raw(f"FACE_OUTER_BOUND('{name}_bound',#{loop.eid},.T.)")
    face = f._emit_raw(
        f"ADVANCED_FACE('{name}',(#{fob.eid}),#{plane.eid},.T.)"
    )
    face_entities.append((name, color, face))

shell = f._emit_raw(
    f"OPEN_SHELL('shell',({','.join(f'#{ent.eid}' for _, _, ent in face_entities)}))"
)
sbsm = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)

# For each named face, emit a STYLED_ITEM color binding + a
# PRESENTATION_LAYER_ASSIGNMENT naming the face's layer.
for name, color, face in face_entities:
    r, g, b = color
    colour = f._emit_raw(f"COLOUR_RGB('{name}_color',{r},{g},{b})")
    fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
    fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
    ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
    sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
    ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
    psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
    f._emit_raw(f"STYLED_ITEM('si_{name}',(#{psa.eid}),#{face.eid})")
    f._emit_raw(
        f"PRESENTATION_LAYER_ASSIGNMENT('layer_{name}','{name}_layer',(#{face.eid}))"
    )
