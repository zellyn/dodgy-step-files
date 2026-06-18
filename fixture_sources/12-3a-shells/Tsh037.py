"""Tsh037 — Free wires/edges in compound (no faces, INTERNAL orientation).

Catalog claim: "A STEP compound contains free wires or edges with no parent face;
wireframe content with no surface model. A receiver expecting solid or surface
bodies needs to handle these as wireframe-only assets."

Demonstration: Build an EDGE_BASED_WIREFRAME_MODEL (or compound with only
ORIENTED_EDGE) containing only free edges with no parent face. The geometry
is wireframe-only.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh037",
             defect="Compound contains only wires, no surface or solid")

# Build a wireframe: a simple rectangular loop with no faces
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# Edges for the wireframe loop
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p0, vec)
e0 = f.edge_curve(v0, v1, ln)
d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p1, vec)
e1 = f.edge_curve(v1, v2, ln)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p2, vec)
e2 = f.edge_curve(v2, v3, ln)
d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p3, vec)
e3 = f.edge_curve(v3, v0, ln)

# Wireframe edges (no EDGE_LOOP binding, just individual ORIENTED_EDGE)
oe0 = f.oriented_edge(e0, True)
oe1 = f.oriented_edge(e1, True)
oe2 = f.oriented_edge(e2, True)
oe3 = f.oriented_edge(e3, True)

# EDGE_BASED_WIREFRAME_MODEL containing only edges (no faces)
# Create an edge set manually since the builder doesn't have EDGE_BASED_WIREFRAME_MODEL
edge_set = f._emit("GEOMETRIC_CURVE_SET", [oe0, oe1, oe2, oe3])

# Build a representation context
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, zdir, xdir)

# Wireframe representation (no surface model)
wireframe = f._emit("WIREFRAME_SURFACE_SHAPE_REPRESENTATION", [edge_set], plc)
f.add_product_chain(wireframe)
