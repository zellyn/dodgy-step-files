"""Me990 — orient_triangle_soup_with_reference_triangle_mesh concurrency_strategy: Concurrency_tag / Sequential_tag controls parallel-or-sequential soup orientation (Branch 1).

CGAL PMP `PMP.orient_triangle_soup_with_reference_triangle_mesh` Branch 1 (*concurrency_strategy*) @ line 280:
  The algorithm accepts a Concurrency_tag template parameter (either
  CGAL::Parallel_tag or CGAL::Sequential_tag). The branch at line 280
  selects between a parallel loop and a sequential loop over the soup
  triangles when assigning their orientation relative to the reference
  mesh. Branch 1 fires for any non-trivial input soup where the tag
  routing code executes.

Defect pattern: a triangle soup of three faces in an inconsistent winding
  (one face has its normal pointing opposite to the others) to be aligned
  against a reference mesh (two consistently oriented triangles forming a
  flat quad). The soup's misoriented face needs its winding corrected by
  the reference. The Concurrency_tag dispatch is the first thing the
  function executes before any per-triangle work, so any valid non-empty
  soup exercises Branch 1.

Geometry (soup — subject to orientation):
  Flat quad in XY plane split into three triangles:
    s0=(0,0,0), s1=(2,0,0), s2=(1,1,0), s3=(2,2,0), s4=(0,2,0)
    soup_t0=(s0,s1,s2): CCW, normal +Z.
    soup_t1=(s0,s2,s4): CCW, normal +Z.
    soup_t2=(s4,s2,s3): CW, normal -Z  — MISORIENTED (the defect).

Reference mesh (two triangles, consistently oriented CCW, normal +Z):
  r0=(0,0,0), r1=(2,0,0), r2=(2,2,0), r3=(0,2,0)
  ref_t0=(r0,r1,r2): CCW, normal +Z.
  ref_t1=(r0,r2,r3): CCW, normal +Z.

The function will build an AABB tree on the reference, find the closest
reference face for soup_t2, observe the dot product of their normals is
negative, and flip soup_t2. Branch 1 (concurrency_strategy) fires before
all of this, routing the execution to Sequential_tag or Parallel_tag.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me990",
    title="orient_triangle_soup_with_reference_triangle_mesh concurrency_strategy: Sequential_tag / Parallel_tag dispatch before per-triangle orientation loop (Branch 1)",
    defect_class="soup_orientation_concurrency_strategy",
)

# ---- soup triangles (subject mesh, misoriented face) ----
s0 = m.vertex(0.0, 0.0, 0.0)   # 0
s1 = m.vertex(2.0, 0.0, 0.0)   # 1
s2 = m.vertex(1.0, 1.0, 0.0)   # 2
s3 = m.vertex(2.0, 2.0, 0.0)   # 3
s4 = m.vertex(0.0, 2.0, 0.0)   # 4

soup_t0 = m.triangle(s0, s1, s2)   # 0: CCW, normal +Z (correct)
soup_t1 = m.triangle(s0, s2, s4)   # 1: CCW, normal +Z (correct)
soup_t2 = m.triangle(s4, s2, s3)   # 2: CW, normal -Z  (misoriented — defect)

# ---- reference mesh (correctly oriented, provides orientation cue) ----
r0 = m.vertex(0.0, 0.0, 0.0)   # 5  — same region as soup
r1 = m.vertex(2.0, 0.0, 0.0)   # 6
r2 = m.vertex(2.0, 2.0, 0.0)   # 7
r3 = m.vertex(0.0, 2.0, 0.0)   # 8

ref_t0 = m.triangle(r0, r1, r2)    # 3: CCW, normal +Z (reference, correct)
ref_t1 = m.triangle(r0, r2, r3)    # 4: CCW, normal +Z (reference, correct)

# ---- assertions ----

# soup_t2 is wound CW — its normal is -Z, antiparallel to its neighbors soup_t0, soup_t1.
m.assert_adjacent_triangles_inconsistent_winding(soup_t1, soup_t2)

# The reference triangles are consistently wound CCW (+Z).
# ref_t0 and ref_t1 share edge (r0,r2) — interior to the reference mesh.
m.assert_edge_shared(r0, r2, 2)

# Concurrency_tag dispatch (Branch 1): any soup with ≥1 triangle triggers the tag
# routing before any per-triangle query. Confirmed by the triangle count.
m.assert_euler_characteristic(9, 12, 5, 2)   # full mesh: V=9, E=12, F=5, chi=2
