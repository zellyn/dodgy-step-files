"""Ad084 — XCAFDoc_ShapeTool::FindSubShape crash building XCAF tree.

Catalog claim: STEP read crashes inside FindSubShape while building XCAF
tree on otherwise well-formed file. The fixture provides the on-disk
shape: a sliver planar face + STYLED_ITEM + PRESENTATION_STYLE_ASSIGNMENT
chain that XCAFDoc walks to build the assembly tree.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: sliver
ADVANCED_FACE on PLANE (aspect 1e6) + STYLED_ITEM color binding.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Ad084",
             defect="sliver planar face + STYLED_ITEM (XCAF FindSubShape crash trigger)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Sliver face: 10.0 wide × 1e-5 tall — aspect 1e6.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 1.0e-5, 0.0))
p3 = f.cartesian_point((0.0, 1.0e-5, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(p0, (1.0, 0.0, 0.0), 10.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0e-5, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 10.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0e-5, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# STYLED_ITEM chain — the catalog claim requires this for XCAFDoc to walk.
colour = f._emit_raw("COLOUR_RGB('xcaf_trigger',0.5,0.5,0.5)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('xcaf_trigger',(#{psa.eid}),#{face.eid})")
