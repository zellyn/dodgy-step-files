"""Tfa215 — ShapeFix_Face.FixMissingSeam.orientation-correction-partial-closure

TOROIDAL_SURFACE with mixed EDGE_CURVE orientations (.T./.F.) and
FACE_OUTER_BOUND orientation mismatch. Tests orientation-correction-partial-
closure path that repairs orientation during partial-closure seam synthesis.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a TOROIDAL_SURFACE. The
torus has major_radius=3.0 and minor_radius=1.0. The face outer boundary is a
quad EDGE_LOOP where some edges are oriented True and some False — mixed
orientation flags. Additionally, the FACE_OUTER_BOUND uses orientation=False
(mismatch with the winding direction). The OCCT ShapeFix_Face.FixMissingSeam
code path at line 2013 detects the orientation conflicts between edges and the
bound, applies sign flips to edges, and rebuilds the seam with corrected
orientation before the partial-closure test. Without this correction, the seam
synthesis would produce a reversed normal on the torus face.

The torus patch covers a quarter of the equatorial u-range (u ∈ [0, π/2]) and
a partial v-range (v ∈ [0, π/2]), with the defect being the orientation
mismatch between oriented edges and the face bound.

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
    catalog_id="Tfa215",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on TOROIDAL_SURFACE; "
        "major_radius=3.0, minor_radius=1.0; "
        "quad EDGE_LOOP with mixed orientations: edges 0,2 True; edges 1,3 False; "
        "FACE_OUTER_BOUND orientation=False (mismatch with winding); "
        "FixMissingSeam line 2013: orientation-correction-partial-closure path; "
        "detects orientation conflicts, applies sign flips, rebuilds seam; "
        "without correction: reversed normal on torus seam face; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

R = 3.0   # major radius
r = 1.0   # minor radius

# ── TOROIDAL_SURFACE ──────────────────────────────────────────────────────────
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

# ── Torus patch: u ∈ [0, π/2], v ∈ [0, π/2] ─────────────────────────────────
# Corners in parametric space → 3D points
u0, u1 = 0.0, _math.pi / 2
v0, v1 = 0.0, _math.pi / 2

c00 = _tp(u0, v0)  # (R+r, 0, 0)
c10 = _tp(u1, v0)  # (0, R+r, 0)
c11 = _tp(u1, v1)  # (0, (R + r*cos(π/2))*sin(π/2), r*sin(π/2)) = (0, R, r)
c01 = _tp(u0, v1)  # ((R + r*cos(π/2))*cos(0), 0, r*sin(π/2)) = (R, 0, r)

v00 = f.vertex_point(f.cartesian_point(c00))
v10 = f.vertex_point(f.cartesian_point(c10))
v11 = f.vertex_point(f.cartesian_point(c11))
v01 = f.vertex_point(f.cartesian_point(c01))

# 4 edges forming the quad border of the torus patch
# edge 0: c00 → c10 (bottom u-edge at v=v0)
# edge 1: c10 → c11 (right v-edge at u=u1)
# edge 2: c11 → c01 (top u-edge at v=v1, reversed direction)
# edge 3: c01 → c00 (left v-edge at u=u0, reversed direction)
e0 = _straight(v00, c00, v10, c10)
e1 = _straight(v10, c10, v11, c11)
e2 = _straight(v11, c11, v01, c01)
e3 = _straight(v01, c01, v00, c00)

# Mixed orientation: edges 0,2 → True; edges 1,3 → False (mismatch)
# FACE_OUTER_BOUND orientation = False (further mismatch)
# These orientation conflicts trigger FixMissingSeam orientation-correction at line 2013
face_loop = f.edge_loop([
    f.oriented_edge(e0, True),    # bottom u-edge: forward
    f.oriented_edge(e1, False),   # right v-edge: reversed (orientation mismatch)
    f.oriented_edge(e2, True),    # top u-edge: forward (should go c01→c11 for CCW)
    f.oriented_edge(e3, False),   # left v-edge: reversed (orientation mismatch)
])
# FACE_OUTER_BOUND with orientation=False: mismatch with winding direction
face_ob = f.face_outer_bound(face_loop, orientation=False)
face = f.advanced_face([face_ob], torus_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa215.stp")
