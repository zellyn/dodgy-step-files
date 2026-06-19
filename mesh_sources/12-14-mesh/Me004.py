"""Me004 — boundary_hole: triangulated patch missing one face (interior).

Catalog claim: 5×5 vertex grid that should be covered by 32 triangles (two
per cell), but one upper triangle of the center cell (2,2) is deliberately
omitted. The result is a closed boundary cycle of edges incident on only
one face — a true interior unfilled hole.

Defect carrier: triangle list omits cell (2,2)'s upper triangle. Healer
must detect the boundary cycle and either fill it (CGAL triangulate_hole,
MeshFix fillSmallBoundaries) or report it.

Using 5×5 (not 3×3) ensures the hole is interior — every edge of the
missing triangle is also incident on a triangle in an adjacent cell.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me004",
             title="boundary hole: interior cell of 5x5 patch missing upper triangle",
             defect_class="boundary_hole")

# 5×5 vertex grid in XY plane.
grid = [[m.vertex(i, j, 0.0) for j in range(5)] for i in range(5)]

# Two triangles per cell, except cell (2, 2) which is missing one triangle.
HOLE_CELL = (2, 2)
for i in range(4):
    for j in range(4):
        a = grid[i][j]
        b = grid[i + 1][j]
        c = grid[i + 1][j + 1]
        d = grid[i][j + 1]
        if (i, j) == HOLE_CELL:
            # Skip the upper triangle to leave an interior triangular hole.
            m.triangle(a, b, c)
            # m.triangle(a, c, d)   # omitted
        else:
            m.triangle(a, b, c)
            m.triangle(a, c, d)

# Hole boundary loop: the 3 vertices of the missing upper triangle.
a = grid[HOLE_CELL[0]][HOLE_CELL[1]]
c = grid[HOLE_CELL[0] + 1][HOLE_CELL[1] + 1]
d = grid[HOLE_CELL[0]][HOLE_CELL[1] + 1]
m.assert_hole_boundary([a, c, d])
