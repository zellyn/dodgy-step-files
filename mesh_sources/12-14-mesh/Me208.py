"""Me208 — zip_triangle_edge_update: triangle's reference to be2 is replaced with be1.

MeshFix `Vertex.zip` Branch 9 (*triangle_edge_update*) @ line 582:
  't->replaceEdge(be2, be1)'
  After selecting the incident triangle t from be2, zip calls t->replaceEdge(be2, be1)
  to update the triangle's edge record: be2 is removed and be1 takes its place. This
  completes the boundary-edge merge step. Branch 9 covers this triangle edge-pointer update.

Defect pattern: boundary vertex v0 with be1 and be2 as its two boundary edges. The
triangle t incident on be2 currently references be2 as one of its boundary edges. After
zip, that triangle's edge record is updated to point to be1 instead, and be2 becomes
unused. This is the structural update that merges the two open seam edges into one.

Geometry: asymmetric two-triangle open fan where be2 has its single incident triangle
on one side (the update target) and be1 is on the other side.
  v0=(0,0,0), v1=(1,0,0), v2=(-1,0,0), v3=(0,1,0)
  t0=(v0,v1,v3) — be1=(v0,v1); this triangle keeps be1
  t1=(v0,v3,v2) — be2=(v0,v2); Branch 9 updates t1 to drop be2 and use be1

The oracle asserts be2 is a boundary edge (n=1) so the fixture demonstrates that
t1 currently references be2 before the update. After replaceEdge, the mesh would
no longer have be2 as a boundary — but the pre-repair fixture captures the state
where t1 still references be2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me208",
             title="zip_triangle_edge_update: t->replaceEdge(be2, be1) swaps be2 out of triangle's edge record during zip",
             defect_class="zip_triangle_edge_update")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — zip vertex
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — be1 endpoint
v2 = m.vertex(-1.0, 0.0, 0.0)  # 2 — be2 endpoint (be2 will be replaced in t1)
v3 = m.vertex(0.0, 1.0, 0.0)   # 3 — apex (interior edge (v0,v3))

t0 = m.triangle(v0, v1, v3)    # 0 — references be1=(v0,v1); unaffected by Branch 9
t1 = m.triangle(v0, v3, v2)    # 1 — references be2=(v0,v2); Branch 9 replaces be2→be1

# be1 is boundary (incident on t0 only)
m.assert_edge_shared(v0, v1, 1)

# be2 is boundary (incident on t1 only) — this is the edge that gets replaced in t1
m.assert_edge_shared(v0, v2, 1)

# Interior shared edge (v0,v3) shared by both triangles
m.assert_edge_shared(v0, v3, 2)

# Confirm t1 is a valid triangle with a boundary edge at (v0,v2)
# Outer boundary edges
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Hole boundary loop: the open seam that zip would close (be1→be2 merge)
m.assert_hole_boundary([v0, v1, v3, v2])
