"""Me004 — boundary_hole: triangulated patch missing one face.

Catalog claim: the mesh is a 3x3 vertex grid that should be covered
by 8 triangles (a unit square split into two triangles per cell), but
one triangle has been deliberately omitted. The result is a closed
boundary cycle of edges incident to only one face — an unfilled hole.

Defect carrier: triangle list literally omits the missing face. A
healer must detect the boundary cycle and either fill it (CGAL
triangulate_hole, MeshFix fillSmallBoundaries) or report it.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me004",
             title="boundary hole: 3x3 patch with one triangle missing",
             defect_class="boundary_hole")

# 3x3 vertex grid in XY plane.
grid = [[m.vertex(i, j, 0.0) for j in range(3)] for i in range(3)]

# Two triangles per cell, except cell (1, 1) which is missing one triangle.
for i in range(2):
    for j in range(2):
        a = grid[i][j]
        b = grid[i+1][j]
        c = grid[i+1][j+1]
        d = grid[i][j+1]
        if (i, j) == (1, 1):
            # Skip the upper triangle to leave a triangular hole.
            m.triangle(a, b, c)
            # m.triangle(a, c, d)   # omitted
        else:
            m.triangle(a, b, c)
            m.triangle(a, c, d)

# Hole boundary: vertices around the missing triangle (a, c, d in cell 1,1).
a = grid[1][1]
c = grid[2][2]
d = grid[1][2]
m.assert_hole_boundary([a, c, d])
