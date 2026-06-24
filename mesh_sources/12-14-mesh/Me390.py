"""Me390 — do_faces_intersect branch 1: shared-edge-vs-incident-vertex.

PMP.do_faces_intersect Branch 1 (*shared-edge-vs-incident-vertex*) @ line 238:
  Tests whether two faces share a full edge (not just a vertex); when they do,
  the algorithm switches from the full geometric SI check to a coplanarity +
  orientation check. Branch 1 fires when `faces_have_a_shared_edge` evaluates
  true.

The fixture models two coplanar triangles that share edge (v0,v1) and whose
interiors overlap (b lies entirely inside a's area). Because they are coplanar
and share a full edge, Branch 1 routes to the coplanar overlap check — which
detects the overlapping interiors as a self-intersection.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(0,2,0), v3=(1,1,0)
  t0=(v0,v1,v2): large triangle in XY plane
  t1=(v0,v1,v3): smaller triangle sharing edge (v0,v1); v3 is inside t0's area
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me390",
    title="do_faces_intersect shared-edge: coplanar triangles sharing full edge with overlapping interiors",
    defect_class="self_intersection_face_pair",
)

# Shared edge between t0 and t1.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(2.0, 0.0, 0.0)  # 1
# t0: large triangle in XY plane.
v2 = m.vertex(0.0, 2.0, 0.0)  # 2: apex of large triangle
# t1: small triangle, same plane, sharing edge v0-v1; v3 is inside t0's area.
v3 = m.vertex(1.0, 1.0, 0.0)  # 3: apex of small triangle — inside t0

t0 = m.triangle(v0, v1, v2)   # 0: large triangle
t1 = m.triangle(v0, v1, v3)   # 1: small triangle sharing edge (v0,v1)

# Shared edge (v0,v1) is incident on BOTH triangles.
m.assert_edge_shared(v0, v1, 2)
# Coplanar overlapping interiors → self-intersection.
m.assert_triangles_self_intersect(t0, t1)
