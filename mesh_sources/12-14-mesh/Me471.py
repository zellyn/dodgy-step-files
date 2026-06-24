"""Me471 — remove_a_border_edge link_condition_violation: border edge collapse breaks topology (Branch 2).

CGAL PMP `PMP.remove_a_border_edge.with_sets` Branch 2 (*link_condition_violation*) @ line 1237:
  'does_satisfy_link_condition(halfedge, tmesh)' → false; mark incident faces, identify region.

The link condition for edge (v0,v1) fails when the common neighbors of v0 and v1
exceed exactly the faces incident to both — a T-junction or wedge configuration.
This happens when v0 and v1 share TWO or more common neighbors (they are already
connected by an interior edge in addition to the border edge), so collapsing would
create a non-manifold vertex.

Geometry: 4-triangle fan creating a T-junction.
  v0=(0,0,0) and v1=(1,0,0) are the border edge endpoints.
  v2=(0.5,1,0) is an apex reachable from BOTH v0 and v1 via interior edges (n=2).
  v3=(0.5,-1,0) is another apex reachable from both via two more triangles.
  This makes link(v0)∩link(v1) = {v2, v3} — two common neighbors — violating the link condition.

  t0=(v0,v1,v2) — upper-right; shared interior edge (v0,v2) and (v1,v2)
  t1=(v0,v2,v3)? Not correct. Instead:
  Use: v0,v1 already connected by an interior edge (v0,v1) n=2 would mean a non-border.
  Better: v0 and v1 share neighbor v2 AND v3, where
    t0=(v0,v1,v2) — upper pair; border edge (v0,v1)
    t1=(v0,v3,v1) — lower pair: also connects v0 and v1 but via v3
    t2=(v0,v2,v3) — left bridge connecting v2 and v3
  With t0+t1: edge (v0,v1) appears in t0 AND t1, so n=2 — no longer a border.

  Correct wedge construction: v0 and v1 are connected by border edge (only n=1),
  but both are ALSO connected to BOTH v2 AND v3:
    t0=(v0,v1,v2) — connects v0,v1,v2; interior edges (v0,v2) and (v1,v2) n=2 each
    t1=(v0,v2,v3) — connects v0,v2,v3; shares (v0,v2) with t0
    t2=(v0,v3,v1) wait — this re-uses edge (v0,v1)...

  The classical link-condition violation: put v1 adjacent to v2 via interior edge
  AND v0 adjacent to v2 via interior edge, AND also (v0,v1) is a border edge (n=1),
  AND there's ALSO another common neighbor. Use 3 triangles around v0:
    t0=(v0,v1,v2) — border; edge (v0,v1)=n=1, (v0,v2)=n=2, (v1,v2)=n=2
    t1=(v0,v2,v3) — connects v0,v2; shares (v0,v2) with t0
    link(v0)={v1,v2,v3} and link(v1)={v0,v2}
    link(v0)∩link(v1)={v2} — only one common neighbor. Still satisfied!

  Must have v1 connect to BOTH v2 AND v3:
    t0=(v0,v1,v2) — (v0,v1)=border, (v0,v2) interior, (v1,v2) interior
    t1=(v1,v3,v0) — (v0,v1)=border AGAIN — this makes (v0,v1) n=2, not border!

  Correct approach: use a V-shape where v0 and v1 share two common vertices v2 and v3
  without sharing the (v0,v1) edge twice:
    v0,v1 connected via border edge (n=1)
    v2 connected to both v0 and v1 via interior edges
    v3 connected to both v0 and v1 via interior edges (a different path)
    Result: link(v0)∩link(v1)⊇{v2,v3} → violation

  Four triangles: t0=(v0,v1,v2), t1=(v0,v2,v1)? No, can't repeat.
  The only way to connect v3 to both v0 and v1 without re-using (v0,v1) is:
    t2=(v0,v3,va), t3=(v1,va,v3) — introducing a 5th vertex va.
  Then: link(v0)={v1,v2,v3,va}, link(v1)={v0,v2,v3,va}
  link(v0)∩link(v1)={v2,v3,va} — multiple common neighbors → violation.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me471",
    title="remove_a_border_edge link_condition_violation: border edge (v0,v1) has multiple common neighbors; collapse would break topology (Branch 2)",
    defect_class="border_edge_link_condition_violation",
)

# Central border-edge vertices.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left endpoint of border edge
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — right endpoint of border edge
# Two common neighbors of v0 and v1 via interior edges.
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — upper apex; linked to both v0 and v1
v3 = m.vertex(1.0, -1.0, 0.0)  # 3 — lower apex; linked to both v0 and v1
# Bridge vertex to create the lower fan without re-using (v0,v1).
va = m.vertex(1.0, 0.0, 1.0)   # 4 — out-of-plane bridge

# Upper fan: t0 links v0,v1,v2; (v0,v2) and (v1,v2) become interior via t1,t2.
t0 = m.triangle(v0, v1, v2)   # 0: upper triangle; (v0,v1)=border
# Lower fan: t1+t2 link both v0 and v1 to v3 and va without repeating (v0,v1).
t1 = m.triangle(v0, v3, va)   # 1: connects v0 to v3 and va
t2 = m.triangle(v1, va, v3)   # 2: connects v1 to va and v3

# Interior edge (v3,va) shared by t1 and t2 — n=2.
m.assert_edge_shared(v3, va, 2)

# Border edge (v0,v1) — n=1 (only in t0).
m.assert_edge_shared(v0, v1, 1)

# Both v0 and v1 are connected to v3: (v0,v3) via t1 n=1, (v1,v3) via t2 n=1.
# Both v0 and v1 are connected to va: (v0,va) via t1 n=1, (v1,va) via t2 n=1.
# link(v0)∩link(v1) ⊇ {v2,v3,va} — multiple common neighbors → link condition violated.
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, va, 1)
m.assert_edge_shared(v1, va, 1)

# Euler: V=5, E=8, F=3, chi=0 (two disconnected open patches — t0 separate from t1+t2).
m.assert_euler_characteristic(5, 8, 3, 0)
