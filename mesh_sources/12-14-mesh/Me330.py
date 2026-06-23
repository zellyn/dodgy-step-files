"""Me330 — pinch_missing_info_field: non-manifold edge has no cached singular-edge info list.

MeshFix `Basic_TMesh.pinch` Branch 1 (*MISSING_INFO_FIELD*) @ line 921:
  'List *ee = (List *)e1->info; if (ee == NULL) return false;'
  The pinch operation starts by reading the cached singular-edge-list from
  e1->info. If info is NULL (no grouping list was attached during the
  cutAndStitch phase), pinch cannot proceed and immediately returns false.

Defect pattern: a non-manifold edge shared by 3 triangles, representing
the state where the edge has been identified as singular but has not yet
had a grouping List cached in its info field. The edge is incident on 3
triangles — a structural non-manifold state — but the algorithm has no
cached metadata to drive the pinch split.

Geometry: T-junction non-manifold. Edge (v0,v1) shared by 3 triangles.
  t0=(v0,v1,v2): base triangle above.
  t1=(v0,v1,v3): base triangle below.
  t2=(v0,v1,v4): third fan triangle through the shared edge.

  v0=(0,0,0), v1=(1,0,0), v2=(0.5, 1,0), v3=(0.5,-1,0), v4=(0.5,0,1)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me330",
             title="pinch_missing_info_field: non-manifold edge (3 triangles) — info list NULL, pinch returns false",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(0.5, -1.0, 0.0)  # 3
v4 = m.vertex(0.5, 0.0, 1.0)   # 4

t0 = m.triangle(v0, v1, v2)  # 0
t1 = m.triangle(v0, v1, v3)  # 1
t2 = m.triangle(v0, v1, v4)  # 2

# The shared edge (v0,v1) is incident on 3 triangles — the singular non-manifold edge.
# Branch 1 fires when this edge's info field is NULL.
m.assert_edge_shared(v0, v1, 3)

# Other edges are boundary (each triangle has two more edges, all n=1).
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v1, v4, 1)
