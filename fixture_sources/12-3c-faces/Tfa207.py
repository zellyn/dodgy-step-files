"""Tfa207 — FixOrientation PeriodicBoundingBoxShift torus seam wrapping

Toroidal surface with outer and two inner wire loops crossing seams. Tests
periodic bounding-box adjustment branch that applies AdjustByPeriod() shifts
to prevent false non-containment when wires wrap across u/v closure boundaries.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a TOROIDAL_SURFACE. The torus
has major_radius=3.0 and minor_radius=1.0. The face covers a full-revolution
U-patch with an outer wire around the full u-period and two inner hole wires
positioned near the u=0/2π seam — one straddling the seam boundary. The OCCT
FixOrientation code path at lines 1295-1310 calls AdjustByPeriod() to shift
wire bounding boxes so that wires crossing the periodic seam boundary are
correctly recognized as contained within the outer wire. Without periodic shift,
a wire that wraps across u=0/2π reports a bbox entirely outside the outer wire's
bbox, causing false non-containment and incorrect orientation assignment.

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
    catalog_id="Tfa207",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on TOROIDAL_SURFACE; "
        "major_radius=3.0, minor_radius=1.0; "
        "outer wire: u-equator circle (full revolution at v=0); "
        "inner wire 1: small rectangle near u=pi/4 (well inside u-period); "
        "inner wire 2: small rectangle straddling u=0/2pi seam boundary; "
        "FixOrientation PeriodicBoundingBoxShift lines 1295-1310: "
        "AdjustByPeriod() shifts seam-straddling wire bbox into outer-wire range; "
        "without periodic shift: wire 2 bbox outside outer wire → false non-containment; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── TOROIDAL_SURFACE ──────────────────────────────────────────────────────────
R = 3.0   # major radius
r = 1.0   # minor radius

torus_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
torus_surf = f.toroidal_surface(torus_plc, R, r)

# ── Torus 3D position from parametric (u, v) ─────────────────────────────────
# x = (R + r*cos(v)) * cos(u)
# y = (R + r*cos(v)) * sin(u)
# z = r * sin(v)
def _tp(u, v):
    x = (R + r * _math.cos(v)) * _math.cos(u)
    y = (R + r * _math.cos(v)) * _math.sin(u)
    z = r * _math.sin(v)
    return (x, y, z)

def _straight(va, ca, vb, cb):
    dx = cb[0] - ca[0]
    dy = cb[1] - ca[1]
    dz = cb[2] - ca[2]
    length = _math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-12:
        length = 1e-12
    d = f.direction((dx / length, dy / length, dz / length))
    return f.edge_curve(va, vb, f.line(f.cartesian_point(ca), f.vector(d, length)))

# ── Outer wire: full-revolution equator circle at v=0 (closed circle) ─────────
# At v=0: x = (R+r)*cos(u), y = (R+r)*sin(u), z = 0
# Use seam vertex at u=0, v=0 = (R+r, 0, 0)
R_eq = R + r   # = 4.0
pt_eq_seam = f.cartesian_point((R_eq, 0.0, 0.0))
v_eq_seam = f.vertex_point(pt_eq_seam)

# Equator circle (full revolution, z=0 plane, normal +Z)
eq_circ_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
eq_circle = f.circle(eq_circ_plc, R_eq)
eq_edge = f.edge_curve(v_eq_seam, v_eq_seam, eq_circle)

outer_loop = f.edge_loop([f.oriented_edge(eq_edge, True)])
outer_fob = f.face_outer_bound(outer_loop)

# ── Inner wire 1: small rectangle at u≈pi/4, v≈pi/4 (well inside period) ─────
u1_lo, u1_hi = _math.pi/4 - 0.1, _math.pi/4 + 0.1
v1_lo, v1_hi = _math.pi/4 - 0.1, _math.pi/4 + 0.1

c1_00 = _tp(u1_lo, v1_lo)
c1_10 = _tp(u1_hi, v1_lo)
c1_11 = _tp(u1_hi, v1_hi)
c1_01 = _tp(u1_lo, v1_hi)

i1_v00 = f.vertex_point(f.cartesian_point(c1_00))
i1_v10 = f.vertex_point(f.cartesian_point(c1_10))
i1_v11 = f.vertex_point(f.cartesian_point(c1_11))
i1_v01 = f.vertex_point(f.cartesian_point(c1_01))

i1_e0 = _straight(i1_v00, c1_00, i1_v10, c1_10)
i1_e1 = _straight(i1_v10, c1_10, i1_v11, c1_11)
i1_e2 = _straight(i1_v11, c1_11, i1_v01, c1_01)
i1_e3 = _straight(i1_v01, c1_01, i1_v00, c1_00)

inner_loop1 = f.edge_loop([
    f.oriented_edge(i1_e0, True),
    f.oriented_edge(i1_e1, True),
    f.oriented_edge(i1_e2, True),
    f.oriented_edge(i1_e3, True),
])
inner_fb1 = f.face_bound(inner_loop1, False)

# ── Inner wire 2: rectangle straddling u=0/2pi seam ─────────────────────────
# u spans from 2*pi - 0.1 to 2*pi + 0.1 (wraps seam), v near 0
# In 3D: both sides near (R_eq, 0, 0) seam on the equator
u2_lo, u2_hi = -0.1, 0.1   # straddles u=0
v2_lo, v2_hi = 0.1, 0.2

c2_00 = _tp(u2_lo, v2_lo)
c2_10 = _tp(u2_hi, v2_lo)
c2_11 = _tp(u2_hi, v2_hi)
c2_01 = _tp(u2_lo, v2_hi)

i2_v00 = f.vertex_point(f.cartesian_point(c2_00))
i2_v10 = f.vertex_point(f.cartesian_point(c2_10))
i2_v11 = f.vertex_point(f.cartesian_point(c2_11))
i2_v01 = f.vertex_point(f.cartesian_point(c2_01))

i2_e0 = _straight(i2_v00, c2_00, i2_v10, c2_10)
i2_e1 = _straight(i2_v10, c2_10, i2_v11, c2_11)
i2_e2 = _straight(i2_v11, c2_11, i2_v01, c2_01)
i2_e3 = _straight(i2_v01, c2_01, i2_v00, c2_00)

inner_loop2 = f.edge_loop([
    f.oriented_edge(i2_e0, True),
    f.oriented_edge(i2_e1, True),
    f.oriented_edge(i2_e2, True),
    f.oriented_edge(i2_e3, True),
])
inner_fb2 = f.face_bound(inner_loop2, False)

# ── Assemble face ─────────────────────────────────────────────────────────────
face = f.advanced_face([outer_fob, inner_fb1, inner_fb2], torus_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa207.stp")
