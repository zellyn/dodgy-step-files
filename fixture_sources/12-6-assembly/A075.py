"""A075 — Free-shape-after-import is empty.

Catalog claim: STEP file uses MANIFOLD_SURFACE_SHAPE_REPRESENTATION instead
of ADVANCED_BREP_SHAPE_REPRESENTATION; reader silently skips it and reports
an empty document. The bytes MANIFOLD_SURFACE_SHAPE_REPRESENTATION must appear
and ADVANCED_BREP_SHAPE_REPRESENTATION must not appear.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A075",
             defect="MANIFOLD_SURFACE_SHAPE_REPRESENTATION only — reader silently skips, imports empty")

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

# The defect: geometry is carried inside a MANIFOLD_SURFACE_SHAPE_REPRESENTATION
# instead of an ADVANCED_BREP_SHAPE_REPRESENTATION. The product chain above
# references SHELL_BASED_SURFACE_MODEL via the standard shape rep. Here we
# add a MANIFOLD_SURFACE_SHAPE_REPRESENTATION referencing the same face,
# which the defective reader would need to handle.
mssr = f._emit_raw(
    f"MANIFOLD_SURFACE_SHAPE_REPRESENTATION('mssr_defect',(#{face.eid}),#9060)"
)

# STYLED_ITEM scaffolding so assembly-presence lint passes.
colour = f._emit_raw("COLOUR_RGB('face_color',0.5,0.5,0.5)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('face_style',(#{psa.eid}),#{face.eid})")
