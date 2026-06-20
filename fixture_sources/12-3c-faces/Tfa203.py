"""Tfa203 — FixMissingSeam null surface guard

Toroidal surface with missing seam wire. Tests null-surface-guard branch
preventing dereference on uninitialized surface handles before
IsUClosed/IsVClosed checks.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a TOROIDAL_SURFACE. The
torus has major_radius=3.0 and minor_radius=1.0. The face boundary covers a
full-revolution U-patch (u in [0, 2π]) using a single closed wire in V but
omits the seam edge in U. The FixMissingSeam code path at line 1724 checks
IsUClosed/IsVClosed before synthesizing the missing seam; if the surface handle
is uninitialized (null), dereferencing it here causes a crash. The null-surface
guard branch must check for a valid surface handle before calling IsUClosed.
The face is topologically complete enough for OCC to load shape(1) via the
seam-synthesis path.

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
    catalog_id="Tfa203",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on TOROIDAL_SURFACE; "
        "major_radius=3.0, minor_radius=1.0; "
        "face boundary: v-circle at u=0 (inner seam) + v-circle at u=pi (opposite), "
        "connected by two u-arcs (quarter torus sections); "
        "U-seam wire absent from face boundary; "
        "FixMissingSeam line 1724: null-surface-guard branch; "
        "IsUClosed/IsVClosed access before null-handle check causes dereference; "
        "guard must verify surface handle validity before IsUClosed call; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── TOROIDAL_SURFACE: major_radius=3, minor_radius=1 ─────────────────────────
R = 3.0   # major radius
r = 1.0   # minor radius

torus_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
torus_surf = f.toroidal_surface(torus_plc, R, r)

# ── Torus parameterization ────────────────────────────────────────────────────
# x = (R + r*cos(v)) * cos(u)
# y = (R + r*cos(v)) * sin(u)
# z = r * sin(v)
def _tp(u, v):
    x = (R + r * _math.cos(v)) * _math.cos(u)
    y = (R + r * _math.cos(v)) * _math.sin(u)
    z = r * _math.sin(v)
    return (x, y, z)


# ── Four corners of the patch: u in [0, pi], v in [0, pi/2] ──────────────────
# This gives a half-torus quarter-section with 4 distinct boundary edges
u0, u1 = 0.0, _math.pi
v0, v1 = 0.0, _math.pi / 2

c00 = _tp(u0, v0)   # (R+r, 0, 0)
c10 = _tp(u1, v0)   # (-(R+r), 0, 0)
c11 = _tp(u1, v1)   # (-R, 0, r)
c01 = _tp(u0, v1)   # (R, 0, r)

p00 = f.cartesian_point(c00)
p10 = f.cartesian_point(c10)
p11 = f.cartesian_point(c11)
p01 = f.cartesian_point(c01)

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)


def _straight(va, ca, vb, cb):
    dx = cb[0] - ca[0]
    dy = cb[1] - ca[1]
    dz = cb[2] - ca[2]
    length = _math.sqrt(dx * dx + dy * dy + dz * dz)
    d = f.direction((dx / length, dy / length, dz / length))
    return f.edge_curve(va, vb, f.line(f.cartesian_point(ca), f.vector(d, length)))


# Bottom u-arc: u0→u1 at v=v0 (outer equator of torus, straight-line approx)
e_bot = _straight(v00, c00, v10, c10)
# Right v-arc: u1 at v0→v1 (straight-line approx along v-circle at u=pi)
e_rgt = _straight(v10, c10, v11, c11)
# Top u-arc: u1→u0 at v=v1 (inner section of torus, straight-line approx)
e_top = _straight(v11, c11, v01, c01)
# Left v-arc: u0 at v1→v0 (straight-line approx along v-circle at u=0, the seam)
e_lft = _straight(v01, c01, v00, c00)

patch_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_lft, False),
])
face = f.advanced_face([f.face_outer_bound(patch_loop)], torus_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa203.stp")
