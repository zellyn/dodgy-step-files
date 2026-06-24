"""Me630 — Basic_TMesh.growSelection branch 1: selected_triangle_vertex_mark.

MeshFix `Basic_TMesh.growSelection` Branch 1 (*selected_triangle_vertex_mark*)
@ line 697:
  'if (IS_VISITED(t)) { MARK_VISIT(v1); MARK_VISIT(v2); MARK_VISIT(v3); }'
  — the first pass iterates all triangles; when a triangle is already
  selected (IS_VISITED), all three of its vertices are marked as VISITED
  so the second pass can propagate the selection outward to unselected
  neighbor triangles.

Defect pattern: a 4-triangle fan sharing a central interior vertex (v0).
  Triangle t0 is pre-selected; t1, t2, t3 are unselected neighbors sharing
  edges or vertices with t0. growSelection first marks v0, v1, v2 (t0's
  vertices) because IS_VISITED(t0) is true → Branch 1 fires.
  The mesh is also non-manifold in intent: the shared central vertex v0
  appears in all four triangles; edge (v0,v1) is shared by t0 and t1.

Geometry:
  v0=(0,0,0) central vertex shared by all 4 triangles
  v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0), v4=(0,-1,0) outer rim
  t0=(v0,v1,v2) — pre-selected triangle (Branch 1 subject)
  t1=(v0,v2,v3) — unselected neighbor sharing edge (v0,v2)
  t2=(v0,v3,v4) — unselected neighbor sharing edge (v0,v3)
  t3=(v0,v4,v1) — unselected neighbor sharing edge (v0,v4)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me630",
    title="growSelection selected_triangle_vertex_mark: IS_VISITED(t0) marks v0,v1,v2; 4-triangle fan with shared interior vertex (Branch 1)",
    defect_class="non_manifold_edge",
)

v0 = m.vertex(0.0,  0.0, 0.0)  # 0 — central vertex shared by all 4 triangles
v1 = m.vertex(1.0,  0.0, 0.0)  # 1 — outer rim E
v2 = m.vertex(0.0,  1.0, 0.0)  # 2 — outer rim N
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3 — outer rim W
v4 = m.vertex(0.0, -1.0, 0.0)  # 4 — outer rim S

# Pre-selected triangle (Branch 1 subject).
t0 = m.triangle(v0, v1, v2)  # 0: selected — IS_VISITED(t0) → mark v0,v1,v2

# Unselected neighbors sharing edges with t0.
t1 = m.triangle(v0, v2, v3)  # 1: shares edge (v0,v2) with t0
t2 = m.triangle(v0, v3, v4)  # 2: shares edge (v0,v3) with t1
t3 = m.triangle(v0, v4, v1)  # 3: shares edge (v0,v4) with t2; shares edge (v0,v1) with t0

# Interior edges shared by exactly 2 triangles (manifold-fan topology).
m.assert_edge_shared(v0, v1, 2)  # t0 and t3
m.assert_edge_shared(v0, v2, 2)  # t0 and t1
m.assert_edge_shared(v0, v3, 2)  # t1 and t2
m.assert_edge_shared(v0, v4, 2)  # t2 and t3

# Boundary edges of the fan (each owned by exactly 1 triangle).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v1, 1)

# Central vertex v0 is an interior (fan) vertex appearing in all 4 triangles.
# vertex_pair_distance_lt is not applicable here; use euler for sanity.
# Euler: V=5, E=8, F=4, chi=1 (open disk).
m.assert_euler_characteristic(5, 8, 4, 1)
