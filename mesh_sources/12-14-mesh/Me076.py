"""Me076 — duplicate_singular_vertices: closed-fan bowtie (wraparound in CW traversal).

Catalog claim: vertex 0 is a non-manifold (singular) vertex. The upper fan is
a **closed** triangle strip (4 triangles forming a full ring around v0, with no
boundary edges at v0 itself — all edges at v0 from the upper fan are interior,
shared by exactly 2 triangles). The lower fan is a separate open triangle that
connects to v0 but shares no edge with the closed ring.

This exercises Branch 7 (*link_traversal_cw*) and Branch 8 (*wraparound_check*):
when the CW traversal of the closed ring returns to the starting polygon, the
algorithm detects the wraparound (next==v0 in CGAL's code path) and terminates
the first link-CC, then starts a new CC for the isolated lower fan.

Layout (closed ring of 4 triangles around v0 in XY plane, plus 1 triangle below):
  Outer ring vertices at radius 1: v1=(0,1,0), v2=(1,0,0), v3=(0,-1,0), v4=(-1,0,0)
  Wait — v3 in the closed ring must not be shared with the lower fan.

Revised layout:
  Closed-ring outer: v1=(0,2,0) v2=(2,0,0) v3=(0,-2,0) v4=(-2,0,0)
    ring triangles: t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4), t3=(v0,v4,v1)
    edges at v0: (v0,v1),(v0,v2),(v0,v3),(v0,v4) each shared by 2 ring triangles
  Lower fan (below the ring, but at the SAME v0): t4=(v0,v5,v6)
    v5=(1,-3,0) v6=(-1,-3,0) — separate fan with no shared edge to ring
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me076",
             title="duplicate_singular_vertices: closed-ring upper fan plus open lower fan at bowtie vertex",
             defect_class="non_manifold_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — singular bowtie vertex

# Closed-ring fan outer rim.
v1 = m.vertex(0.0, 2.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(0.0, -2.0, 0.0)  # 3
v4 = m.vertex(-2.0, 0.0, 0.0)  # 4

# Lower isolated fan.
v5 = m.vertex(1.0, -4.0, 0.0)  # 5
v6 = m.vertex(-1.0, -4.0, 0.0) # 6

# Closed ring of 4 triangles (all edges at v0 shared by 2 ring triangles).
t0 = m.triangle(v0, v1, v2)   # ring — shares (v0,v1) with t3, (v0,v2) with t1
t1 = m.triangle(v0, v2, v3)   # ring — shares (v0,v2) with t0, (v0,v3) with t2
t2 = m.triangle(v0, v3, v4)   # ring — shares (v0,v3) with t1, (v0,v4) with t3
t3 = m.triangle(v0, v4, v1)   # ring — shares (v0,v4) with t2, (v0,v1) with t0

# Lower open fan triangle.
t4 = m.triangle(v0, v5, v6)   # isolated fan — shares only v0 with ring

# All edges at v0 within the closed ring are interior (shared by exactly 2 triangles).
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t3
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2
m.assert_edge_shared(v0, v4, 2)   # shared by t2 and t3

# Lower fan boundary edges.
m.assert_edge_shared(v0, v5, 1)   # boundary — only t4
m.assert_edge_shared(v0, v6, 1)   # boundary — only t4

# v0's fan is disconnected: closed ring (t0–t3) vs. lower fan (t4).
m.assert_vertex_fan_disconnected(v0)
