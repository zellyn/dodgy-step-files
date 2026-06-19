"""Tsh022 — Non-manifold STEP loses XCAF attributes (color/PMI) on read.

Catalog claim: STEP reader's non-manifold path skipped XCAF attribute
application; STEP export in non-manifold mode loses all but one face.

Previous fixture used MANIFOLD_SURFACE_SHAPE_REPRESENTATION with no
STYLED_ITEM/colour entities — neither the non-manifold path nor the
XCAF-attribute path was being exercised. Regen with two faces sharing
an edge (non-manifold T-junction), a STYLED_ITEM colour chain on the
horizontal face, and an explicit NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION
to drive the non-manifold reader path.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh022",
             defect="NMSSR with STYLED_ITEM color payload (XCAF attribute path)")

# Horizontal face: 1x1 square at z=0.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc_h = f.axis2_placement_3d(orig, zdir, xdir)
plane_h = f.plane(plc_h)

loop_h = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face_h = f.advanced_face([f.face_outer_bound(loop_h)], plane_h)

# Vertical face attached to edge e1 (the shared non-manifold edge).
p1z = f.cartesian_point((1.0, 0.0, 1.0))
p2z = f.cartesian_point((1.0, 1.0, 1.0))
v1z = f.vertex_point(p1z)
v2z = f.vertex_point(p2z)

e_up = line_edge(p1, (0.0, 0.0, 1.0), 1.0, v1, v1z)
e_top = line_edge(p1z, (0.0, 1.0, 0.0), 1.0, v1z, v2z)
e_down = line_edge(p2z, (0.0, 0.0, -1.0), 1.0, v2z, v2)

x_axis = f.direction((1.0, 0.0, 0.0))
y_axis = f.direction((0.0, 1.0, 0.0))
plc_v = f.axis2_placement_3d(p1, x_axis, y_axis)
plane_v = f.plane(plc_v)

loop_v = f.edge_loop([
    f.oriented_edge(e1, True),         # shared edge e1 used by both faces
    f.oriented_edge(e_up, False),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_down, False),
])
face_v = f.advanced_face([f.face_outer_bound(loop_v)], plane_v)

shell = f.open_shell([face_h, face_v])

# XCAF colour payload — what the non-manifold reader path drops.
colour = f._emit_raw("COLOUR_RGB('face_red',1.0,0.0,0.0)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('xcaf_color_on_h_face',(#{psa.eid}),#{face_h.eid})")

# Explicit NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION pointing at the shell.
# This is the entity that triggers the reader's non-manifold path.
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f._emit_raw(
    f"NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION('nmssr_color_carrier',"
    f"(#{shell.eid}),$)"
)
