"""Tsh230 — pattern-mined fixture (see catalog for source).

This is part of B4 wave-1-extension issue-tracker mining. LGPL-clean:
synthesized from the defect *pattern*, no upstream bytes copied.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh230",
             defect='OCCT#382: surface from STEP wrongly imported / tessellated')

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

# A B_SPLINE_SURFACE with self-intersecting control net — tessellator
# produces wrong output but loader accepts it.
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((1.0, 0.5, 0.5))
p_c = f.cartesian_point((0.5, 1.0, 0.0))
p_d = f.cartesian_point((0.5, 0.5, 0.5))
f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('selfx_surf',1,1,"
    f"((#{p_a.eid},#{p_b.eid}),(#{p_c.eid},#{p_d.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)
