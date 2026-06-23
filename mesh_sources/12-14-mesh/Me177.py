"""Me177 — orient_orientation_conflict: already-oriented neighbor has incompatible winding.

Catalog claim: two adjacent triangles that are both already marked as oriented
but have incompatible windings. Branch 8 (*orientation_conflict*) fires when
the orient DFS finds a neighbor that is already oriented (oriented[index]==true)
but its orientation is inconsistent with the current polygon — the condition
`if(oriented[index])` with an incompatible winding means the edge gets marked
as a conflict edge and no reversal is attempted.

Geometric signature: a 4-triangle cross where the center seed triangle (t0) is
CCW, two neighbors (t1, t2) were already oriented CCW independently, and the
fourth triangle (t3) bridges between t1 and t2 with CW winding. When orient
processes t3 via its edge to t1, it finds t1 already oriented (Branch 8), and
registers the conflict.

Defect carrier: the pair (t0, t3) are both reachable in the mesh but have
antiparallel normals and share an edge — the orientation conflict Branch 8 must
detect.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me177",
             title="orient orientation_conflict: oriented neighbor found incompatibly wound, edge marked as conflict",
             defect_class="inconsistent_winding")

# Cross arrangement: hub + 4 arms.
hub = m.vertex(0.0, 0.0, 0.0)   # 0
v1  = m.vertex(1.0, 0.0, 0.0)   # 1 — right
v2  = m.vertex(0.0, 1.0, 0.0)   # 2 — top
v3  = m.vertex(-1.0, 0.0, 0.0)  # 3 — left
v4  = m.vertex(0.0, -1.0, 0.0)  # 4 — bottom

t0 = m.triangle(hub, v1, v2)   # CCW, +Z — seed
t1 = m.triangle(hub, v2, v3)   # CCW, +Z — consistent
t2 = m.triangle(hub, v3, v4)   # CCW, +Z — consistent
# t3 is CW and creates a conflict with both t0 and t2.
# t3=(hub, v1, v4): (v1-hub)×(v4-hub) = (1,0,0)×(0,-1,0) = (0,0,-1) → -Z ✓
t3 = m.triangle(hub, v1, v4)   # CW, -Z — orientation conflict

# t0 and t3 share edge (hub,v1); normals antiparallel → orientation conflict.
m.assert_edge_shared(hub, v1, 2)
m.assert_adjacent_triangles_inconsistent_winding(t0, t3)

# t2 and t3 share edge (hub,v4); normals also antiparallel.
m.assert_edge_shared(hub, v4, 2)
m.assert_adjacent_triangles_inconsistent_winding(t2, t3)
