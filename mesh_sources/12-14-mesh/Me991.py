"""Me991 — orient_triangle_soup_with_reference_triangle_mesh aabb_tree_construction: AABB tree built from reference mesh faces for closest-face queries (Branch 2).

CGAL PMP `PMP.orient_triangle_soup_with_reference_triangle_mesh` Branch 2 (*aabb_tree_construction*) @ line 300:
  After the concurrency tag dispatch the function constructs an
  CGAL::AABB_tree over the *reference* triangle mesh faces. This tree is
  used to answer closest_point_and_primitive queries for each soup face.
  Branch 2 fires when the reference mesh is non-empty (has ≥1 face),
  causing the AABB_tree constructor to build internal bounding-box nodes
  over the reference faces.

Defect pattern: a reference mesh that forms a prominent bounding box
  (triangles well separated in all three axes) so the AABB tree is
  forced to build non-trivial internal nodes. The soup contains two
  triangles to be oriented; one is in correct winding, the other is
  reversed. The AABB tree must hold the reference faces and return a
  valid closest primitive for each soup query.

Geometry (reference mesh — clear bounding box, feeds AABB tree):
  A tetrahedron-like reference with faces spanning x=[0,3], y=[0,3], z=[0,3]:
    r0=(0,0,0), r1=(3,0,0), r2=(0,3,0)
    ref_t0=(r0,r1,r2): CCW, normal roughly +Z.

  A second reference triangle at z=1 for spatial extent:
    r3=(0,0,1), r4=(3,0,1), r5=(0,3,1)
    ref_t1=(r3,r4,r5): CCW, normal +Z.

  Together they provide a clear bounding volume [0,3]×[0,3]×[0,1]
  that populates AABB_tree internal nodes — Branch 2 fires.

Geometry (soup — subject triangles to orient):
  Two triangles in the z=0.5 plane (between the two reference layers):
    s0=(0,0,0.5), s1=(2,0,0.5), s2=(0,2,0.5)
    soup_t0=(s0,s1,s2): CCW, normal +Z (correct).

    s3=(1,0,0.5), s4=(3,0,0.5), s5=(1,3,0.5)
    soup_t1=(s3,s5,s4): CW, normal -Z (misoriented — the defect).

The AABB tree over ref_t0 and ref_t1 is queried for each soup triangle's
centroid. Branch 2 has fired by the time the first query is issued.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me991",
    title="orient_triangle_soup_with_reference_triangle_mesh aabb_tree_construction: AABB tree built from non-empty reference mesh with clear bounding box (Branch 2)",
    defect_class="soup_orientation_aabb_tree_construction",
)

# ---- reference mesh (two spatially separated triangles for AABB tree) ----
r0 = m.vertex(0.0, 0.0, 0.0)   # 0
r1 = m.vertex(3.0, 0.0, 0.0)   # 1
r2 = m.vertex(0.0, 3.0, 0.0)   # 2

r3 = m.vertex(0.0, 0.0, 1.0)   # 3
r4 = m.vertex(3.0, 0.0, 1.0)   # 4
r5 = m.vertex(0.0, 3.0, 1.0)   # 5

ref_t0 = m.triangle(r0, r1, r2)    # 0: CCW, normal roughly +Z (reference layer z=0)
ref_t1 = m.triangle(r3, r4, r5)    # 1: CCW, normal +Z (reference layer z=1)

# ---- soup triangles (subject mesh to orient) ----
s0 = m.vertex(0.0, 0.0, 0.5)   # 6
s1 = m.vertex(2.0, 0.0, 0.5)   # 7
s2 = m.vertex(0.0, 2.0, 0.5)   # 8

s3 = m.vertex(1.0, 0.0, 0.5)   # 9
s4 = m.vertex(3.0, 0.0, 0.5)   # 10
s5 = m.vertex(1.0, 3.0, 0.5)   # 11

soup_t0 = m.triangle(s0, s1, s2)   # 2: CCW, normal +Z (correct)
soup_t1 = m.triangle(s3, s5, s4)   # 3: CW, normal -Z  (misoriented — defect)

# ---- assertions ----

# soup_t1 is wound CW — its normal is -Z, defect relative to reference orientation.
m.assert_triangle_normal_z_negative(soup_t1)

# Reference triangles r0-r1-r2 and r3-r4-r5: bounding box spans
# x=[0,3], y=[0,3], z=[0,1]. AABB_tree construction requires ≥1 face — Branch 2.
# Confirm both reference faces exist as separate triangles (no shared edges).
m.assert_edge_shared(r0, r1, 1)   # boundary of ref_t0
m.assert_edge_shared(r3, r4, 1)   # boundary of ref_t1

# Euler for the full mesh (ref + soup, 4 triangles, no shared edges between groups):
# V=12, E=12 (3 per triangle, no sharing across groups), F=4, chi=4
m.assert_euler_characteristic(12, 12, 4, 4)
