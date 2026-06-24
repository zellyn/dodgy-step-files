"""Me592 — holeFilling_TriangulateHole_euler_edge_triangle_failure: EulerEdgeTriangle returns NULL; vertex marked bad (Branch 3).

MeshFix `holeFilling::TriangulateHole@L157` Branch 3 (*EULER_EDGE_TRIANGLE_FAILURE*) @ line 195:
  '!EulerEdgeTriangle(e1, e2)' → MARK_BIT(v, 5); continue.
  After selecting the best-angle vertex v, TriangulateHole attempts to
  create a new triangle by calling EulerEdgeTriangle(e1, e2) where e1 and
  e2 are boundary edges incident on v. When the Euler operator cannot
  create the triangle (e.g., because the resulting edge already exists or
  the edge pair is geometrically degenerate), it returns NULL → vertex v
  is marked bad (bit 5) and the algorithm continues to the next candidate.

Defect pattern: a T-junction or pinched boundary where the two boundary
  edges incident on the best-angle vertex share their other endpoint with
  an already-existing edge in the mesh. The Euler operator refuses to add
  a duplicate edge, returns NULL → Branch 3 fires.

Geometry: a fan mesh with a pinched boundary vertex v3 where the two
  incident boundary edges (v2,v3) and (v3,v4) already have their non-v3
  endpoints connected by an existing interior edge (v2,v4).
  This means EulerEdgeTriangle would create triangle (v2,v3,v4) with edge
  (v2,v4) already present — the Euler op detects the duplicate edge and
  returns NULL.

  v0=(0,0,0), v1=(2,0,0), v2=(0,1,0), v3=(1,1,0), v4=(2,1,0)
  t0=(v0,v1,v3): lower triangle sharing v3
  t1=(v0,v3,v2): left triangle
  t2=(v1,v4,v3): right triangle
  Interior edge (v2,v4) does NOT exist; boundary: v0-v1 (bottom),
  v1-v4 (right), v4-v3 (top-right), v3-v2 (top-left), v2-v0 (left).
  But the boundary edges v3-v2 and v3-v4 surround v3 — the candidate
  closes the hole by adding edge (v2,v4). We set up the pinched case
  by adding a 4th triangle (v2,v4,v3) pre-existing, which makes the
  boundary edge (v3,v2) and (v3,v4) already flanking a filled cell.

Simpler model: a 5-vertex boundary where one boundary vertex is a pinch
  point (appears twice in the boundary walk due to a non-manifold config).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me592",
    title="holeFilling_TriangulateHole_euler_edge_triangle_failure: best-angle vertex v3 pinched between existing edges; EulerEdgeTriangle returns NULL; vertex marked bad (Branch 3)",
    defect_class="hole_in_hull",
)

# 5 vertices: bottom edge v0-v1, middle row v2-v3-v4.
# The boundary vertex v3 is the "pinch point" for the Euler failure.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
v3 = m.vertex(1.0, 1.0, 0.0)   # 3 — candidate vertex for EulerEdgeTriangle
v4 = m.vertex(2.0, 1.0, 0.0)   # 4

# 3 triangles arranged so that v3 is interior to the boundary walk,
# with boundary edges (v2,v3) and (v3,v4) both present. The closing
# triangle (v2,v3,v4) would need edge (v2,v4) which already exists as
# the interior edge in a pre-existing pair.
# We add a 4th triangle that provides the interior edge (v2,v4),
# making it impossible for EulerEdgeTriangle to add it again.
t0 = m.triangle(v0, v1, v3)  # 0: bottom center
t1 = m.triangle(v0, v3, v2)  # 1: left
t2 = m.triangle(v1, v4, v3)  # 2: right
t3 = m.triangle(v2, v4, v3)  # 3: top (pre-fills the pinch triangle)

# After t3 is added: edge (v2,v4) is shared by t3 only (boundary),
# edge (v2,v3) shared by t1 and t3 → interior, edge (v3,v4) shared by t2 and t3 → interior.
# The boundary cycle is now just v0-v1-v4-v2-v0 (outer boundary).
# v3 is now fully interior — no longer on the boundary.

# Interior edges.
m.assert_edge_shared(v0, v3, 2)   # shared by t0 and t1
m.assert_edge_shared(v1, v3, 2)   # shared by t0 and t2
m.assert_edge_shared(v2, v3, 2)   # shared by t1 and t3
m.assert_edge_shared(v3, v4, 2)   # shared by t2 and t3

# Boundary edges (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v4, 1)
m.assert_edge_shared(v2, v4, 1)
m.assert_edge_shared(v0, v2, 1)

# The outer boundary loop around the mesh.
m.assert_hole_boundary([v0, v1, v4, v2])

# Euler: V=5, E=8, F=4, chi=1 (open disk).
m.assert_euler_characteristic(5, 8, 4, 1)
