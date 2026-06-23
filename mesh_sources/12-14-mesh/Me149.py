"""Me149 — isInnerPoint_closest_is_triangle: closest hit is triangle interior, return sign of normal.x.

MeshFix `Basic_TMesh.isInnerPoint` Branch 18 (*closest_is_triangle*) @ line 2066:
  'if (closest_triangle != NULL) return (closest_triangle->getVector().x > 0)'
  The final fallback branch fires when the closest ray-crossing point
  is strictly interior to a triangle (not on any vertex or edge). The
  predicate returns whether the triangle's outward normal X-component
  is positive — positive means the ray exits the mesh at this face
  (the point is inside), negative means the ray enters (point outside).

Geometric signature: a closed box-like mesh where the closest crossing
of an upward ray hits a triangle's interior. The triangle has a normal
with a positive X-component (faces outward in the +X direction), which
MeshFix uses as the "inside" indicator. Two triangles form a closed
wedge; the right face has its normal pointing in +X.

Geometry (wedge closed on 4 faces):
  v0=(0,0,0), v1=(2,0,0), v2=(2,0,1), v3=(0,0,1)  — base quad (split)
  v4=(1,2,0.5)  — apex
  t0=(v0,v1,v4), t1=(v1,v2,v4), t2=(v2,v3,v4), t3=(v3,v0,v4)  — 4 lateral faces
  t4=(v0,v3,v2,v1) split into t4=(v0,v3,v2), t5=(v0,v2,v1)    — base
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me149",
             title="isInnerPoint_closest_is_triangle: ray hits triangle interior, return sign(normal.x) determines inside/outside",
             defect_class="isInnerPoint_closest_is_triangle")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 1.0)   # 2
v3 = m.vertex(0.0, 0.0, 1.0)   # 3
v4 = m.vertex(1.0, 2.0, 0.5)   # 4 — apex

t0 = m.triangle(v0, v1, v4)    # 0 — front lateral face (normal points -Y direction)
t1 = m.triangle(v1, v2, v4)    # 1 — right lateral face (normal has +X component)
t2 = m.triangle(v2, v3, v4)    # 2 — back lateral face
t3 = m.triangle(v3, v0, v4)    # 3 — left lateral face (normal has -X component)
t4 = m.triangle(v0, v3, v2)    # 4 — base triangle 1
t5 = m.triangle(v0, v2, v1)    # 5 — base triangle 2

# All lateral edges shared by two triangles (closed watertight mesh).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v2, v3, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v0, v4, 2)
m.assert_edge_shared(v1, v4, 2)
m.assert_edge_shared(v2, v4, 2)
m.assert_edge_shared(v3, v4, 2)

# Base diagonal is interior (shared by t4 and t5).
m.assert_edge_shared(v0, v2, 2)

# Confirm the mesh is fully watertight: no boundary edges exist.
# The diagonal v1-v3 is NOT an edge in this mesh (the base is split via v0-v2).
# Asserting that the "other" diagonal has zero incidence confirms the quad split.
m.assert_edge_shared(v1, v3, 0)  # v1-v3 not in any triangle → base split correctly via v0-v2
