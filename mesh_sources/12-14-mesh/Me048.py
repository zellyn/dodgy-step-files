"""Me048 — compatible_orientations: orientation constraint propagation yields conflict.

Catalog claim: two chains of triangles are each internally consistently oriented, but
when they are bridged by a shared edge the two chains' orientations are mutually
incompatible. CGAL PMP.compatible_orientations Branch 3 @ line 1290
(*orientation_conflict*) fires when BFS propagation of orientation constraints
reaches a face already labeled with the opposite orientation — the propagate_incompatibility
path marks the mesh as unorientable.

Defect carrier: chain A = triangles 0-1 (CCW, normal +Z) and chain B = triangles 2-3
(internally consistent but both CW, normal -Z). Triangles 1 and 2 share edge {v2, v3}
but their normals are antiparallel. When the BFS reaches triangle 2 from triangle 1 it
must assign the opposite orientation (+Z) but triangle 2 is already labelled -Z by its
internal chain propagation — an orientation conflict.

Layout:
  v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0)
  v4=(0,2,0), v5=(1,2,0)
  Chain A CCW (+Z): tri0=(v0,v1,v2), tri1=(v0,v2,v3)
  Chain B CW  (-Z): tri2=(v3,v5,v2), tri3=(v3,v4,v5) — both wound CW so normals -Z.
  tri2 shares edge {v2,v3} with tri1 (the bridge that creates the conflict).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me048",
             title="orientation constraint conflict: two consistently wound chains are mutually incompatible",
             defect_class="orientation_conflict")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 1.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3
v4 = m.vertex(0.0, 2.0, 0.0)   # 4
v5 = m.vertex(1.0, 2.0, 0.0)   # 5

# Chain A — wound CCW, normals +Z.
t0 = m.triangle(v0, v1, v2)    # tri 0  CCW, +Z
t1 = m.triangle(v0, v2, v3)    # tri 1  CCW, +Z; shares edge {v2,v3} with tri2

# Chain B — wound CW, normals -Z.  Shares edge {v2,v3} with chain A at tri2.
t2 = m.triangle(v3, v5, v2)    # tri 2  CW, -Z — bridges from chain A
t3 = m.triangle(v3, v4, v5)    # tri 3  CW, -Z

# Assert: triangles 1 and 2 share edge {v2,v3} but have antiparallel normals.
m.assert_adjacent_triangles_inconsistent_winding(t1, t2)

# Assert: edge {v2,v3} is shared by exactly 2 triangles (manifold edge — conflict
# is purely about orientation, not topology).
m.assert_edge_shared(v2, v3, 2)
