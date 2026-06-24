"""Me664 — merge_duplicate_points_in_polygon_soup polygon_remap: polygon[i]=point_index[polygon[i]]; duplicate vertices remapped in every polygon referencing them (Branch 5).

CGAL PMP `PMP.merge_duplicate_points_in_polygon_soup` Branch 5 (*polygon_remap*) @ line 565:
  'for(P_ID polygon_index=0; polygon_index<polygons.size(); ++polygon_index)
   { auto& polygon = polygons[polygon_index];
     for(std::size_t i=0; i<polygon.size(); ++i)
       polygon[i] = point_index[polygon[i]]; }'
  — After confirming that duplicates exist (Branch 4), the algorithm
  iterates every polygon and every vertex index within it, replacing each
  original index with the canonical unique-point index from point_index[].
  Two polygons that previously referenced separate-but-coincident vertices
  are rewritten to share a single vertex index, merging them topologically.

Defect pattern: four triangles arranged so that two coincident vertices
  w1 and w4 (both at (1,0,0)) are referenced by different triangles.
  After deduplication scan: point_index[1]=1 (w1 canonical),
  point_index[4]=1 (w4 remapped to w1's id). The remap loop rewrites
  every polygon's vertex indices, converting references to w4 into w1.

Geometry:
  w0=(0,0,0), w1=(1,0,0), w2=(0.5,1,0), w3=(1.5,1,0),
  w4=(1,0,0) [coincident with w1], w5=(2,0,0)
  t0=(w0,w1,w2), t1=(w1,w3,w2) sharing (w1,w2)
  t2=(w4,w5,w3), t3=(w4,w3,w2) sharing (w3,w2) and (w4,w3)

  Sharing: (w1,w2) in t0,t1 → n=2; (w2,w3) in t1,t3 → n=2;
           (w3,w4) in t2,t3 → n=2.
  After remap, w4 becomes w1; polygon t3 referencing w4 → w1;
  polygon t2 referencing w4 → w1. Polygon remap fires for t2 and t3.
  Euler: V=6, E=9, F=4, chi=1 (open disk).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me664",
    title="merge_duplicate_points_in_polygon_soup polygon_remap: w1==w4 at (1,0,0); point_index[4] remapped to 1; polygon[i]=point_index[polygon[i]] rewrites t2 and t3 (Branch 5)",
    defect_class="near_coincident_vertex",
)

w0 = m.vertex(0.0, 0.0, 0.0)  # 0
w1 = m.vertex(1.0, 0.0, 0.0)  # 1 — canonical; coincident with w4
w2 = m.vertex(0.5, 1.0, 0.0)  # 2 — shared apex
w3 = m.vertex(1.5, 1.0, 0.0)  # 3 — upper right
w4 = m.vertex(1.0, 0.0, 0.0)  # 4 — coincident with w1; will be remapped to index 1
w5 = m.vertex(2.0, 0.0, 0.0)  # 5 — far right

# Four triangles.
t0 = m.triangle(w0, w1, w2)  # 0: left-bottom
t1 = m.triangle(w1, w3, w2)  # 1: left-top  (shares (w1,w2) with t0)
t2 = m.triangle(w4, w5, w3)  # 2: right-bottom (w4 will be remapped to w1)
t3 = m.triangle(w4, w3, w2)  # 3: right-middle (w4 remapped; shares (w3,w2) with t1)

# Interior shared edges (n=2).
m.assert_edge_shared(w1, w2, 2)   # t0 and t1
m.assert_edge_shared(w2, w3, 2)   # t1 and t3
m.assert_edge_shared(w3, w4, 2)   # t2 and t3

# Boundary edges (n=1).
m.assert_edge_shared(w0, w1, 1)   # t0 bottom-left
m.assert_edge_shared(w0, w2, 1)   # t0 left
m.assert_edge_shared(w1, w3, 1)   # t1 top (before remap w1 stays w1)
m.assert_edge_shared(w3, w5, 1)   # t2 right
m.assert_edge_shared(w4, w5, 1)   # t2 bottom
m.assert_edge_shared(w2, w4, 1)   # t3 left (before remap)

# w1 and w4 are coincident; point_index[4] == point_index[1].
# polygon_remap rewrites indices in t2 and t3 to unify them.
m.assert_vertex_pair_distance_lt(w1, w4, 1e-9)
m.assert_vertex_pair_no_shared_triangle(w1, w4)

# Euler: V=6, E=9, F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
