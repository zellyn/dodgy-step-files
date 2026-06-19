"""Twi194 — FixIntersectingEdges shared-vertex misclassification.

Catalog claim: three edges form a closed triangle; E1 (param u=0..10) and
E3 (param u=0..20) share only vertex V1 at their endpoints but their
parameter ranges [0,10] and [0,20] overlap. FixIntersectingEdges flags this
as an intersection, applying unnecessary tolerance inflation.

Previous fixture had three collinear edges (zero-area "face") and no
surface — face was untestable. Regen: a real triangle with two edges
sharing the same param-domain origin (0..10 vs 0..20) on a carrier plane.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Twi194",
             defect="triangle wire where two edges share param-range origin")

# Three triangle vertices.
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((10.0, 0.0, 0.0))
p_c = f.cartesian_point((10.0, 20.0, 0.0))

v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)

# E1: A → B along +X; LINE with VECTOR magnitude 1, so param domain [0, 10].
d_e1 = f.direction((1.0, 0.0, 0.0))
vec_e1 = f.vector(d_e1, 1.0)
ln_e1 = f.line(p_a, vec_e1)
e1 = f.edge_curve(v_a, v_b, ln_e1)

# E2: B → C along +Y; param domain [0, 20].
d_e2 = f.direction((0.0, 1.0, 0.0))
vec_e2 = f.vector(d_e2, 1.0)
ln_e2 = f.line(p_b, vec_e2)
e2 = f.edge_curve(v_b, v_c, ln_e2)

# E3: C → A along (-10, -20, 0); LINE starts at A (param 0), so its
# parameter domain overlaps with E1's [0, 10] near the shared vertex A.
import math
dx, dy = -10.0, -20.0
mag = math.hypot(dx, dy)
d_e3 = f.direction((dx / mag, dy / mag, 0.0))
vec_e3 = f.vector(d_e3, 1.0)
ln_e3 = f.line(p_c, vec_e3)
e3 = f.edge_curve(v_c, v_a, ln_e3)

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# Carrier plane so the wire lives on a surface.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
