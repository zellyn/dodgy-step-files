"""Me151 — flipNormals_neighbor_enqueue_t1: t1 neighbor enqueued during winding propagation.

MeshFix `Basic_TMesh.flipNormals` Branch 2 (*neighbor_enqueue_t1*) @ line 1652:
  't1 != NULL && !IS_BIT(t1,6)' — after flipping the seed triangle, its t1
  neighbor exists and has not yet been flipped. flipNormals enqueues t1 for
  propagation. Branch 2 fires specifically for the t1 adjacency slot.

Geometric signature: two adjacent CW triangles sharing an edge via the t1 slot.
The seed triangle (t0) has a CW normal (-Z). When flipNormals inverts t0, it
discovers t1 (the adjacent triangle through edge e1/t1 slot) is also CW and
unflipped, so it enqueues t1 for flipping.

In MeshFix, t1 is the triangle adjacent across edge e1 (the edge opposite vertex 2
in the half-edge representation). We model this as two triangles sharing edge (v0,v1)
where the triangle across that shared edge corresponds to the t1 adjacency.

Geometry (z=0):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0.5,-1,0)
  t0=(v0, v2, v1)  — CW, normal -Z (seed)
  t1=(v0, v1, v3)  — CW, normal -Z (t1 neighbor, across edge v0-v1)

Both triangles have inverted winding; flipNormals propagates from t0 to t1 via
the t1-neighbor slot (Branch 2 fire) and inverts both.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me151",
             title="flipNormals_neighbor_enqueue_t1: t1 neighbor CW, enqueued for flip propagation",
             defect_class="inverted_normals")

v0 = m.vertex(0.0,  0.0, 0.0)   # 0
v1 = m.vertex(1.0,  0.0, 0.0)   # 1
v2 = m.vertex(0.5,  1.0, 0.0)   # 2  — above the shared edge
v3 = m.vertex(0.5, -1.0, 0.0)   # 3  — below the shared edge

# t0: CW → normal -Z.  (v2-v0)×(v1-v0) = (0.5,1,0)×(1,0,0) = (0,0,-0.5) → -Z
t0 = m.triangle(v0, v2, v1)

# t1: CW → normal -Z.  (v1-v0)×(v3-v0) = (1,0,0)×(0.5,-1,0) = (0,0,-1) → -Z
t1 = m.triangle(v0, v1, v3)

# Both normals are inverted (-Z); they also point in the same direction which is
# inconsistent for adjacent triangles in a correctly-oriented mesh (neighbors
# should have anti-parallel normals across a shared edge in the original problem).
m.assert_triangle_normal_z_negative(t0)
m.assert_triangle_normal_z_negative(t1)

# Shared edge (v0,v1) is interior — incident on exactly 2 triangles.
m.assert_edge_shared(v0, v1, 2)
# Boundary edges appear once.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
