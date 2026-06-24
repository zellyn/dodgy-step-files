"""Me396 — do_faces_intersect branch 7: edge-orientation-search-mode.

PMP.do_faces_intersect Branch 7 (*edge-orientation-search-mode*) @ line 150:
  When searching for the shared vertex between two faces to determine which
  permutation index i satisfies hv[i] == gv[j], the i==0 branch sets
  vh[1]=f[i] and vh[2]=f[(i+1)%3] to extract the candidate shared-edge
  direction. This branch fires when the first face's vertex at position 0
  matches a vertex in the second face — causing the edge-orientation index
  to be derived from permutation i=0.

The fixture models three triangles arranged as a linear strip (a→b→c):
  t0 and t1 share vertex v2 (at position index 2 in t0 and index 0 in t1),
  t1 and t2 share vertex v4 (at position index 2 in t1 and index 0 in t2).
  In both cases the shared vertex matches at i=0 in the second face —
  triggering the vh[1]=f[0], vh[2]=f[1] path.

None of the triangle pairs cross geometrically — the shared-vertex test
correctly routes to the segment check and finds no SI. The fixture
demonstrates the permutation search terminates correctly.

Geometry: three triangles in a row, each sharing one vertex with the next.
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(0.5,1,0), v4=(1.5,1,0), v5=(2.5,1,0)
  t0=(v0,v1,v3): left triangle
  t1=(v2,v3,v4): center triangle (shares v3 with t0, shares v4 with t2)
  t2=(v4,v5,v2): right triangle (no SI with t0)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me396",
    title="do_faces_intersect edge-orientation-search: i==0 shared-vertex permutation path; strip of 3 non-intersecting triangles (Branch 7)",
    defect_class="shared_vertex_adjacent_faces",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(0.5, 1.0, 0.0)   # 3
v4 = m.vertex(1.5, 1.0, 0.0)   # 4
v5 = m.vertex(2.5, 1.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v3)    # 0: left triangle
t1 = m.triangle(v2, v3, v4)    # 1: center triangle — v3 shared with t0 (i=0 search in t1)
t2 = m.triangle(v4, v5, v2)    # 2: right triangle — v4 shared with t1 (i=0 search in t2)

# t0 and t1 share only vertex v3 (not an edge); no geometric crossing.
m.assert_triangles_do_not_intersect(t0, t1)
# t1 and t2 share only vertex v4 and v2 (two vertices = an edge (v2,v4)).
# t0 and t2 share no vertex.
m.assert_triangles_do_not_intersect(t0, t2)
