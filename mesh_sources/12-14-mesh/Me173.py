"""Me173 — orient_edge_iteration: per-edge scan of a quad-patch polygon.

Catalog claim: a rectangular patch where each of the 4 edges of the patch
polygon must be iterated (Branch 4, *edge_iteration*) to find adjacent
polygons. The orient algorithm loops `for(P_ID ih = 0; ih < size; ++ih)` over
all edges of the current polygon — Branch 4 fires once per edge.

Geometric signature: 4 triangles forming a 2×2 quad patch. The top-left and
bottom-right triangles are consistently CCW; the top-right triangle is wound
CW (the defect). The per-edge iteration over the bottom-left (seed) triangle
visits all 3 of its edges and discovers the adjacent defect triangle via one
of those edges.

Defect carrier: t3 = (v2, v1, v4) is CW (normal -Z). It shares edge (v1,v2)
with the seed t0 = (v0, v1, v2). The edge_iteration loop walks all 3 edges
of t0 before finding t3.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me173",
             title="orient edge_iteration: per-edge scan of patch finds defect triangle via edge loop",
             defect_class="inconsistent_winding")

# 3×2 vertex grid in XY plane.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3
v4 = m.vertex(1.0, 1.0, 0.0)   # 4
v5 = m.vertex(2.0, 1.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v3)   # CCW, +Z — seed, 3 edges to iterate
t1 = m.triangle(v1, v4, v3)   # CCW, +Z — adjacent to t0 via edge (v1,v3)
t2 = m.triangle(v1, v2, v5)   # CCW, +Z
# t3 is CW: (v2-v1)×(v4-v1) = (1,0,0)×(0,1,0) = (0,0,1) → actually check:
# v1=(1,0), v2=(2,0), v4=(1,1). t3=(v2,v1,v4): (v1-v2)×(v4-v2)=(-1,0,0)×(-1,1,0)=(0,0,-1) → -Z ✓
t3 = m.triangle(v2, v1, v4)   # CW, -Z — defect: discovered via edge-iteration on t0 or t2

# t0 and t1 share edge v1-v3 (consistent CCW).
m.assert_edge_shared(v1, v3, 2)

# t2 and t3 share edge v1-v2; t2 is CCW, t3 is CW → antiparallel normals.
m.assert_edge_shared(v1, v2, 2)
m.assert_adjacent_triangles_inconsistent_winding(t2, t3)

# t1 and t3 share edge v1-v4 (t1 CCW, t3 CW).
m.assert_edge_shared(v1, v4, 2)
m.assert_adjacent_triangles_inconsistent_winding(t1, t3)
