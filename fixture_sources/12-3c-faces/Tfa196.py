"""Tfa196 — ShapeAnalysis_Surface.ComputeSingularities toroidal-pinch

A toroidal face whose minor radius approaches zero creates a "pinch" singularity
where opposite surface points coincide. The singularity detector must recognize
this degenerate locus; incomplete classification allows pinched geometries to
pass validation unchecked, producing unpredictable healing outcomes downstream.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE on a TOROIDAL_SURFACE with major
radius 5.0 and near-zero minor radius 0.005. The tube cross-section radius is
at 0.1% of the major radius, creating a "pinched" torus where points on
opposite sides of the tube nearly coincide. The face covers a small
parametric patch (u in [0, pi/2], v full circle) to yield n_faces_total == 1.
ComputeSingularities must identify the pinch locus at the inner equator
(where tube radius ≈ 0) and classify it as a boundary singularity.
Defect IS on live face traversal path.

Byte assertions:
  - contains(b'TOROIDAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(4) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa196",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on TOROIDAL_SURFACE; "
        "major_radius=5.0, minor_radius=0.005 (near-zero pinch); "
        "patch: u in [0, pi/2] × v full circle (small v-patch); "
        "pinch locus: inner equator where tube radius ≈ 0; "
        "ComputeSingularities incomplete: misses pinch singularity on degenerate torus; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# Parameters: major R=5, minor r=0.005 (pinch torus)
R = 5.0
r = 0.005

# ── TOROIDAL_SURFACE at origin ────────────────────────────────────────────────
torus_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
torus_surf = f.toroidal_surface(torus_plc, R, r)

# ── Rectangular patch on the torus: u in [0, pi/2], v in [0, pi/2] ───────────
# Torus parameterization: x=(R+r*cos(v))*cos(u), y=(R+r*cos(v))*sin(u), z=r*sin(v)
def _torus_pt(u, v):
    x = (R + r * _math.cos(v)) * _math.cos(u)
    y = (R + r * _math.cos(v)) * _math.sin(u)
    z = r * _math.sin(v)
    return (x, y, z)


u0, u1 = 0.0, _math.pi / 2
v0, v1 = 0.0, _math.pi / 2

c00 = _torus_pt(u0, v0)
c10 = _torus_pt(u1, v0)
c11 = _torus_pt(u1, v1)
c01 = _torus_pt(u0, v1)

p00 = f.cartesian_point(c00)
p10 = f.cartesian_point(c10)
p11 = f.cartesian_point(c11)
p01 = f.cartesian_point(c01)

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)


def _straight_edge(va, ca, vb, cb):
    dx = cb[0] - ca[0]
    dy = cb[1] - ca[1]
    dz = cb[2] - ca[2]
    length = _math.sqrt(dx * dx + dy * dy + dz * dz)
    d = f.direction((dx / length, dy / length, dz / length))
    return f.edge_curve(va, vb, f.line(f.cartesian_point(ca), f.vector(d, length)))


e_bot = _straight_edge(v00, c00, v10, c10)  # u-bottom (v=v0)
e_rgt = _straight_edge(v10, c10, v11, c11)  # v-right  (u=u1)
e_top = _straight_edge(v11, c11, v01, c01)  # u-top    (v=v1)
e_lft = _straight_edge(v01, c01, v00, c00)  # v-left   (u=u0)

patch_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_lft, False),
])
face = f.advanced_face([f.face_outer_bound(patch_loop)], torus_surf)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa196.stp")
