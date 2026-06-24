"""Me981 — merge_reversible_connected_components orientation_flip_feasibility:
  flipping one component's orientation enables boundary stitching (Branch 2).

CGAL PMP `PMP.merge_reversible_connected_components` Branch 2
  (*orientation_flip_feasibility*) @ line 1080:
  'if (can_stitch_after_flip(component_A, component_B))
   { reverse_face_orientations(component_A); stitch(component_A, component_B); }'
  — after collecting component candidates the algorithm tests whether flipping
  a component's winding enables the boundary halfedges to pair up. This branch
  fires when two components have geometrically matching boundary loops but
  opposite winding orders — i.e., one must be flipped before borders can be
  stitched together.

Defect pattern: two flat, open triangle-pair patches whose shared-position
  boundary edges are present but with reversed halfedge orientation. Patch A
  (triangles 0-1) is wound CCW; Patch B (triangles 2-3) covers the same XY
  rectangle but wound CW (all triangles reversed). Their boundaries are
  geometrically coincident but half-edges point in opposite directions. Flipping
  Patch B's winding makes its border halfedges align with Patch A's, enabling
  stitch_borders to merge them.

Geometry:
  Patch A (CCW): a0=(0,0,0), a1=(1,0,0), a2=(1,1,0), a3=(0,1,0)
    t0=(a0,a1,a2), t1=(a0,a2,a3)  — normal = +Z
  Patch B (CW, misoriented): same XY positions shifted to (0,0,0.001) …
    b0=(0,0,0.001), b1=(1,0,0.001), b2=(1,1,0.001), b3=(0,1,0.001)
    t2=(b0,b2,b1), t3=(b0,b3,b2)  — normal = -Z (CW winding)
  CCs are disjoint (no shared edges) but geometrically very close (dZ=0.001).
  Inconsistent winding between t0 and t2 is detectable via normal dot product.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me981",
    title="merge_reversible_connected_components orientation_flip_feasibility: Patch-B wound CW vs Patch-A CCW; flip Patch-B enables stitch (Branch 2)",
    defect_class="inverted_normals",
)

# Patch A: CCW-wound flat quad (normal = +Z).
a0 = m.vertex(0.0, 0.0, 0.0)   # 0
a1 = m.vertex(1.0, 0.0, 0.0)   # 1
a2 = m.vertex(1.0, 1.0, 0.0)   # 2
a3 = m.vertex(0.0, 1.0, 0.0)   # 3
t0 = m.triangle(a0, a1, a2)    # 0: CCW; normal +Z
t1 = m.triangle(a0, a2, a3)    # 1: CCW; normal +Z

# Patch B: CW-wound flat quad (normal = -Z), nearly co-planar (dZ=0.001).
b0 = m.vertex(0.0, 0.0, 0.001)  # 4
b1 = m.vertex(1.0, 0.0, 0.001)  # 5
b2 = m.vertex(1.0, 1.0, 0.001)  # 6
b3 = m.vertex(0.0, 1.0, 0.001)  # 7
t2 = m.triangle(b0, b2, b1)     # 2: CW → normal -Z (misoriented)
t3 = m.triangle(b0, b3, b2)     # 3: CW → normal -Z (misoriented)

# Components are disconnected: no shared edge between Patch A and Patch B.
m.assert_triangle_not_reachable_from(2, 0)

# Patch A: interior diagonal edge shared by 2 triangles.
m.assert_edge_shared(a0, a2, 2)

# Patch B: interior diagonal shared by 2 triangles.
m.assert_edge_shared(b0, b2, 2)

# Patch B's t2 has CW winding → normal Z-component is negative.
# t2 = (b0,b2,b1): (b2-b0)×(b1-b0) = (1,1,0.001)×(1,0,0.001) = (1*0.001-0.001*0, 0.001*1-1*0.001, 1*0-1*1) ≈ (0, 0, -1)
m.assert_triangle_normal_z_negative(2)

# Euler: two open quad patches — each V=4,E=5,F=2,chi=1; combined V=8,E=10,F=4,chi=2.
m.assert_euler_characteristic(8, 10, 4, 2)
