"""Me1173 — Basic_TMesh.forceNormalConsistence non_orientable_surface:
  triangle already marked in orientation pass → return without re-propagating
  (Branch 1).

MeshFix `Basic_TMesh.forceNormalConsistence` Branch 1 (*non_orientable_surface*)
  @ line 929:
  'if (isDMark(t)) return r;' —
  When forceNormalConsistence is called recursively on a triangle, it first
  checks if the triangle has already been visited (isDMark). If yes, the
  function returns immediately without re-processing. Branch 1 fires whenever
  the recursive descent encounters an already-marked triangle, preventing
  infinite loops and double-counting.

Defect pattern: a simple closed triangle fan around a central vertex — a
  tetrahedron-like mesh where all triangles have consistent CCW normals. When
  forceNormalConsistence is called on t0, it recursively propagates to t1,
  then to t2. From t2, the recursion tries to go back to t0 — but t0 is
  already marked (isDMark(t0)==true), so Branch 1 fires and t0 returns
  immediately. This prevents infinite recursion.

Geometry: tetrahedron — 4 vertices, 4 triangles, all consistently oriented.
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,0.87,0), v3=(0.5,0.29,0.82)
  t0=(v0,v1,v2), t1=(v0,v1,v3), t2=(v0,v2,v3), t3=(v1,v2,v3)
  All normals outward; chi=2 (closed surface, genus 0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1173",
    title="Basic_TMesh.forceNormalConsistence non_orientable_surface: already-marked triangle short-circuits recursion; tetrahedron all consistent (Branch 1)",
    defect_class="inverted_normal",
)

# Tetrahedron vertices
v0 = m.vertex(0.0,   0.0,   0.0)
v1 = m.vertex(1.0,   0.0,   0.0)
v2 = m.vertex(0.5,   0.87,  0.0)
v3 = m.vertex(0.5,   0.29,  0.82)

# Four consistently-oriented triangles (CCW from outside)
t0 = m.triangle(v0, v2, v1)   # 0: bottom (normal -Z)
t1 = m.triangle(v0, v1, v3)   # 1: front  (normal outward)
t2 = m.triangle(v1, v2, v3)   # 2: right  (normal outward)
t3 = m.triangle(v0, v3, v2)   # 3: left   (normal outward)

# All edges shared by exactly 2 triangles (closed manifold)
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Closed manifold: V=4, E=6, F=4, chi=2
m.assert_euler_characteristic(4, 6, 4, 2)
