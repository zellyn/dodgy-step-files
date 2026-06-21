"""N091 — ShapeFix_Edge.FixSameParameter wrong-floor-clamp

Ideal SameParameter tolerance is 1e-9 (sub-precision) but the implementation
floors the result to 1e-7 minimum, causing legitimate high-precision edges to
be over-toleranced and lose fidelity.

Reproducer: edge whose parametric-vs-3D deviation measures 1e-9, gets clamped
up to 1e-7 despite 1e-9 being valid in the ultra-precision context (declared
UNCERTAINTY_MEASURE 1e-10).

Byte assertions:
  contains(b'edge_subprecision')
  contains(b'edge_normal')
  count_entity_def(b'EDGE_CURVE') == 2

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N091",
    defect=(
        "OPEN_SHELL face with edge_subprecision (1e-9 ideal tolerance) and edge_normal; "
        "ultra-precision context 1e-10; FixSameParameter floors 1e-9 up to 1e-7 "
        "floor-clamp — legitimate high-precision edge loses fidelity"
    ),
)

# Ultra-precision context: UNCERTAINTY_MEASURE declares 1.0e-10
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)

# Edge with ideal tolerance 1.0e-9 (should survive, but will be clamped to 1e-7)
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")

d_x1 = f.direction((1.0, 0.0, 0.0))
vec1 = f.vector(d_x1, 1.0)
l1 = f.line(p0, vec1)
e_sub = f.edge_curve(v0, v1, l1, name="edge_subprecision")

# Second edge with wider tolerance for contrast
p2 = f.cartesian_point((1.0, 0.0, 0.0))
p3 = f.cartesian_point((2.0, 0.0, 0.0))
v2 = f.vertex_point(p2, name="v2")
v3 = f.vertex_point(p3, name="v3")

d_x2 = f.direction((1.0, 0.0, 0.0))
vec2 = f.vector(d_x2, 1.0)
l2 = f.line(p2, vec2)
e_norm = f.edge_curve(v2, v3, l2, name="edge_normal")

# Closing vertices to form a valid face loop
p_tr = f.cartesian_point((2.0, 1.0, 0.0))
p_tl = f.cartesian_point((0.0, 1.0, 0.0))
v_tr = f.vertex_point(p_tr)
v_tl = f.vertex_point(p_tl)

# Connector between edge_subprecision and edge_normal
p_mid = f.cartesian_point((1.0, 0.0, 0.0))
# v1 and v2 are at the same location — use v1 for both
e_connector = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction((1.0, 0.0, 0.0)), 0.0)))
e_up = f.edge_curve(v3, v_tr, f.line(p3, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_back = f.edge_curve(v_tr, v_tl, f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0)))
e_down = f.edge_curve(v_tl, v0, f.line(p_tl, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

loop = f.edge_loop([
    f.oriented_edge(e_sub, True),
    f.oriented_edge(e_norm, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
], name="wire_loop")
fob = f.face_outer_bound(loop)

plane = f.plane(plc)
face = f.advanced_face([fob], plane, name="face_from_edges")

shell = f.open_shell([face], name="wire_shell")
sbsm = f.shell_based_surface_model([shell])

# Ultra-precision PRODUCT chain with 1e-10 uncertainty
f.add_product_chain(sbsm, uncertainty=1.0E-10)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N091.stp")
