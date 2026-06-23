"""Me087 — connectivity_null_triangle_edge: single isolated triangle with all-boundary edges.

Catalog claim: a mesh containing a single isolated triangle has all three of its
edges as boundary (incident on exactly 1 triangle each). MeshFix
checkConnectivity Branch 11 (*NULL_TRIANGLE_EDGE*) fires when a triangle has
a NULL pointer for one of its three required edge slots in the half-edge
structure. An isolated single triangle is the minimal mesh where this condition
can arise: because no adjacent face is present to fill the t2 slot, the twin
edge pointer would be NULL in any partial half-edge initialisation that only
sets up t1 and leaves the boundary half-edge slot unfilled.

Defect carrier: exactly one triangle (v0, v1, v2) with no other geometry. All
three edges have incidence count 1. The mesh is open on all sides.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me087",
             title="connectivity null triangle edge: single isolated triangle — all 3 edges are boundary (incidence 1)",
             defect_class="open_boundary")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)

# Single isolated triangle.
m.triangle(v0, v1, v2)

# All three edges are boundary edges — each incident on exactly 1 triangle.
# In MeshFix's half-edge structure, each edge needs pointers to both t1 and t2;
# here t2 for every edge is NULL → Branch 11 fires for all three.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# The full boundary cycle is the triangle's own perimeter.
m.assert_hole_boundary([v0, v1, v2])
