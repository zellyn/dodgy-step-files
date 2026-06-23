"""Me007 — inverted_normals: closed tetrahedron wound inward (CW in right-hand system).

Catalog claim: all four triangles of a tetrahedron are wound clockwise when
viewed from outside. The mesh is topologically closed and manifold, but the
implied volume is negative — every normal points inward. CGAL
is_outward_oriented returns False; orient_to_bound_a_volume must flip all faces.

Defect carrier: triangle list winds every face so that the cross product
(v1-v0) × (v2-v0) points toward the interior of the tetrahedron.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me007",
             title="inverted normals: tetrahedron with all faces wound inward (CW)",
             defect_class="inverted_normals")

# Tetrahedron vertices.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, 0.5, 1.0)

# Standard CCW winding would be (v0,v1,v2), (v0,v2,v3), (v0,v3,v1), (v1,v3,v2).
# Invert each by swapping last two vertices → all normals flip inward.
m.triangle(v0, v2, v1)   # face 0: base, CW → normal points down (-Z)
m.triangle(v0, v3, v2)   # face 1: CW → normal points inward
m.triangle(v0, v1, v3)   # face 2: CW → normal points inward
m.triangle(v1, v2, v3)   # face 3: CW → normal points inward

# Assert that face 0 (base in XY plane) has inward (downward) normal.
# The base triangle (v0,v2,v1) with v0=(0,0,0), v2=(0.5,1,0), v1=(1,0,0):
# (v2-v0) × (v1-v0) = (0.5,1,0)×(1,0,0) = (0*0-0*0, 0*1-0.5*0, 0.5*0-1*1) = (0, 0, -0.5)
# z-component is negative → normal points in -Z direction (inward for a base face).
m.assert_triangle_normal_z_negative(0)
