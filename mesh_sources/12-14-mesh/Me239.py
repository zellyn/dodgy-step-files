"""Me239 — topTriangle_degenerate_edge_check: boundary edge fe causes topTriangle to return NULL.

MeshFix `Basic_TMesh.topTriangle` Branch 10 (*degenerate_edge_check*) @ line 1727:
  'fe->t1 == NULL || fe->t2 == NULL' — the steepest descending edge fe is a
  boundary edge (one of its two triangle slots is NULL). topTriangle returns NULL
  to signal topological degeneracy.

Branch 10 fires as a final guard: if the edge selected as the steepest descent
from the highest vertex hv is a boundary edge (shared by only 1 triangle rather
than 2), the algorithm cannot safely walk the surface topology and returns NULL.

Geometry: open strip where the steepest edge from hv is a boundary edge.
  v0=(0,0,0), v1=(2,0,0), v2=(1,0,3)   — triangle with apex at z=3
  t0=(v0,v1,v2) — single triangle; all three edges are boundary (n=1).

hv=v2 (z=3). Candidate edges incident on hv:
  - (v0,v2): boundary (n=1), slope=(3-0)/sqrt(1+9)=(3)/sqrt(10)≈0.949
  - (v1,v2): boundary (n=1), slope=(3-0)/sqrt(1+9)=(3)/sqrt(10)≈0.949 (symmetric)
Branch 8 selects one of them as fe. Then Branch 10 checks: fe->t1==NULL or
fe->t2==NULL → yes (boundary edge) → return NULL.

The fixture's defect carrier is the boundary edge that would be returned as the
steepest descent path, triggering the NULL-return guard.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me239",
             title="topTriangle_degenerate_edge_check: steepest edge is boundary; topTriangle returns NULL",
             defect_class="topTriangle_degenerate_edge_check")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 0.0, 3.0)   # 2 — hv (z=3, highest)

t0 = m.triangle(v0, v1, v2)   # 0 — single triangle; all edges are boundary

# All three edges are boundary (n=1) — the steepest edge will be a boundary edge.
m.assert_edge_shared(v0, v1, 1)   # base; NOT incident on hv → rejected by B7
m.assert_edge_shared(v0, v2, 1)   # incident on hv=v2 → passes B7; boundary → B10
m.assert_edge_shared(v1, v2, 1)   # incident on hv=v2 → passes B7; boundary → B10

# The boundary loop is the triangle's own perimeter.
m.assert_hole_boundary([v0, v1, v2])

# v2 is the highest vertex (z=3 >> z=0 for v0 and v1).
# Both candidate edges have nonzero length and are boundary → Branch 10 triggers NULL.
m.assert_vertex_pair_distance_lt(v0, v2, 4.0)   # length=sqrt(1+9)≈3.16
m.assert_vertex_pair_distance_lt(v1, v2, 4.0)   # length=sqrt(1+9)≈3.16
