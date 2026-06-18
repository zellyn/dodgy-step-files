"""N170 — BRepBuilderAPI_Sewing unevaluated distance filter first-pass bypass.

Catalog claim: "BRepBuilderAPI_Sewing.AnalysisNearestEdges skips unevaluated
distance threshold check on first pass, allowing edges beyond tolerance distance
to enter the sewing candidate pool. Subsequent filtering steps may fail to
reject them, creating invalid seams."

Demonstration: Two faces with edges that are nominally parallel but separated
by a distance slightly beyond the sewing tolerance. First-pass distance evaluation
is bypassed, so both edges appear as sewing candidates despite exceeding the
tolerance. Sewing proceeds and produces invalid or degenerate edges.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="N170",
    defect="Sewing unevaluated distance filter first-pass allows over-tolerance edges"
)

# Create two rectangular faces with parallel edges separated by distance > tolerance

# Face 1: rectangle at z=0
v1_1 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v1_2 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
v1_3 = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))
v1_4 = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))

line1_a = f.line(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)
)
line1_b = f.line(
    f.cartesian_point((1.0, 0.0, 0.0)),
    f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)
)
line1_c = f.line(
    f.cartesian_point((1.0, 1.0, 0.0)),
    f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)
)
line1_d = f.line(
    f.cartesian_point((0.0, 1.0, 0.0)),
    f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)
)

edge1_a = f.edge_curve(v1_1, v1_2, line1_a)
edge1_b = f.edge_curve(v1_2, v1_3, line1_b)
edge1_c = f.edge_curve(v1_3, v1_4, line1_c)
edge1_d = f.edge_curve(v1_4, v1_1, line1_d)

oe1_a = f.oriented_edge(edge1_a, True)
oe1_b = f.oriented_edge(edge1_b, True)
oe1_c = f.oriented_edge(edge1_c, True)
oe1_d = f.oriented_edge(edge1_d, True)
loop1 = f.edge_loop([oe1_a, oe1_b, oe1_c, oe1_d])

# Face 2: offset rectangle at z=0.0015 (slightly beyond typical sewing tolerance 0.001)
v2_1 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0015)))
v2_2 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0015)))
v2_3 = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0015)))
v2_4 = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0015)))

line2_a = f.line(
    f.cartesian_point((0.0, 0.0, 0.0015)),
    f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)
)
line2_b = f.line(
    f.cartesian_point((1.0, 0.0, 0.0015)),
    f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)
)
line2_c = f.line(
    f.cartesian_point((1.0, 1.0, 0.0015)),
    f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)
)
line2_d = f.line(
    f.cartesian_point((0.0, 1.0, 0.0015)),
    f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)
)

edge2_a = f.edge_curve(v2_1, v2_2, line2_a)
edge2_b = f.edge_curve(v2_2, v2_3, line2_b)
edge2_c = f.edge_curve(v2_3, v2_4, line2_c)
edge2_d = f.edge_curve(v2_4, v2_1, line2_d)

oe2_a = f.oriented_edge(edge2_a, True)
oe2_b = f.oriented_edge(edge2_b, True)
oe2_c = f.oriented_edge(edge2_c, True)
oe2_d = f.oriented_edge(edge2_d, True)
loop2 = f.edge_loop([oe2_a, oe2_b, oe2_c, oe2_d])

# Create planes for both faces
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc1 = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane1 = f.plane(plc1)

ax_orig2 = f.cartesian_point((0.0, 0.0, 0.0015))
plc2 = f.axis2_placement_3d(ax_orig2, zdir, xdir)
plane2 = f.plane(plc2)

fob1 = f.face_outer_bound(loop1)
face1 = f.advanced_face([fob1], plane1)

fob2 = f.face_outer_bound(loop2)
face2 = f.advanced_face([fob2], plane2)

shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])

f.add_product_chain(sbsm, mode="surface_shape")
