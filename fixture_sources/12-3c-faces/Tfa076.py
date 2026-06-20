"""Tfa076 — FixAddNaturalBound seam-edge skip.

Catalog claim: Surface-of-revolution with seam edge. Natural boundary insertion
skipped when seam edge confuses the closure detector on periodicity-conditional
surfaces. Face has outer wire on torus-like surface; FixAddNaturalBound should
detect periodic boundary and insert natural edges, but seam edge at u=0 causes
interval detection to bypass U-closed surface condition on non-periodic mode.

Mechanism: CLOSED_SHELL containing a TOROIDAL_SURFACE face that wraps the full
U-period (2*pi). The seam edge at u=0 (the vertex at theta=0) appears in the
outer wire and confuses the interval closure detector. A second face (a disc
on a plane) closes the shell to form shape(1).

Byte assertions:
  - contains(b'TOROIDAL_SURFACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa076",
    defect=(
        "CLOSED_SHELL: TOROIDAL_SURFACE face (major=5, minor=2) wrapping full U-period; "
        "seam EDGE_CURVE at u=0 (theta=0) used .T. and .F. in same EDGE_LOOP; "
        "v-circle (inner equator) closed edge at v-seam; "
        "seam edge at u=0 confuses FixAddNaturalBound interval detector: "
        "periodicity-conditional path bypassed when seam coincides with u=0; "
        "natural bounds at U-seam not inserted; "
        "second face: closed disc on inner-equator plane closes shell; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Torus parameters: major radius R=5 (distance to tube center), minor radius r=2 (tube radius)
R = 5.0
r = 2.0

# ── Seam vertex on torus: at u=0, v=0 → position (R+r, 0, 0) = (7, 0, 0) ────
pt_seam = f.cartesian_point((R + r, 0.0, 0.0))
v_seam  = f.vertex_point(pt_seam)

# ── U-seam edge: the meridian circle at u=0 (the seam circle on the tube) ────
# This is a circle in the XZ plane centered at (R, 0, 0) with radius r
seam_ctr = f.cartesian_point((R, 0.0, 0.0))
seam_ax  = f.direction((0.0, 1.0, 0.0))   # axis pointing in Y (the rotation axis of the tube at u=0)
seam_ref = f.direction((1.0, 0.0, 0.0))   # reference towards (R+r, 0, 0)
seam_plc = f.axis2_placement_3d(seam_ctr, seam_ax, seam_ref)
seam_circle = f.circle(seam_plc, r)
seam_edge = f.edge_curve(v_seam, v_seam, seam_circle)   # closed seam circle

# ── V-seam edge: the spine circle in XY plane, full revolution, at v=0 ────────
# This is a circle at z=0 centered at origin with radius R, closed at seam vertex
spine_ctr = f.cartesian_point((0.0, 0.0, 0.0))
spine_ax  = f.direction((0.0, 0.0, 1.0))
spine_ref = f.direction((1.0, 0.0, 0.0))
spine_plc = f.axis2_placement_3d(spine_ctr, spine_ax, spine_ref)
spine_circle = f.circle(spine_plc, R + r)
# Closed circle edge: start=end=v_seam (outer equator at z=0, r_outer=R+r)
spine_edge = f.edge_curve(v_seam, v_seam, spine_circle)

# ── TOROIDAL_SURFACE ──────────────────────────────────────────────────────────
torus_orig = f.cartesian_point((0.0, 0.0, 0.0))
torus_ax   = f.direction((0.0, 0.0, 1.0))
torus_ref  = f.direction((1.0, 0.0, 0.0))
torus_plc  = f.axis2_placement_3d(torus_orig, torus_ax, torus_ref)
torus_surf = f.toroidal_surface(torus_plc, R, r)

# ── Torus face: full torus, seam at u=0, v=0 ──────────────────────────────────
# EDGE_LOOP for full torus:
#   seam (u=0 circle) .T., spine (v=0 circle) .T., seam .F., spine .F.
# This is the pattern that trips FixAddNaturalBound: seam at u=0 prevents
# natural bound insertion when the interval detector sees the seam as a zero-measure interval.
torus_loop = f.edge_loop([
    f.oriented_edge(seam_edge,   True),
    f.oriented_edge(spine_edge,  True),
    f.oriented_edge(seam_edge,   False),
    f.oriented_edge(spine_edge,  False),
])
torus_fob  = f.face_outer_bound(torus_loop)
face_torus = f.advanced_face([torus_fob], torus_surf)

# ── Closing face: outer-equator disc at z=0 ──────────────────────────────────
# A flat disc on Z=0 closing the outer equatorial loop (radius=R+r)
disc_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
disc_plane = f.plane(disc_plc)
disc_loop  = f.edge_loop([f.oriented_edge(spine_edge, True)])
disc_fob   = f.face_outer_bound(disc_loop)
face_disc  = f.advanced_face([disc_fob], disc_plane)

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face_torus, face_disc])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa076.stp")
