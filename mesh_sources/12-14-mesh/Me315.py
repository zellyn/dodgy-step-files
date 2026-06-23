"""Me315 — watsonInsert_boundary_edge_selection: mixed internal/external edges at cavity boundary vertex.

MeshFix `holeFilling::watsonInsert` Branch 6 (*BOUNDARY_EDGE_SELECTION*) @ line 325:
  '!IS_BIT(e->t1, 6) || !IS_BIT(e->t2, 6)'
  During cavity boundary traversal, each boundary vertex's incident edges are
  examined. Branch 6 selects the cavity boundary edge by checking that one of
  its two adjacent triangles is marked (bit 6 = cavity member) and the other
  is NOT marked — i.e. it's on the boundary between cavity and non-cavity.
  Mixed internal/external incidence at a vertex.

Defect pattern: a triangulated pentagon with the center vertex connected to
  all 5 outer vertices. When 3 of the 5 fan triangles are marked as cavity
  (their circumspheres contain the inserted point), each of the 2 boundary
  vertices of the cavity has exactly one marked triangle and one unmarked
  triangle incident on the shared edge — Branch 6 selects those edges.

Geometry: 6-vertex fan (hub v5, outer ring v0-v4).
  v0=(2,0,0), v1=(0.618,1.902,0), v2=(-1.618,1.176,0),
  v3=(-1.618,-1.176,0), v4=(0.618,-1.902,0), v5=(0,0,0)

  All 5 fan triangles present. The cavity would be {t0, t1, t2} and the
  boundary edges at v0-v5 and v2-v5 are the selected boundary edges (Branch 6).

We represent the full 5-triangle fan. The boundary-edge-selection situation is
  evidenced by the two hub edges at the cavity seam each being incident on
  exactly 2 triangles (one cavity, one non-cavity in the full mesh).
"""
from step_corpus.mesh_builder import MeshFile

import math

m = MeshFile(catalog_id="Me315",
             title="watsonInsert_boundary_edge_selection: mixed cavity/non-cavity edges at boundary vertex (Branch 6)",
             defect_class="hole_in_hull")

# Pentagon outer ring + hub.
# Regular pentagon vertices at unit radius, scaled to radius 2.
r = 2.0
angles = [2 * math.pi * k / 5 for k in range(5)]
outer = []
for a in angles:
    outer.append(m.vertex(round(r * math.cos(a), 6), round(r * math.sin(a), 6), 0.0))

v0, v1, v2, v3, v4 = outer
v5 = m.vertex(0.0, 0.0, 0.0)   # 5 — hub

# 5-triangle fan.
t0 = m.triangle(v0, v1, v5)   # 0
t1 = m.triangle(v1, v2, v5)   # 1
t2 = m.triangle(v2, v3, v5)   # 2
t3 = m.triangle(v3, v4, v5)   # 3
t4 = m.triangle(v4, v0, v5)   # 4

# Hub edges — each shared by exactly 2 triangles (one cavity, one non-cavity
# at the seam: e.g. edge v0-v5 is on t0 and t4).
m.assert_edge_shared(v0, v5, 2)
m.assert_edge_shared(v1, v5, 2)
m.assert_edge_shared(v2, v5, 2)
m.assert_edge_shared(v3, v5, 2)
m.assert_edge_shared(v4, v5, 2)

# Outer boundary edges — each incident on 1 triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v0, 1)

# Outer loop: 5 vertices form the boundary of the open fan.
m.assert_hole_boundary([v0, v1, v2, v3, v4])
