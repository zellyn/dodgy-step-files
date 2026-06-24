"""Me393 — do_faces_intersect branch 4: shared-vertex-presence-detection.

PMP.do_faces_intersect Branch 4 (*shared-vertex-presence-detection*) @ line 264:
  Tests whether two faces share any vertex (checking all 3 vertex pairs:
  hv[i] == gv[j]). When a shared vertex is found but the faces do NOT share
  a full edge, the algorithm switches to detailed segment-triangle tests rather
  than the full geometric SI check.

The fixture models two triangles that share exactly ONE vertex (v0=(0,0,0)) but
no shared edge. Both triangles point away from each other in opposite quadrants,
so their interiors do NOT overlap — Branch 4 detects the shared vertex and
performs the segment test, which confirms no actual SI. The
`triangles_do_not_intersect` assertion verifies the geometric non-crossing.

Geometry:
  Shared vertex v0=(0,0,0).
  t0: (v0,v1,v2) in first quadrant.
  t1: (v0,v3,v4) in third quadrant — pointing away.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me393",
    title="do_faces_intersect shared-vertex-only: one shared vertex, no shared edge, no geometric SI (Branch 4)",
    defect_class="shared_vertex_adjacent_faces",
)

# Shared vertex.
v0 = m.vertex(0.0,  0.0, 0.0)   # 0: shared vertex

# t0 vertices — first quadrant.
v1 = m.vertex(2.0,  0.0, 0.0)   # 1
v2 = m.vertex(0.0,  2.0, 0.0)   # 2

# t1 vertices — third quadrant (pointing away from t0).
v3 = m.vertex(-2.0, 0.0, 0.0)   # 3
v4 = m.vertex(0.0, -2.0, 0.0)   # 4

t0 = m.triangle(v0, v1, v2)     # 0: first-quadrant triangle
t1 = m.triangle(v0, v3, v4)     # 1: third-quadrant triangle (shares only v0)

# These faces share exactly one vertex (v0) — no shared edge.
m.assert_vertex_pair_no_shared_triangle(v1, v3)  # v1 and v3 are in different triangles only
# The shared vertex is present but geometries do NOT intersect.
m.assert_triangles_do_not_intersect(t0, t1)
