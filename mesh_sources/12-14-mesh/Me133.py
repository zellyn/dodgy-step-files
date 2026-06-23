"""Me133 — removeIfRedundant_overlapping_incident_edge: an incident edge overlaps
another edge in the mesh, blocking vertex removal.

MeshFix `Vertex.removeIfRedundant` Branch 4 (*overlapping_incident_edge*) @ line 359:
  'if (e->overlaps())'
  After the neighborhood check, each incident edge is tested for overlap with
  other edges. If any incident edge overlaps, the vertex topology is too complex
  for safe collapse and removeIfRedundant returns false.

Geometric signature: vertex v2 has an incident edge (v0, v2) that lies along the
same line as edge (v0, v1) (a collinear chain on y=0). In MeshFix, two edges
overlap when they share a common interior segment. Here (v0,v2) and (v0,v1) are
collinear and share the sub-segment from v0 to v2, so e->overlaps() fires.

Geometry:
  v0=(0,0,0), v1=(3,0,0), v2=(1,0,0), v3=(0,1,0), v4=(3,1,0)

  t0 = (v0, v2, v3)   — left triangle
  t1 = (v2, v1, v4)   — right triangle (v2,v1 and v0,v1 are collinear)
  t2 = (v0, v1, v3)   — long base triangle: creates edge (v0,v1) that overlaps (v0,v2)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me133",
             title="removeIfRedundant_overlapping_incident_edge: incident edge collinear-overlap blocks vertex removal",
             defect_class="redundant_vertex_removal_edge_overlap")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 0.0, 0.0)   # 2 — on segment v0-v1
v3 = m.vertex(0.0, 1.0, 0.0)   # 3
v4 = m.vertex(3.0, 1.0, 0.0)   # 4

# t0 and t2 share edge (v0,v3), and t2 has the long edge (v0,v1).
t0 = m.triangle(v0, v2, v3)    # 0 — left small triangle
t1 = m.triangle(v2, v1, v4)    # 1 — right triangle
t2 = m.triangle(v0, v1, v3)    # 2 — large base triangle with edge (v0,v1)

# v2 lies exactly on edge (v0, v1) of t2 — T-junction / overlap condition.
m.assert_vertex_on_edge(v2, v0, v1)

# Edge (v0,v3) shared by t0 and t2 (both use these vertices).
m.assert_edge_shared(v0, v3, 2)

# Edges at v2: (v0,v2) is boundary (only in t0); (v2,v1) boundary (only in t1).
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
