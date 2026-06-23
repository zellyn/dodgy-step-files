"""Me111 — intersects_shared_edge_proper: adjacent triangles sharing an edge — Branch 3 returns false.

MeshFix `Triangle.intersects` Branch 3 (*SHARED_EDGE_PROPER*):
'if (eq1 && eq2)' — triangles share an edge (vertex pairs 1 and 2 of t1
match vertex pairs of t2). In proper mode (justproper) the code checks
whether the opposite vertex of t2 lies on the same side of the shared-edge
plane as implied by the coplanar condition. For a standard manifold fold
(free vertices on non-crossing sides), the predicate returns false.

Geometric signature: a clean two-triangle patch (a folded quad) where both
triangles share edge (v0,v1) and their free vertices (v2, v3) lie in non-
intersecting half-spaces. MeshFix Branch 3 recognizes the shared edge and
returns false without running the full geometric intersection test.

The defect this fixture exposes: a repair tool MUST recognize shared-edge
adjacency as non-intersecting before attempting topological repairs — failing
to do so would incorrectly trigger SI-repair on every manifold face pair.

Geometry:
  Shared edge: v0=(0,0,0), v1=(1,0,0)
  t0 free vertex: v2=(0.5, 0.0, 1.0)   — above the base in Z
  t1 free vertex: v3=(0.5, 1.0, 0.0)   — in front in Y
  t0 = (v0, v1, v2)
  t1 = (v0, v1, v3)   — shared edge (v0,v1); free vertices in distinct planes
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me111",
             title="intersects_shared_edge_proper: manifold adjacent triangles sharing an edge — Branch 3 returns false",
             defect_class="mesh_adjacent_shared_edge")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 0.0, 1.0)   # t0 free vertex — in XZ plane
v3 = m.vertex(0.5, 1.0, 0.0)   # t1 free vertex — in XY plane

t0 = m.triangle(v0, v1, v2)
t1 = m.triangle(v0, v1, v3)

# Shared edge is incident on exactly 2 triangles (manifold fold).
m.assert_edge_shared(v0, v1, 2)

# Free vertices are on strictly non-overlapping sides; the two free boundary
# edges confirm each triangle has exactly one boundary edge.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
