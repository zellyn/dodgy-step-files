"""Me882 — duplicateNonManifoldVertices NONMANIFOLD_VERTICES_PRESENT: dv>0 triggers topology-dirty branch.

MeshFix `checkAndRepair::duplicateNonManifoldVertices` Branch 3
(*NONMANIFOLD_VERTICES_PRESENT*) @ line 171:
  'if (dv) { d_boundaries = d_handles = d_shells = 1; }'
  — after the repair loop has duplicated one or more non-manifold
  vertices (dv > 0), the topology-dirty flag is set: boundary, handle
  and shell counts must be recomputed. Branch 3 fires whenever the mesh
  contained at least one non-manifold vertex, regardless of how many
  were split. The typical symptom reported in bug trackers is "topology
  computation invalidated" or "d_boundaries = d_handles = d_shells = 1".

Defect pattern: the mesh has at least one non-manifold (bowtie) vertex.
  A single bowtie — two triangle fans meeting only at v0 — is the
  minimal structure that forces dv >= 1 and triggers Branch 3. The
  fixture uses a minimal two-triangle bowtie (identical to the classic
  Me011 pattern) so that exactly one non-manifold vertex is detected.

Geometry (2 triangles, 5 vertices):
  v0=(0,0,0)   — bowtie vertex; dv incremented to 1 by repair loop
  Upper fan: v1=(1,1,0), v2=(-1,1,0)    — t0=(v0,v1,v2)
  Lower fan: v3=(1,-1,0), v4=(-1,-1,0)  — t1=(v0,v3,v4)
  Both fans share only v0; no shared edge exists between them.
  After both Branch 1 and Branch 2 checks have completed for all edges,
  dv equals the number of vertices duplicated (>= 1); Branch 3 fires
  and marks the topology dirty.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me882",
    title="duplicateNonManifoldVertices NONMANIFOLD_VERTICES_PRESENT: at least one non-manifold vertex found; dv>0 marks topology dirty (Branch 3)",
    defect_class="non_manifold_vertex",
)

# Bowtie vertex — dv is incremented when this vertex is split.
v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — the non-manifold vertex

# Upper fan.
v1 = m.vertex(1.0,  1.0, 0.0)   # 1
v2 = m.vertex(-1.0, 1.0, 0.0)   # 2

# Lower fan.
v3 = m.vertex(1.0, -1.0, 0.0)   # 3
v4 = m.vertex(-1.0, -1.0, 0.0)  # 4

# Two-triangle bowtie: t0 upper, t1 lower, sharing only v0.
t0 = m.triangle(v0, v1, v2)   # 0: upper fan
t1 = m.triangle(v0, v3, v4)   # 1: lower fan

# All four edges at v0 are boundary edges (n=1 each).
m.assert_edge_shared(v0, v1, 1)   # upper fan boundary
m.assert_edge_shared(v0, v2, 1)   # upper fan boundary
m.assert_edge_shared(v0, v3, 1)   # lower fan boundary
m.assert_edge_shared(v0, v4, 1)   # lower fan boundary

# No edge connects the two fans directly.
m.assert_edge_shared(v1, v3, 0)   # upper-right to lower-right: no edge
m.assert_edge_shared(v2, v4, 0)   # upper-left to lower-left: no edge

# v0's fan is disconnected — the structural cause of dv>=1 and Branch 3.
m.assert_vertex_fan_disconnected(v0)
