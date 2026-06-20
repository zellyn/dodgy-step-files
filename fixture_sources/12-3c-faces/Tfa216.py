"""Tfa216 — seam_detection_orientation_loss

TOROIDAL_SURFACE with seam edge used twice (forward and backward) in an
EDGE_LOOP. The isForward flag for the seam edge becomes stale after edge
reversal in UnionPCurves, corrupting accumulated pcurve orientation.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a TOROIDAL_SURFACE.
Major radius=2.0, minor radius=0.5. The seam edge (at u=0, full v-circle)
is used twice in the EDGE_LOOP: once forward (.T.) and once backward (.F.)
to close the revolution. Two circle arcs at v=0 (top) and v=π (bottom) of
the meridian complete the loop.

The OCCT UnionPCurves code path at line 1829 reverses the seam edge but
does not update the isForward tracking flag, leaving orientation state
stale. The accumulated pcurve orientation is then corrupted when subsequent
edges are merged.

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
    catalog_id="Tfa216",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on TOROIDAL_SURFACE; "
        "major_radius=2.0, minor_radius=0.5; "
        "seam edge (v_top→v_bot at u=0) used twice in EDGE_LOOP (.T. and .F.); "
        "two meridian circles (v=0 top, v=π bottom) close the revolution; "
        "UnionPCurves line 1829: seam reversal without isForward flag update; "
        "stale isForward tracking corrupts accumulated pcurve orientation; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

R = 2.0    # major radius
r = 0.5    # minor radius

# ── TOROIDAL_SURFACE at origin, axis +Z ───────────────────────────────────────
torus_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
torus_surf = f.toroidal_surface(torus_plc, R, r)

# ── Seam vertices: u=0, v=0 (top of minor circle) and u=0, v=π (bottom) ──────
# At (u=0, v=0): x = (R+r)*cos(0) = R+r, y=0, z=0 → (2.5, 0, 0)
# At (u=0, v=π): x = (R-r)*cos(0) = R-r, y=0, z=0 → (1.5, 0, 0)
pt_seam_top = f.cartesian_point((R + r, 0.0, 0.0))
pt_seam_bot = f.cartesian_point((R - r, 0.0, 0.0))

v_seam_top = f.vertex_point(pt_seam_top)
v_seam_bot = f.vertex_point(pt_seam_bot)

# ── Seam edge: line from seam_top to seam_bot (inward radial at u=0) ─────────
dx = (R - r) - (R + r)   # = -2r = -1.0
dy = 0.0
dz = 0.0
seam_len = abs(dx)
seam_dir = f.direction((-1.0, 0.0, 0.0))
seam_vec = f.vector(seam_dir, seam_len)
seam_line = f.line(pt_seam_top, seam_vec)
seam_edge = f.edge_curve(v_seam_top, v_seam_bot, seam_line)

# ── Top meridian circle: center (R, 0, 0), radius r, in the XZ plane at u=0 ──
# v=0 → top of minor circle at u=0; circle axis in +Y direction (XZ plane)
top_ctr = f.cartesian_point((R, 0.0, 0.0))
top_plc = f.axis2_placement_3d(
    top_ctr,
    f.direction((0.0, 1.0, 0.0)),   # normal to XZ plane
    f.direction((1.0, 0.0, 0.0)),   # ref dir → v=0 at (R+r, 0, 0)
)
# Full minor circle from v_seam_top back to v_seam_top (closed circle)
top_circle = f.circle(top_plc, r)
top_edge = f.edge_curve(v_seam_top, v_seam_top, top_circle)

# ── Bottom meridian circle: center (R, 0, 0), same circle, v_seam_bot loop ───
# Actually for the revolution closure we need a full torus revolution.
# Use the major circle (u-circle) at v=0: center (0,0,0), radius R+r, in XY.
major_ctr = f.cartesian_point((0.0, 0.0, 0.0))
# Major circle at v=0 (outer equator): center origin, radius R+r, in XY plane
major_outer_plc = f.axis2_placement_3d(
    major_ctr,
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
major_outer_circle = f.circle(major_outer_plc, R + r)
# Full outer equator circle: v_seam_top → v_seam_top (full revolution)
outer_edge = f.edge_curve(v_seam_top, v_seam_top, major_outer_circle)

# ── EDGE_LOOP: seam .T., outer_circle .T., seam .F. ─────────────────────────
# 3-edge loop: seam forward, full outer circle, seam backward
# The seam is the defect: used twice, isForward tracking fails
face_loop = f.edge_loop([
    f.oriented_edge(seam_edge,   True),    # up the seam (top→bot direction)
    f.oriented_edge(outer_edge,  True),    # full revolution outer equator
    f.oriented_edge(seam_edge,   False),   # down the seam — same edge reversed
])
face = f.advanced_face([f.face_outer_bound(face_loop)], torus_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa216.stp")
