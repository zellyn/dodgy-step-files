"""Tfa241 — ShapeFix_Face.FixOrientation.WireBoundingBoxComputation

Periodic bounding-box centering on first-wire midpoint for toroidal containment
checks. Two concentric wires on torus; without anchor uMiddle/vMiddle, secondary
wire box shifts unanchored relative to first → false containment classification.

Mechanism: CLOSED_SHELL with TWO ADVANCED_FACEs. face[0] is the defect carrier:
a TOROIDAL_SURFACE patch with TWO wires — an outer FACE_OUTER_BOUND (large ring
at parametric midpoint u≈π, v≈π) and an inner FACE_BOUND (smaller concentric
ring) where the inner-wire bounding box is computed without anchoring to the
first-wire midpoint uMiddle/vMiddle, causing a periodic shift that makes the
inner box appear disjoint from the outer, producing false containment
classification inside FixOrientation. face[1] is a flat companion face on PLANE
to ensure the manifold shell closes.

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
    catalog_id="Tfa241",
    defect=(
        "CLOSED_SHELL: face[0] TOROIDAL_SURFACE with two wires (outer + inner); "
        "outer FACE_OUTER_BOUND: large parametric ring near (u≈π, v≈π); "
        "inner FACE_BOUND: concentric smaller ring; "
        "ShapeFix_Face::FixOrientation bounding-box computation: "
        "inner wire box not anchored to first-wire uMiddle/vMiddle; "
        "periodic shift makes inner box appear disjoint → false containment; "
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
    """Build a 4-edge loop from 4 (u,v) parameter pairs."""
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


# Outer wire: parametric rectangle near u≈π, v≈π (far from seam at u=0, v=0)
# Wide enough that the inner-wire box, without anchoring, may shift by 2π
du_out = 0.6
dv_out = 0.5
uc, vc = _math.pi, _math.pi
outer_corners = [
    (uc - du_out, vc - dv_out),
    (uc + du_out, vc - dv_out),
    (uc + du_out, vc + dv_out),
    (uc - du_out, vc + dv_out),
]
outer_bound = _make_rect_loop(outer_corners, outer=True)

# Inner wire: smaller concentric rectangle — same centre, half the span
du_in = 0.2
dv_in = 0.18
inner_corners = [
    (uc - du_in, vc - dv_in),
    (uc + du_in, vc - dv_in),
    (uc + du_in, vc + dv_in),
    (uc - du_in, vc + dv_in),
]
inner_bound = _make_rect_loop(inner_corners, outer=False)

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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa241.stp")
