"""Me1163 — triangulate_and_refine_hole.main triangulation_failure_handling:
  triangulate_hole called before refine; successful triangulation produces
  patch; refine runs on non-empty patch (Branch 3).

CGAL PMP `triangulate_and_refine_hole.main` Branch 3 (*triangulation_failure_handling*)
  @ line 394:
  'triangulate_hole(mesh, border_halfedge, std::back_inserter(patch_facets), ...);
   // then: refine(mesh, patch_facets, ...)' —
  triangulate_and_refine_hole calls triangulate_hole first to fill the hole
  boundary, collecting new face descriptors in patch_facets. If triangulation
  succeeds the patch is non-empty and refine runs on it. If triangulation
  fails patch_facets is empty and refine is a no-op. Branch 3 fires when the
  triangulate_hole call is made and patch_facets is built.

Defect pattern: a pentagonal hole bordered by five hat-triangles. triangulate_hole
  fills the 5-edge hole with 3 new triangles, populating patch_facets. Refine
  then runs on those 3 faces. The triangulation succeeds, demonstrating the
  successful-fill path.

Geometry:
  Pentagon corners: p0=(0,0,0), p1=(2,0,0), p2=(2.6,1.9,0),
                    p3=(1,3,0), p4=(-0.6,1.9,0)
  Hat outer vertices: p5=(1,-1.2,0), p6=(3.5,0.5,0), p7=(3,3,0),
                      p8=(1,4.2,0), p9=(-1.5,0.5,0)
  t0=(p0,p5,p1), t1=(p1,p6,p2), t2=(p2,p7,p3), t3=(p3,p8,p4), t4=(p4,p9,p0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1163",
    title="triangulate_and_refine_hole.main triangulation_failure_handling: 5-edge hole; triangulate_hole fills patch; refine runs on non-empty result (Branch 3)",
    defect_class="boundary_hole",
)

# Pentagon hole boundary vertices.
p0 = m.vertex(0.0,   0.0,   0.0)    # 0
p1 = m.vertex(2.0,   0.0,   0.0)    # 1
p2 = m.vertex(2.6,   1.9,   0.0)    # 2
p3 = m.vertex(1.0,   3.0,   0.0)    # 3
p4 = m.vertex(-0.6,  1.9,   0.0)    # 4

# Hat outer vertices.
p5 = m.vertex(1.0,   -1.2,  0.0)    # 5 — south hat
p6 = m.vertex(3.5,   0.5,   0.0)    # 6 — SE hat
p7 = m.vertex(3.0,   3.0,   0.0)    # 7 — NE hat
p8 = m.vertex(1.0,   4.2,   0.0)    # 8 — north hat
p9 = m.vertex(-1.5,  0.5,   0.0)    # 9 — NW hat

# Five hat triangles surrounding the pentagonal hole.
t0 = m.triangle(p0, p5, p1)  # 0: south hat
t1 = m.triangle(p1, p6, p2)  # 1: SE hat
t2 = m.triangle(p2, p7, p3)  # 2: NE hat
t3 = m.triangle(p3, p8, p4)  # 3: north hat
t4 = m.triangle(p4, p9, p0)  # 4: NW hat

# Hole boundary edges — each n=1.
m.assert_edge_shared(p0, p1, 1)
m.assert_edge_shared(p1, p2, 1)
m.assert_edge_shared(p2, p3, 1)
m.assert_edge_shared(p3, p4, 1)
m.assert_edge_shared(p0, p4, 1)

# Hat outer boundary edges.
m.assert_edge_shared(p0, p5, 1)
m.assert_edge_shared(p1, p5, 1)
m.assert_edge_shared(p1, p6, 1)
m.assert_edge_shared(p2, p6, 1)
m.assert_edge_shared(p2, p7, 1)
m.assert_edge_shared(p3, p7, 1)
m.assert_edge_shared(p3, p8, 1)
m.assert_edge_shared(p4, p8, 1)
m.assert_edge_shared(p4, p9, 1)
m.assert_edge_shared(p0, p9, 1)

# Hole boundary loop.
m.assert_hole_boundary([p0, p1, p2, p3, p4])

# Open mesh with pentagonal hole: V=10, E=15, F=5, chi=0.
m.assert_euler_characteristic(10, 15, 5, 0)
