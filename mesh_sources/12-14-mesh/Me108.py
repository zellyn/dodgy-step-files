"""Me108 — unlink_triangle_v1_manifold_duplication: v1 is non-manifold and must
be duplicated before the triangle is unlinked.

MeshFix `Basic_TMesh.unlinkTriangle` Branch 11 (*manifold_duplication_v1*):
'if (v1nm)' — v1 was flagged as non-manifold at the earlier Branch 1 check
(boundary but both incident edges are non-boundary). After that detection, the
algorithm must clone v1, redirect all incident edges in one fan to the new
duplicate vertex, and then perform the unlink. Branch 11 carries out the actual
duplication for v1.

Geometric signature: v1 is a bowtie (vertex_fan_disconnected) vertex where one
fan includes the target triangle and the other fan is a separate group. The
bowtie condition means v1 is simultaneously on the topological boundary (its fan
is open) yet its edges in the target triangle are interior. Unlinking the target
triangle is the trigger for the duplication.

Geometry — same structural pattern as Me100 but with an explicit bowtie/
disconnected-fan assertion to confirm the v1nm condition:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0)
  v3=(1,1,0), v4=(0,-1,0), v5=(2,-1,0)

  Upper fan (includes target t0):
    t0 = (v0, v1, v3)   ← target; (v0,v1) and (v1,v3) are interior
    t1 = (v1, v2, v3)   — shares (v1,v3) with t0
    t2 = (v0, v3, v2)   — closes upper fan from above
    Note: edge (v0,v1) is in t0 only if no lower triangle shares it.

  Lower fan (isolated from upper):
    t3 = (v1, v4, v5)   — shares v1 but not connected to upper fan
                            (no edge links t0/t1/t2 to t3 except through v1)

  v1 belongs to both fans with no shared edge between fans → bowtie.
  Branch 11 fires when t0 is about to be unlinked.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me108",
             title="unlink_triangle_v1_manifold_duplication: v1 is non-manifold bowtie requiring duplication on unlink",
             defect_class="unlink_manifold_duplication_v1")

v0 = m.vertex(0.0, 0.0, 0.0)    # 0
v1 = m.vertex(1.0, 0.0, 0.0)    # 1 — bowtie center = v1 in target
v2 = m.vertex(2.0, 0.0, 0.0)    # 2
v3 = m.vertex(1.0, 1.0, 0.0)    # 3 — upper apex
v4 = m.vertex(0.0, -1.0, 0.0)   # 4 — lower fan left
v5 = m.vertex(2.0, -1.0, 0.0)   # 5 — lower fan right

# Target triangle: v1 is first vertex.
t0 = m.triangle(v0, v1, v3)     # 0 — target

# Upper fan second triangle (shares (v1,v3) with t0).
t1 = m.triangle(v1, v2, v3)     # 1

# Upper fan closure.
t2 = m.triangle(v0, v3, v2)     # 2 — closes upper fan (v0,v2,v3)

# Lower fan — isolated from upper fan, connected only through v1.
t3 = m.triangle(v1, v4, v5)     # 3

# Interior edges in upper fan at v1.
m.assert_edge_shared(v1, v3, 2)   # shared by t0 and t1
m.assert_edge_shared(v1, v2, 1)   # boundary of upper fan (only in t1)

# Edge (v0,v1): in t0 only → boundary.
m.assert_edge_shared(v0, v1, 1)   # boundary (triggers edge_reference_update branch)

# Lower fan boundary edges (v1 not shared with upper fan via any edge).
m.assert_edge_shared(v1, v4, 1)   # boundary in lower fan
m.assert_edge_shared(v1, v5, 1)   # boundary in lower fan

# v1's fan is disconnected (bowtie) — the core non-manifold condition.
m.assert_vertex_fan_disconnected(v1)
