"""Tsh138 — ShapeFix_Shell.Perform repeated-call-state

Catalog claim: "Shell with inverted face orientation. ShapeFix_Shell::Perform
called twice; second call reuses myStatus from first Perform without reset,
skipping needed orientation fixes. Tests state-accumulation regression."

Demonstration: construct a shell where one face has intentionally inverted
orientation (same_sense=False on ADVANCED_FACE). This requires two different
fix passes to detect and repair. The defect manifests when processing logic
caches state between calls.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh138",
             defect="Shell with inverted face orientation for state-accumulation test")

# Create two adjacent rectangular faces on the same plane
# Face A: normal facing up (+Z)
# Face B: normal facing down (-Z, inverted) sharing an edge with Face A

# Left rectangle (Face A) - (0,0,0) to (1,1,0)
pA0 = f.cartesian_point((0.0, 0.0, 0.0))
pA1 = f.cartesian_point((1.0, 0.0, 0.0))
pA2 = f.cartesian_point((1.0, 1.0, 0.0))
pA3 = f.cartesian_point((0.0, 1.0, 0.0))

# Right rectangle (Face B) - (1,0,0) to (2,1,0)
pB1 = f.cartesian_point((2.0, 0.0, 0.0))
pB2 = f.cartesian_point((2.0, 1.0, 0.0))

vA0 = f.vertex_point(pA0)
vA1 = f.vertex_point(pA1)
vA2 = f.vertex_point(pA2)
vA3 = f.vertex_point(pA3)
vB1 = f.vertex_point(pB1)
vB2 = f.vertex_point(pB2)

# Shared edge between A and B (from pA1 to pA2)
d_shared = f.direction((0.0, 1.0, 0.0))
vec_shared = f.vector(d_shared, 1.0)
line_shared = f.line(pA1, vec_shared)
shared_edge = f.edge_curve(vA1, vA2, line_shared)

# Face A edges (bottom, right, top, left)
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA0, vec)
eA_bot = f.edge_curve(vA0, vA1, ln)

d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA2, vec)
eA_top = f.edge_curve(vA2, vA3, ln)

d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA3, vec)
eA_left = f.edge_curve(vA3, vA0, ln)

loopA = f.edge_loop([
    f.oriented_edge(eA_bot, True),
    f.oriented_edge(shared_edge, True),
    f.oriented_edge(eA_top, True),
    f.oriented_edge(eA_left, True),
])

# Face B edges (bottom, right, top, left where top is the shared edge)
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA1, vec)
eB_bot = f.edge_curve(vA1, vB1, ln)

d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pB1, vec)
eB_right = f.edge_curve(vB1, vB2, ln)

d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pB2, vec)
eB_top = f.edge_curve(vB2, vA2, ln)

loopB = f.edge_loop([
    f.oriented_edge(eB_bot, True),
    f.oriented_edge(eB_right, True),
    f.oriented_edge(eB_top, True),
    f.oriented_edge(shared_edge, False),  # reversed orientation
])

# Create plane for both faces
ax_origin = f.cartesian_point((1.0, 0.5, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

# Face A with normal same_sense=True
faceA = f.advanced_face([f.face_outer_bound(loopA)], plane, same_sense=True)

# Face B with INVERTED orientation (same_sense=False, the defect)
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane, same_sense=False)

# Open shell with both faces
shell = f.open_shell([faceA, faceB])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
