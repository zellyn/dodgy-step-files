"""A105 — Regression OCC 6.9.1 → 7.4.0: colours stop appearing on STEP files.

Catalog claim: colours routed through MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION
rather than per-face STYLED_ITEM.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: one real
face + STYLED_ITEM + a MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION
wrapper carrying the styled item — the 6.9.x route the 7.4.0 reader skips.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A105",
             defect="STYLED_ITEM routed through MDGPR (the 7.4.0-regressed path)")

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

# STYLED_ITEM + COLOUR_RGB chain.
colour = f._emit_raw("COLOUR_RGB('mdgpr_routed',0.7,0.2,0.2)")
fasc = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
styled = f._emit_raw(f"STYLED_ITEM('si_via_mdgpr',(#{psa.eid}),#{face.eid})")

# Wrap the styled_item via MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION
# — the 6.9.x route the 7.4.0 reader doesn't consult.
f._emit_raw(
    f"MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION("
    f"'old_colour_route',(#{styled.eid}),#9010)"
)
