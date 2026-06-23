"""Me190 — splitTriangle_new_triangle_from_e3_e1: nt1 created from e3 and e1 sides.

MeshFix `Basic_TMesh.splitTriangle` Branch 1 (*new_triangle_from_e3_e1*) @ line 1919:
  'nt1 = newTriangle(nv, v3, v1)'
  A new vertex nv is inserted inside triangle t(v1,v2,v3), splitting it into
  3 children. The first new triangle nt1 is created from the e3/e1 corner:
  it uses the e3 side (v3→v1) and connects to nv.

Geometry (flat XY plane):
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0)  — original triangle t
  nv=(1,0.7,0) — new interior vertex inserted into t

After the split:
  t   := (v0, v1, nv)   — original slot (uses e2 side: v0→v1)
  nt1 := (nv, v2, v0)   — new triangle 1 (from e3: v2→v0 corner)
  nt2 := (nv, v1, v2)   — new triangle 2 (from e1: v1→v2 corner)

The defect carrier: the input mesh has triangle t(v0,v1,v2) with a vertex
nv coincident-but-distinct from the interior of t, flagged because nv sits
inside t but is not yet connected — a T-junction-like split readiness marker.
The nt1 creation (branch 1) is triggered when the healer calls splitTriangle
to replace this configuration with a proper 3-way split.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me190",
             title="splitTriangle_new_triangle_from_e3_e1: first child triangle nt1 connects nv to v2-v0 side",
             defect_class="split_triangle_interior_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left vertex of original triangle
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — right vertex of original triangle
v2 = m.vertex(1.0, 2.0, 0.0)   # 2 — apex of original triangle
nv = m.vertex(1.0, 0.7, 0.0)   # 3 — new interior vertex (inside t)

# Post-split triangle topology:
# t  (reused slot) := (v0, v1, nv)   index 0
# nt1              := (nv, v2, v0)   index 1  ← Branch 1: new triangle from e3/e1
# nt2              := (nv, v1, v2)   index 2

t0  = m.triangle(v0, v1, nv)   # 0 — reused original triangle slot
nt1 = m.triangle(nv, v2, v0)   # 1 — Branch 1: first new child triangle
nt2 = m.triangle(nv, v1, v2)   # 2 — second new child triangle

# The new vertex nv lies inside the original triangle t(v0,v1,v2).
# Assert this via vertex_on_edge (nv should NOT be on any edge — it is interior,
# but we confirm topological adjacency). The key assertion: each pair of child
# triangles shares exactly one of the three new inner edges through nv.

# Inner edge (nv, v0) = shared by t0 and nt1
m.assert_edge_shared(nv, v0, 2)   # ne2: shared by t and nt1

# Inner edge (nv, v1) = shared by t0 and nt2
m.assert_edge_shared(nv, v1, 2)   # ne1: shared by t and nt2

# Inner edge (nv, v2) = shared by nt1 and nt2
m.assert_edge_shared(nv, v2, 2)   # ne3: shared by nt1 and nt2

# Original outer edges are now each owned by exactly one child triangle.
m.assert_edge_shared(v0, v1, 1)   # e2: boundary (original base edge, now in t only)
m.assert_edge_shared(v2, v0, 1)   # e3: boundary (original left edge, now in nt1 only)
m.assert_edge_shared(v1, v2, 1)   # e1: boundary (original right edge, now in nt2 only)
