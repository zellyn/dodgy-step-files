"""Me257 — openToDisk_non_boundary_edge_dup: interior edge duplicated to cut mesh to disk (Branch 8).

MeshFix `Basic_TMesh.openToDisk` Branch 8 (*non_boundary_edge_dup*) @ line 1844:
  '!IS_BIT(e, 3) && !e->isOnBoundary()' — interior edge not yet in spanning tree;
  duplicate it (newEdge) to convert the mesh to disk topology.

After tracing all boundary cycles, openToDisk cuts the mesh to disk topology by
identifying interior edges not yet marked in the spanning tree and duplicating them.
Duplicating an interior edge is the topological "cut" that opens a handle (genus
reduction). For a genus-g mesh, exactly g interior edges must be cut.

Geometry: a triangulated torus-like surface with genus 1 — a closed mesh with one
handle. This requires V-E+F = 0 (Euler characteristic of the torus). A minimal
triangulation of the torus uses 7 vertices and 14 triangles (Möbius-Heawood), but
for fixture compactness we use a "square torus" identification: a rectangular grid
with opposite edges identified.

Simpler: construct a genus-1 open mesh by connecting two disks via a tube. Here we
use a rectangular band (cylinder surface) where the seam edge is the non-boundary
interior edge that must be duplicated. A cylinder has 0 handles but we can create
a figure-8 connected strip.

Most compact genus-1 surface: an octahedron (genus 0) won't work.
A "handle" on a disk: take a triangulated disk and attach a bridge between two
interior edges.

Clearest minimal example: a triangulated annulus where top and bottom boundary loops
are identified (glued) — creating a torus. But that's hard to represent in triangle soup.

Alternative: a "twisted strip" or a direct numerical construction. Use a cube surface
(genus 0) plus an added handle bridge.

For fixture clarity: we use a small cylindrical band — 2 rings × 4 triangles = 8
triangles, closed top and bottom with caps (triangle fans), giving a sphere. Then
remove caps to get a cylinder (genus 0 with 2 boundary loops). Not genus 1.

Most direct: an octahedron with 2 extra triangles pinching a handle. This is complex.

PRACTICAL CHOICE: Use a closed triangulated square mesh (4×4 grid with wrap-around
in both directions = torus). With V=9, E=18, F=9... V-E+F = 0 for torus.

Compact torus triangulation:
  Grid 3×3 with both axes wrapped: 9 vertices, 18 triangles, 27 edges.
  chi = 9 - 27 + 18 = 0. This IS a torus!

Vertices: v(i,j) for i,j in {0,1,2}, identified as (i mod 3, j mod 3).
v0=(0,0), v1=(1,0), v2=(2,0), v3=(0,1), v4=(1,1), v5=(2,1), v6=(0,2), v7=(1,2), v8=(2,2)
Triangulation (each square → 2 triangles):
  Square (i,j): UL=(i,j), UR=(i+1,j), LL=(i,j+1), LR=(i+1,j+1) (mod 3)

Squares and their triangles:
  (0,0): v0,v1,v3  and  v1,v4,v3
  (1,0): v1,v2,v4  and  v2,v5,v4
  (2,0): v2,v0,v5  and  v0,v3,v5  [wraps: col 3 → col 0]
  (0,1): v3,v4,v6  and  v4,v7,v6
  (1,1): v4,v5,v7  and  v5,v8,v7
  (2,1): v5,v3,v8  and  v3,v6,v8  [wraps]
  (0,2): v6,v7,v0  and  v7,v1,v0  [wraps: row 3 → row 0]
  (1,2): v7,v8,v1  and  v8,v2,v1  [wraps]
  (2,2): v8,v6,v2  and  v6,v0,v2  [wraps]

Total: 18 triangles, 9 vertices → 27 edges → chi = 9-27+18 = 0. Torus.

We need to pick ACTUAL 3D coordinates for these 9 "torus" vertices, since the
torus topology is represented as a flat grid in 3D (geometrically self-intersecting
when embedded, but topologically correct for the defect test).

Use a flat 3×3 grid [0,3]×[0,3] in z=0 with wrap-around edges identified:
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me257",
             title="openToDisk_non_boundary_edge_dup: torus (chi=0) — interior edges must be duplicated to open to disk",
             defect_class="open_to_disk_edge_dup")

# 3×3 torus triangulation embedded in flat 3D (geometrically self-intersecting).
# Vertex (i,j) placed at (i, j, 0) for i,j in {0,1,2}.
v0 = m.vertex(0.0, 0.0, 0.0)   # (0,0)
v1 = m.vertex(1.0, 0.0, 0.0)   # (1,0)
v2 = m.vertex(2.0, 0.0, 0.0)   # (2,0)
v3 = m.vertex(0.0, 1.0, 0.0)   # (0,1)
v4 = m.vertex(1.0, 1.0, 0.0)   # (1,1)
v5 = m.vertex(2.0, 1.0, 0.0)   # (2,1)
v6 = m.vertex(0.0, 2.0, 0.0)   # (0,2)
v7 = m.vertex(1.0, 2.0, 0.0)   # (1,2)
v8 = m.vertex(2.0, 2.0, 0.0)   # (2,2)

# 18 triangles covering all 9 squares with wrap-around identification.
# Square (0,0):
m.triangle(v0, v1, v3)    # 0
m.triangle(v1, v4, v3)    # 1
# Square (1,0):
m.triangle(v1, v2, v4)    # 2
m.triangle(v2, v5, v4)    # 3
# Square (2,0) — wraps col 3→0: right column is v0,v3 (col 0)
m.triangle(v2, v0, v5)    # 4
m.triangle(v0, v3, v5)    # 5
# Square (0,1):
m.triangle(v3, v4, v6)    # 6
m.triangle(v4, v7, v6)    # 7
# Square (1,1):
m.triangle(v4, v5, v7)    # 8
m.triangle(v5, v8, v7)    # 9
# Square (2,1) — wraps col: right is v3,v6
m.triangle(v5, v3, v8)    # 10
m.triangle(v3, v6, v8)    # 11
# Square (0,2) — wraps row 3→0: bottom row is v0,v1 (row 0)
m.triangle(v6, v7, v0)    # 12
m.triangle(v7, v1, v0)    # 13
# Square (1,2) — wraps row:
m.triangle(v7, v8, v1)    # 14
m.triangle(v8, v2, v1)    # 15
# Square (2,2) — wraps row+col:
m.triangle(v8, v6, v2)    # 16
m.triangle(v6, v0, v2)    # 17

# On a torus all edges are interior (shared by exactly 2 triangles).
# The "horizontal" and "vertical" edges are all interior — openToDisk must
# duplicate some of them to cut the torus to a disk.

# Verify a few representative interior edges (chi=0 handles these via euler_characteristic).
# Interior horizontal edges (non-boundary — must be duplicated in openToDisk Branch 8):
m.assert_edge_shared(v0, v1, 2)   # horizontal interior (bottom row)
m.assert_edge_shared(v1, v2, 2)   # horizontal interior
m.assert_edge_shared(v2, v0, 2)   # horizontal wrap-around interior

# Interior vertical edges:
m.assert_edge_shared(v0, v3, 2)   # vertical interior (left column)
m.assert_edge_shared(v3, v6, 2)   # vertical interior
m.assert_edge_shared(v6, v0, 2)   # vertical wrap-around interior

# Diagonal edges (one per square, all interior):
m.assert_edge_shared(v1, v3, 2)   # diagonal of square (0,0)
m.assert_edge_shared(v2, v4, 2)   # diagonal of square (1,0)
m.assert_edge_shared(v0, v5, 2)   # diagonal of square (2,0)

# Euler characteristic of torus: V=9, E=27, F=18, chi=0.
m.assert_euler_characteristic(9, 27, 18, 0)
