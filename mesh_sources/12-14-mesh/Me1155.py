"""Me1155 — PMP.orient component_orientation_selection: outward_orientation parameter
  controls inward vs outward assignment; CW-wound tetrahedron flipped outward (Branch 1).

CGAL PMP `PMP.orient` Branch 1 (*component_orientation_selection*) @ line 375:
  'if(outward_orientation(np)) orient_outward(cc); else orient_inward(cc);' —
  the orient function checks the outward_orientation named parameter to decide
  whether each connected component should have its normals pointing outward (the
  default) or inward. Branch 1 fires when the parameter is evaluated for the
  first component.

Defect pattern: a closed tetrahedron whose four faces are all wound clockwise when
  viewed from outside, giving inward-pointing normals. `PMP.orient` with
  outward_orientation=true must flip all faces so normals point outward. The mesh
  is manifold and topologically valid; only the winding sense is wrong.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,0.866,0), v3=(0.5,0.289,0.816)
  Four CW-wound faces forming a closed tetrahedron with chi=2.
  All face normals point inward initially — orient flips them outward.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1155",
    title="PMP.orient component_orientation_selection: outward_orientation flag evaluated for CW-wound closed tetrahedron (Branch 1)",
    defect_class="inverted_normals",
)

# Closed tetrahedron vertices.
v0 = m.vertex(0.0,   0.0,    0.0)    # 0 — base front-left
v1 = m.vertex(1.0,   0.0,    0.0)    # 1 — base front-right
v2 = m.vertex(0.5,   0.866,  0.0)    # 2 — base back
v3 = m.vertex(0.5,   0.289,  0.816)  # 3 — apex

# CW-wound faces (normals pointing inward) — all four faces of a tetrahedron.
t0 = m.triangle(v0, v2, v1)  # 0: base face (CW from above)
t1 = m.triangle(v0, v1, v3)  # 1: front-right face (CW from outside)
t2 = m.triangle(v1, v2, v3)  # 2: right-back face (CW from outside)
t3 = m.triangle(v2, v0, v3)  # 3: left face (CW from outside)

# Every edge is shared by exactly 2 faces — closed manifold.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# At least one face has downward-pointing (negative-Z component) normal due to CW winding.
m.assert_triangle_normal_z_negative(t0)

# Closed orientable manifold: V=4, E=6, F=4, chi=2.
m.assert_euler_characteristic(4, 6, 4, 2)
