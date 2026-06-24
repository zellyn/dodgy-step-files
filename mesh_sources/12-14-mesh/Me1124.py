"""Me1124 — constrained smoothing stalls; unconstrained fallback fires (smoothing-fallback-escalation branch).

CGAL PMP.remove_self_intersections Branch 10 @ line 2207 — *smoothing-fallback-escalation*:
  'if (!fixed_by_smoothing) { smooth(..., constrain_sharp_edges=false); }'
  — the SI repair dispatcher first attempts constrained smoothing (Branch 9 pass),
  locking high-dihedral edges to preserve sharp features. If that constrained pass leaves
  self-intersections unresolved (fixed_by_smoothing=false), the dispatcher re-runs
  smoothing WITHOUT sharp-edge constraints, allowing the smoother to relax across the
  feature crease. This two-pass escalation is the fallback pattern.

Defect pattern: three co-planar floor triangles plus two perpendicular wall triangles form
  a mesh with two sharp creases. An intruder triangle self-intersects the central floor
  face. Both creases are high-dihedral (90°), so constrained smoothing cannot move the
  intruder's displaced apex without crossing a locked edge. The unconstrained fallback
  succeeds by relaxing the crease locks.

  Mesh layout (all vertices, z=0 for floor):
    v0=(0,1,0), v1=(1,0,0), v2=(1,2,0), v3=(2,1,0), v4=(1,1,0)
    Floor tiles: tri 0 = (v0,v1,v4), tri 1 = (v0,v4,v2), tri 2 = (v1,v3,v4), tri 3 = (v4,v3,v2)
    Wall A rises from edge (v1,v4) at 90°: apex v5=(1,0,1).
    Wall B rises from edge (v4,v2) at 90°: apex v6=(1,2,1).
    Intruder tri 5: apex v7=(1,1,-0.5) below floor, pierces tri 0 and tri 1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1124",
             title="SI under two-crease floor: constrained smoothing stalls, unconstrained fallback fires",
             defect_class="self_intersection_smoothing_fallback")

# Floor centre (5-vertex quad subdivided into 4 triangles — cross pattern).
v0 = m.vertex(0.0, 1.0, 0.0)  # 0 — floor left
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — floor bottom
v2 = m.vertex(1.0, 2.0, 0.0)  # 2 — floor top
v3 = m.vertex(2.0, 1.0, 0.0)  # 3 — floor right
v4 = m.vertex(1.0, 1.0, 0.0)  # 4 — floor centre

# Four floor triangles.
t0 = m.triangle(v0, v1, v4)   # tri 0 — bottom-left floor cell
t1 = m.triangle(v0, v4, v2)   # tri 1 — top-left floor cell
t2 = m.triangle(v1, v3, v4)   # tri 2 — bottom-right floor cell
t3 = m.triangle(v4, v3, v2)   # tri 3 — top-right floor cell

# Wall A: rises from edge (v1,v4) at 90° (x=1 plane, z≥0).
v5 = m.vertex(1.0, 0.5, 1.0)  # 5 — wall-A apex
t4 = m.triangle(v1, v4, v5)   # tri 4 — wall A

# Wall B: rises from edge (v4,v2) at 90°.
v6 = m.vertex(1.0, 1.5, 1.0)  # 6 — wall-B apex
t5 = m.triangle(v4, v2, v6)   # tri 5 — wall B

# Intruder: apex v7 below the floor, bridging into z<0 territory.
# It self-intersects tri 0 (bottom-left floor cell).
v7 = m.vertex(0.5, 0.7, -0.5)  # 7 — below floor (defect)
v8 = m.vertex(0.2, 0.4,  0.5)  # 8 — above floor
v9 = m.vertex(0.8, 0.4,  0.5)  # 9 — above floor
t6 = m.triangle(v7, v8, v9)    # tri 6 — intruder crossing tri 0

# Assert: intruder self-intersects bottom-left floor cell.
m.assert_triangles_self_intersect(0, 6)

# Assert: crease-A edge (v1,v4) shared by floor tri 0, floor tri 2, and wall-A tri 4.
# n=3 (non-manifold crease) — this is the stiff constraint that blocks the first pass.
m.assert_edge_shared(v1, v4, 3)

# Assert: floor interior edges are shared manifold (n=2).
m.assert_edge_shared(v0, v4, 2)  # shared by tri 0 and tri 1
m.assert_edge_shared(v3, v4, 2)  # shared by tri 2 and tri 3

# Assert: outer floor boundary edges are open (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
