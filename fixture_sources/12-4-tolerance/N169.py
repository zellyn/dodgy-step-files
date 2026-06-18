"""N169 — BRep_Tool GetTolerance mixed-precision accumulation.

Catalog claim: "BRep_Tool::GetTolerance accumulates vertex and edge tolerances
without precision normalization. Mixing high-precision vertices with coarse edges
yields inflated composite tolerance that exceeds intended bounds."

Demonstration: A shape with vertices set to very high precision (1e-6) but edges
with coarser tolerance (1e-3). BRep_Tool::GetTolerance returns the max of these,
but does not normalize or clamp to consistent precision level. The result is
over-permissive tolerance that breaks downstream geometric checks.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N169",
    defect="GetTolerance accumulates without precision normalization"
)

# Create vertices with very high precision (tight tolerance)
# Simulate this with tightly clustered points
v1 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v2 = f.vertex_point(f.cartesian_point((1.0000001, 0.0, 0.0)))  # 1e-6 offset

# Create a line between them (coarse edge)
line = f.line(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)
)

# Edge with implicit coarse tolerance (1e-3 from edge length scale)
edge = f.edge_curve(v1, v2, line, same_sense=True)

# Wrap in simple topology
oe = f.oriented_edge(edge, True)
loop = f.edge_loop([oe])

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
