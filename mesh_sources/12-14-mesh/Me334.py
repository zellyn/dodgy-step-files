"""Me334 — pinch_interior_edge_asymmetry_t2: interior edge with only t2 set, mirror has t1 — merge.

MeshFix `Basic_TMesh.pinch` Branch 5 (*INTERIOR_EDGE_ASYMMETRY*) @ line 944:
  'else { if (e2->t1 != NULL) { ... e1->merge(e2); return true; } }'
  The opposite of Branch 4: edge e1 has only t2 attached (t1 is NULL). The
  algorithm scans for a mirror edge e2 whose t1 slot is occupied. When found,
  the two edges are merged. This is the t2-side (else) case.

Defect pattern: the same interior-edge-asymmetry defect as Branch 4, but with
  the roles flipped — the edge of interest carries t2 rather than t1. The
  non-manifold vertex v0 is the pinch point where a fan of triangles connects
  in an asymmetric way requiring the t2-side scan.

Geometry: two coplanar triangles sharing vertex v0 that form a disconnected
  fan (non-manifold bowtie at v0). One triangle's edge is recorded in the
  t2 slot; the other is in the t1 slot.

  v0=(0,0,0): pinch/bowtie vertex
  Fan left:  t0=(v1,v0,v2) — v0 edge recorded as t2 for edge (v0,v1)
  Fan right: t1=(v0,v3,v4) — v0 edge recorded as t1 for edge (v0,v3)

  The two fans share v0 but no edges through v0 — disconnected fan.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me334",
             title="pinch_interior_edge_asymmetry_t2: e1->t2 set only, mirror e2->t1 set — merge resolves asymmetry",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — bowtie vertex
v1 = m.vertex(1.0,  0.0, 0.0)   # 1
v2 = m.vertex(0.5,  1.0, 0.0)   # 2
v3 = m.vertex(-1.0, 0.0, 0.0)   # 3
v4 = m.vertex(-0.5, 1.0, 0.0)   # 4

t0 = m.triangle(v1, v0, v2)   # 0 — left fan (v0 is middle vertex — t2 slot for edge v0-v1)
t1 = m.triangle(v0, v3, v4)   # 1 — right fan (t1 slot for edge v0-v3)

# v0 is a bowtie/non-manifold pinch vertex — fan is disconnected.
m.assert_vertex_fan_disconnected(v0)

# All edges are boundary (each triangle is isolated at v0 level).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v3, v4, 1)

# Two disconnected components (no shared edges).
m.assert_triangle_not_reachable_from(t1, t0)
