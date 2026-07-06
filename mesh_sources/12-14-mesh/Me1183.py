"""Me1183 — polygon-soup box-corner: THREE coincident-but-distinct copies of a
  shared corner vertex leave un-welded seam cracks where three faces meet.

Input pattern (defect class: multi_vertex_seam_crack):
  A polygon soup of the corner of a box where three planar faces (XY, YZ, XZ)
  meet at the origin. Each face was exported with its OWN copy of every vertex
  it touches — the standard behaviour of a naive STL/OBJ writer that does not
  share vertices across faces. The result is that the single geometric corner
  point (0,0,0) is represented by THREE distinct vertex records (indices 0, 3,
  6), and each shared box edge is represented by TWO coincident-but-distinct
  edges (one per adjacent face). Because the indices differ, the half-edge
  structure never pairs the seams: every seam edge is incident on exactly one
  triangle, so instead of a watertight 3-face corner the mesh has three open
  cracks radiating from the corner.

  This is the >2-coincident-vertex generalization of the classic near-
  coincident-vertex pair (Me003, Me281): a seam where MORE THAN TWO distinct
  vertices sit at one position, which a pairwise snap/merge must collapse to a
  single vertex before the cracks can be stitched. A robust kernel must merge
  all three copies (CGAL merge_duplicate_points_in_polygon_soup / snap_vertices
  with a multiplicity > 2 cluster) and then stitch the coincident edge pairs.

Geometry (all faces as a single corner triangle, unwelded):
  Face XY (z=0): 0=(0,0,0)  1=(1,0,0)  2=(0,1,0)
  Face YZ (x=0): 3=(0,0,0)  4=(0,1,0)  5=(0,0,1)
  Face XZ (y=0): 6=(0,0,0)  7=(0,0,1)  8=(1,0,0)
  Corner copies 0,3,6 are all at (0,0,0) — three coincident distinct vertices.
  Seam +x is edge (0,1)[XY] coincident with edge (6,8)[XZ]; unshared → crack.
  Seam +z is edge (3,5)[YZ] coincident with edge (6,7)[XZ]; unshared → crack.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1183",
    title="polygon-soup box corner: three coincident-but-distinct copies of the shared corner vertex leave un-welded seam cracks (multi-vertex seam)",
    defect_class="multi_vertex_seam_crack",
)

# Face XY (z=0) — its own copies
xy0 = m.vertex(0.0, 0.0, 0.0)   # 0 — corner copy A
xy1 = m.vertex(1.0, 0.0, 0.0)   # 1 — +x
xy2 = m.vertex(0.0, 1.0, 0.0)   # 2 — +y

# Face YZ (x=0) — its own copies
yz0 = m.vertex(0.0, 0.0, 0.0)   # 3 — corner copy B
yz1 = m.vertex(0.0, 1.0, 0.0)   # 4 — +y
yz2 = m.vertex(0.0, 0.0, 1.0)   # 5 — +z

# Face XZ (y=0) — its own copies
xz0 = m.vertex(0.0, 0.0, 0.0)   # 6 — corner copy C
xz1 = m.vertex(0.0, 0.0, 1.0)   # 7 — +z
xz2 = m.vertex(1.0, 0.0, 0.0)   # 8 — +x

t_xy = m.triangle(xy0, xy1, xy2)   # 0
t_yz = m.triangle(yz0, yz1, yz2)   # 1
t_xz = m.triangle(xz0, xz1, xz2)   # 2

# --- THREE coincident-but-distinct copies of the corner point (0,0,0) ---
m.assert_vertex_pair_distance_lt(xy0, yz0, 1e-9)   # copy A ≈ copy B
m.assert_vertex_pair_distance_lt(yz0, xz0, 1e-9)   # copy B ≈ copy C
m.assert_vertex_pair_distance_lt(xy0, xz0, 1e-9)   # copy A ≈ copy C
# ...and they are genuinely distinct records, un-welded (no edge between them):
m.assert_vertex_pair_no_shared_triangle(xy0, yz0)
m.assert_vertex_pair_no_shared_triangle(yz0, xz0)
m.assert_vertex_pair_no_shared_triangle(xy0, xz0)

# --- coincident-but-distinct seam edges → the cracks ---
# +x seam: XY face edge (0,1) coincident with XZ face edge (6,8)
m.assert_edge_pair_coincident((xy0, xy1), (xz0, xz2), eps=1e-9)
m.assert_edge_shared(xy0, xy1, 1)   # each seam edge incident on 1 triangle
m.assert_edge_shared(xz0, xz2, 1)   #   (would be 2 if the faces were welded)
# +z seam: YZ face edge (3,5) coincident with XZ face edge (6,7)
m.assert_edge_pair_coincident((yz0, yz2), (xz0, xz1), eps=1e-9)
m.assert_edge_shared(yz0, yz2, 1)
m.assert_edge_shared(xz0, xz1, 1)
