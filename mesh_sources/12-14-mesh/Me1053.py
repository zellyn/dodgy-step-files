"""Me1053 — merge_duplicate_polygons_in_polygon_soup early_exit_empty: tetrahedron-patch with no duplicates (Branch 4).

CGAL PMP `PMP.merge_duplicate_polygons_in_polygon_soup` Branch 4 (*early_exit_empty*) @ line 973:
  'if(all_duplicate_polygons.empty()) return 0;'
  — if the collection step finds no duplicate groups, the function immediately
  returns 0 without entering the removal loop.

Defect pattern: a clean 4-triangle polygon soup forming a partial tetrahedron patch
  where every triangle has a distinct vertex-index set. No pair of triangles shares
  its canonical vertex triple. The empty-check branch fires and the function returns
  immediately with 0.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,0,2), v3=(1,2,1).
  t0=(v0,v1,v2): base front, t1=(v0,v2,v3): left face, t2=(v1,v3,v2): right face,
  t3=(v0,v3,v1): back face. Each triangle has a unique vertex triple.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1053",
    title="merge_duplicate_polygons early_exit_empty: 4-triangle partial-tetrahedron soup with all-distinct vertex triples; returns 0 immediately (Branch 4)",
    defect_class="duplicate_triangles",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — origin corner
v1 = m.vertex(2.0, 0.0, 0.0)  # 1 — right base corner
v2 = m.vertex(1.0, 0.0, 2.0)  # 2 — front apex
v3 = m.vertex(1.0, 2.0, 1.0)  # 3 — top apex

t0 = m.triangle(v0, v1, v2)  # 0 — base-front face
t1 = m.triangle(v0, v2, v3)  # 1 — left side face (v2 shared with t0; triple differs)
t2 = m.triangle(v1, v3, v2)  # 2 — right side face (note v3 before v2 — distinct triple)
t3 = m.triangle(v0, v3, v1)  # 3 — back face (distinct triple)

# Verify distinct vertex sets (each edge should be shared by ≤2 faces, no repeated triples).
# Interior edges shared by 2 triangles in the tetrahedron.
m.assert_edge_shared(v0, v2, 2)  # shared by t0 and t1
m.assert_edge_shared(v2, v3, 2)  # shared by t1 and t2
m.assert_edge_shared(v1, v3, 2)  # shared by t2 and t3
m.assert_edge_shared(v0, v3, 2)  # shared by t1 and t3
m.assert_edge_shared(v0, v1, 2)  # shared by t0 and t3
m.assert_edge_shared(v1, v2, 2)  # shared by t0 and t2

# Closed tetrahedron surface: V=4, E=6, F=4, chi=2 (genus 0).
m.assert_euler_characteristic(4, 6, 4, 2)
