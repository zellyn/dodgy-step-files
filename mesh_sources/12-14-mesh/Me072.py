"""Me072 — duplicate_singular_vertices: triple-fan vertex (3 link CCs).

Catalog claim: vertex 0 is a non-manifold (singular) vertex whose incident
polygon link has **3** connected components — three disjoint triangle fans
meeting only at v0. This exercises CGAL PMP.Polygon_soup_orienter.duplicate_
singular_vertices Branch 4 (*link_cc_count*: nb_link_ccs increments past 1
twice) and Branch 5 (*non_manifold_vertex*: fires because nb_link_ccs > 1).
After repair, v0 must be split into 3 copies — one per fan — generating 2 new
duplicate points (Branch 11, *new_point_creation*) and updating 3 polygon
references (Branch 12, *polygon_index_replacement*).

Defect carrier:
  Fan A (XY plane):  tri0=(v0,v1,v2)   v1=(1,0.5,0)  v2=(-1,0.5,0)
  Fan B (−Y half):   tri1=(v0,v3,v4)   v3=(1,-1,0)   v4=(-1,-1,0)
  Fan C (XZ plane):  tri2=(v0,v5,v6)   v5=(1,0,1)    v6=(-1,0,1)
  All three fans share only v0; three separate link components.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me072",
             title="duplicate_singular_vertices: triple-fan vertex — 3 disjoint link CCs at v0",
             defect_class="non_manifold_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — triple-bowtie vertex
v1 = m.vertex(1.0, 0.5, 0.0)   # 1 — fan A
v2 = m.vertex(-1.0, 0.5, 0.0)  # 2 — fan A
v3 = m.vertex(1.0, -1.0, 0.0)  # 3 — fan B
v4 = m.vertex(-1.0, -1.0, 0.0) # 4 — fan B
v5 = m.vertex(1.0, 0.0, 1.0)   # 5 — fan C
v6 = m.vertex(-1.0, 0.0, 1.0)  # 6 — fan C

t0 = m.triangle(v0, v1, v2)   # fan A
t1 = m.triangle(v0, v3, v4)   # fan B — shares only v0 with fan A
t2 = m.triangle(v0, v5, v6)   # fan C — shares only v0 with fans A and B

# Boundary edges incident on v0 from each fan.
m.assert_edge_shared(v0, v1, 1)   # fan A boundary
m.assert_edge_shared(v0, v3, 1)   # fan B boundary
m.assert_edge_shared(v0, v5, 1)   # fan C boundary
# v0's fan is disconnected (3 separate link components).
m.assert_vertex_fan_disconnected(v0)
