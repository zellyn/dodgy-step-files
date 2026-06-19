"""M162 — Fillet emitted as B-spline instead of torus on STEP export.

Catalog claim: a fillet between a planar face and a cylindrical face is
emitted as a B_SPLINE_SURFACE_WITH_KNOTS cubic patch instead of an
analytical TOROIDAL_SURFACE. Receivers classify the result as "rounded
edge" rather than "fillet feature" because they look for TOROIDAL_SURFACE.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: three faces
in one shell — a PLANE face, a CYLINDRICAL_SURFACE face, and a
B_SPLINE_SURFACE_WITH_KNOTS face (the lost-classification fillet).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="M162",
             defect="PLANE + CYLINDER + B-spline-fillet (lost fillet classification)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)

# Plane (the flat face the fillet rounds away from).
plane = f.plane(plc)
plane_origin = f.cartesian_point((0.0, 0.0, 0.0))
plane_far = f.cartesian_point((5.0, 0.0, 0.0))
pv0 = f.vertex_point(plane_origin)
pv1 = f.vertex_point(plane_far)
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 5.0); ln = f.line(plane_origin, vec)
plane_edge = f.edge_curve(pv0, pv1, ln)
plane_loop = f.edge_loop([f.oriented_edge(plane_edge, True)])
plane_face = f.advanced_face([f.face_outer_bound(plane_loop)], plane)

# Cylindrical surface (the cylinder side).
cyl_origin = f.cartesian_point((5.0, 0.0, 0.0))
cyl_plc = f.axis2_placement_3d(cyl_origin, zdir, xdir)
cylinder = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl',#{cyl_plc.eid},2.0)")
v_cyl_bot = f.vertex_point(f.cartesian_point((7.0, 0.0, 0.0)))
v_cyl_top = f.vertex_point(f.cartesian_point((7.0, 0.0, 3.0)))
seam_dir = f.direction((0.0, 0.0, 1.0)); seam_vec = f.vector(seam_dir, 3.0)
seam_line = f.line(f.cartesian_point((7.0, 0.0, 0.0)), seam_vec)
seam_edge = f.edge_curve(v_cyl_bot, v_cyl_top, seam_line)
cyl_loop = f.edge_loop([f.oriented_edge(seam_edge, True)])
cyl_face = f.advanced_face([f.face_outer_bound(cyl_loop)], cylinder)

# B-spline surface — the wrongly-classified fillet (should be torus).
# 4x3 control grid for a degree-3 × degree-2 spline.
pts = [[f.cartesian_point(p) for p in row] for row in [
    [(4.0, 0.0, 0.0), (4.0, 1.0, 0.0), (4.0, 2.0, 0.0)],
    [(4.5, 0.0, 0.3), (4.5, 1.0, 0.5), (4.5, 2.0, 0.3)],
    [(5.0, 0.0, 0.5), (5.0, 1.0, 0.8), (5.0, 2.0, 0.5)],
    [(5.5, 0.0, 0.0), (5.5, 1.0, 0.3), (5.5, 2.0, 0.0)],
]]
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)
fillet_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('bspline_fillet_should_be_torus',3,2,"
    f"({grid}),"
    ".UNSPECIFIED.,.F.,.F.,.F.,"
    "(4,4),(3,3),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)
fv0 = f.vertex_point(f.cartesian_point((4.0, 0.0, 0.0)))
fv1 = f.vertex_point(f.cartesian_point((5.5, 0.0, 0.0)))
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.5); ln = f.line(f.cartesian_point((4.0, 0.0, 0.0)), vec)
fillet_edge = f.edge_curve(fv0, fv1, ln)
fillet_loop = f.edge_loop([f.oriented_edge(fillet_edge, True)])
fillet_face = f.advanced_face([f.face_outer_bound(fillet_loop)], fillet_surf)

shell = f.open_shell([plane_face, cyl_face, fillet_face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
