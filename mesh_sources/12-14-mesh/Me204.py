"""Me204 — zip_geometry_check_enabled: check_geom=true rejects zip when opposite vertices are distinct.

MeshFix `Vertex.zip` Branch 5 (*geometry_check_enabled*) @ line 571:
  'if (check_geom && ((*ov1)!=(*ov2))) return 0'
  After confirming both be1 and be2 are boundary, zip finds the opposite vertices ov1
  (opposite to be2 from the zip vertex) and ov2 (opposite to be1). With check_geom=true,
  if ov1 and ov2 have different coordinates, zip returns 0 — refusing to merge edges that
  would create a geometrically invalid seam.

Defect pattern: a boundary vertex v0 with exactly two boundary edges. Their opposite
vertices ov1 and ov2 are at clearly distinct positions. With check_geom=true, zip detects
the coordinate mismatch and returns 0.

Geometry: two isolated triangles sharing only v0. Each triangle has v0 as one vertex
and contributes one boundary edge incident on v0.
  v0=(0,0,0) — zip vertex
  t0=(v0,v1,v3): edges (v0,v1) boundary [be1], (v0,v3) boundary, (v1,v3) boundary
  t1=(v0,v2,v4): edges (v0,v2) boundary [be2], (v0,v4) boundary, (v2,v4) boundary
  ov1 = v3 = (0,1,0);  ov2 = v4 = (0,3,0)  — clearly distinct positions

No edges are shared between t0 and t1 (they only share the vertex v0, not any edge).
With check_geom=true, zip finds ov1 != ov2 by coordinates and returns 0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me204",
             title="zip_geometry_check_enabled: check_geom rejects zip when ov1 and ov2 have distinct coordinates",
             defect_class="zip_geometry_check_enabled")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — zip vertex; shared by both triangles
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — be1 far endpoint
v2 = m.vertex(-1.0, 0.0, 0.0)  # 2 — be2 far endpoint
v3 = m.vertex(0.0, 1.0, 0.0)   # 3 — ov1 (opposite to v0 via be2 side in t0)
v4 = m.vertex(0.0, 3.0, 0.0)   # 4 — ov2 (opposite to v0 via be1 side in t1); distinct

t0 = m.triangle(v0, v1, v3)    # 0 — triangle containing be1=(v0,v1); ov is v3
t1 = m.triangle(v0, v2, v4)    # 1 — triangle containing be2=(v0,v2); ov is v4

# be1 and be2 at v0 — both boundary (each incident on exactly 1 triangle)
m.assert_edge_shared(v0, v1, 1)  # be1 — boundary
m.assert_edge_shared(v0, v2, 1)  # be2 — boundary

# Other boundary edges (all n=1 since the two triangles share no edges)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v4, 1)

# Outer boundary holes: two disconnected open triangles meeting only at v0
# ov1=v3=(0,1,0) and ov2=v4=(0,3,0) — check_geom sees (*ov1)!=(*ov2) → return 0
m.assert_hole_boundary([v0, v1, v3])
m.assert_hole_boundary([v0, v2, v4])
