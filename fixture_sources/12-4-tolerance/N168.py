"""N168 — ShapeFix_ShapeTolerance.LimitTolerance recursive wire double-mutation.

Catalog claim: "ShapeFix_ShapeTolerance.LimitTolerance WIRE branch recursively
applies tolerance limiting to V1/V2 vertices without preventing double-application.
A single call on a wire can mutate vertex tolerances twice, leading to over-clamping."

Demonstration: A wire with multiple edges sharing vertices. The LimitTolerance call
recursively processes each WIRE's V1 and V2, and if vertices are reused across edges,
they get limited twice. The shared vertices end up with compounded tolerance mutations.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="N168",
    defect="LimitTolerance applies double mutations to shared wire vertices"
)

# Create a poly-line wire with shared vertices
# Vertices: A -> B -> C -> D, where B and C are shared across edges
v_a = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_b = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
v_c = f.vertex_point(f.cartesian_point((2.0, 1.0, 0.0)))
v_d = f.vertex_point(f.cartesian_point((3.0, 0.0, 0.0)))

# Create line segments
line_ab = f.line(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)
)
line_bc = f.line(
    f.cartesian_point((1.0, 0.0, 0.0)),
    f.vector(f.direction((0.5, 0.5, 0.0)), math.sqrt(2.0))
)
line_cd = f.line(
    f.cartesian_point((2.0, 1.0, 0.0)),
    f.vector(f.direction((0.5, -0.5, 0.0)), math.sqrt(2.0))
)

# Create edges
edge_ab = f.edge_curve(v_a, v_b, line_ab, same_sense=True)
edge_bc = f.edge_curve(v_b, v_c, line_bc, same_sense=True)
edge_cd = f.edge_curve(v_c, v_d, line_cd, same_sense=True)

# Create oriented edges and wire
oe_ab = f.oriented_edge(edge_ab, True)
oe_bc = f.oriented_edge(edge_bc, True)
oe_cd = f.oriented_edge(edge_cd, True)
loop = f.edge_loop([oe_ab, oe_bc, oe_cd])

# Create a face to hold the wire
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane = f.plane(plc)

fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])

f.add_product_chain(sbsm, mode="surface_shape")
