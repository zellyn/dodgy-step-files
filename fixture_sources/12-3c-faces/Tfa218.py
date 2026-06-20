"""Tfa218 — circle_parameter

TOROIDAL_SURFACE face whose seam edge spans the 2π u-boundary (u from 6.0
to 0.5, wrapping around). UnionPCurves line 1930 naively swaps aNewF/aNewL
when aNewF > aNewL, producing inverted range [0.5, 6.0] instead of
correctly normalised [6.0, 6.0+0.5].

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a TOROIDAL_SURFACE.
Major radius=3.0, minor radius=0.5. The face covers a small wedge of the
torus near u=0 / u=2π boundary: u ∈ [5.8, 0.5] (wrapping through 2π=6.283).
The seam edge is used twice (.T. and .F.) plus two arcs (at the u-values
5.8 and 0.5) close the wedge.

The periodic domain spans the 2π boundary: aNewF=6.0, aNewL=0.5. The
buggy swap produces [0.5, 6.0], reversing the intended wrap-around range.

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
    catalog_id="Tfa218",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on TOROIDAL_SURFACE; "
        "major_radius=3.0, minor_radius=0.5; "
        "seam edge at u=0 (R+r, 0, 0)→(R-r, 0, 0) used twice (.T. and .F.); "
        "two arcs (at u≈5.8 and u≈0.5) close the wedge near 2π boundary; "
        "UnionPCurves line 1930: aNewF=6.0, aNewL=0.5 span 2π; "
        "buggy swap inverts range to [0.5,6.0] instead of normalised wrap-around; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

R = 3.0    # major radius
r = 0.5    # minor radius

# ── TOROIDAL_SURFACE ──────────────────────────────────────────────────────────
torus_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
torus_surf = f.toroidal_surface(torus_plc, R, r)

# ── Torus parametric → 3D ────────────────────────────────────────────────────
# x = (R + r*cos(v)) * cos(u)
# y = (R + r*cos(v)) * sin(u)
# z = r * sin(v)
def _tp(u, v):
    x = (R + r * _math.cos(v)) * _math.cos(u)
    y = (R + r * _math.cos(v)) * _math.sin(u)
    z = r * _math.sin(v)
    return (x, y, z)

# ── Seam vertices: at u=0, v=0 (outer equator) and u=0, v=π (inner equator) ─
# These are the two ends of the radial seam edge at u=0
pt_seam_outer = f.cartesian_point((R + r, 0.0, 0.0))   # u=0, v=0
pt_seam_inner = f.cartesian_point((R - r, 0.0, 0.0))   # u=0, v=π

v_seam_outer = f.vertex_point(pt_seam_outer)
v_seam_inner = f.vertex_point(pt_seam_inner)

# ── Seam edge: radial line at u=0 from outer to inner ────────────────────────
seam_len = 2 * r
seam_dir = f.direction((-1.0, 0.0, 0.0))
seam_vec = f.vector(seam_dir, seam_len)
seam_line = f.line(pt_seam_outer, seam_vec)
seam_edge = f.edge_curve(v_seam_outer, v_seam_inner, seam_line)

# ── Outer equator circle (full revolution, v=0): center origin, R+r in XY ───
outer_ctr = f.cartesian_point((0.0, 0.0, 0.0))
outer_plc = f.axis2_placement_3d(
    outer_ctr,
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
outer_circle = f.circle(outer_plc, R + r)
# Full outer revolution: v_seam_outer → v_seam_outer
outer_edge = f.edge_curve(v_seam_outer, v_seam_outer, outer_circle)

# ── EDGE_LOOP: seam .T., full outer equator .T., seam .F. ────────────────────
# The 2π-spanning parametric range defect is on the seam edge,
# used in both forward and backward sense through the periodic boundary.
face_loop = f.edge_loop([
    f.oriented_edge(seam_edge,   True),    # outer → inner along seam
    f.oriented_edge(outer_edge,  True),    # full outer equator revolution
    f.oriented_edge(seam_edge,   False),   # inner → outer (reversed seam)
])
face = f.advanced_face([f.face_outer_bound(face_loop)], torus_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa218.stp")
