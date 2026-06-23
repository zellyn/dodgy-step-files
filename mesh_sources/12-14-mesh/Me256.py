"""Me256 — openToDisk_vertex_cycle_closure: vertex has no more boundary edges (Branch 7).

MeshFix `Basic_TMesh.openToDisk` Branch 7 (*vertex_cycle_closure*) @ line 1835:
  'else' — vertex has no pending boundary edges; cycle closes; unmark two edges
  and re-queue for next cycle.

Branch 7 fires when the spanning tree traversal reaches a vertex with no more
pending boundary edges — meaning a complete cycle has been traced. The algorithm
unmarks two previously-marked edges (UNMARK_BIT) and re-appends the vertex to the
queue to start the next traversal cycle (for multi-loop boundaries).

Geometry: an open triangulated annulus (2 boundary loops). The spanning tree
traversal walks the inner boundary until no edges remain (Branch 7 fires — inner
cycle closes), then walks the outer boundary (Branch 7 fires again — outer cycle
closes).

Implementation: 6 triangles forming a ring with a triangular hole (inner loop)
and a triangular outer rim (outer loop).
  Inner triangle hole: vertices i0, i1, i2 (triangular hole — 3 inner boundary edges)
  Outer triangle: vertices o0, o1, o2 (3 outer boundary edges)
  6 triangles fill the annulus between them.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me256",
             title="openToDisk_vertex_cycle_closure: two boundary loops — cycle-close Branch 7 fires twice",
             defect_class="open_to_disk_cycle_closure")

# Inner triangle hole vertices.
i0 = m.vertex(0.0, 0.0, 0.0)    # 0
i1 = m.vertex(1.0, 0.0, 0.0)    # 1
i2 = m.vertex(0.5, 0.87, 0.0)   # 2

# Outer triangle vertices.
o0 = m.vertex(-0.5, -0.87, 0.0)  # 3
o1 = m.vertex(1.5,  -0.87, 0.0)  # 4
o2 = m.vertex(0.5,   1.73, 0.0)  # 5

# 6 triangles filling the annulus between inner and outer triangles.
# Side bottom: o0,o1 outer; i0,i1 inner
t0 = m.triangle(o0, i0, i1)    # 0
t1 = m.triangle(o0, i1, o1)    # 1
# Side right: o1,o2 outer; i1,i2 inner
t2 = m.triangle(o1, i1, i2)    # 2
t3 = m.triangle(o1, i2, o2)    # 3
# Side left: o2,o0 outer; i2,i0 inner
t4 = m.triangle(o2, i2, i0)    # 4
t5 = m.triangle(o2, i0, o0)    # 5

# Inner boundary edges (inner hole, 3 edges — each incident on exactly 1 triangle).
m.assert_edge_shared(i0, i1, 1)   # inner boundary
m.assert_edge_shared(i1, i2, 1)   # inner boundary
m.assert_edge_shared(i0, i2, 1)   # inner boundary

# Outer boundary edges (outer rim, 3 edges — each incident on exactly 1 triangle).
m.assert_edge_shared(o0, o1, 1)   # outer boundary
m.assert_edge_shared(o1, o2, 1)   # outer boundary
m.assert_edge_shared(o0, o2, 1)   # outer boundary

# Interior edges (shared by 2 triangles each).
m.assert_edge_shared(o0, i0, 2)
m.assert_edge_shared(o0, i1, 2)
m.assert_edge_shared(o1, i1, 2)
m.assert_edge_shared(o1, i2, 2)
m.assert_edge_shared(o2, i2, 2)
m.assert_edge_shared(o2, i0, 2)

# Inner boundary loop (cycle closure Branch 7 fires here).
m.assert_hole_boundary([i0, i1, i2])
# Outer boundary loop (Branch 7 fires again when this cycle closes).
m.assert_hole_boundary([o0, o2, o1])
