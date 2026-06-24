"""Me920 — keep_largest_component_count_mismatch: desired_num exceeds total component count; return 0.

Catalog claim: CGAL PMP.keep_largest_connected_components Branch 1 @
line 401 (*component_count_mismatch*) fires when the caller supplies a
desired_num that is greater than or equal to the actual number of connected
components. The function returns 0 immediately — no faces are removed
because the mesh already has fewer (or equal) components than requested.

Geometric signature: a single connected triangulated patch (one component).
If a caller asks to keep the largest 5 components, but total_components==1,
desired_num (5) >= total_components (1), so Branch 1 fires and returns 0.

Defect carrier: triangles 0-2 form a connected L-shaped strip (one
component). All three triangles share edges so the whole mesh is reachable
from t0. There is no second component — the nb_components_to_keep >
total_components condition is satisfied by design.

Source: CGAL PMP.keep_largest_connected_components Branch 1 @ line 401 —
*component_count_mismatch*: `if (nb_to_keep >= num_components) return 0`.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me920",
             title="keep_largest component_count_mismatch: desired_num > total_components → return 0",
             defect_class="disconnected_components")

# Single connected component: three triangles sharing edges (L-strip).
# v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0), v4=(2,0,0)
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
v4 = m.vertex(2.0, 0.0, 0.0)

# t0: (v0,v1,v2) — lower triangle of unit square
t0 = m.triangle(v0, v1, v2)  # area=0.5
# t1: (v0,v2,v3) — upper triangle of unit square; shares edge (v0,v2) with t0
t1 = m.triangle(v0, v2, v3)  # area=0.5
# t2: (v1,v4,v2) — extension triangle; shares edge (v1,v2) with t0
t2 = m.triangle(v1, v4, v2)  # area=0.5

# Assert connectivity: shared edges confirm single component.
# Edge (v0,v2) shared by t0 and t1; edge (v1,v2) shared by t0 and t2.
m.assert_edge_shared(v0, v2, 2)  # shared by t0 and t1 → connected
m.assert_edge_shared(v1, v2, 2)  # shared by t0 and t2 → connected

# Euler check: V=5, E=7 (3 interior + 4 boundary... actually: 3 inner edges?
# t0 has edges (v0,v1),(v1,v2),(v0,v2); t1 adds (v0,v3),(v2,v3); t2 adds (v1,v4),(v2,v4)
# Total distinct edges: 7. V=5, E=7, F=3, chi = 5-7+3 = 1 (open disk-like surface).
m.assert_euler_characteristic(v=5, e=7, f=3, chi=1)
