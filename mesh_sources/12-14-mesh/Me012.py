"""Me012 — inconsistent_face_orientation: one flipped triangle in an otherwise CCW mesh.

Catalog claim: a patch of 4 triangles has one face with reversed winding.
Triangles 0, 1, 3 are wound CCW (normal pointing +Z); triangle 2 is wound CW
(normal pointing -Z). Adjacent triangles 2 and 3 share edge (v1,v5) but have
antiparallel normals — shading and CSG operations will produce a seam artefact.
CGAL orient / reverse_face_orientations and MeshFix forceNormalConsistence both
target this pattern.

Defect carrier: 6 vertices in two adjacent quads; triangle 2 has vertex order
(v1, v5, v2) instead of the consistent CCW order, flipping its normal to -Z.

Normals (cross product of first two edge vectors):
  Face 2 (v1,v5,v2): (v5-v1)×(v2-v1) = (1,1,0)×(1,0,0) = (0,0,-1) → -Z (CW)
  Face 3 (v1,v5,v4): (v5-v1)×(v4-v1) = (1,1,0)×(0,1,0) = (-1,0,1) → net +Z-ish (CCW)
  Dot product = -1 < 0 → inconsistent winding confirmed.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me012",
             title="inconsistent face orientation: triangle 2 wound CW inside CCW mesh",
             defect_class="inconsistent_face_orientation")

# 2×2 grid of vertices (XY plane, CCW = normal pointing +Z).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(2.0, 0.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
v4 = m.vertex(1.0, 1.0, 0.0)
v5 = m.vertex(2.0, 1.0, 0.0)

m.triangle(v0, v1, v3)   # face 0: CCW, normal +Z
m.triangle(v1, v4, v3)   # face 1: CCW, normal +Z
m.triangle(v1, v5, v2)   # face 2: CW (flipped!), normal -Z — the defect
m.triangle(v1, v5, v4)   # face 3: CCW normal, shares edge (v1,v5) with face 2

# Assert: triangles 2 and 3 share edge (v1,v5) but have antiparallel normals.
m.assert_adjacent_triangles_inconsistent_winding(2, 3)
