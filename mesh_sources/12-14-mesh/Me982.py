"""Me982 — merge_reversible_connected_components stitching_compatibility_check:
  border halfedges are geometrically compatible; vertices merged (Branch 3).

CGAL PMP `PMP.merge_reversible_connected_components` Branch 3
  (*stitching_compatibility_check*) @ line 1110:
  'for (halfedge h : border_halfedges(component))
   { if (compatible_for_stitch(h, candidate))
     { stitch_borders(component, candidate); } }'
  — the stitching pass iterates over border halfedges of each component and
  tests geometric compatibility with the other component's boundary edges.
  Compatible pairs (endpoint coordinates match within tolerance) are merged
  via stitch_borders. This branch fires when at least one border halfedge
  pair passes the geometric compatibility test.

Defect pattern: two open triangle patches that share no triangles but whose
  boundary edge endpoints are spatially coincident. Patch A and Patch B each
  form an open fan (one triangle each), and their free boundary edges have
  vertices at the same XYZ coordinates (within tolerance). The stitch
  compatibility check passes; stitch_borders merges the vertex pairs and
  welds the two components into one connected surface.

Geometry:
  Patch A: a0=(0,0,0), a1=(1,0,0), a2=(0.5,1,0)
    t0=(a0,a1,a2) — one open triangle; boundary = a0→a1→a2→a0
  Patch B: b0=(1,0,0), b1=(2,0,0), b2=(1.5,1,0)
    t1=(b0,b1,b2) — one open triangle; boundary = b0→b1→b2→b0
  b0 is at (1,0,0) which equals a1; these endpoints are coincident → stitch.
  After stitch, a1/b0 merge: the two triangles share a vertex at (1,0,0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me982",
    title="merge_reversible_connected_components stitching_compatibility_check: border edge a1–a2 and b0 endpoint coincident; stitch_borders welds components (Branch 3)",
    defect_class="near_coincident_vertex",
)

# Patch A: single open triangle.
a0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left base
a1 = m.vertex(1.0, 0.0, 0.0)   # 1 — right base (will coincide with b0)
a2 = m.vertex(0.5, 1.0, 0.0)   # 2 — apex
t0 = m.triangle(a0, a1, a2)    # 0: Patch A

# Patch B: single open triangle, sharing b0 position with a1.
b0 = m.vertex(1.0, 0.0, 0.0)   # 3 — coincides with a1 at (1,0,0)
b1 = m.vertex(2.0, 0.0, 0.0)   # 4 — far right base
b2 = m.vertex(1.5, 1.0, 0.0)   # 5 — far apex
t1 = m.triangle(b0, b1, b2)    # 1: Patch B

# Components are disconnected (no shared edges in the half-edge structure
# despite the geometric coincidence at (1,0,0)).
m.assert_triangle_not_reachable_from(1, 0)

# The coincident boundary vertex pair (a1, b0) = (vertex 1, vertex 3).
# Both at (1,0,0); their distance is 0 — well within stitch tolerance.
m.assert_vertex_pair_distance_lt(1, 3, 1e-9)

# a1 and b0 do not share any triangle in the current (unstitched) mesh.
m.assert_vertex_pair_no_shared_triangle(1, 3)

# Euler: two isolated open triangles — V=6,E=6,F=2,chi=2.
m.assert_euler_characteristic(6, 6, 2, 2)
