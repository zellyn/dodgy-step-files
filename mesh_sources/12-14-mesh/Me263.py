"""Me263 — range_with_face_set_preserve_genus: hole-fill blocked by genus preservation.

Catalog claim: CGAL PMP.remove_degenerate_edges.range_with_face_set Branch 4 @ line 1591
(*preserve_genus*): the degenerate border edge bounds a triangular hole, BUT the
preserve_genus option is set. Filling the hole would change the topological genus of
the surface. The algorithm therefore marks the degenerate edge as not fully removable
(all_removed=false) and skips the fill.

Geometric signature: a mesh with a triangular hole formed by 3 boundary edges. One of
those boundary edges is degenerate (near-zero length: v0≈v1). Unlike Branch 3, the
preserve_genus constraint prevents closing the hole. The fixture demonstrates the
boundary-3-edge hole with the same degenerate border edge pattern as Me262 but in a
larger patch context where topological constraints apply.

The 3-edge hole has boundary: v0 → v1 → v2 → v0.
  - Edge (v0, v1): degenerate border edge (v0≈v1, both border vertices)
  - Edge (v1, v2): normal border edge
  - Edge (v2, v0): normal border edge
Surrounding patch: 4 triangles using outer vertices v3, v4.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me263",
             title="range_with_face_set preserve_genus: degenerate border edge in 3-edge hole; genus preservation blocks fill_hole",
             defect_class="degenerate_edge")

# Hole vertices: v0≈v1 (degenerate border edge).
v0 = m.vertex(0.0,   0.0, 0.0)
v1 = m.vertex(1e-10, 0.0, 0.0)   # nearly coincident with v0
v2 = m.vertex(0.5,   1.0, 0.0)   # hole apex

# Outer patch vertices.
v3 = m.vertex(-1.0,  0.5, 0.0)   # left outer
v4 = m.vertex(1.5,   0.5, 0.0)   # right outer

# Four patch triangles surrounding the triangular hole (v0,v1,v2).
# Hole boundary edges: (v0,v1), (v1,v2), (v2,v0) — each must be on exactly 1 triangle.
t0 = m.triangle(v3, v0, v2)    # 0: left — uses border edge (v2,v0) and (v3,v0), (v2,v3)
t1 = m.triangle(v3, v1, v0)    # 1: bottom — uses border edge (v0,v1) in position (v1,v0)? no
                                 #   edges: (3,1),(1,0),(0,3) → (0,1) is in this triangle!
t2 = m.triangle(v2, v4, v1)    # 2: right-top — uses border edge (v1,v2)
                                 #   edges: (2,4),(4,1),(1,2)
t3 = m.triangle(v1, v4, v0)    # 3: right-bottom — wait, this adds edge (0,1) again

# Problem: (v0,v1) would appear in both t1 and t3. Let me redesign with 3 triangles:
# t0 uses border edge (v0,v2) — only place
# t1 uses border edge (v0,v1) — only place
# t2 uses border edge (v1,v2) — only place
# But we need the mesh connected, so triangles must share edges.

# Clean restart with minimal 3-triangle patch:
m.vertices.clear()
m.triangles.clear()
m.assertions.clear()

# Hole vertices.
v0 = m.vertex(0.0,   0.0, 0.0)
v1 = m.vertex(1e-10, 0.0, 0.0)
v2 = m.vertex(0.5,   1.0, 0.0)

# Three outer vertices — each adjacent to one hole edge.
v3 = m.vertex(-0.5,  0.5, 0.0)   # adjacent to (v0, v2)
v4 = m.vertex(0.5,   2.0, 0.0)   # adjacent to (v2, v1) ... wait, want (v1,v2)
v5 = m.vertex(0.5,  -0.5, 0.0)   # adjacent to (v1, v0)

# Three patch triangles, each using one hole-boundary edge:
# t0 uses (v2, v0) as border edge: t0=(v3, v2, v0) → edges (3,2),(2,0),(0,3) → (0,2)=border ✓
# t1 uses (v0, v1) as border edge: t1=(v5, v0, v1) → edges (5,0),(0,1),(1,5) → (0,1)=border ✓
# t2 uses (v1, v2) as border edge: t2=(v4, v1, v2) → edges (4,1),(1,2),(2,4) → (1,2)=border ✓
# Connect the outer ring: need shared edges between t0,t1,t2.
# t0 and t1 share edge (v0,v3)? No: t0 has (v3,v2),(v2,v0),(v0,v3); t1 has (v5,v0),(v0,v1),(v1,v5).
# No shared edge. Need extra triangles to connect.

t0 = m.triangle(v3, v2, v0)    # 0: left — border edge (v2,v0)
t1 = m.triangle(v5, v0, v1)    # 1: bottom — border edge (v0,v1)
t2 = m.triangle(v4, v1, v2)    # 2: right — border edge (v1,v2)
# Connect outer ring: t3=(v3,v4,v2), t4=(v3,v5,v0), t5=(v4,v5,v1) — but then (v3,v0) shared etc.
# Simpler: just add 3 triangles connecting outer ring verts.
t3 = m.triangle(v3, v4, v2)    # 3: (3,4),(4,2),(2,3) — connects t0 and t2
t4 = m.triangle(v3, v5, v4)    # 4: connects all outer verts
t5 = m.triangle(v5, v1, v4)    # 5: (5,1),(1,4),(4,5) — connects t1 and t2

# Hole boundary edges (each incident on exactly 1 triangle in our mesh).
m.assert_hole_boundary([v0, v1, v2])

# Degenerate border edge (v0, v1) — border, shared by 1 triangle.
m.assert_edge_shared(v0, v1, 1)

# v0 and v1 are nearly coincident.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-9)
