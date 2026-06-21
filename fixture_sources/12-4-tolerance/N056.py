"""N056 — ShapeFix_ShapeTolerance.SetTolerance bulk-rewrite silent precision loss

SetTolerance(shape, t, type) overwrites tolerances on all sub-elements even
when they already exceed the new tolerance value, causing silent precision loss.
When tolerance is reduced globally, higher-precision edges/vertices should be
preserved or warned; instead they are silently clamped downward.

Byte assertions:
  contains(b'edge1_high_tol')
  contains(b'edge2_low_tol')
  contains(b'edge3_high_tol')
  count_entity_def(b'EDGE_CURVE') == 4

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(5) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N056",
    defect=(
        "four-edge closed face with mixed tolerances: edge1_high_tol (0.005), "
        "edge2_low_tol (0.001), edge3_high_tol (0.004); "
        "SetTolerance(shape, 0.002) silently overwrites all edges including "
        "the two with tolerance > 0.002 — precision loss without warning"
    ),
)

# Shape with three edges: two high-tolerance, one low-tolerance.
# SetTolerance(shape, 0.002) should detect edges #31 and #51 already have
# tolerance 0.005 and 0.004 (>0.002) but silently overwrites them all.
p_origin = f.cartesian_point((0.0, 0.0, 0.0), name="p_origin")
p1 = f.cartesian_point((1.0, 0.0, 0.0), name="p1")
p2 = f.cartesian_point((2.0, 0.0, 0.0), name="p2")
p3 = f.cartesian_point((3.0, 0.0, 0.0), name="p3")

v_origin = f.vertex_point(p_origin, name="v_origin")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")
v3 = f.vertex_point(p3, name="v3")

# Edge 1: from origin to p1, high tolerance 0.005
d1 = f.direction((1.0, 0.0, 0.0), name="d1")
vec1 = f.vector(d1, 1.0, name="vec1")
l1 = f.line(p_origin, vec1, name="line1")
e1 = f.edge_curve(v_origin, v1, l1, name="edge1_high_tol")

# Edge 2: from p1 to p2, low tolerance 0.001
d2 = f.direction((1.0, 0.0, 0.0), name="d2")
vec2 = f.vector(d2, 1.0, name="vec2")
l2 = f.line(p1, vec2, name="line2")
e2 = f.edge_curve(v1, v2, l2, name="edge2_low_tol")

# Edge 3: from p2 to p3, high tolerance 0.004
d3 = f.direction((1.0, 0.0, 0.0), name="d3")
vec3 = f.vector(d3, 1.0, name="vec3")
l3 = f.line(p2, vec3, name="line3")
e3 = f.edge_curve(v2, v3, l3, name="edge3_high_tol")

# Closing edge: from p3 back to origin
d_close = f.direction((-1.0, 0.0, 0.0), name="d_close")
vec_close = f.vector(d_close, 3.0, name="vec_close")
l_close = f.line(p3, vec_close, name="line_close")
e_close = f.edge_curve(v3, v_origin, l_close, name="edge_close")

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
    f.oriented_edge(e_close, True),
])
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0), name="zdir")
xdir = f.direction((1.0, 0.0, 0.0), name="xdir")
plc = f.axis2_placement_3d(p_origin, zdir, xdir, name="ax3")
plane = f.plane(plc, name="plane_xy")
face = f.advanced_face([fob], plane, name="face1")

shell = f.open_shell([face], name="shell1")
sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N056.stp")
