"""Me174 — orient_marked_edge_skip: non-manifold edge marked, skipped by orient.

Catalog claim: three triangles share a single edge (non-manifold). During
orientation, the orient algorithm marks this edge as conflicting/non-manifold
and Branch 5 (*marked_edge_skip*) causes the orient DFS to skip it rather than
propagating orientation across it. The `continue` fires once per marked edge.

Geometric signature: edge (v0,v1) is shared by three triangles — a genuine
non-manifold edge. Two of the triangles (t0, t1) are consistently CCW; the
third (t2) is also CCW but on the 'third' side of the non-manifold edge. The
orient algorithm would mark edge (v0,v1) early as non-manifold and skip it
when iterating from any of the three triangles.

Defect carrier: the non-manifold edge itself is the mark trigger. The orient
code's inner edge loop checks is_edge_marked(i1,i2,marked_edges) and
continues without propagating orientation if the edge is marked.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me174",
             title="orient marked_edge_skip: non-manifold edge marked; orientation skip continues past it",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — above edge
v3 = m.vertex(0.5,-1.0, 0.0)   # 3 — below edge
v4 = m.vertex(0.5, 0.0, 1.0)   # 4 — out of plane

t0 = m.triangle(v0, v1, v2)   # CCW in XY, +Z normal
t1 = m.triangle(v0, v1, v3)   # CW when viewed from +Z, but distinct face
t2 = m.triangle(v0, v1, v4)   # third triangle on the same edge (non-manifold)

# The edge (v0,v1) is incident on all 3 triangles — the non-manifold mark trigger.
m.assert_edge_shared(v0, v1, 3)

# t0 and t1 share only the non-manifold edge; their normals may differ.
# t0 normal: (v1-v0)×(v2-v0) = (1,0,0)×(0.5,1,0) = (0,0,1) → +Z
# t1 normal: (v1-v0)×(v3-v0) = (1,0,0)×(0.5,-1,0) = (0,0,-1) → -Z
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)
