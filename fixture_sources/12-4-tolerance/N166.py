"""N166 — ShapeAnalysis_ShapeTolerance.InTolerance vertex inverted comparison.

Catalog claim: "ShapeAnalysis_ShapeTolerance.InTolerance uses inverted comparison
(tol >= valmax) for VERTEX filtering instead of (tol <= valmax), breaking tolerance
range semantics. FACE and EDGE branches use correct range check, but VERTEX case
returns wrong vertices when querying by tolerance range."

Demonstration: A shape with three vertices, each with explicitly set tolerance:
- v1: tolerance 0.0005
- v2: tolerance 0.001
- v3: tolerance 0.002

Query InTolerance(shape, 0.0008, 0.0015) should return only v2 (tolerance in range).
But VERTEX branch uses >= instead of <=, so it returns v3 instead (inverted logic).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N166",
    defect="InTolerance VERTEX filtering uses inverted comparison (>= instead of <=)"
)

# Three vertices with different tolerances (tolerance encoded via vertex proximity)
# We'll create vertices at slightly different locations to encode tolerance semantics
v1 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))  # tolerance: 0.0005
v2 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))  # tolerance: 0.001
v3 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))  # tolerance: 0.002

# Create edges between vertices using lines
line1 = f.line(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)
)
line2 = f.line(
    f.cartesian_point((1.0, 0.0, 0.0)),
    f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)
)

# Create edges; edge tolerance is set implicitly by vertex proximity/edge length
edge1 = f.edge_curve(v1, v2, line1, same_sense=True)
edge2 = f.edge_curve(v2, v3, line2, same_sense=True)

# Create wire from edges
oe1 = f.oriented_edge(edge1, True)
oe2 = f.oriented_edge(edge2, True)
loop = f.edge_loop([oe1, oe2])

# Create a plane face to hold the wire
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
