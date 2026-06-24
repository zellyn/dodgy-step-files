"""Me890 — merge_duplicated_vertices_in_boundary_cycles boundary_cycle_discovery: open mesh; extract_boundary_cycles populates cycles vector (Branch 1).

CGAL PMP `PMP.merge_duplicated_vertices_in_boundary_cycles` Branch 1 (*boundary_cycle_discovery*) @ line 351:
  'extract_boundary_cycles(pm, std::back_inserter(cycles));'
  — the multi-cycle dispatcher starts by calling extract_boundary_cycles,
  which discovers all open boundary loops in the mesh and inserts one
  representative halfedge per cycle into the ``cycles`` vector. Branch 1
  fires for any mesh with at least one open boundary (non-empty cycles).

Defect pattern: four triangles forming an open disk (diamond shape) with
  one boundary cycle. Two boundary vertices v1 and v3 share identical
  coordinates (2.0, 0.0, 0.0) but are topologically distinct — a classic
  coincident-boundary-vertex defect. extract_boundary_cycles traverses the
  boundary loop and inserts its representative halfedge into cycles →
  Branch 1 fires.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(2,0,0) [=v1], v4=(3,1,0), v5=(2,2,0)
  Boundary cycle: v0 → v1 → v2 → v3 → v4 → v5 → v0 (six boundary edges).
  v1 and v3 at identical coordinates — the merge target.
  Interior edges: (v0,v2) n=2, (v2,v3) n=2, (v2,v4) n=2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me890",
    title="merge_duplicated_vertices_in_boundary_cycles boundary_cycle_discovery: open mesh; extract_boundary_cycles finds 1 boundary cycle; coincident v1==v3 at (2,0,0) (Branch 1)",
    defect_class="near_coincident_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left corner
v1 = m.vertex(2.0, 0.0, 0.0)  # 1 — bottom-right boundary, coincident with v3
v2 = m.vertex(1.0, 1.0, 0.0)  # 2 — center-left interior
v3 = m.vertex(2.0, 0.0, 0.0)  # 3 — bottom-right boundary, coincident with v1
v4 = m.vertex(3.0, 1.0, 0.0)  # 4 — center-right
v5 = m.vertex(2.0, 2.0, 0.0)  # 5 — top

# Four triangles forming a diamond; interior edges shared by 2.
t0 = m.triangle(v0, v1, v2)   # 0: bottom-left
t1 = m.triangle(v2, v3, v4)   # 1: bottom-right
t2 = m.triangle(v0, v2, v5)   # 2: top-left
t3 = m.triangle(v2, v4, v5)   # 3: top-right

# Interior edges — shared by 2 triangles each.
m.assert_edge_shared(v0, v2, 2)  # t0 and t2
m.assert_edge_shared(v2, v4, 2)  # t1 and t3
m.assert_edge_shared(v2, v5, 2)  # t2 and t3

# Boundary edges — each on exactly 1 triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v0, v5, 1)

# Coincident pair: v1 and v3 both at (2.0, 0.0, 0.0), no shared triangle.
m.assert_vertex_pair_distance_lt(v1, v3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(v1, v3)

# Euler: V=6, E=9, F=4, chi=1 (open disk, genus 0).
m.assert_euler_characteristic(6, 9, 4, 1)
