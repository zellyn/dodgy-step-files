"""Me1142 — volume_connected_components orientation_consistency: one flipped face creates normal inconsistency; orientation_error flagged (Branch 3).

CGAL PMP `PMP.volume_connected_components` Branch 3 (*orientation_consistency*) @ line 640:
  'if(!PMP::is_outward_oriented(cc, pmesh, np))
   { output.orientation_errors.push_back(cc); continue; }'
  — after confirming the component is closed and non-self-intersecting, the
  orientation consistency of face normals is checked. If one or more faces have
  their normal pointing inward (inconsistent with the outward convention), the
  component is flagged as orientation_error.

Defect pattern: a closed tetrahedron (V=4, E=6, F=4, χ=2) where one face has
  been wound clockwise (CW) instead of counter-clockwise (CCW). The three
  correctly-wound faces have outward normals, but the flipped face has its
  normal pointing INTO the tetrahedron's interior. When is_outward_oriented checks
  the consistency of the component's orientation, the flipped face causes the
  check to fail → Branch 3 fires.

Geometry:
  v0=(0,0,0), v1=(3,0,0), v2=(1.5,3,0), v3=(1.5,1,2) — tetrahedron vertices.
  Correct CCW winding (outward normals):
    bottom: (v0,v2,v1) — normal points -Z (down)
    front:  (v0,v1,v3) — normal points outward-front
    right:  (v1,v2,v3) — normal points outward-right
  Flipped face (CW winding, normal points INTO the tetrahedron):
    left:   (v0,v3,v2) — reversed from correct (v0,v2,v3) → normal points inward
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1142",
    title="volume_connected_components orientation_consistency: closed tetrahedron with one CW-wound face; is_outward_oriented fails; orientation_error flagged (Branch 3)",
    defect_class="inconsistent_face_orientation",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.5, 3.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 2.0)   # 3 — apex

# Three correctly wound faces (CCW from outside → outward normals).
t0 = m.triangle(v0, v2, v1)   # 0 — bottom face; normal = -Z (outward-down)
t1 = m.triangle(v0, v1, v3)   # 1 — front face; normal outward-front
t2 = m.triangle(v1, v2, v3)   # 2 — right face; normal outward-right

# One flipped face (CW winding → inward normal — the orientation defect).
# Correct winding for outward normal would be (v0,v3,v2); we use (v0,v2,v3) to flip.
t3 = m.triangle(v0, v2, v3)   # 3 — left face; FLIPPED — normal points into interior

# All edges of the closed tetrahedron shared by exactly 2 faces.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# The flipped face (t3) traverses its shared edges in the SAME direction as its
# neighbors rather than opposite (a consistently-oriented manifold traverses each
# edge in opposite directions across its two incident faces). Both t0 and t3 use
# v0→v2; both t2 and t3 use v2→v3. CGAL's is_outward_oriented detects this by
# shooting a ray from the mesh and checking volume parity → Branch 3 fires.

# Euler: V=4, E=6, F=4, chi = 4-6+4 = 2 (sphere topology, closed manifold).
m.assert_euler_characteristic(4, 6, 4, 2)
