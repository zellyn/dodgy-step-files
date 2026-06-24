"""Me514 — Edge.swap branch 5: TRIANGLE_ORIENTATION_FLIP.

MeshFix `Edge.swap` Branch 5 (*TRIANGLE_ORIENTATION_FLIP*) @ line 158:
  't1->invert(); t2->invert();'
  — after edge and triangle replacement steps, both triangles are inverted
  (vertex winding order reversed) to restore consistent outward normals.
  Without this inversion the diagonal swap would leave one or both new
  triangles with a flipped normal, breaking watertight orientation.
  Branch 5 fires for every successful swap.

Defect pattern: a 2-triangle quad where the two triangles share diagonal
  (v0,v2) but BOTH traverse the shared edge in the same direction (v2→v0),
  producing inconsistent winding. This is the intermediate state after
  Edge.swap has updated endpoints but before invert() is called. The
  fixture captures the pre-invert defect state: one triangle with +z normal
  and the other with -z normal on the same shared edge.

Geometry (z=0):
  v0=(0,0,0), v1=(1,-1,0), v2=(0.5,1,0), v3=(0,1,0)
  t0=(v0,v1,v2): edges v0→v1,v1→v2,v2→v0; n0=(0,0,1.5) → +z (CCW)
  t1=(v3,v2,v0): edges v3→v2,v2→v0,v0→v3; n1=(0,0,-0.5) → -z (CW)
  Both traverse shared edge (v0,v2) as v2→v0 — SAME direction → inconsistent.

Shared diagonal (v0,v2) is interior (n=2). The invert() calls on t1 and t2
  in the swap implementation correct this inconsistency after the flip.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me514",
    title="Edge.swap TRIANGLE_ORIENTATION_FLIP: inconsistent winding across shared diagonal (v0,v2); both triangles traverse v2→v0, n0=+z n1=-z; t1.invert()+t2.invert() restore consistency (Branch 5)",
    defect_class="edge_swap_orientation_flip",
)

v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — shared diagonal bottom endpoint
v1 = m.vertex(1.0, -1.0,  0.0)   # 1 — opposite vertex of t0 (below diagonal)
v2 = m.vertex(0.5,  1.0,  0.0)   # 2 — shared diagonal top endpoint
v3 = m.vertex(0.0,  1.0,  0.0)   # 3 — opposite vertex of t1 (above diagonal)

# t0 = (v0,v1,v2): traverses shared edge as v2→v0; normal = +z
# t1 = (v3,v2,v0): traverses shared edge as v2→v0 (SAME dir as t0) → inconsistent
# Normal t0: (v1-v0)×(v2-v0) = (1,-1,0)×(0.5,1,0) = (0,0,1·1-(-1)·0.5) = (0,0,1.5) → +z
# Normal t1: (v2-v3)×(v0-v3) = (0.5,0,0)×(0,-1,0) = (0,0,-0.5) → -z
# dot = (0)(0)+(0)(0)+(1.5)(-0.5) = -0.75 < 0 → oracle sees inconsistent ✓
t0 = m.triangle(v0, v1, v2)   # 0: lower triangle, normal +z
t1 = m.triangle(v3, v2, v0)   # 1: wound CW (v2→v0 same dir as t0), normal -z → inconsistent

# Shared interior diagonal (v0,v2) — the candidate swap edge.
m.assert_edge_shared(v0, v2, 2)

# Inconsistent winding: both triangles traverse (v0,v2) in the same direction.
m.assert_adjacent_triangles_inconsistent_winding(0, 1)

# Boundary edges — n=1 each.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
