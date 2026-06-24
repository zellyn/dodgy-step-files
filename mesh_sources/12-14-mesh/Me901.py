"""Me901 — orient_triangle_soup_with_reference_triangle_soup closest_face_search: closest_point_and_primitive finds nearest non-degenerate reference face (Branch 2).

CGAL PMP `PMP.orient_triangle_soup_with_reference_triangle_soup` Branch 2
(*closest_face_search*) @ line 175:
  'auto [closest_point, closest_prim] = tree.closest_point_and_primitive(centroid);'
  — for each non-degenerate reference triangle the algorithm computes the centroid
  of the query face and finds the closest reference face using an AABB tree.
  Branch 2 fires when a valid primitive is returned (the tree is non-empty and
  at least one reference triangle is non-degenerate).

Defect pattern: three distinct non-degenerate query triangles arranged in a fan
  from a central hub. Three non-degenerate reference triangles are placed directly
  below (z=-1) with clear spatial separation so each query face has an unambiguous
  nearest reference face. The centroid-to-reference AABB lookup returns a valid
  primitive for each query triangle → Branch 2 fires for each.

Geometry (query mesh):
  hub=(0,0,0), a=(2,0,0), b=(-1,1.7,0), c=(-1,-1.7,0)
  t0=(hub,a,b)   — sector 0
  t1=(hub,b,c)   — sector 1
  t2=(hub,c,a)   — sector 2
  Interior edges (hub shared, 3 pairs each n=2). Boundary: a-b, b-c, c-a (n=1).

Reference soup (z=-1 plane, clear 1-to-1 proximity):
  r_hub=(0,0,-1), r_a=(2,0,-1), r_b=(-1,1.7,-1), r_c=(-1,-1.7,-1)
  ref_t0=(r_hub,r_a,r_b)   — near t0
  ref_t1=(r_hub,r_b,r_c)   — near t1
  ref_t2=(r_hub,r_c,r_a)   — near t2
  All reference triangles non-degenerate (positive area); each centroid of a query
  face maps closest to the corresponding reference face.

Assertion evidence:
  - edge_shared_by_n_triangles for interior hub-spoke edges (n=2): confirms
    connected fan structure → centroids are geometrically distinct.
  - adjacent_triangles_inconsistent_winding absent: all query triangles share the
    same CCW winding; no orientation conflict within the query mesh.
  - Euler for query fan: V=4, E=6, F=3, chi=1 (open disk).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me901",
    title="orient_triangle_soup_with_reference_triangle_soup closest_face_search: three-sector fan; AABB closest_point_and_primitive returns valid reference face for each query centroid (Branch 2)",
    defect_class="inverted_normal",
)

# --- Query mesh vertices (z=0 plane) ---
hub = m.vertex(0.0,  0.0,   0.0)  # 0 — fan hub
a   = m.vertex(2.0,  0.0,   0.0)  # 1
b   = m.vertex(-1.0, 1.732, 0.0)  # 2  ≈ 120° from a
c   = m.vertex(-1.0,-1.732, 0.0)  # 3  ≈ 240° from a

# --- Reference soup vertices (z=-1 plane) ---
r_hub = m.vertex(0.0,  0.0,   -1.0)  # 4
r_a   = m.vertex(2.0,  0.0,   -1.0)  # 5
r_b   = m.vertex(-1.0, 1.732, -1.0)  # 6
r_c   = m.vertex(-1.0,-1.732, -1.0)  # 7

# --- Query triangles (CCW viewed from +Z) ---
t0 = m.triangle(hub, a, b)   # 0: sector 0
t1 = m.triangle(hub, b, c)   # 1: sector 1
t2 = m.triangle(hub, c, a)   # 2: sector 2

# --- Reference triangles (CCW viewed from +Z, matching query orientation) ---
ref_t0 = m.triangle(r_hub, r_a, r_b)   # 3: near query t0
ref_t1 = m.triangle(r_hub, r_b, r_c)   # 4: near query t1
ref_t2 = m.triangle(r_hub, r_c, r_a)   # 5: near query t2

# Interior edges of the fan (shared by 2 query triangles).
m.assert_edge_shared(hub, a, 2)   # t0 and t2
m.assert_edge_shared(hub, b, 2)   # t0 and t1
m.assert_edge_shared(hub, c, 2)   # t1 and t2

# Boundary edges of the fan (n=1 each).
m.assert_edge_shared(a, b, 1)   # t0 outer edge
m.assert_edge_shared(b, c, 1)   # t1 outer edge
m.assert_edge_shared(c, a, 1)   # t2 outer edge

# Euler for query mesh (only): V=4, E=6, F=3, chi=1 (open disk / triangle fan).
m.assert_euler_characteristic(4, 6, 3, 1)
