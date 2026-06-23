"""Me303 — retriangulateSelectedRegion_internal_vertices_extraction: region has internal vertices to extract.

MeshFix `Basic_TMesh.retriangulateSelectedRegion` Branch 4 (*internal_vertices_extraction*) @ line 978:
  `ms = getRegionInternalVertices(ttbr)` — extracts internal (non-boundary) vertices
  of the selected region. These Steiner points are needed by the Delaunay
  hole-filling step. A region whose interior contains vertices (not just boundary
  vertices) exercises this extraction path.

An internal vertex of the region is one that is incident only on selected
triangles — it touches no boundary edge of the region. It is "interior" to
the patch and will become a Steiner point for re-triangulation.

Defect carrier: four triangles forming a fan around a central vertex `vi`.
The fan covers the interior; `vi` is an internal vertex of the selection.
The boundary of the selection is the outer cycle (v0, v1, v2, v3).

Geometry (flat XY plane):
  vi = (1, 1, 0) — center, internal vertex of the selected region
  v0 = (0, 0, 0), v1 = (2, 0, 0), v2 = (2, 2, 0), v3 = (0, 2, 0) — outer ring

Fan triangles (all selected):
  t0 = (vi, v0, v1)
  t1 = (vi, v1, v2)
  t2 = (vi, v2, v3)
  t3 = (vi, v3, v0)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me303",
    title="retriangulateSelectedRegion_internal_vertices_extraction: central vertex is internal to region (Branch 4)",
    defect_class="retriangulate_region_internal_vertex",
)

vi = m.vertex(1.0, 1.0, 0.0)   # 0 — internal vertex (Steiner point)
v0 = m.vertex(0.0, 0.0, 0.0)   # 1
v1 = m.vertex(2.0, 0.0, 0.0)   # 2
v2 = m.vertex(2.0, 2.0, 0.0)   # 3
v3 = m.vertex(0.0, 2.0, 0.0)   # 4

t0 = m.triangle(vi, v0, v1)   # 0
t1 = m.triangle(vi, v1, v2)   # 1
t2 = m.triangle(vi, v2, v3)   # 2
t3 = m.triangle(vi, v3, v0)   # 3

# Inner edges (all incident on vi): each shared by 2 triangles.
m.assert_edge_shared(vi, v0, 2)   # shared by t0 and t3
m.assert_edge_shared(vi, v1, 2)   # shared by t0 and t1
m.assert_edge_shared(vi, v2, 2)   # shared by t1 and t2
m.assert_edge_shared(vi, v3, 2)   # shared by t2 and t3

# Outer edges: each incident on only 1 triangle (boundary of selection).
m.assert_edge_shared(v0, v1, 1)   # boundary
m.assert_edge_shared(v1, v2, 1)   # boundary
m.assert_edge_shared(v2, v3, 1)   # boundary
m.assert_edge_shared(v3, v0, 1)   # boundary

# vi (vertex 0) is the internal vertex — not on any boundary edge.
# The 4 triangles form a complete fan around vi, covering the interior.
# getRegionInternalVertices identifies vi as a Steiner point for re-tri.
# Euler: V=5, E=8, F=4, chi = 5-8+4 = 1 (open disk).
m.assert_euler_characteristic(v=5, e=8, f=4, chi=1)
