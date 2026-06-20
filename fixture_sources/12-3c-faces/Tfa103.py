"""Tfa103 — ShapeFix_Face.FixPeriodicDegenerated apex-at-V-min.

Catalog claim: Surface-of-revolution with apex at v_min (instead of v_max);
the degenerate-edge insertion logic only handles v_max apex.

Mechanism: MANIFOLD_SOLID_BREP with a CONICAL_SURFACE face whose apex is at
v=0 (v_min). The face has a 5-vertex wire encircling the cone at v=5.0
(away from the apex). FixPeriodicDegenerated must insert a degenerate edge at
the v_min apex, but its logic only handles v_max; the v_min case is missed,
leaving the face without its required degenerate-edge closure.

A flat disk-cap companion face closes the open top at z=5 to ensure shape(1).

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(12) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa103",
    defect=(
        "CLOSED_SHELL: CONICAL_SURFACE with apex at v_min (v=0, z=0 origin); "
        "5-vertex outer wire encircles the cone at v=5.0 (z=5 height); "
        "ShapeFix_Face::FixPeriodicDegenerated inserts degenerate edge only at v_max; "
        "apex at v_min is not handled — degenerate edge at apex missing; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# CONICAL_SURFACE: apex at v=0 (z=0), semi-angle 30°
# radius at height v = v * tan(30°)
semi_angle = _math.pi / 6
tan_sa = _math.tan(semi_angle)
r5 = 5.0 * tan_sa   # radius at v=5 ≈ 2.887

cn_orig = f.cartesian_point((0.0, 0.0, 0.0))
cn_zdir = f.direction((0.0, 0.0, 1.0))
cn_xdir = f.direction((1.0, 0.0, 0.0))
cn_plc  = f.axis2_placement_3d(cn_orig, cn_zdir, cn_xdir)
cone    = f.conical_surface(cn_plc, 0.0, semi_angle)

# 5-vertex wire at v=5 (z=5), pentagonal approximation
n = 5
pts = []
verts = []
for i in range(n):
    angle = 2.0 * _math.pi * i / n
    x = r5 * _math.cos(angle)
    y = r5 * _math.sin(angle)
    p = f.cartesian_point((x, y, 5.0))
    pts.append(p)
    verts.append(f.vertex_point(p))

# Build n line edges around the pentagon
edges = []
for i in range(n):
    i2 = (i + 1) % n
    px, py, pz = pts[i].args[1]
    qx, qy, qz = pts[i2].args[1]
    dx, dy, dz = qx - px, qy - py, qz - pz
    length = _math.sqrt(dx*dx + dy*dy + dz*dz)
    edges.append(f.edge_curve(
        verts[i], verts[i2],
        f.line(pts[i], f.vector(f.direction((dx/length, dy/length, dz/length)), length))
    ))

cone_loop = f.edge_loop([f.oriented_edge(e, True) for e in edges])
cone_face = f.advanced_face([f.face_outer_bound(cone_loop)], cone)

# ── Cap: flat pentagon-approximated disk at z=5 ──────────────────────────────
cap_pts = []
cap_verts = []
for i in range(n):
    angle = 2.0 * _math.pi * i / n
    x = r5 * _math.cos(angle)
    y = r5 * _math.sin(angle)
    p = f.cartesian_point((x, y, 5.0))
    cap_pts.append(p)
    cap_verts.append(f.vertex_point(p))

cap_edges = []
for i in range(n):
    i2 = (i + 1) % n
    px, py, pz = cap_pts[i].args[1]
    qx, qy, qz = cap_pts[i2].args[1]
    dx, dy, dz = qx - px, qy - py, qz - pz
    length = _math.sqrt(dx*dx + dy*dy + dz*dz)
    cap_edges.append(f.edge_curve(
        cap_verts[i], cap_verts[i2],
        f.line(cap_pts[i], f.vector(f.direction((dx/length, dy/length, dz/length)), length))
    ))

# Cap winding: reversed to point outward (+Z) from the solid
cap_loop = f.edge_loop([f.oriented_edge(e, False) for e in reversed(cap_edges)])
cap_plc  = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 5.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0))
)
cap_face = f.advanced_face([f.face_outer_bound(cap_loop)], f.plane(cap_plc))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([cone_face, cap_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa103.stp")
