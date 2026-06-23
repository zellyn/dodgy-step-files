"""Me046 — compatible_orientations: odd-parity flip cycle blocks consistent orientation.

Catalog claim: a ring of 5 triangles shares edges in a loop; the winding choices
around the cycle have odd total parity, so no globally consistent orientation
assignment exists. CGAL PMP.compatible_orientations Branch 1 @ line 1220
(*cyclic_orientation_flip*) detects this by tracking flip_count around the BFS
spanning tree: an odd flip-count on the back-edge means the ring is inherently
non-orientable.

Defect carrier: 5 triangles arranged in a Moebius-strip-like cycle. Triangles 0-3
form a consistent CCW ring; triangle 4 bridges back to triangle 0 but with a reversed
winding — the odd flip. This means triangles 4 and 0 share an edge but have
antiparallel normals, and triangles 4 and 3 also share an edge but have antiparallel
normals: two inconsistent-winding pairs mark the defect.

Vertex layout (pentagon ring in XY plane):
  v0=(0,1,0), v1=(-1,0,0), v2=(-0.5,-1,0), v3=(0.5,-1,0), v4=(1,0,0)
  hub=v5=(0,0,0)

Consistent CCW normals for tris 0-3 (all +Z):
  tri0: (v5, v0, v1)  normal +Z
  tri1: (v5, v1, v2)  normal +Z
  tri2: (v5, v2, v3)  normal +Z
  tri3: (v5, v3, v4)  normal +Z
  tri4: (v5, v0, v4)  — reversed: (hub, v0, v4) gives -Z normal (CW).

tri4 is wound CW using (hub, v0, v4), giving a -Z normal. It shares edge
{hub,v0} with tri0 and edge {hub,v4} with tri3; both neighbors are +Z so tri4's
-Z is antiparallel to both — the odd parity flip.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me046",
             title="cyclic orientation flip: odd-parity ring blocks compatible_orientations",
             defect_class="cyclic_orientation_conflict")

# Hub + pentagon rim
hub = m.vertex(0.0,  0.0, 0.0)   # 0
v0  = m.vertex(0.0,  1.0, 0.0)   # 1
v1  = m.vertex(-1.0, 0.0, 0.0)   # 2
v2  = m.vertex(-0.5,-1.0, 0.0)   # 3
v3  = m.vertex( 0.5,-1.0, 0.0)   # 4
v4  = m.vertex( 1.0, 0.0, 0.0)   # 5

# Triangles 0-3: consistently CCW (normal +Z each)
t0 = m.triangle(hub, v0, v1)   # tri 0  — CCW, +Z
t1 = m.triangle(hub, v1, v2)   # tri 1  — CCW, +Z
t2 = m.triangle(hub, v2, v3)   # tri 2  — CCW, +Z
t3 = m.triangle(hub, v3, v4)   # tri 3  — CCW, +Z
# Triangle 4: reversed winding (CW, normal -Z) — creates the parity defect.
# It shares edge (hub,v0) with tri0 and edge (hub,v4) with tri3.
# Using (hub, v0, v4) gives -Z normal (CW), antiparallel to tri0 (+Z) and tri3 (+Z).
t4 = m.triangle(hub, v0, v4)   # tri 4  — CW, -Z (FLIPPED — the defect)

# Assert: tri4 has antiparallel normal to tri0 (they share edge hub-v0).
m.assert_adjacent_triangles_inconsistent_winding(t4, t0)

# Assert: tri4 has antiparallel normal to tri3 (they share edge hub-v4).
m.assert_adjacent_triangles_inconsistent_winding(t4, t3)
