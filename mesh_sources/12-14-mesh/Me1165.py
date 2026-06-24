"""Me1165 — triangulate_and_refine_hole.main density_control_parameterization:
  density_control_factor parameter forwarded to refine(); triangular hole
  with density factor controlling Steiner vertex insertion (Branch 5).

CGAL PMP `triangulate_and_refine_hole.main` Branch 5 (*density_control_parameterization*)
  @ line 404:
  'refine(mesh, patch_facets.begin(), patch_facets.end(),
    std::back_inserter(patch_facets), vertex_out,
    density_control_factor(choose_parameter(...)));' —
  triangulate_and_refine_hole passes the density_control_factor named parameter
  to refine(). This controls how aggressively the refinement step inserts
  Steiner vertices to improve mesh quality. Branch 5 fires when this parameter
  is forwarded to refine().

Defect pattern: a triangular hole bordered by 3 hat-triangles — the minimal
  hole configuration for refine to act upon. density_control_factor is
  forwarded from the outer function to the refine call. The triangulated patch
  (1 new face from triangulate_hole) is then passed to refine; with
  density_control_factor > 1.4 (the default), refine may insert Steiner points
  to improve aspect ratios.

Geometry:
  Hole corners: s0=(0,0,0), s1=(3,0,0), s2=(1.5,2.6,0)
  Hat outer: s3=(1.5,-1.5,0), s4=(4.5,1,0), s5=(-1.5,1,0)
  t0=(s0,s3,s1), t1=(s1,s4,s2), t2=(s2,s5,s0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1165",
    title="triangulate_and_refine_hole.main density_control_parameterization: density_control_factor forwarded to refine(); triangular hole; Steiner insertion controlled (Branch 5)",
    defect_class="boundary_hole",
)

# Equilateral triangular hole boundary vertices.
s0 = m.vertex(0.0,   0.0,    0.0)   # 0 — left corner
s1 = m.vertex(3.0,   0.0,    0.0)   # 1 — right corner
s2 = m.vertex(1.5,   2.6,    0.0)   # 2 — top corner

# Hat outer vertices.
s3 = m.vertex(1.5,  -1.5,    0.0)   # 3 — south hat
s4 = m.vertex(4.5,   1.0,    0.0)   # 4 — SE hat
s5 = m.vertex(-1.5,  1.0,    0.0)   # 5 — SW hat

# Three hat triangles around the triangular hole.
t0 = m.triangle(s0, s3, s1)  # 0: south hat
t1 = m.triangle(s1, s4, s2)  # 1: SE hat
t2 = m.triangle(s2, s5, s0)  # 2: SW hat

# Hole boundary edges — each n=1.
m.assert_edge_shared(s0, s1, 1)
m.assert_edge_shared(s1, s2, 1)
m.assert_edge_shared(s0, s2, 1)

# Hat outer edges.
m.assert_edge_shared(s0, s3, 1)
m.assert_edge_shared(s1, s3, 1)
m.assert_edge_shared(s1, s4, 1)
m.assert_edge_shared(s2, s4, 1)
m.assert_edge_shared(s2, s5, 1)
m.assert_edge_shared(s0, s5, 1)

# Hole boundary loop.
m.assert_hole_boundary([s0, s1, s2])

# Open mesh with triangular hole: V=6, E=9, F=3, chi=0.
m.assert_euler_characteristic(6, 9, 3, 0)
