"""Me944 — orient_polygon_soup manifoldness_check: return initial_nb_pts==points.size().

CGAL PMP `PMP.orient_polygon_soup` Branch 5 (*manifoldness_check*) @ line 563:
  'return initial_nb_pts == points.size();'
  — the final statement of orient_polygon_soup. It returns true if the number of
  points is unchanged from the start (no duplication was needed → input was already
  manifold at every vertex), or false if new points were added by
  duplicate_singular_vertices (input had non-manifold vertices).

Defect pattern: a clean, manifold, consistently-oriented three-triangle strip.
  Every vertex has a connected fan and the winding is uniform (all CCW). After
  orient_polygon_soup completes: fill_edge_map() records all shared edges,
  orient() finds no inconsistencies (nothing to flip), duplicate_singular_vertices()
  finds no singular vertices (nothing to add). points.size() == initial_nb_pts →
  the function returns true. Branch 5 fires on any manifold input.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(0.5,1,0), v4=(1.5,1,0)
  t0=(v0,v1,v3), t1=(v1,v4,v3), t2=(v1,v2,v4)  — three CCW triangles.
  Shared edges: (v1,v3)n=2, (v1,v4)n=2. All vertices have connected fans.
  No duplication needed → initial_nb_pts==5==points.size() → returns true.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me944",
    title="orient_polygon_soup manifoldness_check: clean 3-triangle manifold strip; initial_nb_pts==points.size()==5 → returns true (Branch 5)",
    defect_class="inconsistent_face_orientation",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left base
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — center base (shared by all three triangles)
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — right base
v3 = m.vertex(0.5, 1.0, 0.0)   # 3 — left apex
v4 = m.vertex(1.5, 1.0, 0.0)   # 4 — right apex

# Three CCW triangles forming a connected, manifold strip.
t0 = m.triangle(v0, v1, v3)    # 0: left triangle, normal +Z (CCW)
t1 = m.triangle(v1, v4, v3)    # 1: center triangle, normal +Z (CCW)
t2 = m.triangle(v1, v2, v4)    # 2: right triangle, normal +Z (CCW)

# Shared interior edges — n=2; fill_edge_map() records both.
m.assert_edge_shared(v1, v3, 2)   # t0 ∩ t1
m.assert_edge_shared(v1, v4, 2)   # t1 ∩ t2

# Boundary edges — n=1 each.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v4, 1)

# All triangles consistently wound CCW — orient() makes no changes.
# No bowtie vertices — duplicate_singular_vertices() makes no changes.
# Euler: V=5, E=7, F=3, chi=1 (open disk).
m.assert_euler_characteristic(5, 7, 3, 1)
