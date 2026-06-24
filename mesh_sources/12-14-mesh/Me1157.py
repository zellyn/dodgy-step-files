"""Me1157 — PMP.orient component_orientation_consistency: open-boundary mesh skipped
  by orient; is_closed returns false (Branch 3).

CGAL PMP `PMP.orient` Branch 3 (*component_orientation_consistency*) @ line 410:
  'if(!PMP::is_closed(mesh)) { skip_component(); continue; }' —
  orient only processes closed components. If a connected component has boundary
  edges (is not a closed manifold), orient cannot assign a consistent outward
  orientation (no well-defined inside/outside) and skips it. Branch 3 fires
  when is_closed returns false for a component.

Defect pattern: an open mesh (a flat triangulated patch with boundary edges).
  A two-triangle open strip — topologically a disk with boundary. orient
  evaluates is_closed for the component, finds boundary halfedges, and skips
  the component. The mesh retains its original winding unchanged.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1.5,1,0)
  t0=(v0,v1,v2), t1=(v1,v3,v2)
  One shared interior edge (v1,v2) n=2; four boundary edges n=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1157",
    title="PMP.orient component_orientation_consistency: open strip with 4 boundary edges; is_closed=false; component skipped by orient (Branch 3)",
    defect_class="inverted_normals",
)

v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — front-left
v1 = m.vertex(1.0,  0.0,  0.0)   # 1 — front-right / shared edge endpoint
v2 = m.vertex(0.5,  1.0,  0.0)   # 2 — back-left / shared edge endpoint
v3 = m.vertex(1.5,  1.0,  0.0)   # 3 — back-right

t0 = m.triangle(v0, v1, v2)  # 0: left triangle
t1 = m.triangle(v1, v3, v2)  # 1: right triangle

# Interior shared edge — forms the hinge between the two triangles.
m.assert_edge_shared(v1, v2, 2)

# Boundary edges — the open perimeter means is_closed = false.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Open manifold with boundary: V=4, E=5, F=2, chi=1.
m.assert_euler_characteristic(4, 5, 2, 1)
