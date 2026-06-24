"""Me1176 — Basic_TMesh.forceNormalConsistence recursion_base_case:
  recursive propagation halts on marked triangles at boundary of oriented set
  (Branch 4).

MeshFix `Basic_TMesh.forceNormalConsistence` Branch 4 (*recursion_base_case*)
  @ line 975:
  'forceNormalConsistence(t1, ...)' — recursive call that terminates when
  the called instance hits isDMark(t)==true at the start (Branch 1).
  Branch 4 is the recursive call site itself — it represents the propagation
  that will halt when it reaches already-marked triangles, establishing the
  recursion base case.

Defect pattern: a three-triangle fan where all triangles are consistently
  oriented. forceNormalConsistence is called on t0, marks it, then recursively
  calls itself on t1 and t2. From t1, it recursively tries t0 (already marked,
  Branch 1 halts) and t2 (not yet marked, continues). From t2, it tries t0 and
  t1 (both marked, Branch 1 halts twice). Branch 4 (the recursive call site)
  fires repeatedly throughout this traversal, with Branch 1 providing the
  actual termination.

Geometry: 3-triangle fan around central vertex v0.
  v0=(0,0,0) central, v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0)
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v1)  — all CCW
  Interior edges (v0,v1), (v0,v2), (v0,v3) each shared by 2 triangles.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1176",
    title="Basic_TMesh.forceNormalConsistence recursion_base_case: recursive call halts at already-marked triangles; 3-fan all consistent (Branch 4)",
    defect_class="inverted_normal",
)

# Central vertex + three outer vertices
v0 = m.vertex(0.0,   0.0,  0.0)   # 0 — fan center
v1 = m.vertex(1.0,   0.0,  0.0)   # 1 — right
v2 = m.vertex(0.0,   1.0,  0.0)   # 2 — top
v3 = m.vertex(-1.0,  0.0,  0.0)   # 3 — left

# Three CCW-oriented triangles of the fan
t0 = m.triangle(v0, v1, v2)   # 0: right sector, normal +Z
t1 = m.triangle(v0, v2, v3)   # 1: top sector, normal +Z
t2 = m.triangle(v0, v3, v1)   # 2: bottom sector, normal +Z

# Interior edges around the fan (each shared by 2 triangles)
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)

# Outer boundary edges (each owned by 1 triangle)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v1, v3, 1)

# Open mesh with one hole (center vertex v0 is a boundary vertex too):
# V=4, E=6, F=3, chi=1
m.assert_euler_characteristic(4, 6, 3, 1)
