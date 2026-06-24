"""Me1170 — fill_edge_map edge_recording: polygon edges inserted into edge map;
  two-triangle manifold soup fires the per-edge record insertion (Branch 1).

CGAL PMP `PMP.Polygon_soup_orienter.fill_edge_map` Branch 1 (*edge_recording*)
  @ line 182:
  'edges[i0][i1].insert(polygon_id)' —
  For each directed edge of each polygon, its polygon id is inserted into the
  nested map keyed by (i0, i1). This fires for every edge of every polygon in
  the soup. Branch 1 is the fundamental edge-recording step.

Defect pattern: a minimal two-triangle manifold polygon soup — two CCW-oriented
  triangles sharing an interior edge. The fill_edge_map function is called as
  the first step of orienting the polygon soup. For each of the 5 directed
  edges, edges[i0][i1].insert(polygon_id) is called (Branch 1 fires for each).
  The shared edge (v1,v2) appears once as (1,2) in t0 and once as (2,1) in t1
  — these are different directed edges so each inserts separately. The
  non-manifold check (Branch 2) does NOT fire because each directed edge has
  exactly 1 polygon (nb_edges==1 for each directed edge).

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0): left triangle t0
  v3=(1.5,1,0): right outer vertex for t1
  t0=(v0,v1,v2), t1=(v2,v1,v3)   — CCW, shared edge v1-v2
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1170",
    title="fill_edge_map edge_recording: per-edge insertion into polygon map; two-triangle manifold soup (Branch 1)",
    defect_class="non_manifold_edge",
)

# Four vertices: two triangles sharing edge v1-v2
v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — left base
v1 = m.vertex(1.0,  0.0,  0.0)   # 1 — shared base right
v2 = m.vertex(0.5,  1.0,  0.0)   # 2 — shared apex
v3 = m.vertex(1.5,  1.0,  0.0)   # 3 — right outer

# Two CCW triangles sharing the interior edge v1-v2
t0 = m.triangle(v0, v1, v2)  # 0: left triangle
t1 = m.triangle(v2, v1, v3)  # 1: right triangle (shares v1-v2, reversed)

# Shared interior edge: appears in t0 as (v1,v2) and in t1 as (v2,v1)
# — two directed edges, each with nb_edges==1, so no non-manifold detection
m.assert_edge_shared(v1, v2, 2)  # undirected edge shared by 2 triangles (manifold)

# Boundary edges (each belongs to 1 triangle only)
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# V=4, E=5, F=2, chi=1 (open manifold strip)
m.assert_euler_characteristic(4, 5, 2, 1)
