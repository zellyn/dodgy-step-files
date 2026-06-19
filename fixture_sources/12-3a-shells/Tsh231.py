"""Tsh231 — pattern-mined fixture (see catalog for source).

B4 wave-3 issue-tracker mining. LGPL-clean: synthesized from the defect
*pattern*, no upstream bytes copied.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh231",
             defect='CadQuery#1338: revolve 288°-360° band: SURFACE_OF_REVOLUTION orientation flip')

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

# SURFACE_OF_REVOLUTION around Y axis from an arc profile — between
# 288°-360° OCCT's split-angle boundary triggers a bound-orientation flip.
arc_p1 = f.cartesian_point((1.0, 0.0, 0.0))
arc_p2 = f.cartesian_point((0.0, 1.0, 0.0))
yaxis = f.direction((0.0, 1.0, 0.0))
axis_line_plc = f.axis2_placement_3d(orig, yaxis, xdir)
# Revolution profile + axis
rev_axis = f._emit_raw(f"AXIS1_PLACEMENT('rev_axis',#{orig.eid},#{yaxis.eid})")
prof_line = f.line(arc_p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0))
f._emit_raw(
    f"SURFACE_OF_REVOLUTION('revolve_288to360',#{prof_line.eid},#{rev_axis.eid})"
)
