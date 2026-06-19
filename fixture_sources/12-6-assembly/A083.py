"""A083 — STEP exporter generates bad geometry for revolution / extrusion.

Catalog claim: SURFACE_OF_REVOLUTION of a non-circular (e.g. parabolic)
profile is exported as a B-spline approximation with C0 isolines.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: a
SURFACE_OF_REVOLUTION on a degree-2 B-spline 'parabolic_profile' curve.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A083",
             defect="SURFACE_OF_REVOLUTION on B-spline parabolic_profile")

# Parabolic profile in XZ plane: control points approximate y=x^2.
p0 = f.cartesian_point((0.1, 0.0, 0.0))    # near axis
p1 = f.cartesian_point((0.5, 0.0, 0.25))
p2 = f.cartesian_point((1.0, 0.0, 1.0))
profile = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('parabolic_profile',2,"
    f"(#{p0.eid},#{p1.eid},#{p2.eid}),"
    ".UNSPECIFIED.,.F.,.F.,(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

# Revolution axis = Z axis through origin.
origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
axis = f._emit_raw(
    f"AXIS1_PLACEMENT('rev_axis',#{origin.eid},#{zdir.eid})"
)
surf = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('parabolic_revolution',#{profile.eid},#{axis.eid})"
)

# Minimal face boundary so the fixture is consumable.
v_start = f.vertex_point(p0)
v_end = f.vertex_point(p2)
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 0.9)
ln = f.line(p0, vec)
edge = f.edge_curve(v_start, v_end, ln)
loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
