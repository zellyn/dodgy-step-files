"""N042 — Self-intersecting wire from coarse-discretization bbox check (sample-count too small)

When OCCT computed a curve's bounding box for self-intersection detection,
it used too few sampling points; near-tangent intersections were missed.
step-g hits the inverse: sampling p-curves with <2 points produces degenerate
trims. Two near-tangent edges on a planar face actually cross, but a
fixed-sample bbox check declares them disjoint.

Byte assertions:
  contains(b'curveA')
  contains(b'curveB')
  count_entity_def(b'B_SPLINE_CURVE_WITH_KNOTS') == 2

Tier-3: face[0].surface_type == "plane"
Tier-3: n_edges_total >= 2
Tier-3: n_vertices_total >= 4
Expected: occt=shape(1)/shape(1) gmsh=shape(5) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N042",
    defect=(
        "planar face outer wire has two near-tangent B_SPLINE_CURVE segments "
        "that cross at ~5e-4 mm inside the face; default bbox sampler with "
        "N=4 points misses the crossing — self-intersection undetected"
    ),
)

# Host PLANE z=0
orig = f.cartesian_point((0.0, 0.0, 0.0), name="origin")
zdir = f.direction((0.0, 0.0, 1.0), name="z")
xdir = f.direction((1.0, 0.0, 0.0), name="x")
plc = f.axis2_placement_3d(orig, zdir, xdir, name="plane_plc")
plane = f.plane(plc, name="host_plane")

# Two near-tangent B-spline curves that actually cross at ~0.0005 inside
# a 10x10 face. Bbox sampler with default ~4 samples sees their bounding
# boxes overlap but misses the crossing point.
a_p0 = f.cartesian_point((0.0, 5.0, 0.0), name="a_p0")
a_p1 = f.cartesian_point((5.0, 5.0005, 0.0), name="a_p1")
a_p2 = f.cartesian_point((10.0, 5.0, 0.0), name="a_p2")
b_p0 = f.cartesian_point((0.0, 5.0005, 0.0), name="b_p0")
b_p1 = f.cartesian_point((5.0, 5.0, 0.0), name="b_p1")
b_p2 = f.cartesian_point((10.0, 5.0005, 0.0), name="b_p2")

# Quadratic B-spline curves (degree 2)
curveA = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('curveA',2,"
    f"(#{a_p0.eid},#{a_p1.eid},#{a_p2.eid}),.UNSPECIFIED.,"
    f".F.,.F.,(3,3),(0.0,1.0),.UNSPECIFIED.)"
)
curveB = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('curveB',2,"
    f"(#{b_p0.eid},#{b_p1.eid},#{b_p2.eid}),.UNSPECIFIED.,"
    f".F.,.F.,(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

va_start = f.vertex_point(a_p0, name="a_start")
va_end = f.vertex_point(a_p2, name="a_end")
vb_start = f.vertex_point(b_p0, name="b_start")
vb_end = f.vertex_point(b_p2, name="b_end")

eA = f.edge_curve(va_start, va_end, curveA, name="eA_near_tangent_xs")
eB = f.edge_curve(vb_start, vb_end, curveB, name="eB_near_tangent_xs")

# Defect site: wire is self-intersecting (eA crosses eB) but a fixed-N
# bbox sampler with N=4 misses the crossing -- check passes erroneously.
loop = f.edge_loop([
    f.oriented_edge(eA, True),
    f.oriented_edge(eB, True),
], name="self_xs_loop_undetected_by_bbox")
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="coarse_bbox_self_xs_face")

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, uncertainty=1.0E-6)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N042.stp")
