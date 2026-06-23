"""Me138 — removeIfRedundant_double_flat_edge_selection: e1 is preferred as the
collapse edge; if e1 is NULL, the algorithm scans remaining edges for misalignment.

MeshFix `Vertex.removeIfRedundant` Branch 9 (*double_flat_edge_selection*) @ line 382:
  'if (e1 != NULL) e = e1; else { for each edge ... misalignment check }'
  After removing e1 and e2 from the candidate list (Branches 5 and 6), Branch 9
  selects the actual edge 'e' for the vertex collapse. If e1 was found earlier
  (and preserved as a reference even after being removed from 've'), it is
  preferred directly. Otherwise the algorithm scans remaining edges for
  misalignment with the opposite vertex to find the best collapse target.

Geometric signature: vertex v2 is a DoubleFlat subject on the x-axis. Only one
special ridge edge e1=(v1,v2) was identified at classification time (e2 is NULL —
the far side has no ridge). Branch 9 fires the 'e = e1' branch, selecting e1
as the collapse target edge.

Geometry (z=0):
  v0=(0,0,0), v1=(1,1,0), v2=(2,0,0), v4=(4,0,0)
  Left fan (only one side has a ridge at v1):
    t0 = (v0, v1, v2)   — upper left
    t1 = (v0, v2, v4)   — lower/right (flat, no ridge on lower side)

  v0-v2-v4 are collinear on y=0; v2 is Flat (not DoubleFlat since e2 is NULL).
  e1 = (v1,v2) is the one ridge edge; no e2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me138",
             title="removeIfRedundant_double_flat_edge_selection: e1 preferred as collapse edge when e2 is absent",
             defect_class="redundant_vertex_double_flat_edge_selection")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left axis point
v1 = m.vertex(1.0, 1.0, 0.0)   # 1 — ridge neighbor (e1 edge)
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — Flat vertex (one-sided ridge)
v3 = m.vertex(4.0, 0.0, 0.0)   # 3 — right axis point

t0 = m.triangle(v0, v1, v2)    # 0 — above, with ridge edge e1=(v1,v2)
t1 = m.triangle(v0, v2, v3)    # 1 — lower/right, flat

# v2 lies on segment v0-v3 (Flat vertex on x-axis).
m.assert_vertex_on_edge(v2, v0, v3)

# e1 = (v1,v2): interior edge shared by t0 only since t1 doesn't touch v1.
# Actually v1 is only in t0; e1=(v1,v2) is boundary (only t0 references it).
m.assert_edge_shared(v1, v2, 1)   # e1: boundary (only in t0) — e2 absent

# Axis edges.
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v2, v3, 1)   # boundary: only t1
m.assert_edge_shared(v0, v3, 1)   # boundary: only t1
