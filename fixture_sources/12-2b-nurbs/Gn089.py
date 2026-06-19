"""Gn089 — SplitSurface non-rectangular (triangular) trim region.

Catalog claim: B-spline surface trimmed to a non-rectangular (triangular)
region; ShapeUpgrade_SplitSurface's axis-aligned-split assumption breaks
when the trim boundary isn't a U/V-axis-parallel rectangle.

Previous fixture had a B-spline surface + three boundary curves but no
structural attachment — the trim wasn't expressed as a face boundary, so
SplitSurface couldn't even see the triangular region. Regen: wrap the
B-spline surface in an ADVANCED_FACE whose FACE_OUTER_BOUND is a
triangular EDGE_LOOP, properly structurally attached.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn089",
             defect="B-spline surface with triangular face boundary")

# Degree-3 × degree-2 B-spline surface, 4×3 control grid.
pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 2.0, 0.0)],
    [(1.0, 0.0, 0.5), (1.0, 1.0, 1.0), (1.0, 2.0, 0.5)],
    [(2.0, 0.0, 0.5), (2.0, 1.0, 1.0), (2.0, 2.0, 0.5)],
    [(3.0, 0.0, 0.0), (3.0, 1.0, 0.0), (3.0, 2.0, 0.0)],
]]
grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)
surf = f._emit_raw(
    "B_SPLINE_SURFACE_WITH_KNOTS('triangular_trim',3,2,"
    f"({grid}),"
    ".UNSPECIFIED.,.F.,.F.,.F.,"
    "(4,4),(3,3),"
    "(0.0,1.0),(0.0,1.0),"
    ".UNSPECIFIED.)"
)

# Three corner vertices forming a triangular boundary in 3D space.
# Picked at the surface corners so the boundary is on the surface itself.
v0_pt = f.cartesian_point((0.0, 0.0, 0.0))
v1_pt = f.cartesian_point((3.0, 0.0, 0.0))
v2_pt = f.cartesian_point((1.5, 2.0, 0.0))
v0 = f.vertex_point(v0_pt)
v1 = f.vertex_point(v1_pt)
v2 = f.vertex_point(v2_pt)

# Three straight edges between the corners.
def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# Use unit-length DIRECTIONs; magnitudes carry the length.
import math
e0 = line_edge(v0_pt, (1.0, 0.0, 0.0), 3.0, v0, v1)
# Edge from (3,0,0) to (1.5,2,0): direction normalized, length sqrt(1.5^2+2^2)
dx, dy = -1.5, 2.0
mag = math.hypot(dx, dy)
e1 = line_edge(v1_pt, (dx / mag, dy / mag, 0.0), mag, v1, v2)
# Edge from (1.5,2,0) to (0,0,0): direction normalized.
dx, dy = -1.5, -2.0
mag = math.hypot(dx, dy)
e2 = line_edge(v2_pt, (dx / mag, dy / mag, 0.0), mag, v2, v0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
