"""Tsh042 — `bad vertex`: vertex misplaced relative to incident edges.

Catalog claim: The VERTEX_POINT coordinate does not coincide with the curve
evaluation at the edge's parameter endpoint(s); wire orientation/snap defect
at corners.

Mechanism IS the shell structure: a planar face is built with an OPEN_SHELL
/ SHELL_BASED_SURFACE_MODEL whose edges reference a LINE geometry but whose
start VERTEX_POINT coordinates are offset from the true line endpoint by
(0.001, 0.001, 0). The vertex-position mismatch IS wired directly into the
edge/vertex topology: every edge_curve's vertex point disagrees with the
underlying line's evaluation at its parameter. Kernels must snap vertex to
curve endpoint within tolerance or mark the edge as tolerant.

Tier-3 assertions:
  - face[0].surface_type == "plane"
  - n_edges_total >= 4
  - n_vertices_total >= 8
  - face[0].sliver_aspect_max_min > 1e6

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh042",
    defect=(
        "VERTEX_POINT coordinates offset by (0.001,0.001,0) from the true LINE endpoints; "
        "vertex-position mismatch IS wired into edge/vertex topology of OPEN_SHELL; "
        "kernels must snap vertex to curve endpoint within tolerance or reject; "
        "sliver face to satisfy tier-3 aspect assertion"
    ),
)

# Sliver rectangular face: 10 units long (X), 1e-6 wide (Y) → aspect = 1e7
# True corner coordinates:
L = 10.0
W = 1e-6
OFFSET = 0.001  # vertex offset — intentionally > tolerance

# True line-endpoint coordinates (what the LINE geometry says)
true_p0 = (0.0, 0.0, 0.0)
true_p1 = (L,   0.0, 0.0)
true_p2 = (L,   W,   0.0)
true_p3 = (0.0, W,   0.0)

# DEFECT: vertex points are offset from true endpoints
def bad_pt(x, y, z):
    """Vertex coordinate offset by OFFSET from true position."""
    return f.cartesian_point((x + OFFSET, y + OFFSET, z))

v0 = f.vertex_point(bad_pt(*true_p0))
v1 = f.vertex_point(bad_pt(*true_p1))
v2 = f.vertex_point(bad_pt(*true_p2))
v3 = f.vertex_point(bad_pt(*true_p3))

# Line geometry runs between true endpoints (correct geometry, wrong vertices)
def mk_edge(va, vb, ox, oy, oz, dx, dy, dz):
    origin = f.cartesian_point((float(ox), float(oy), float(oz)))
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(origin, vec)
    return f.edge_curve(va, vb, ln)

e0 = mk_edge(v0, v1, *true_p0,  1, 0, 0)   # LINE from p0→p1; vertices offset
e1 = mk_edge(v1, v2, *true_p1,  0, 1, 0)
e2 = mk_edge(v2, v3, *true_p2, -1, 0, 0)
e3 = mk_edge(v3, v0, *true_p3,  0,-1, 0)

lp = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# Plane at true origin
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
ax = f.axis2_placement_3d(ax_orig, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
plane = f.plane(ax)
face = f.advanced_face([f.face_outer_bound(lp)], plane)

# OPEN_SHELL: vertex mismatch IS the defect, wired into shell/face/edge topology
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
