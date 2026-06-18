"""M075 — AP238 selective control-flow references unresolved branch executable.

Catalog claim: "A SELECTIVE lists branch executables in its its_elements list,
but one or more of those entity ids are not declared in the file."

Demonstration: construct a SELECTIVE (AP238 control flow) with two branch
references in its_elements list. The first branch is properly defined;
the second is a DanglingRef that will never be resolved. This demonstrates
the exact defect: a control-flow construct referencing undefined downstream
entities.
"""
from step_corpus.step_builder import StepFile, DanglingRef

f = StepFile(catalog_id="M075",
             defect="SELECTIVE control-flow with unresolved branch executable reference")

# AP238 requires a basic product context.
# We need to create executables and a selective that references them.

# First, create a simple EXECUTABLE (a basic work instruction).
# EXECUTABLE has (name, description, kind, ownerships, properties).
# We'll use _emit_raw to construct AP238-specific entities since the builder
# doesn't have dedicated methods for them.

# Branch executable #100 (valid)
exec1 = f._emit_raw("EXECUTABLE('exec1','first branch','WORK_INSTRUCTION',(),())")

# Now create the SELECTIVE that references two branches:
# - exec1 (valid ref #100)
# - branch2 (dangling ref #999, never defined)
# SELECTIVE is (name, description, kind, ownerships, properties, its_elements).

selective = f._emit_raw(
    "SELECTIVE('sel1','control selector','SELECTIVE_BRANCHING',(),(),(#100,#999))"
)

# Add to product model via shell_based_surface_model wrapper (required for serialization)
# Since we're in AP238, we'll just emit the entities without wrapping in a geometry model.
# The builder's add_product_chain will handle the basic product/representation linkage.

# For now, create a minimal geometry model to anchor the AP238 control flow.
# We'll use a dummy point to satisfy the model requirement.
origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(origin, zdir, xdir)
plane = f.plane(plc)

# Create a minimal degenerate face (just to have a shape)
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# Build edges
dirs = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0), (0.0, -1.0, 0.0)]
verts = [(v0, v1), (v1, v2), (v2, v3), (v3, v0)]
points = [(p0, p1), (p1, p2), (p2, p3), (p3, p0)]
edges = []
for (dx, dy, dz), (va, vb), (pa, pb) in zip(dirs, verts, points):
    d = f.direction((dx, dy, dz))
    vec = f.vector(d, 1.0)
    line = f.line(pa, vec)
    edges.append(f.edge_curve(va, vb, line))

loop = f.edge_loop([f.oriented_edge(e) for e in edges])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])

# Add product chain (required for validator)
f.add_product_chain(sbsm)
