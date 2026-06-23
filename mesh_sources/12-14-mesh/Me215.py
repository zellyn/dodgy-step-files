"""Me215 — cutAndStitch_group_coincident_edges: new grouping list created for distinct edge.

MeshFix `Basic_TMesh.cutAndStitch` Branch 6 (*GROUP_COINCIDENT_EDGES*) @ line 1011:
  'if (e2 == NULL || lexEdgeCompare(e1, e2) != 0) { e1->info = new List(); e2 = e1; }'
  When iterating the sorted singular_edges list, each time an edge is
  lexicographically different from the previous anchor e2 (or when e2 is NULL
  for the first edge), a new grouping List is allocated in e1->info and e1
  becomes the new anchor. Edges with the same coordinate get appended to
  the same group.

Defect pattern: three boundary patches whose seam edges fall at three distinct
lexicographic positions — each will start a new group. The geometry shows
three unconnected boundary edges that could not be sorted into a single group
because their endpoint coordinates differ.

Geometry: three single-triangle patches with boundary edges at distinct positions.
  Patch A: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0); boundary edge (v0,v1)
  Patch B: v3=(2,0,0), v4=(3,0,0), v5=(2.5,1,0); boundary edge (v3,v4)
  Patch C: v6=(4,0,0), v7=(5,0,0), v8=(4.5,1,0); boundary edge (v6,v7)
  All three boundary edges are lexicographically distinct → each creates a
  new group in Branch 6.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me215",
             title="cutAndStitch_group_coincident_edges: three distinct boundary edges each start a new group",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)    # 0
v1 = m.vertex(1.0, 0.0, 0.0)    # 1
v2 = m.vertex(0.5, 1.0, 0.0)    # 2

v3 = m.vertex(2.0, 0.0, 0.0)    # 3
v4 = m.vertex(3.0, 0.0, 0.0)    # 4
v5 = m.vertex(2.5, 1.0, 0.0)    # 5

v6 = m.vertex(4.0, 0.0, 0.0)    # 6
v7 = m.vertex(5.0, 0.0, 0.0)    # 7
v8 = m.vertex(4.5, 1.0, 0.0)    # 8

t0 = m.triangle(v0, v1, v2)    # 0 — patch A
t1 = m.triangle(v3, v4, v5)    # 1 — patch B
t2 = m.triangle(v6, v7, v8)    # 2 — patch C

# Each patch is a disconnected component: t0 unreachable from t1.
m.assert_triangle_not_reachable_from(t1, t0)
m.assert_triangle_not_reachable_from(t2, t0)

# All edges are boundary (each triangle is isolated).
m.assert_edge_shared(v0, v1, 1)   # patch A bottom — group A anchor
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

m.assert_edge_shared(v3, v4, 1)   # patch B bottom — group B anchor
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)

m.assert_edge_shared(v6, v7, 1)   # patch C bottom — group C anchor
m.assert_edge_shared(v7, v8, 1)
m.assert_edge_shared(v6, v8, 1)
