"""Me141 — isInnerPoint_yz_bbox_reject: query point outside triangle's Y-Z bounding box.

MeshFix `Basic_TMesh.isInnerPoint` Branch 2 (*yz_bounding_box_reject*) @ line 1995:
  'if (v1->y > p.y || ...) continue'
  Branch 3 (*z-axis bbox*) @ line 1997:
  'if (v1->z > p.z || ...) continue'
  For each triangle in the mesh, isInnerPoint first checks whether the
  query point p falls within the triangle's Y-Z bounding box. If p.y or
  p.z is outside the triangle's extent on those axes, the triangle is
  skipped without any intersection computation.

Geometric signature: a single flat triangle in the Z=0 plane, with all
vertices at y ∈ [0, 2] and z ∈ [0, 1]. A query point at y=5.0 is above
the triangle's Y-Z bounding box; a query point at z=5.0 is above the
Z-extent. Both queries trigger the skip branch.

Geometry (in XY-plane, z=0):
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0)
  One triangle: t0=(v0,v1,v2) — Y∈[0,2], Z∈[0,0]

The triangle hole_boundary assertion confirms the three boundary edges
(open mesh — no other face shares these edges).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me141",
             title="isInnerPoint_yz_bbox_reject: query point outside triangle Y-Z extent, skip branch fires",
             defect_class="isInnerPoint_yz_bbox_reject")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2

t0 = m.triangle(v0, v1, v2)    # 0 — single open triangle

# All three edges are boundary (incident on exactly 1 triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Confirm boundary loop: the Y-Z extent of the triangle is [0,2]×[0,0],
# so a point at y=5 or z=5 lies outside this box → bbox-reject.
m.assert_hole_boundary([v0, v1, v2])
