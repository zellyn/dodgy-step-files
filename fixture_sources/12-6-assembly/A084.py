"""A084 — STEP exporter writes untrimmed curve where trimmed expected.

Catalog claim: an edge backed by a trimmed circle arc (t=0 to t=π) is
exported as the full parent circle with trim parameters omitted. The
bytes CIRCLE, EDGE_CURVE, and 'half_arc_full_curve' or 'parent' must appear.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A084",
             defect="CIRCLE + EDGE_CURVE with 'half_arc_full_curve' — exporter emits full parent curve, trim params omitted")

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

# The defect: a half-arc EDGE_CURVE using the full parent CIRCLE.
# The exporter should emit a TRIMMED_CURVE [0,π] but instead emits the
# full CIRCLE directly as the edge geometry — 'half_arc_full_curve' names
# the offending edge.
arc_orig = f.cartesian_point((0.0, 0.0, 5.0))
arc_plc = f.axis2_placement_3d(arc_orig, zdir, xdir)
circle = f._emit_raw(f"CIRCLE('half_arc_full_curve',#{arc_plc.eid},5.0)")
vp_s = f.cartesian_point((5.0, 0.0, 5.0))
vp_e = f.cartesian_point((-5.0, 0.0, 5.0))
v_s = f.vertex_point(vp_s)
v_e = f.vertex_point(vp_e)
# EDGE_CURVE backed by the full CIRCLE — trim parameters were omitted.
f._emit_raw(
    f"EDGE_CURVE('half_arc_edge',#{v_s.eid},#{v_e.eid},#{circle.eid},.T.)"
)

# STYLED_ITEM scaffolding for assembly-presence lint.
colour = f._emit_raw("COLOUR_RGB('arc_color',0.5,0.5,0.5)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('arc_style',(#{psa.eid}),#{face.eid})")
