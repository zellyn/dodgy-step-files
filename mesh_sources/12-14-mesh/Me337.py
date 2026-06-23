"""Me337 — pinch_cascade_v2: after merge, v2 still has non-manifold edges — recursive pinch(e_2, true).

MeshFix `Basic_TMesh.pinch` Branch 8 (*CASCADE_PINCH_NEEDED_V2*) @ line 974:
  'if (e_2 != NULL) pinch(e_2, true);'
  Mirror of Branch 7, but at the v2 endpoint of e1. After the primary merge,
  v2 is checked for remaining cached non-manifold edges. If e_2 != NULL, a
  second recursive pinch(e_2, true) is dispatched to resolve the cascade
  at v2.

Defect pattern: multi-level non-manifold at vertex v1 (v2 in the algorithm).
  The primary pinch resolves the defect at v0, but v1 remains non-manifold
  because it connects to a third disconnected fan sector. The cascade fires
  to clean up v1.

Geometry: edge (v0,v1) is the primary pinch edge. After merging, v1 still
  has a second disconnected fan sector (fan B).

  v0=(0,0,0), v1=(2,0,0): primary pinch edge endpoints.
  Fan A: t0=(v0,v1,v2), t1=(v0,v1,v3) — edge (v0,v1) n=2 shared interior.
         Wait — these two triangles already make (v0,v1) n=2 (manifold).
         The cascade is at v1 which has an extra disconnected fan.

  More precisely: v1 is a bowtie vertex in addition to being part of the
  primary edge. Two fans at v1:
    Fan X: t0=(v0,v1,v2), t1=(v1,v3,v4) — connected through v1 but no shared edge.
    Fan Y: t2=(v1,v5,v6) — additional disconnected sector at v1.

  The disconnect at v1 spans fan X and fan Y.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me337",
             title="pinch_cascade_v2: v2 still non-manifold after primary merge — recursive pinch(e_2,true) fires",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0,  0.0, 0.0)   # 0
v1 = m.vertex(2.0,  0.0, 0.0)   # 1 — cascade vertex (v2 in algorithm)
v2 = m.vertex(1.0,  1.0, 0.0)   # 2
v3 = m.vertex(3.0,  1.0, 0.0)   # 3
v4 = m.vertex(3.0, -1.0, 0.0)   # 4
v5 = m.vertex(2.0, -1.5, 0.0)   # 5
v6 = m.vertex(1.0, -1.5, 0.0)   # 6

# Fan X at v1: t0 and t1 share v1 but no edge through v1.
t0 = m.triangle(v0, v1, v2)   # 0 — includes v1
t1 = m.triangle(v1, v3, v4)   # 1 — includes v1, disconnected sector from t0

# Fan Y at v1: t2 is a third sector at v1.
t2 = m.triangle(v1, v5, v6)   # 2 — additional disconnected sector at v1

# v1 is a bowtie / non-manifold vertex with 3 disconnected fan sectors.
m.assert_vertex_fan_disconnected(v1)

# All triangles are disconnected from each other (no shared edges).
m.assert_triangle_not_reachable_from(t1, t0)
m.assert_triangle_not_reachable_from(t2, t0)
m.assert_triangle_not_reachable_from(t2, t1)

# All edges are boundary.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v4, 1)
m.assert_edge_shared(v1, v5, 1)
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v1, v6, 1)
