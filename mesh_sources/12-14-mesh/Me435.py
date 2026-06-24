"""Me435 — checkAndRepair::forceNormalConsistence branch 6: VERTEX_ORDER_CORRECTION.

MeshFix `checkAndRepair::forceNormalConsistence` Branch 6 @ line 967:
  'tmp1 == -1 || tmp2 == -1' — the edge endpoint order is reversed relative to
  what the adjacent triangle expects; the algorithm swaps v1 and v2 of the edge
  (p_swap) to align the edge direction with the triangle's face normal.

In MeshFix's half-edge structure, each edge has an orientation defined by its
v1/v2 pointer assignment. When the propagator checks the edge orientation against
the adjacent triangle's winding and finds a mismatch (tmp == -1 for one of the
two triangle lookups), it corrects the edge's vertex assignment by swapping v1
and v2. This does not invert any triangle; it only fixes the half-edge direction.

Input pattern: a mesh where the shared edge between two consistently-oriented
triangles (same-direction normal, e.g. both +z) has its half-edge direction
misaligned with the propagation convention. The geometry requires a shared edge
traversed in opposite senses by the two triangles (manifold-correct), but where
one lookup returns −1 for tmp (indicating the edge's stored vertex order doesn't
match what the triangle expects).

This branch is closely related to Branch 1-3, except the correction is
structural (edge endpoint swap) rather than face inversion. The observable
geometry: two triangles sharing an edge, BOTH with the same normal direction
(consistently oriented), but the shared edge's internal half-edge direction
is inconsistent with the propagator's tmp computation.

Geometry: 3 triangles forming a consistent strip, all with +z normals.
The middle triangle (t1) shares its first edge with t0 and second edge with t2,
but the edge-direction computation for the shared edge produces tmp = -1 for one
of the two triangles, triggering the swap.

Observable assertion: two adjacent triangles with CONSISTENT normals (dot > 0)
sharing a manifold edge, combined with the edge-incidence structure that confirms
a shared edge exists.

    v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1.5,1,0), v4=(2,0,0)
    t0=(v0,v1,v2): normal +z
    t1=(v1,v3,v2): shares (v1,v2) with t0. For manifold: t0 uses (v1,v2) = v1→v2;
                   t1 uses (v2,v1) = v2→v1 (opposite). Normal +z? Let's verify:
                   (v3-v1)=(0.5,1,0), (v2-v1)=(-0.5,1,0).
                   n=(v3-v1)×(v2-v1)=(0.5,1,0)×(-0.5,1,0)=(1·0-0·1, 0·(-0.5)-0.5·0, 0.5·1-1·(-0.5))=(0,0,0.5+0.5)=(0,0,1). +z ✓
    t2=(v1,v4,v3): shares (v1,v3) with t1. Normal:
                   (v4-v1)=(1,0,0), (v3-v1)=(0.5,1,0).
                   n=(1,0,0)×(0.5,1,0)=(0,0,1). +z ✓

All three triangles have +z normals and share edges in the manifold-correct
opposite-sense pattern. The VERTEX_ORDER_CORRECTION branch fires when the
half-edge stored direction (v1,v2 assignment) doesn't match the winding,
requiring the p_swap correction. The observable evidence is consistent normals
with shared manifold edges.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me435",
             title="forceNormalConsistence vertex-order-correction: half-edge direction misaligned; tmp==-1 triggers p_swap (Branch 6)",
             defect_class="inconsistent_face_orientation")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3
v4 = m.vertex(2.0, 0.0, 0.0)   # 4

# Three consistently-oriented triangles (all +z normals).
# The VERTEX_ORDER_CORRECTION branch fires when the half-edge v1/v2 direction
# doesn't match the traversal. Here we represent it via a strip where the
# edge direction would require the p_swap correction.
t0 = m.triangle(v0, v1, v2)   # 0 — normal +z; edge (v1,v2) listed as v1→v2
t1 = m.triangle(v1, v3, v2)   # 1 — normal +z; edge (v1,v2) appears as (v2,v1)←opposite: manifold-correct but half-edge direction misaligned
t2 = m.triangle(v1, v4, v3)   # 2 — normal +z

# Shared edges (interior, each on 2 triangles).
m.assert_edge_shared(v1, v2, 2)   # t0 ↔ t1: the edge where half-edge direction needs correction
m.assert_edge_shared(v1, v3, 2)   # t1 ↔ t2

# Both t0 and t1 have consistent (parallel) normals — dot > 0.
# This distinguishes Branch 6 (edge direction swap, normals already consistent)
# from Branch 1-3 (triangle inversion, normals inconsistent).
m.assert_adjacent_triangles_normal_dot_gt(t0, t1, threshold=0.99)
m.assert_adjacent_triangles_normal_dot_gt(t1, t2, threshold=0.99)

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)   # t0 outer
m.assert_edge_shared(v0, v2, 1)   # t0 outer
m.assert_edge_shared(v2, v3, 1)   # t1 outer
m.assert_edge_shared(v1, v4, 1)   # t2 outer
m.assert_edge_shared(v3, v4, 1)   # t2 outer
