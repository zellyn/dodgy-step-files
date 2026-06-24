"""Me1158 — PMP.orient_to_bound_a_volume single_component_trivial: one closed CC;
  num_components==1 path; orient directly outward without nesting analysis (Branch 1).

CGAL PMP `PMP.orient_to_bound_a_volume` Branch 1 (*single_component_trivial*) @ line 975:
  'if(num_components == 1) { orient_to_bound_a_volume_single(mesh, np); return; }' —
  when the mesh has exactly one connected component, orient_to_bound_a_volume
  takes a fast path: it orients the single component so its normals point
  outward, without running any nesting/ray-casting analysis. Branch 1 fires
  when the component count equals 1.

Defect pattern: a single closed tetrahedron with CW-wound faces (inward normals).
  orient_to_bound_a_volume detects num_components=1, takes the trivial single-
  component path, and flips all faces so normals point outward.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,0.866,0), v3=(0.5,0.289,0.816)
  All four CW-wound faces — normals point inward initially.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1158",
    title="PMP.orient_to_bound_a_volume single_component_trivial: single CW-wound closed tetrahedron; num_components==1 fast-path (Branch 1)",
    defect_class="inverted_normals",
)

v0 = m.vertex(0.0,  0.0,    0.0)    # 0 — base front-left
v1 = m.vertex(1.0,  0.0,    0.0)    # 1 — base front-right
v2 = m.vertex(0.5,  0.866,  0.0)    # 2 — base back
v3 = m.vertex(0.5,  0.289,  0.816)  # 3 — apex

# CW-wound faces — normals point inward.
t0 = m.triangle(v0, v2, v1)  # 0: base face (CW)
t1 = m.triangle(v0, v1, v3)  # 1: front-right face (CW)
t2 = m.triangle(v1, v2, v3)  # 2: right-back face (CW)
t3 = m.triangle(v2, v0, v3)  # 3: left face (CW)

# All 6 edges shared by exactly 2 faces — closed manifold.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Base face normal points in -Z direction due to CW winding.
m.assert_triangle_normal_z_negative(t0)

# One closed manifold component: V=4, E=6, F=4, chi=2.
m.assert_euler_characteristic(4, 6, 4, 2)
