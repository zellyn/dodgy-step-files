"""Me082 — connectivity_null_edge_endpoint: degenerate triangle with duplicate vertex index.

Catalog claim: triangle t1 references vertex 0 for two of its three corners
(indices [0, 0, 2]), creating a self-loop edge (v0, v0) with zero length.
MeshFix checkConnectivity Branch 4 (*NULL_EDGE_ENDPOINT*) fires when an edge
in the half-edge structure has one or both endpoints set to NULL. The triangle-
list equivalent is a triangle where two corners share the same vertex index,
producing an edge with coincident endpoints (a degenerate edge). The edge
(v0, v0) has zero length and its two endpoints are identical — the very
condition Branch 4 was designed to catch.

Defect carrier: t0 is a valid triangle; t1 = [v0, v0, v2] is degenerate — the
edge from v0 to v0 is a zero-length self-loop.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me082",
             title="connectivity null edge endpoint: degenerate triangle [v0,v0,v2] has zero-length self-loop edge",
             defect_class="degenerate_triangle")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)

# Valid triangle.
m.triangle(v0, v1, v2)

# Degenerate triangle: v0 appears twice → self-loop edge (v0, v0).
m.triangle(v0, v0, v2)

# The degenerate triangle (index 1) has zero area.
m.assert_triangle_area_lt(1, 1e-12)

# The self-loop edge: canonical form (min, max) = (v0, v0) appears once.
# Shared count == 1 because only triangle 1 contributes it.
m.assert_edge_shared(v0, v0, 1)
