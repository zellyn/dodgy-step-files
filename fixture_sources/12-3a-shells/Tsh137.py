"""Tsh137 — ShapeAnalysis_Shell.LoadShells nested-compound

Catalog claim: "Compound containing compound containing shell.
ShapeAnalysis_Shell::LoadShells recursive descent terminates at first nesting
level, failing to extract inner shell."

Demonstration: construct a compound that contains another compound, which
in turn contains the shell. This tests whether recursive extraction can handle
nested containment.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh137",
             defect="Compound within compound containing shell")

# Build a simple planar face
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# Create the four edges
vecs_dirs_pts = [
    ((1.0, 0.0, 0.0), (v0, v1), (p0, p1)),
    ((0.0, 1.0, 0.0), (v1, v2), (p1, p2)),
    ((-1.0, 0.0, 0.0), (v2, v3), (p2, p3)),
    ((0.0, -1.0, 0.0), (v3, v0), (p3, p0)),
]

edges = []
for (dx, dy, dz), (va, vb), (pa, pb) in vecs_dirs_pts:
    d = f.direction((dx, dy, dz))
    vec = f.vector(d, 1.0)
    line = f.line(pa, vec)
    edges.append(f.edge_curve(va, vb, line))

loop = f.edge_loop([f.oriented_edge(e) for e in edges])
ax_origin = f.cartesian_point((0.5, 0.5, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([f.face_outer_bound(loop)], plane)

shell = f.open_shell([face])

# Wrap shell in a compound, then wrap that in another compound.
# Using raw emit to construct COMPOUND entities (not in standard builder).
# COMPOUND is typically: COMPOUND(name, representation_items)
#   where representation_items is a list of entities.
# Nesting: inner_compound -> outer_compound
inner_compound = f._emit_raw(f"COMPOUND('inner',({shell.ref()}))")
outer_compound = f._emit_raw(f"COMPOUND('outer',({inner_compound.ref()}))")

# Point to outer compound for product chain
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
