"""Tfa242 — ShapeFix_Face.FixOrientation.PeriodicBoundingBoxShift

Seam-crossing wire adjustment via ShapeAnalysis::AdjustByPeriod(). Wires
wrapping across torus seam (u≈0) at opposite ends; without periodic shift,
bounding boxes classified as disjoint despite containment.

Mechanism: CLOSED_SHELL with TWO ADVANCED_FACEs. face[0] is the defect carrier:
a TOROIDAL_SURFACE with TWO wires that straddle the u=0 seam. The outer
FACE_OUTER_BOUND sits at u near 2π (just before the seam), and the inner
FACE_BOUND sits at u near 0 (just after the seam). Without
ShapeAnalysis::AdjustByPeriod() shifting the inner bounding box by ±uRange,
the two boxes are classified as disjoint (one at u≈6 the other at u≈0),
producing incorrect containment results inside FixOrientation. face[1] is a
flat companion face on PLANE to ensure the manifold shell closes.

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
    catalog_id="Tfa242",
    defect=(
        "CLOSED_SHELL: face[0] TOROIDAL_SURFACE with two seam-crossing wires; "
        "outer FACE_OUTER_BOUND: rect straddling u=2π seam (outer box u≈5.8-6.5); "
        "inner FACE_BOUND: rect near u=0 (inner box u≈0.1-0.3); "
        "ShapeFix_Face::FixOrientation: AdjustByPeriod() must shift inner box by "
        "uRange=2π to align with outer box before containment test; "
        "without shift boxes appear disjoint → false containment classification; "
        "face[1]: flat PLANE cap; defect IS on live traversal path; no orphans"
    ),
)

R = 5.0   # major radius
r = 1.5   # minor radius

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


def _make_rect_loop(corners_uv, outer=True):
    pts = [_torus_pt(u, v) for u, v in corners_uv]
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


# uRange = 2π; v fixed near 0 to keep wires geometrically simple
_2PI = 2.0 * _math.pi
vc = 0.3   # fixed v-center for both wires

# Outer wire: large rectangle straddling the u=0/2π seam
# Corners span u = 5.5 to 6.8 (wrapping past 2π≈6.283)
# We place corners in physical space without modular reduction so line edges
# connect the correct 3D points; OCC processes the 2D parameter space.
du_out = 0.4
dv_out = 0.3
# Outer rect: u in [5.6, 6.4], v in [vc-dv_out, vc+dv_out]
# Note: u=6.4 > 2π so it wraps; we use raw u values for 3D point mapping
outer_corners_uv = [
    (5.6, vc - dv_out),
    (6.4, vc - dv_out),
    (6.4, vc + dv_out),
    (5.6, vc + dv_out),
]
# Clamp u to [0, 2π) for 3D evaluation
def _torus_pt_mod(u, v):
    return _torus_pt(u % _2PI, v)

outer_pts = [_torus_pt_mod(u, v) for u, v in outer_corners_uv]
outer_verts = [f.vertex_point(f.cartesian_point(p)) for p in outer_pts]
outer_edges = []
n = len(outer_pts)
for i in range(n):
    outer_edges.append(_line_edge(outer_verts[i], outer_pts[i],
                                   outer_verts[(i + 1) % n], outer_pts[(i + 1) % n]))
outer_loop = f.edge_loop([f.oriented_edge(e, True) for e in outer_edges])
outer_bound = f.face_outer_bound(outer_loop)

# Inner wire: smaller rectangle just after u=0 seam (u in [0.05, 0.25])
inner_corners_uv = [
    (0.05, vc - 0.12),
    (0.25, vc - 0.12),
    (0.25, vc + 0.12),
    (0.05, vc + 0.12),
]
inner_pts = [_torus_pt(u, v) for u, v in inner_corners_uv]
inner_verts = [f.vertex_point(f.cartesian_point(p)) for p in inner_pts]
inner_edges = []
for i in range(n):
    inner_edges.append(_line_edge(inner_verts[i], inner_pts[i],
                                   inner_verts[(i + 1) % n], inner_pts[(i + 1) % n]))
inner_loop = f.edge_loop([f.oriented_edge(e, True) for e in inner_edges])
inner_bound = f.face_bound(inner_loop, orientation=False)

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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa242.stp")
