"""Me1175 — Basic_TMesh.forceNormalConsistence orientation_conflict:
  adjacent triangle has opposite orientation → seam cut performed (Branch 3).

MeshFix `Basic_TMesh.forceNormalConsistence` Branch 3 (*orientation_conflict*)
  @ line 955:
  'if (tmp1*tmp2 < 0) { newEdge(e->v2, e->v1); ...; wrn++; }' —
  After checking the neighbor triangle (Branch 2), forceNormalConsistence
  computes orientation products tmp1 and tmp2. If tmp1*tmp2 < 0, the two
  adjacent triangles have contradictory orientations — one is CCW and the
  other is CW. The function cuts a seam by creating a new edge along the
  shared boundary and increments the warning counter wrn. Branch 3 fires
  on this orientation conflict.

Defect pattern: two adjacent triangles sharing edge v1-v2 but with OPPOSITE
  winding orders — t0 is CCW (normal +Z) and t1 is CW (normal -Z). This is
  the classic "inconsistent face orientation" defect. When forceNormalConsistence
  propagates from t0 to t1 via the shared edge, it detects the flip and cuts
  the seam (Branch 3 fires).

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0,1,0)
  t0=(v0,v1,v2): CCW normal +Z
  t1=(v1,v2,v3): CW in CCW context (same shared edge direction → normals antiparallel)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1175",
    title="Basic_TMesh.forceNormalConsistence orientation_conflict: antiparallel normals on shared edge fire seam cut; inconsistent winding (Branch 3)",
    defect_class="inverted_normal",
)

# Four vertices, two triangles sharing v1-v2 with OPPOSITE orientation
v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — left base
v1 = m.vertex(1.0,  0.0,  0.0)   # 1 — right base
v2 = m.vertex(0.5,  1.0,  0.0)   # 2 — shared apex
v3 = m.vertex(0.0,  1.0,  0.0)   # 3 — left outer

# t0: CCW (normal +Z); t1: CW (normal -Z) — INCONSISTENT winding
# For t1 to have normal -Z with vertices in z=0, we use CW winding: v3,v2,v1
# Both share undirected edge (v1,v2); t0 traverses it v1→v2 (CCW), t1 traverses
# it v2→v1 (also CCW for t1 itself) so their normals would be parallel.
# To get OPPOSITE normals: t1 = (v3,v1,v2) gives normal +Z, or
# t1 = (v2,v3,v1) gives normal +Z too. We need t1 with normal -Z:
# v3=(0,1,0), so t1=(v2,v1,v3): cross of (v1-v2) x (v3-v2) = (0.5,-1,0)x(-0.5,0,0)
# = (-1*0-0*0, 0*(-0.5)-0.5*0, 0.5*0-(-1)*(-0.5)) = (0,0,-0.5) → normal -Z ✓
t0 = m.triangle(v0, v1, v2)   # 0: CCW, normal +Z
t1 = m.triangle(v2, v1, v3)   # 1: CW, normal -Z — opposite orientation to t0

# Shared edge n=2 (interior manifold edge)
m.assert_edge_shared(v1, v2, 2)

# Adjacent triangles have antiparallel normals
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)

# Boundary edges
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Open mesh: V=4, E=5, F=2, chi=1
m.assert_euler_characteristic(4, 5, 2, 1)
