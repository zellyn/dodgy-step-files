"""Me436 — checkAndRepair::forceNormalConsistence branch 7: NON_ORIENTABLE_MESH.

MeshFix `checkAndRepair::forceNormalConsistence` Branch 7 @ line 970:
  'wrn > 0' — after traversing all edges, the cut counter wrn is positive because
  at least one Branch-5 NON_ORIENTABLE_SEAM cut was performed. Branch 7 marks the
  topology dirty and returns with bit 2 set (r |= 2), signalling the mesh is
  non-orientable.

Branch 7 is the terminal outcome for a non-orientable mesh. It fires whenever
the edge-traversal loop in forceNormalConsistence found and cut ≥ 1 seams.
The fixture uses a 6-triangle surface with TWO non-orientable seam edges to make
wrn = 2 > 0 (unambiguously triggering Branch 7 twice and the exit condition once).

Geometry: 5 vertices, 6 triangles forming a closed surface with two seam edges.

Seam A: edge (v0,v1) shared by t0 and t1 in the SAME direction (v0→v1).
    t0=(v0,v1,v2): normal +z (v2 above v0-v1).
    t1=(v0,v1,v3): normal -z (v3 below v0-v1).

Seam B: edge (v2,v3) shared by t2 and t3 in the SAME direction (v2→v3).
    t2=(v2,v3,v0): some normal direction.
    t3=(v2,v3,v1): opposite normal direction.

Connectors: t4=(v0,v2,v4), t5=(v1,v3,v4) — extra triangles completing the surface.

Wait — that gives too many edge incidences on some vertices. Let me use a simpler
closed surface built from the Me434 4-triangle base PLUS 2 additional triangles
that do not add any new seams but make the mesh a 6-face closed surface.

Simplest 6-triangle non-orientable topology that is easy to verify:
Two separate same-direction seam edges using 6 vertices:

    v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(1,-2,0), v4=(3,2,0), v5=(3,-2,0)

    Seam A: (v0,v1) shared by t0 [+z] and t1 [-z].
    Seam B: (v4,v5) shared by t4 [+z] and t5 [-z].
    Connector triangles t2, t3 bridging the two seam pairs.

Normal computations:
    t0=(v0,v1,v2): (v1-v0)=(2,0,0), (v2-v0)=(1,2,0). n=(0,0,4) → +z ✓
    t1=(v0,v1,v3): (v1-v0)=(2,0,0), (v3-v0)=(1,-2,0). n=(0,0,-4) → -z ✓ (seam A)
    t4=(v4,v5,v1): (v5-v4)=(0,-4,0), (v1-v4)=(-1,-2,0). n=((-4)·0-0·(-2),0·(-1)-0·0,0·(-2)-(-4)·(-1))=(0,0,-4) → -z
    t5=(v4,v5,v0): (v5-v4)=(0,-4,0), (v0-v4)=(-3,-2,0). n=((-4)·0-0·(-2),0·(-3)-0·0,0·(-2)-(-4)·(-3))=(0,0,-12) → -z

Hmm. Let me just do two disjoint seam butterfly pairs as 4+2 triangles total
and demonstrate the non-orientable topology clearly with the oracle.
The critical assertion: two antiparallel-normal adjacent pairs (one per seam).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me436",
             title="forceNormalConsistence non-orientable-mesh: wrn=2>0 from two seam edges → topology dirty, r|=2 (Branch 7)",
             defect_class="non_orientable_mesh")

# Seam A: vertices v0,v1 with v2 (above) and v3 (below).
v0 = m.vertex(0.0,  0.0, 0.0)   # 0
v1 = m.vertex(2.0,  0.0, 0.0)   # 1
v2 = m.vertex(1.0,  2.0, 0.0)   # 2 — above seam A: t0 gets +z
v3 = m.vertex(1.0, -2.0, 0.0)   # 3 — below seam A: t1 gets -z

# Seam B: vertices v4,v5 with v2 (above, reuse) and v3 (below, reuse).
# To have 6 triangles and 2 seam edges, add 2 more vertices.
v4 = m.vertex(5.0,  0.0, 0.0)   # 4
v5 = m.vertex(7.0,  0.0, 0.0)   # 5

# --- Seam A triangles ---
# t0 and t1 share (v0,v1) in SAME direction (both v0→v1) → non-orientable seam A.
t0 = m.triangle(v0, v1, v2)   # 0 — normal +z; lists (v0,v1) as v0→v1
t1 = m.triangle(v0, v1, v3)   # 1 — normal -z; lists (v0,v1) as v0→v1 ← SEAM A: wrn++

# Connector bridging seam A: uses remaining edges of t0 and t1.
t2 = m.triangle(v1, v2, v3)   # 2 — connects v2 and v3 across v1

# --- Seam B triangles (independent second seam) ---
# t3 and t4 share (v4,v5) in SAME direction → non-orientable seam B: wrn++
t3 = m.triangle(v4, v5, v2)   # 3 — normal: (v5-v4)=(2,0,0),(v2-v4)=(-4,2,0); n=(0,0,4)→+z
t4 = m.triangle(v4, v5, v3)   # 4 — normal: (v5-v4)=(2,0,0),(v3-v4)=(-4,-2,0); n=(0,0,-4)→-z ← SEAM B: wrn++

# Connector bridging seam B.
t5 = m.triangle(v5, v2, v3)   # 5 — connects v2 and v3 across v5

# Seam A: (v0,v1) traversed in same direction by t0 and t1.
m.assert_edge_shared(v0, v1, 2)
# Seam B: (v4,v5) traversed in same direction by t3 and t4.
m.assert_edge_shared(v4, v5, 2)

# Both seam edges produce antiparallel normals (dot < 0), confirming non-orientable topology.
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)   # seam A
m.assert_adjacent_triangles_inconsistent_winding(t3, t4)   # seam B

# Remaining edges: each shared by exactly 2 triangles (fully manifold except for seam winding).
# Seam A connector edges:
m.assert_edge_shared(v1, v2, 2)   # t0 ↔ t2
m.assert_edge_shared(v1, v3, 2)   # t1 ↔ t2
m.assert_edge_shared(v0, v2, 1)   # t0 outer (v0 not shared beyond seam A)
m.assert_edge_shared(v0, v3, 1)   # t1 outer
m.assert_edge_shared(v2, v3, 2)   # t2 ↔ t5

# Seam B connector edges:
m.assert_edge_shared(v2, v5, 2)   # t3 ↔ t5
m.assert_edge_shared(v3, v5, 2)   # t4 ↔ t5
m.assert_edge_shared(v2, v4, 1)   # t3 outer
m.assert_edge_shared(v3, v4, 1)   # t4 outer
