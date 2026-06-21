"""N081 — BRepLib.UpdateEdgeTol dual-path divergence

SameParameter path uses EvalMaxParametricDistance; non-SameParameter uses
EvalMaxDistanceAlongParameter with differing sampling semantics. Two distance
evaluation branches depend on SameParameter flag; parameter sampling strategy
inverts, risking tolerance underestimation on one path.

Fixture: Edge with SameParameter=true but actual disparity in domain
parametrization; EvalMaxParametricDistance samples 3D curve at uniform
parameter, misses peak deviation.

Byte assertions:
  contains(b'edge_3d')
  count_entity_def(b'EDGE_CURVE') >= 2

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N081",
    defect=(
        "edge_3d with SameParameter=.T. but domain parametrization mismatch; "
        "UpdateEdgeTol SameParameter path uses EvalMaxParametricDistance while "
        "non-SameParameter uses EvalMaxDistanceAlongParameter — divergent sampling"
    ),
)

# Edge with SameParameter=true but actual disparity in domain parametrization.
# EvalMaxParametricDistance samples 3D curve at uniform parameter, misses peak deviation.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))

v0 = f.vertex_point(p0, name="V1")
v1 = f.vertex_point(p1, name="V2")

d_x = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 1.0)
l1 = f.line(p0, vec_x, name="edge_3d")
e1 = f.edge_curve(v0, v1, l1)

# Second edge for SameRange comparison: same geometry different param scale
d_x2 = f.direction((1.0, 0.0, 0.0))
vec_x2 = f.vector(d_x2, 0.1)  # 10x smaller vector = 10x larger param domain
l2 = f.line(p0, vec_x2)
e2 = f.edge_curve(v0, v1, l2, name="edge_sameParam")

# Rectangular face to host the edges
p2 = f.cartesian_point((10.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

d_y = f.direction((0.0, 1.0, 0.0))
vec_y = f.vector(d_y, 1.0)
l_up = f.line(p1, vec_y)
e_up = f.edge_curve(v1, v2, l_up)

d_negx = f.direction((-1.0, 0.0, 0.0))
vec_negx = f.vector(d_negx, 10.0)
l_back = f.line(p2, vec_negx)
e_back = f.edge_curve(v2, v3, l_back)

d_negy = f.direction((0.0, -1.0, 0.0))
vec_negy = f.vector(d_negy, 1.0)
l_down = f.line(p3, vec_negy)
e_down = f.edge_curve(v3, v0, l_down)

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
])
fob = f.face_outer_bound(loop)

d_z = f.direction((0.0, 0.0, 1.0))
d_x3 = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p0, d_z, d_x3)
plane = f.plane(plc)
face = f.advanced_face([fob], plane)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N081.stp")
