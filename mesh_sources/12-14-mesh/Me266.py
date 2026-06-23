"""Me266 — range_with_face_set_nonmanifold_marked_region: non-manifold in marked faces region.

Catalog claim: CGAL PMP.remove_degenerate_edges.range_with_face_set Branch 7 @ line 1741
(*nonmanifold_marked_region*): after collecting the initial marked faces around the
degenerate edge, the boundary of the marked region has non-manifold vertices (nb_cc != 1,
exploration_finished is false). The algorithm must mark additional small connected
components to heal the non-manifold boundary before the disk-removal step.

Geometric signature: a configuration where the degenerate edge (v0,v1) is surrounded by
faces, but when those faces are marked, the boundary of the marked region has a
non-manifold vertex — the same vertex appears twice in the boundary loop of the marked
region. The algorithm expands the marked set to include small additional components
adjacent to the non-manifold boundary vertex.

The key structural feature is a BOWTIE (non-manifold) vertex in the neighbourhood of the
degenerate edge: vertex v4 appears as a non-manifold vertex (bowtie) where two fan groups
meet — one group is part of the marked region, and the bowtie at v4 creates a
non-manifold boundary that triggers Branch 7.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me266",
             title="range_with_face_set nonmanifold_marked_region: bowtie vertex in degenerate-edge neighbourhood triggers nb_cc!=1 expansion",
             defect_class="degenerate_edge")

# Near-coincident degenerate edge.
v0 = m.vertex(0.0,   0.0, 0.0)
v1 = m.vertex(1e-10, 0.0, 0.0)

# Upper neighbourhood.
v2 = m.vertex(0.0,  1.0, 0.0)
v3 = m.vertex(1.0,  1.0, 0.0)

# v4: the bowtie / non-manifold vertex — appears in two disconnected fans.
v4 = m.vertex(1.0,  0.0, 0.0)

# Lower neighbourhood.
v5 = m.vertex(0.0, -1.0, 0.0)
v6 = m.vertex(1.0, -1.0, 0.0)

# Upper fan (2 triangles around v4, connected to degenerate edge region).
t0 = m.triangle(v0, v1, v2)    # 0: degenerate edge triangle (upper)
t1 = m.triangle(v1, v3, v2)    # 1: adjacent to degenerate edge (uses v1)
t2 = m.triangle(v1, v4, v3)    # 2: connects to v4 upper fan A

# Lower fan (2 triangles around v4, disconnected from upper fan via v4).
t3 = m.triangle(v1, v0, v5)    # 3: degenerate edge triangle (lower)
t4 = m.triangle(v0, v6, v5)    # 4: extends lower
t5 = m.triangle(v4, v6, v0)    # 5: connects to v4 lower fan B — v4 shares only vertex with upper

# v4 is a bowtie vertex: incident on t2 (upper) and t5 (lower), no shared edge.
m.assert_vertex_fan_disconnected(v4)

# The degenerate edge (v0,v1) is interior: shared by t0 and t3.
m.assert_edge_shared(v0, v1, 2)

# v0 and v1 are nearly coincident.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-9)
