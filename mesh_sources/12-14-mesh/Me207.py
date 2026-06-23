"""Me207 — zip_edge_triangle_selection: be2's incident triangle selected via t1 or t2 slot.

MeshFix `Vertex.zip` Branch 8 (*edge_triangle_selection*) @ line 581:
  't = (be2->t1!=NULL)?(be2->t1):(be2->t2)'
  After merging ov1/ov2, zip retrieves the single incident triangle of boundary edge be2.
  Because boundary edges have exactly one incident triangle, zip checks which slot (t1 or
  t2) holds it via a ternary. Branch 8 covers this slot selection.

Defect pattern: an open boundary vertex v0 where be2 is a boundary edge incident on
exactly one triangle. The ternary selects whichever of the two triangle slots (t1 or t2)
is non-NULL. This is confirmed by asserting be2 has n=1 incidence.

Geometry: simple open two-triangle fan at v0. be1=(v0,v1), be2=(v0,v2) each incident
on exactly one triangle. The triangle selection for be2 retrieves the one incident face
for the subsequent edge-update step.
  v0=(0,0,0), v1=(1,0,0), v2=(-1,0,0), v3=(0,1,0)
  t0=(v0,v1,v3) — be1=(v0,v1) is boundary; incident on t0
  t1=(v0,v3,v2) — be2=(v0,v2) is boundary; incident on t1 → Branch 8 selects t1
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me207",
             title="zip_edge_triangle_selection: be2 is boundary with exactly 1 incident triangle; ternary selects t1 or t2 slot",
             defect_class="zip_edge_triangle_selection")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — zip vertex
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — be1 endpoint
v2 = m.vertex(-1.0, 0.0, 0.0)  # 2 — be2 endpoint
v3 = m.vertex(0.0, 1.0, 0.0)   # 3 — shared interior apex

t0 = m.triangle(v0, v1, v3)    # 0 — be1=(v0,v1) boundary; t1 slot of be1
t1 = m.triangle(v0, v3, v2)    # 1 — be2=(v0,v2) boundary; t selected via Branch 8

# be1 boundary — incident on exactly 1 triangle
m.assert_edge_shared(v0, v1, 1)

# be2 boundary — incident on exactly 1 triangle → Branch 8 ternary selects it
m.assert_edge_shared(v0, v2, 1)

# Interior edge shared by both triangles
m.assert_edge_shared(v0, v3, 2)

# Outer boundary edges
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)
