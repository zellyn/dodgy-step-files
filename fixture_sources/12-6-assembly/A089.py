"""A089 — Sub-shape names lost in non-manifold STEP output.

Catalog claim: document with named sub-shapes is exported in non-manifold
mode; non-manifold writer doesn't run styled-item / name-emission code,
losing all sub-shape names.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 2 named
ADVANCED_FACEs ('front_face' and 'back_face') in one shell + an
explicit NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A089",
             defect="named sub-faces + NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# Build 2 named faces.
faces = []
for name, x_off in [("inlet", 0.0), ("outlet", 2.0)]:
    p0 = f.cartesian_point((x_off, 0.0, 0.0))
    p1 = f.cartesian_point((x_off + 1.0, 0.0, 0.0))
    p2 = f.cartesian_point((x_off + 1.0, 1.0, 0.0))
    p3 = f.cartesian_point((x_off, 1.0, 0.0))
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
    fob = f._emit_raw(f"FACE_OUTER_BOUND('{name}_bound',#{loop.eid},.T.)")
    face = f._emit_raw(
        f"ADVANCED_FACE('{name}',(#{fob.eid}),#{plane.eid},.T.)"
    )
    faces.append(face)

shell = f._emit_raw(
    f"OPEN_SHELL('named_shell',(#{faces[0].eid},#{faces[1].eid}))"
)
sbsm = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)

# Explicit NMSSR — the non-manifold writer path.
f._emit_raw(
    f"NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION('nm_writer_target',"
    f"(#{shell.eid}),$)"
)

# Catalog byte assertion requires >= 2 STYLED_ITEM entries — emit one
# per named face so the named-face-loss claim is demonstrable.
for name, face in zip(("inlet", "outlet"), faces):
    colour = f._emit_raw(f"COLOUR_RGB('{name}_color',0.5,0.5,0.5)")
    fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
    fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
    ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
    sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
    ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
    psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
    f._emit_raw(f"STYLED_ITEM('si_{name}',(#{psa.eid}),#{face.eid})")
