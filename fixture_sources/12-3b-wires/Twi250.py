"""Twi250 — FindVertAndSplitEdge endpoint-selection ambiguity.

Catalog claim: intersection point equidistant from both edge endpoints;
ShapeFix_IntersectionTool::FindVertAndSplitEdge's distance comparison
`if (pi1.Distance(PV1) < pi1.Distance(PV2))` at line ~994 picks an
arbitrary endpoint without deterministic ordering.

Previous fixture had only a midpoint-equidistant edge but no second
wire actually crossing it — the split logic was never triggered. Regen
with two intersecting wires: a horizontal edge whose midpoint is
equidistant from its endpoints, plus a vertical edge that crosses at
exactly that midpoint.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Twi250",
             defect="two wires intersecting at equidistant midpoint of edge1")

# Horizontal edge: A=(0,0,0) → B=(2,0,0); midpoint at (1,0,0) is equidistant.
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((2.0, 0.0, 0.0))
p_mid = f.cartesian_point((1.0, 0.0, 0.0))   # intersection target

v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)

d_h = f.direction((1.0, 0.0, 0.0))
vec_h = f.vector(d_h, 2.0)
ln_h = f.line(p_a, vec_h)
edge_h = f.edge_curve(v_a, v_b, ln_h)

# Vertical edge crossing the horizontal at the equidistant midpoint:
# C=(1,-1,0) → D=(1,1,0), passing through (1,0,0).
p_c = f.cartesian_point((1.0, -1.0, 0.0))
p_d = f.cartesian_point((1.0, 1.0, 0.0))
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

d_v = f.direction((0.0, 1.0, 0.0))
vec_v = f.vector(d_v, 2.0)
ln_v = f.line(p_c, vec_v)
edge_v = f.edge_curve(v_c, v_d, ln_v)

# Open wire containing both edges so the IntersectionTool sees the crossing.
loop = f.edge_loop([
    f.oriented_edge(edge_h, True),
    f.oriented_edge(edge_v, True),
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
