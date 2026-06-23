"""Me345 — init_edge_triangle_reference_link: edge t1/t2 pointers set to copied triangles.

MeshFix `Basic_TMesh.init` Branch 6 (*EDGE_TRIANGLE_REFERENCE_LINK*) @ line 210:
  '((Edge *)e->info)->t1 = (e->t1)' — for each edge in the source, the clone edge's
  t1 and t2 triangle pointers are set to the corresponding cloned triangles. When a
  boundary edge (open mesh) has t2 == NULL (no second triangle), the clone edge's t2
  is also set to NULL. This branch exercises the half-edge bookkeeping that init must
  reconstruct faithfully.

Defect pattern: an open-boundary mesh (triangulated flat strip with boundary edges).
  Each boundary edge has exactly 1 incident triangle; the init loop must correctly
  reconstruct the t1/t2 pair for each clone edge: interior edges get two clone triangles;
  boundary edges get one clone triangle + NULL.

Geometry: two adjacent triangles sharing edge (v1,v2) — a simple quad split.
  v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0).
  t0=(v0,v1,v2), t1=(v0,v2,v3).
  Interior edge (v0,v2) incident on 2 triangles; all other edges are boundary (n=1).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me345",
             title="init_edge_triangle_reference_link: open-boundary mesh forces clone edge t1=non-NULL t2=NULL on boundary edges",
             defect_class="hole_in_hull")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v0, v2, v3)   # 1

# Interior (shared) edge — init sets both t1 and t2 on the clone edge.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges — init sets t1 to the clone triangle and leaves t2 NULL.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# The four boundary edges form the hole boundary.
m.assert_hole_boundary([v0, v1, v2, v3])

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
