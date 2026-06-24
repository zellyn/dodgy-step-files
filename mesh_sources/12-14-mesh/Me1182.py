"""Me1182 — triangulate_hole.main geometry_traits_deduction: explicit vs
  deduced geometric traits — CGAL::Kernel_traits deduces from point type
  (Branch 6).

CGAL PMP `triangulate_hole.main` Branch 6 (*geometry_traits_deduction*)
  @ line 231:
  'typename GetGeomTraits<PolygonMesh, NamedParameters>::type GT;' —
  The last branch in triangulate_hole.main is the geometry-traits deduction
  system. If the caller provides an explicit geom_traits named parameter, that
  is used directly. Otherwise, GetGeomTraits applies CGAL::Kernel_traits to
  deduce the geometric traits from the PolygonMesh's point type. Branch 6
  fires for every call where the default (deduced) traits path is taken —
  which is the common case when no explicit traits are supplied.

Defect pattern: a triangular hole in a mesh — the minimal hole that
  triangulate_hole.main can fill. Branch 6 fires when the traits are deduced
  from the PolygonMesh point type rather than explicitly provided. This is the
  normal/default calling convention. The fixture demonstrates a 3-edge hole
  that the function will fill by deducing Kernel_traits from the PolygonMesh's
  vertex point type.

Geometry: triangular hole with three hat triangles.
  a0=(0,0,0), a1=(3,0,0), a2=(1.5,2.6,0): hole corners
  b0=(1.5,-1.5,0), b1=(4.5,1,0), b2=(-1.5,1,0): outer hat vertices
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1182",
    title="triangulate_hole.main geometry_traits_deduction: GetGeomTraits deduces traits from point type; triangular hole; default deduction path (Branch 6)",
    defect_class="boundary_hole",
)

# Triangular hole corners
a0 = m.vertex(0.0,   0.0,   0.0)   # 0 — left
a1 = m.vertex(3.0,   0.0,   0.0)   # 1 — right
a2 = m.vertex(1.5,   2.6,   0.0)   # 2 — top

# Hat outer vertices
b0 = m.vertex(1.5,  -1.5,   0.0)   # 3 — south hat
b1 = m.vertex(4.5,   1.0,   0.0)   # 4 — SE hat
b2 = m.vertex(-1.5,  1.0,   0.0)   # 5 — SW hat

# Three hat triangles
t0 = m.triangle(a0, b0, a1)   # 0: south
t1 = m.triangle(a1, b1, a2)   # 1: SE
t2 = m.triangle(a2, b2, a0)   # 2: SW

# Hole boundary edges (n=1)
m.assert_edge_shared(a0, a1, 1)
m.assert_edge_shared(a1, a2, 1)
m.assert_edge_shared(a0, a2, 1)

m.assert_hole_boundary([a0, a1, a2])

# Hat outer edges (n=1)
m.assert_edge_shared(a0, b0, 1)
m.assert_edge_shared(a1, b0, 1)
m.assert_edge_shared(a1, b1, 1)
m.assert_edge_shared(a2, b1, 1)
m.assert_edge_shared(a2, b2, 1)
m.assert_edge_shared(a0, b2, 1)

# Open mesh with triangular hole: V=6, E=9, F=3, chi=0
m.assert_euler_characteristic(6, 9, 3, 0)
