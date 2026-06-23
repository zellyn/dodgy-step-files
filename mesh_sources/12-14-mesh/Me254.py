"""Me254 — openToDisk_no_leaf_found: no spanning-tree root — error (Branch 5).

MeshFix `Basic_TMesh.openToDisk` Branch 5 (*no_leaf_found*) @ line 1819:
  '!triList.numels()' — after scanning all boundary vertices no leaf was found;
  TMeshError raised: cannot find spanning tree root.

After BFS labels boundary edges, openToDisk looks for a boundary vertex with
numels()==1 (exactly one incident boundary edge) to use as the root of the
spanning tree. Branch 5 fires if no such leaf exists — i.e., every boundary vertex
has != 1 incident boundary edge.

In a manifold open mesh every boundary vertex has exactly 2 incident boundary edges
(never 1), so Branch 5 never fires on manifold inputs. It fires on closed meshes
(no boundary at all — every vertex has 0 boundary edges) or on non-manifold meshes
where boundary vertex degrees are ≥ 2 but not 1. A closed mesh is the minimal
trigger: the BFS finds no boundary edges at all, so no leaf vertex exists.

Geometry: a closed tetrahedron — genus 0, no boundary. Every edge is shared by
exactly 2 triangles (no boundary edges). When openToDisk scans for a leaf boundary
vertex (numels()==1), the scan finds nothing → Branch 5 error fires.

  V=4, E=6, F=4, chi=2 — sphere topology.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me254",
             title="openToDisk_no_leaf_found: closed tetrahedron has no boundary, no leaf vertex — error",
             defect_class="open_to_disk_no_leaf")

# Closed tetrahedron — no boundary edges.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(0.5, 0.5, 1.0)   # 3 — apex

t0 = m.triangle(v0, v2, v1)   # 0 — bottom (outward normal down)
t1 = m.triangle(v0, v1, v3)   # 1 — front
t2 = m.triangle(v1, v2, v3)   # 2 — right
t3 = m.triangle(v2, v0, v3)   # 3 — left

# Every edge shared by exactly 2 triangles — no boundary at all.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Euler characteristic confirms sphere topology: chi=2, genus=0.
m.assert_euler_characteristic(4, 6, 4, 2)
