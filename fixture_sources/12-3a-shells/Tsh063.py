"""Tsh063 — Adjacent toroidal faces with identical parameters are not detected as same-surface.

Catalog claim: Two adjacent faces on the same TOROIDAL_SURFACE (e.g., a torus split into
halves by a planar cut, both halves later resurrected) are not detected as sharing a surface
because the surface-equality check uses pointer comparison rather than geometric equivalence.
Both halves reference distinct TOROIDAL_SURFACE entities with identical parameters, so
adjacent same-surface face merging skips them.

Mechanism IS the shell structure: 2 ADVANCED_FACEs are wired into one OPEN_SHELL, each
referencing its own TOROIDAL_SURFACE entity but with IDENTICAL major_radius (4.0),
minor_radius (1.0), and AXIS2_PLACEMENT_3D parameters. The two TOROIDAL_SURFACE entities
ARE distinct entities (different entity IDs) but parametrically equivalent. The shared
boundary edge (at v=pi, the equatorial circle) IS wired into both faces' EDGE_LOOPs via
shared EDGE_CURVE/VERTEX_POINT entities. A pointer-comparison-based surface-equality check
returns false; the merge is skipped despite the surfaces being geometrically identical.

Byte assertions:
  - contains(b'TOROIDAL_SURFACE')
  - contains(b'OPEN_SHELL')
  - count_entity_def(b'ADVANCED_FACE') == 2

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh063",
    defect=(
        "OPEN_SHELL with 2 ADVANCED_FACEs each on its own TOROIDAL_SURFACE entity; "
        "both TOROIDAL_SURFACE entities have IDENTICAL parameters (major=4.0, minor=1.0, "
        "same AXIS2_PLACEMENT_3D) but ARE distinct entities (different IDs); "
        "distinct TOROIDAL_SURFACE entities with identical parameters IS the mechanism; "
        "pointer-comparison surface-equality check returns false despite geometric identity; "
        "same-surface face merge is skipped; "
        "fix: compare surface parameters structurally (axis position, radii) not by pointer; "
        "collapse parametrically equal surfaces to one canonical entity"
    ),
)

# Shared torus axis: origin at (0,0,0), Z-axis up, X-ref
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))

# Two DISTINCT AXIS2_PLACEMENT_3D entities with IDENTICAL parameters — IS the defect
plc_a = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)), f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
plc_b = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)), f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))

MAJOR_R = 4.0
MINOR_R = 1.0

# Two DISTINCT TOROIDAL_SURFACE entities with IDENTICAL radii — IS the mechanism
torus_a = f.toroidal_surface(plc_a, MAJOR_R, MINOR_R)
torus_b = f.toroidal_surface(plc_b, MAJOR_R, MINOR_R)

# Shared boundary: equatorial circle at v=0 (the outer equator of the torus)
# At v=0, the seam circle is the circle at radius MAJOR_R in the XY plane
seam_orig = f.cartesian_point((0.0, 0.0, 0.0))
seam_plc  = f.axis2_placement_3d(seam_orig, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
seam_circle = f.circle(seam_plc, MAJOR_R)

# Seam point at (MAJOR_R, 0, 0): start/end of the shared boundary
p_seam = f.cartesian_point((MAJOR_R, 0.0, 0.0))
v_seam_start = f.vertex_point(p_seam)
# Degenerate full-circle seam: same vertex for start and end
v_seam_end   = f.vertex_point(f.cartesian_point((MAJOR_R, 0.0, 0.0)))

# Shared boundary edge: full circle (v=0 meridian of torus in XY plane)
shared_edge = f.edge_curve(v_seam_start, v_seam_end, seam_circle)

# Upper half torus (v = 0..pi): ADVANCED_FACE A on torus_a
loop_a = f.edge_loop([f.oriented_edge(shared_edge, True)])
face_a = f.advanced_face([f.face_outer_bound(loop_a)], torus_a)

# Lower half torus (v = pi..2pi): ADVANCED_FACE B on torus_b
loop_b = f.edge_loop([f.oriented_edge(shared_edge, False)])
face_b = f.advanced_face([f.face_outer_bound(loop_b)], torus_b)

# OPEN_SHELL: two torus halves on distinct-but-identical TOROIDAL_SURFACE IS the shell
shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
