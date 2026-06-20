"""Tfa235 — FixMissingSeam P-curve absence on torus

TOROIDAL_SURFACE face with U-seam loop traversing toroidal topology; missing
P-curve geometry on seam edge. Tests P-curve lookup failure path and early
abort before seam insertion.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a TOROIDAL_SURFACE. The
torus (major=4.0, minor=1.0) has a seam edge along the U=0 meridian. The face
loop includes the seam edge (used forward then reversed) and top/bottom circles
in the V direction. Because the seam edge carries no PCURVE entity, the
ShapeFix_Face::FixMissingSeam() lookup for a 2D parameter-space curve on the
seam edge fails — the code finds no pcurve attached to that edge — and aborts
the seam-insertion procedure early, before any geometry is written. This
exercises the P-curve lookup failure path (early abort branch) in the seam-
insertion logic.

Byte assertions:
  - contains(b'TOROIDAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa235",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on TOROIDAL_SURFACE; "
        "major_radius=4.0, minor_radius=1.0; "
        "seam loop: seam_line(T) + v_circle_at_0(T) + seam_line(F) + v_circle_at_pi(F); "
        "seam edge has NO PCURVE: 3D line only, no 2D parameter-space curve; "
        "ShapeFix_Face::FixMissingSeam(): P-curve lookup fails on seam edge; "
        "early abort before seam insertion: no pcurve → skip seam write; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

R = 4.0   # major radius
r = 1.0   # minor radius

# ── TOROIDAL_SURFACE ──────────────────────────────────────────────────────────
torus_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
torus_surf = f.toroidal_surface(torus_plc, R, r)

# ── 3D positions from torus parametric: u=0 meridian ─────────────────────────
# At u=0: x=(R+r*cos(v)), y=0, z=r*sin(v)
# v=0:  (R+r, 0, 0) = (5, 0, 0)
# v=pi: (R-r, 0, 0) = (3, 0, 0)
pt_v0  = f.cartesian_point((R + r, 0.0, 0.0))   # v=0 point on u=0 meridian
pt_vpi = f.cartesian_point((R - r, 0.0, 0.0))   # v=π point on u=0 meridian

v_v0  = f.vertex_point(pt_v0)
v_vpi = f.vertex_point(pt_vpi)

# ── Seam edge: 3D line along u=0 meridian from v=0 to v=π ───────────────────
# No PCURVE attached — the missing P-curve triggers the failure path.
seam_dx  = (R - r) - (R + r)  # = -2r = -2
seam_len = abs(seam_dx)
seam_line = f.line(pt_v0, f.vector(f.direction((-1.0, 0.0, 0.0)), seam_len))
seam_edge = f.edge_curve(v_v0, v_vpi, seam_line)

# ── V-circles: at v=0 and v=π of the torus (full revolution in U) ────────────
# v=0 circle: radius = R+r, in z=0 plane
v0_ctr = f.cartesian_point((0.0, 0.0, 0.0))
v0_plc = f.axis2_placement_3d(v0_ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
v0_circle = f.circle(v0_plc, R + r)
v0_edge   = f.edge_curve(v_v0, v_v0, v0_circle)   # degenerate (same vertex)

# v=π circle: radius = R-r, in z=0 plane
vpi_ctr = f.cartesian_point((0.0, 0.0, 0.0))
vpi_plc = f.axis2_placement_3d(vpi_ctr, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
vpi_circle = f.circle(vpi_plc, R - r)
vpi_edge   = f.edge_curve(v_vpi, v_vpi, vpi_circle)  # degenerate (same vertex)

# ── EDGE_LOOP: seam(T) + v0_circle(T) + seam(F) + vpi_circle(F) ─────────────
# Traversal: v0→vpi via seam forward; full circle at v=0; vpi→v0 via seam back;
# full circle at v=π (reversed).
face_loop = f.edge_loop([
    f.oriented_edge(seam_edge,  True),
    f.oriented_edge(v0_edge,    True),
    f.oriented_edge(seam_edge,  False),
    f.oriented_edge(vpi_edge,   False),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], torus_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa235.stp")
