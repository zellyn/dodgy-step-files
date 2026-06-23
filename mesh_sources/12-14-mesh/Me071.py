"""Me071 — duplicate_singular_vertices: 3D bowtie (fans in orthogonal planes).

Catalog claim: vertex 0 is a non-manifold (singular) vertex whose incident
polygons form 2 link connected components. Unlike Me070 (flat XY bowtie), here
the two triangle fans lie in orthogonal planes — one in XY (z=0), one in XZ
(y=0). This exercises CGAL PMP.Polygon_soup_orienter.duplicate_singular_vertices
Branch 5 (*non_manifold_vertex*) in a 3D configuration where the two fans
project differently on every coordinate axis, stressing the link-CC traversal.

Defect carrier:
  Upper fan (XY plane): tri0=(v0,v1,v2) — v1=(1,1,0), v2=(-1,1,0)
  Side fan (XZ plane): tri1=(v0,v3,v4) — v3=(1,0,1), v4=(-1,0,1)
  The two fans share only v0; no shared edge; link has 2 CCs.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me071",
             title="duplicate_singular_vertices: 3D bowtie — two fans in orthogonal planes",
             defect_class="non_manifold_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — singular bowtie vertex
v1 = m.vertex(1.0, 1.0, 0.0)   # 1 — XY fan
v2 = m.vertex(-1.0, 1.0, 0.0)  # 2 — XY fan
v3 = m.vertex(1.0, 0.0, 1.0)   # 3 — XZ fan
v4 = m.vertex(-1.0, 0.0, 1.0)  # 4 — XZ fan

t0 = m.triangle(v0, v1, v2)   # XY-plane fan
t1 = m.triangle(v0, v3, v4)   # XZ-plane fan — shares only v0

# Every edge at v0 is a boundary edge (1 incident triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)
# Link at v0 is disconnected — two separate fan components.
m.assert_vertex_fan_disconnected(v0)
