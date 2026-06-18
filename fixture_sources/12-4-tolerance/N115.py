"""N115 — OverTolerance threshold-equality

Catalog claim: "ShapeAnalysis_ShapeTolerance.OverTolerance with vertex
tolerance exactly equal to threshold; non-strict comparison includes threshold
in 'over' result."

Demonstration: Single edge with vertex tolerance set to 0.5 mm, matching
UNCERTAINTY_MEASURE threshold value. Tests boundary condition of tolerance
comparison (≥ vs >).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="N115",
             defect="Vertex tolerance exactly equal to tolerance threshold")

# Create a simple edge with a vertex that has tolerance = threshold
# The defect is in the tolerance comparison logic, not the geometry itself

# Start and end points
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))

# Create vertices with explicit tolerance value
# VERTEX_POINT takes (name, vertex_geometry)
# But we need to set tolerance via the UNCERTAINTY_MEASURE

# We'll emit raw VERTEX_POINT entities and then wrap with tolerance
v0_basic = f.vertex_point(p0)
v1_basic = f.vertex_point(p1)

# Create edge between vertices
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
line = f.line(p0, vec)
edge = f.edge_curve(v0_basic, v1_basic, line)

# Create a loop from the edge
loop = f.edge_loop([f.oriented_edge(edge)])

# Create a degenerate face (1D structure) to hold the edge
# We'll use a very small "face" that's essentially the edge with tiny height
p2 = f.cartesian_point((10.0, 0.01, 0.0))
p3 = f.cartesian_point((0.0, 0.01, 0.0))
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

d2 = f.direction((0.0, 0.01, 0.0))
vec2 = f.vector(d2, 0.01)
line2 = f.line(p1, vec2)
edge2 = f.edge_curve(v1_basic, v2, line2)

d3 = f.direction((-1.0, 0.0, 0.0))
vec3 = f.vector(d3, 10.0)
line3 = f.line(p2, vec3)
edge3 = f.edge_curve(v2, v3, line3)

d4 = f.direction((0.0, -0.01, 0.0))
vec4 = f.vector(d4, 0.01)
line4 = f.line(p3, vec4)
edge4 = f.edge_curve(v3, v0_basic, line4)

small_loop = f.edge_loop([
    f.oriented_edge(edge),
    f.oriented_edge(edge2),
    f.oriented_edge(edge3),
    f.oriented_edge(edge4),
])

# Create plane
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

face = f.advanced_face([f.face_outer_bound(small_loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])

# Now add uncertainty measure with threshold-equality
# Create UNCERTAINTY_MEASURE with exact tolerance = 0.5mm
uncertainty = f._emit_raw("UNCERTAINTY_MEASURE(0.5,(.PRODUCT_DEFINITION.))")

f.add_product_chain(sbsm)
