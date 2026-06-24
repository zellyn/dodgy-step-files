"""Me841 — duplicate_non_manifold_vertices vertex-occurrence-detection: visited_vertices null_h; same vertex re-encountered across half-cycle (Branch 2).

CGAL PMP `PMP.duplicate_non_manifold_vertices` Branch 2 (*vertex-occurrence-detection*) @ line 342:
  'if(visited_vertices.count(v)) { ... null_h ... }'
  — while traversing halfedge cycles around a non-manifold vertex, the function
  records each encountered vertex in visited_vertices. When a vertex already in
  the set is encountered again from a *different* half-cycle, null_h is used as a
  sentinel to indicate a new duplication event must be created.

Defect pattern: multi-sector pinch vertex hub appearing in three disconnected
  triangle sectors. As CGAL iterates the first sector's halfedge ring, it records
  hub in visited_vertices. When it advances to the second or third sector and
  encounters hub again, visited_vertices.count(hub) > 0 → Branch 2 fires.
  This is distinct from Branch 1 (which guards halfedge re-visitation): here the
  guard is on the vertex itself being seen in a second cycle.

Geometry:
  hub=(0,0,0): pinch vertex shared by three disconnected fans.
  Fan A (right): a0=(2,0,0), a1=(1,1,0)  → t0=(hub,a0,a1) [single triangle]
  Fan B (top): b0=(0,2,0), b1=(-1,1,0)   → t1=(hub,b0,b1) [single triangle]
  Fan C (bottom): c0=(0,-2,0), c1=(1,-1,0) → t2=(hub,c0,c1) [single triangle]
  Each sector is a single triangle sharing only hub.
  No edges between fans except through hub vertex.
  V=7, E=6 (each triangle has 3 boundary edges; hub edges: hub-a0,hub-a1 in t0;
             hub-b0,hub-b1 in t1; hub-c0,hub-c1 in t2; 6 hub-incident edges total).
  All edges n=1 (boundary). E=9 (3 triangles × 3 edges, none shared). F=3.
  chi = V - E + F = 7 - 9 + 3 = 1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me841",
    title="duplicate_non_manifold_vertices vertex-occurrence-detection: three-sector pinch hub re-encountered in visited_vertices across half-cycles; null_h sentinel fires (Branch 2)",
    defect_class="non_manifold_vertex",
)

hub = m.vertex(0.0,  0.0, 0.0)   # 0 — three-sector pinch hub

# Fan A: single triangle, right sector.
a0 = m.vertex(2.0,  0.0, 0.0)    # 1
a1 = m.vertex(1.0,  1.0, 0.0)    # 2

# Fan B: single triangle, top sector.
b0 = m.vertex(0.0,  2.0, 0.0)    # 3
b1 = m.vertex(-1.0, 1.0, 0.0)    # 4

# Fan C: single triangle, bottom sector.
c0 = m.vertex(0.0, -2.0, 0.0)    # 5
c1 = m.vertex(1.0, -1.0, 0.0)    # 6

# Each fan is a single triangle — no shared interior edges.
t0 = m.triangle(hub, a0, a1)     # 0: Fan A
t1 = m.triangle(hub, b0, b1)     # 1: Fan B
t2 = m.triangle(hub, c0, c1)     # 2: Fan C

# All 9 edges are boundary (n=1): three triangles with no shared edges.
m.assert_edge_shared(hub, a0, 1)
m.assert_edge_shared(a0,  a1, 1)
m.assert_edge_shared(hub, a1, 1)

m.assert_edge_shared(hub, b0, 1)
m.assert_edge_shared(b0,  b1, 1)
m.assert_edge_shared(hub, b1, 1)

m.assert_edge_shared(hub, c0, 1)
m.assert_edge_shared(c0,  c1, 1)
m.assert_edge_shared(hub, c1, 1)

# Hub vertex fan is disconnected across three sectors.
# First sector (Fan A): hub recorded in visited_vertices.
# Second sector (Fan B): visited_vertices.count(hub) > 0 → Branch 2 fires (null_h).
# Third sector (Fan C): same Branch 2 path, second re-encounter.
m.assert_vertex_fan_disconnected(hub)

# Euler: V=7, E=9, F=3, chi=1.
m.assert_euler_characteristic(7, 9, 3, 1)
