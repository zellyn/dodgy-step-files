"""N120 — ShapeAnalysis_ShapeTolerance.GlobalTolerance averaging-over-empty

Call GlobalTolerance with mode=avg on a shape containing no vertices/edges of
the requested type; division-by-zero produces NaN. The method accumulates sum
across elements and divides by count at the end, but does not guard against
empty iteration.

Reproducer: closed shell with a single triangular face and three boundary edges,
but no free (isolated) vertices. Calling GlobalTolerance with selector=VERTEX
and mode=averaging iterates over an empty vertex set, dividing total(0) by
count(0) to produce NaN.

Byte assertions:
  contains(b'v0')
  contains(b'v1')
  contains(b'e_01')

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N120",
    defect=(
        "CLOSED_SHELL with a single triangular face (v0, v1, v2, v3) with edges "
        "e_01, e_12, e_20; no free isolated vertices; GlobalTolerance(VERTEX, avg) "
        "iterates empty vertex set, divides 0/0 producing NaN"
    ),
)

# Triangle vertices
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((0.0, 10.0, 0.0))

v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")

# Triangle edges
d_01 = f.direction((1.0, 0.0, 0.0))
vec_01 = f.vector(d_01, 10.0)
l_01 = f.line(p0, vec_01)
e_01 = f.edge_curve(v0, v1, l_01, name="e_01")

d_12 = f.direction((-1.0, 1.0, 0.0))
vec_12 = f.vector(d_12, 10.0)
l_12 = f.line(p1, vec_12)
e_12 = f.edge_curve(v1, v2, l_12, name="e_12")

d_20 = f.direction((0.0, -1.0, 0.0))
vec_20 = f.vector(d_20, 10.0)
l_20 = f.line(p2, vec_20)
e_20 = f.edge_curve(v2, v0, l_20, name="e_20")

loop = f.edge_loop([
    f.oriented_edge(e_01, True),
    f.oriented_edge(e_12, True),
    f.oriented_edge(e_20, True),
])
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane)

shell = f.closed_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N120.stp")
