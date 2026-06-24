"""Me831 — is_non_manifold_vertex null-face-multiplicity: bowtie vertex with two disconnected umbrella sectors, each contributing a null-face halfedge (Branch 2).

CGAL PMP `PMP.is_non_manifold_vertex` Branch 2 (*null-face-multiplicity*) @ line 71:
  'if(border_counter > 1) return true;'
  — after counting null-faced halfedges incident at vertex v, if the count exceeds
  one the vertex is declared non-manifold and the function returns true immediately.
  A bowtie (pinch point) is the canonical case: two triangle fans touch at v but are
  not connected by any shared edge, so each fan contributes at least one boundary
  halfedge → border_counter ≥ 2 → returns true.

Defect pattern: two triangles share only the apex vertex v0 (bowtie / pinch point).
  Fan A = t0 (upper triangle, v0 is one corner); Fan B = t1 (lower triangle, v0 is
  one corner). No edge is shared between the fans. Each fan has exactly two boundary
  halfedges incident at v0, giving border_counter = 4 (well above the >1 threshold).
  The function returns true → Branch 2 fires.

Geometry:
  v0=(0,0,0)  — bowtie hub (non-manifold vertex)
  v1=(1,1,0), v2=(-1,1,0)  — upper fan outer vertices
  v3=(1,-1,0), v4=(-1,-1,0)  — lower fan outer vertices
  t0=(v0,v1,v2), t1=(v0,v3,v4)
  All edges appear n=1 (no interior edge across fans).

Euler: V=5, E=6, F=2, chi=1 (two triangles touching at a point; χ = 5-6+2 = 1).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me831",
    title="is_non_manifold_vertex null-face-multiplicity: bowtie hub v0 shared by two disconnected fans; border_counter>1 fires (Branch 2)",
    defect_class="non_manifold_vertex",
)

v0 = m.vertex( 0.0,  0.0, 0.0)   # 0 — bowtie hub (non-manifold)
v1 = m.vertex( 1.0,  1.0, 0.0)   # 1 — upper-right
v2 = m.vertex(-1.0,  1.0, 0.0)   # 2 — upper-left
v3 = m.vertex( 1.0, -1.0, 0.0)   # 3 — lower-right
v4 = m.vertex(-1.0, -1.0, 0.0)   # 4 — lower-left

# Upper fan: single triangle — all three edges are boundary.
t0 = m.triangle(v0, v1, v2)

# Lower fan: single triangle — all three edges are boundary.
t1 = m.triangle(v0, v3, v4)

# All edges are boundary (no shared interior edge between fans).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v3, v4, 1)

# v0 has disconnected fan (two separate umbrella sectors meeting only at v0).
m.assert_vertex_fan_disconnected(v0)

# Euler: V=5, E=6, F=2, chi=5-6+2=1.
m.assert_euler_characteristic(5, 6, 2, 1)
