"""Tfa243 — ShapeFix_Face.FixOrientation.ToroidalDiagonalShift

2×2 grid of diagonal period wraps (±uRange, ±vRange) for toroidal surfaces.
Outer loop near corner (u≈0, v≈0), inner loop near opposite corner (u≈2π,
v≈π); without diagonal enumeration, single u-shift succeeds but v-shift
overrides it.

Mechanism: CLOSED_SHELL with TWO ADVANCED_FACEs. face[0] is the defect carrier:
a TOROIDAL_SURFACE with TWO wires at diagonally opposite corners of the (u,v)
parameter domain. The outer FACE_OUTER_BOUND sits near (u≈0, v≈0) and the inner
FACE_BOUND sits near (u≈2π, v≈π). FixOrientation must attempt all four diagonal
shifts (Δu=0/±2π, Δv=0/±π) to align boxes; without the full 2×2 enumeration,
applying just the u-shift succeeds momentarily but the v-shift then overrides it,
and the containment test fails. face[1] is a flat companion on PLANE.

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
    catalog_id="Tfa243",
    defect=(
        "CLOSED_SHELL: face[0] TOROIDAL_SURFACE; two wires at diagonal corners; "
        "outer FACE_OUTER_BOUND: near (u≈0.2, v≈0.2); "
        "inner FACE_BOUND: near (u≈2π-0.2, v≈π-0.2) — diagonally opposite; "
        "FixOrientation diagonal 2×2 shift: (±uRange=2π, ±vRange=π); "
        "single u-shift or v-shift alone fails to align boxes; "
        "full diagonal (Δu=+2π, Δv=+π) required for correct containment; "
        "face[1]: flat PLANE cap; defect IS on live traversal path; no orphans"
    ),
)

R = 5.0   # major radius
r = 1.5   # minor radius

_2PI = 2.0 * _math.pi
_PI = _math.pi

# ── TOROIDAL_SURFACE ───────────────────────────────────────────────────────────
tor_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
torus = f.toroidal_surface(tor_plc, R, r)


def _torus_pt(u, v):
    x = (R + r * _math.cos(v)) * _math.cos(u)
    y = (R + r * _math.cos(v)) * _math.sin(u)
    z = r * _math.sin(v)
    return (x, y, z)


def _line_edge(va, ca, vb, cb):
    dx = cb[0] - ca[0]
    dy = cb[1] - ca[1]
    dz = cb[2] - ca[2]
    length = _math.sqrt(dx * dx + dy * dy + dz * dz)
    d = f.direction((dx / length, dy / length, dz / length))
    return f.edge_curve(va, vb, f.line(f.cartesian_point(ca), f.vector(d, length)))


def _rect_bound(corners_uv, outer=True):
    pts = [_torus_pt(u % _2PI, v % _2PI) for u, v in corners_uv]
    verts = [f.vertex_point(f.cartesian_point(p)) for p in pts]
    edges = []
    n = len(pts)
    for i in range(n):
        edges.append(_line_edge(verts[i], pts[i], verts[(i + 1) % n], pts[(i + 1) % n]))
    loop = f.edge_loop([f.oriented_edge(e, True) for e in edges])
    if outer:
        return f.face_outer_bound(loop)
    else:
        return f.face_bound(loop, orientation=False)


# Outer wire: near (u=0, v=0) corner
du = 0.25
dv = 0.25
outer_corners = [
    (0.05,       0.05),
    (0.05 + du,  0.05),
    (0.05 + du,  0.05 + dv),
    (0.05,       0.05 + dv),
]
outer_bound = _rect_bound(outer_corners, outer=True)

# Inner wire: near (u=2π, v=π) corner — diagonally opposite
# Parametrically these are at the far end of both periods
u_far = _2PI - 0.3
v_far = _PI - 0.3
inner_corners = [
    (u_far,       v_far),
    (u_far + du,  v_far),
    (u_far + du,  v_far + dv),
    (u_far,       v_far + dv),
]
inner_bound = _rect_bound(inner_corners, outer=False)

torus_face = f.advanced_face([outer_bound, inner_bound], torus)

# ── Companion flat PLANE face to close the shell ──────────────────────────────
pc0 = f.cartesian_point((0.0, 0.0, -5.0))
pc1 = f.cartesian_point((1.0, 0.0, -5.0))
pc2 = f.cartesian_point((1.0, 1.0, -5.0))
pc3 = f.cartesian_point((0.0, 1.0, -5.0))
pv0 = f.vertex_point(pc0)
pv1 = f.vertex_point(pc1)
pv2 = f.vertex_point(pc2)
pv3 = f.vertex_point(pc3)
pe01 = f.edge_curve(pv0, pv1, f.line(pc0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
pe12 = f.edge_curve(pv1, pv2, f.line(pc1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
pe23 = f.edge_curve(pv2, pv3, f.line(pc2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
pe30 = f.edge_curve(pv3, pv0, f.line(pc3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))
comp_loop = f.edge_loop([
    f.oriented_edge(pe01, True),
    f.oriented_edge(pe12, True),
    f.oriented_edge(pe23, True),
    f.oriented_edge(pe30, True),
])
comp_plc = f.axis2_placement_3d(
    pc0, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0))
)
comp_face = f.advanced_face([f.face_outer_bound(comp_loop)], f.plane(comp_plc))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([torus_face, comp_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa243.stp")
