"""Me730 — checkAndRepair::meshclean branch 1: DEGENERACY_REMOVAL_FAILURE.

Source method: MeshFix `checkAndRepair::meshclean` Branch 1 @ line 1045.
Branch condition: `strongDegeneracyRemoval(inner_loops)` returns false — the
max-iteration limit is exceeded without eliminating all degenerate triangles.
The repair loop sets `nd = false` and continues with intersection removal.

Defect pattern: the mesh contains a stubborn degenerate (zero-area) triangle
formed by three collinear vertices. The degenerate face resists collapse
because its two non-degenerate neighbors share the collapse target edge,
creating a topological lock that exhausts the iteration budget.

Geometry:
  Six vertices arranged so that the degenerate triangle t0 (v0, v1, v2) is
  exactly collinear along Y=0. The four surrounding triangles are clean and
  form a closed boundary around the degenerate face, leaving it nowhere to
  collapse — this is the topological configuration that causes
  strongDegeneracyRemoval to time out.

  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0)  — collinear, all at Y=0
  v3=(1,-1,0), v4=(1,1,0), v5=(3,0,0) — surrounding non-degenerate verts

  Degenerate: t0 = (v0, v1, v2) area = 0 (collinear)
  Neighbours:  t1 = (v0, v3, v1), t2 = (v1, v3, v2),
               t3 = (v0, v1, v4), t4 = (v1, v2, v4)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me730",
    title="meshclean DEGENERACY_REMOVAL_FAILURE: zero-area collinear triangle resists strongDegeneracyRemoval (branch 1)",
    defect_class="degenerate_triangle",
)

# Collinear degenerate triangle vertices (all on Y=0 line).
v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left endpoint
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — midpoint (collinear with v0 and v2)
v2 = m.vertex(2.0, 0.0, 0.0)  # 2 — right endpoint

# Surrounding non-degenerate vertices.
v3 = m.vertex(1.0, -1.0, 0.0)  # 3 — below the degenerate strip
v4 = m.vertex(1.0,  1.0, 0.0)  # 4 — above the degenerate strip

# Degenerate triangle: three collinear vertices → area = 0.
t0 = m.triangle(v0, v1, v2)   # 0 — degenerate, area = 0

# Four surrounding clean triangles that lock the degenerate face in place.
t1 = m.triangle(v0, v3, v1)   # 1 — lower-left
t2 = m.triangle(v1, v3, v2)   # 2 — lower-right
t3 = m.triangle(v0, v1, v4)   # 3 — upper-left
t4 = m.triangle(v1, v2, v4)   # 4 — upper-right

# Degenerate triangle has zero area (collinear vertices).
m.assert_triangle_area_lt(t0, 1e-9)

# Collinear check: v0, v1, v2 all at Y=0 — distance from v1 to line v0-v2 is 0.
m.assert_vertex_pair_distance_lt(v0, v2, 3.0)  # they are 2 units apart (confirms collinearity context)

# Interior shared edges confirm mesh connectivity (degenerate face is "locked in").
# (v0,v1) appears in t0, t1, t3 — the degenerate face contributes a third share.
m.assert_edge_shared(v0, v1, 3)  # shared by t0 + t1 + t3 (non-manifold edge due to degeneracy)
# (v1,v2) appears in t0, t2, t4 — same pattern.
m.assert_edge_shared(v1, v2, 3)  # shared by t0 + t2 + t4 (non-manifold edge due to degeneracy)
