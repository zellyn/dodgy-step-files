"""Me119 — intersects_proper_mode_endpoint_touch: justproper mode skips endpoint-only contact.

MeshFix `Triangle.intersects` Branch 1 (*INTERSECTION_MODE_PROPER*):
'if (justproper)' — when the justproper flag is set the code applies strict
coincident vertex/edge tests and skips improper touching cases (vertex of
one triangle touching the interior of an edge or vertex of the other).
Without justproper, a vertex-touches-interior contact still counts.

Geometric signature: vertex v2 of t1 touches the interior of edge (v0,v1)
of t0 (T-junction geometry). In non-justproper mode this is an improper
intersection (v2 lies inside t0). In justproper mode no interior edge or
face is pierced, so the predicate returns false.

The fixture captures the geometry that triggers the justproper branch gate —
a T-junction where one triangle's vertex lands precisely on the other's edge.

Geometry:
  t0: (0,0,0)–(2,0,0)–(1,2,0)  — flat triangle in XY plane
  t1: (1,0,0)–(0,2,0)–(2,2,0)  — v3=(1,0,0) lies on edge (v0,v1) of t0
  t1 vertex v3 = midpoint of (v0,v1) → T-junction at (1,0,0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me119",
             title="intersects_proper_mode_endpoint_touch: T-junction vertex on edge — improper touching contact",
             defect_class="mesh_tjunction_vertex_on_edge")

v0 = m.vertex(0.0, 0.0, 0.0)   # t0 base left
v1 = m.vertex(2.0, 0.0, 0.0)   # t0 base right
v2 = m.vertex(1.0, 2.0, 0.0)   # t0 apex

# t1's first vertex is exactly on the midpoint of t0's base edge (v0,v1).
v3 = m.vertex(1.0, 0.0, 0.0)   # T-junction: midpoint of (v0,v1)
v4 = m.vertex(0.0, 2.0, 0.0)
v5 = m.vertex(2.0, 2.0, 0.0)

t0 = m.triangle(v0, v1, v2)
t1 = m.triangle(v3, v4, v5)

# v3 lies exactly on edge (v0,v1) of t0 — T-junction contact.
m.assert_vertex_on_edge(v3, v0, v1)

# t1's v3 vertex touches t0's base edge interior — an improper intersection.
# The justproper branch (Branch 1) is the gate that distinguishes whether
# this endpoint-only touch counts as an intersection.
m.assert_triangles_self_intersect(t0, t1)
