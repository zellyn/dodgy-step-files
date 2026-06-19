"""N154 — Spatial closure detection via distance threshold.

Catalog claim: V0.IsSame(V1)=false (topologically distinct vertices) but
3D distance is ~1e-8, well within UNCERTAINTY_MEASURE 1e-7. Healer should
detect spatial closure and snap, but distance-threshold check is missing.

Previous fixture had near-coincident vertices but no EDGE_LOOP or wire
structure linking them — closure wasn't a wire-level scenario. Regen with
two edges forming an almost-closed arc loop, end vertices distinct but
~1e-8 apart on a planar carrier.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="N154",
             defect="topologically open wire with sub-tolerance spatial closure")

# Two distinct vertex entries 1.41e-8 apart — within global uncertainty 1e-7.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1a = f.cartesian_point((1.0, 0.0, 0.0))         # edge0 end
p1b = f.cartesian_point((1.00000001, 1.0e-8, 0.0))  # edge1 start, distinct vertex
p2 = f.cartesian_point((2.0, 0.0, 0.0))

v0 = f.vertex_point(p0)
v1a = f.vertex_point(p1a)
v1b = f.vertex_point(p1b)   # distinct topological vertex at ~p1a (1.4e-8 away)
v2 = f.vertex_point(p2)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

import math
# Edge 0 to v1a (the "near-close" endpoint).
e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1a)
# Edge from v1b (distinct vertex, sub-tolerance neighbor of v1a) onward.
e1 = line_edge(p1b, (1.0, 0.0, 0.0), 1.0, v1b, v2)
# Closing edge back to v0.
dx, dy = -2.0, 0.0
mag = math.hypot(dx, dy)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 2.0, v2, v0)

# EDGE_LOOP that's *almost* closed: v0 → v1a (e0) | v1b → v2 (e1) | v2 → v0 (e2)
# The gap between v1a and v1b is the spatial-closure scenario CheckShapeConnect
# is supposed to detect.
loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])

# Carrier plane.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
