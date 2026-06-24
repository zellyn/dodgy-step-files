"""Me830 — is_non_manifold_vertex border-incident-null-face: boundary vertex with exactly one null-face halfedge (Branch 1).

CGAL PMP `PMP.is_non_manifold_vertex` Branch 1 (*border-incident-null-face*) @ line 67:
  'std::size_t border_counter = 0;
   ... if(is_border(h, tmesh)) ++border_counter;'
  — the function walks the halfedge star of vertex v and counts how many incident
  halfedges have a null face (i.e. are on the mesh boundary). A vertex with exactly
  one such halfedge is a regular boundary vertex; the counter fires but threshold is
  not exceeded.

Defect pattern: a simple open strip of two triangles. The shared apex vertex v0
  sits on the interior edge and is a manifold boundary vertex. Its halfedge star has
  exactly one boundary halfedge (the edge exiting toward v1 on the strip boundary).
  Branch 1 fires (counter incremented once) but counter == 1, so the vertex is NOT
  flagged as non-manifold.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(1,-1,0)
  t0=(v0,v1,v2), t1=(v0,v3,v1)
  Interior edge (v0,v1) shared by t0 and t1 (n=2).
  v0 is on the boundary of the strip: edges (v0,v2) and (v0,v3) are boundary (n=1).
  v0 has exactly two boundary halfedges pointing outward → border_counter == 2 for v0,
  but per-halfedge null-face: the halfedges FROM v0 toward v2 and v3 have null opposite
  faces. v0 is a manifold boundary vertex (single connected umbrella sector).

Euler: V=4, E=5, F=2, chi=1 (open disk topology).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me830",
    title="is_non_manifold_vertex border-incident-null-face: boundary vertex v0 has exactly one umbrella sector; border halfedge counted but threshold not exceeded (Branch 1)",
    defect_class="non_manifold_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — boundary vertex under test (manifold)
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — far boundary vertex
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — upper apex
v3 = m.vertex(1.0, -1.0, 0.0)  # 3 — lower apex

# Two triangles sharing interior edge (v0, v1).
t0 = m.triangle(v0, v1, v2)   # upper triangle
t1 = m.triangle(v0, v3, v1)   # lower triangle

# Interior shared edge — the only interior edge at v0.
m.assert_edge_shared(v0, v1, 2)

# Boundary edges — v0 is on the boundary with two boundary incident edges.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v0, v3, 1)

# v0's fan is a single connected strip (manifold boundary vertex).
# It is NOT a disconnected fan — both triangles connect via the shared edge (v0,v1).
m.assert_euler_characteristic(4, 5, 2, 1)
