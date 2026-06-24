"""Me1151 — remove_a_border_edge simple: wrapper without state-tracking sets.

CGAL PMP `PMP.remove_a_border_edge` Branch 1 (*simple*) @ line 1263:
  'bool remove_a_border_edge(typename boost::graph_traits<PolygonMesh>::edge_descriptor ed,
   PolygonMesh& pmesh)' — the no-argument overload that delegates directly to
  the full form without passing any vertex-set or halfedge-set tracking
  arguments. This wrapper path fires whenever the caller does not need state
  tracking.

Defect pattern: a minimal open mesh with a clear border edge. Two triangles
  sharing one interior edge (v0,v2) give a quadrilateral boundary cycle with
  four border edges. Any of those border edges is a candidate for
  remove_a_border_edge; the simple (no-set) overload is exercised. After
  removal the two-triangle fan would collapse to a single triangle with a hole.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1.5,1,0)
  t0=(v0,v1,v2), t1=(v1,v3,v2) sharing interior edge (v1,v2).
  Border edges: (v0,v1), (v0,v2), (v3,v2), (v1,v3).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1151",
    title="remove_a_border_edge simple: border-edge removal without tracking sets; open mesh with 4 border edges",
    defect_class="open_boundary",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — base left
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — base right
v2 = m.vertex(0.5, 1.0, 0.0)  # 2 — apex left
v3 = m.vertex(1.5, 1.0, 0.0)  # 3 — apex right

# Two triangles sharing interior edge (v1, v2).
t0 = m.triangle(v0, v1, v2)  # 0: left triangle
t1 = m.triangle(v1, v3, v2)  # 1: right triangle

# Interior shared edge — incident on 2 triangles.
m.assert_edge_shared(v1, v2, 2)

# Four border edges — each incident on exactly 1 triangle.
m.assert_edge_shared(v0, v1, 1)  # t0 base
m.assert_edge_shared(v0, v2, 1)  # t0 left
m.assert_edge_shared(v2, v3, 1)  # t1 top
m.assert_edge_shared(v1, v3, 1)  # t1 right

# Euler: V=4, E=5, F=2, chi=1 (open disk topology).
m.assert_euler_characteristic(4, 5, 2, 1)
