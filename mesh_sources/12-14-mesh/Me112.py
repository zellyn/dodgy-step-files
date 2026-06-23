"""Me112 — intersects_shared_vertex_proper: triangles sharing one vertex but no edge crossing.

MeshFix `Triangle.intersects` Branch 6 (*SHARED_VERTEX_PROPER*):
'if (cv1)' — triangles share exactly one vertex in proper mode, so the
code checks whether the opposite edge of each triangle intersects the
interior of the other triangle. When both triangles fan away from the
shared vertex into non-overlapping half-spaces, no edge crosses the
opposing triangle and the predicate returns false.

Geometric signature: a bowtie-like arrangement with shared apex but
each triangle's open edge pointing away from the other. The apex is the
only common point; the triangles are otherwise disjoint.

Geometry:
  Shared vertex: v0=(0,0,0)
  t0: (v0, v1=(2,1,0), v2=(2,-1,0))  — pointing in +X direction
  t1: (v0, v3=(-2,1,0), v4=(-2,-1,0)) — pointing in -X direction

The triangles share only v0. Their free edges (v1,v2) and (v3,v4) are in
disjoint half-planes so neither edge pierces the other triangle.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me112",
             title="intersects_shared_vertex_proper: shared-apex triangles pointing in opposite directions do not intersect",
             defect_class="mesh_shared_vertex_no_intersection")

v0 = m.vertex( 0.0,  0.0, 0.0)   # shared apex
v1 = m.vertex( 2.0,  1.0, 0.0)
v2 = m.vertex( 2.0, -1.0, 0.0)
v3 = m.vertex(-2.0,  1.0, 0.0)
v4 = m.vertex(-2.0, -1.0, 0.0)

t0 = m.triangle(v0, v1, v2)   # fans +X
t1 = m.triangle(v0, v3, v4)   # fans -X

# Only the apex vertex is shared; each edge of the pair is a boundary edge.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)

# Shared-vertex branch: opposite edges do not pierce the opposing triangle.
m.assert_triangles_do_not_intersect(t0, t1)
