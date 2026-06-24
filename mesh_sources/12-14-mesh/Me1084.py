"""Me1084 — remove_degenerate_faces border_degenerate_face: degenerate triangle on open mesh boundary; is_border(opposite) fires (Branch 5).

CGAL PMP `PMP.remove_degenerate_faces` Branch 5 (*border_degenerate_face*) @ line 2118:
  'if (is_border(opposite(halfedge(f, tmesh), tmesh), tmesh)) { border_deg_faces.push(f); continue; }'
  — when a degenerate face is found with at least one edge that is a border edge
  (its opposite halfedge has no adjacent face), it is queued separately in
  border_deg_faces for boundary-aware processing rather than the interior repair path.

Defect pattern: a degenerate (zero-area, collinear) triangle that shares one edge
  with a valid non-degenerate triangle, and has two other edges on the open mesh
  boundary. The shared edge is interior (n=2); the other two edges are boundary (n=1).
  When processing the degenerate face, is_border fires for the opposite halfedge
  of the two boundary edges → Branch 5 triggers border_deg_faces queuing.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0) — collinear on x-axis
  v3=(0.5, 1.0, 0.0) — apex of clean triangle
  t0=(v0,v1,v3): clean non-degenerate triangle (area=0.5)
  t1=(v0,v1,v2): degenerate collinear triangle sharing edge (v0,v1) with t0;
                 edges (v1,v2) and (v0,v2) are boundary edges (n=1 each)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1084",
    title="remove_degenerate_faces border_degenerate_face: collinear t1 shares interior edge with clean t0; two boundary edges on t1 trigger is_border(opposite) → border_deg_faces (Branch 5)",
    defect_class="degenerate_triangle",
)

# Vertices: three collinear + one apex.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(2.0, 0.0, 0.0)  # 2 — extends the collinear chain
v3 = m.vertex(0.5, 1.0, 0.0)  # 3 — apex above v0-v1 (gives t0 positive area)

# Clean control triangle with positive area.
t0 = m.triangle(v0, v1, v3)   # 0: area = 0.5; non-degenerate

# Degenerate border triangle: collinear with two boundary edges.
t1 = m.triangle(v0, v1, v2)   # 1: v0,v1,v2 collinear → area = 0;
                                #    shares edge (v0,v1) with t0 (interior, n=2);
                                #    edge (v1,v2) is boundary (n=1);
                                #    edge (v0,v2) is boundary (n=1)

# t1 has zero area (collinear vertices).
m.assert_triangle_area_lt(t1, 1e-12)

# Interior shared edge (v0,v1): t0 and t1 both reference it.
m.assert_edge_shared(v0, v1, 2)

# Boundary edges on the degenerate triangle (each on only t1).
m.assert_edge_shared(v1, v2, 1)   # boundary — triggers is_border check
m.assert_edge_shared(v0, v2, 1)   # boundary — triggers is_border check

# Boundary edges of the clean triangle (v0,v3) and (v1,v3).
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
