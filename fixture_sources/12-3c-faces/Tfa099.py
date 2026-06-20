"""Tfa099 — ShapeAnalysis_CheckSmallFace.CheckTwisted concave-cone.

Catalog claim: Face on cone with wire wrapped such that v-parameter decreases
(reverse height wrap). CheckTwisted's normal-direction test mis-classifies for
v-decreasing wraps on cone surfaces.

Mechanism: MANIFOLD_SOLID_BREP with two faces:
  face[0] — CONICAL_SURFACE lateral face. Outer wire traverses from vertices
    at v=4 (z=4) down to vertices at v=2 (z=2), i.e. v-parameter decreases
    around the loop. This is the defect: v-decreasing wrap on a cone.
  face[1] — flat PLANE cap at z=2 to close the shell as shape(1).

The defect is live: face[0] on the CONICAL_SURFACE IS wired into CLOSED_SHELL.
CheckTwisted's normal-direction test mis-classifies this as malformed/twisted
because it sees a v-decreasing traversal on the cone surface.

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa099",
    defect=(
        "CLOSED_SHELL: CONICAL_SURFACE face with v-decreasing wrap — outer loop "
        "vertices go from z=4 (v=4) to z=2 (v=2), so v-parameter decreases; "
        "ShapeAnalysis_CheckSmallFace::CheckTwisted normal-direction test "
        "mis-classifies v-decreasing wraps on cone surfaces as twisted; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Semi-vertical angle 30°: at height v, radius = v * tan(30°)
semi_angle = _math.pi / 6
tan_sa = _math.tan(semi_angle)

r4 = 4.0 * tan_sa   # radius at v=4 (z=4)  ≈ 2.309
r2 = 2.0 * tan_sa   # radius at v=2 (z=2)  ≈ 1.155

# Cone placed with apex at origin, axis +Z
cn_orig = f.cartesian_point((0.0, 0.0, 0.0))
cn_zdir = f.direction((0.0, 0.0, 1.0))
cn_xdir = f.direction((1.0, 0.0, 0.0))
cn_plc  = f.axis2_placement_3d(cn_orig, cn_zdir, cn_xdir)
cone    = f.conical_surface(cn_plc, 0.0, semi_angle)

# Four corner vertices: two at z=4, two at z=2
# Wire order: A(z=4,+x) → B(z=4,-x) → C(z=2,-x) → D(z=2,+x)
# v decreases from 4 to 2 between the second and third pair → v-decreasing wrap
p_A = f.cartesian_point(( r4, 0.0, 4.0))
p_B = f.cartesian_point((-r4, 0.0, 4.0))
p_C = f.cartesian_point((-r2, 0.0, 2.0))
p_D = f.cartesian_point(( r2, 0.0, 2.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

# Slant edge length
slant = _math.sqrt((r4 - r2)**2 + (4.0 - 2.0)**2)

e_AB = f.edge_curve(v_A, v_B, f.line(p_A, f.vector(
    f.direction((-1.0, 0.0, 0.0)), 2.0 * r4)))
e_BC = f.edge_curve(v_B, v_C, f.line(p_B, f.vector(
    f.direction(((r2 - r4)/slant, 0.0, -2.0/slant)), slant)))
e_CD = f.edge_curve(v_C, v_D, f.line(p_C, f.vector(
    f.direction((1.0, 0.0, 0.0)), 2.0 * r2)))
e_DA = f.edge_curve(v_D, v_A, f.line(p_D, f.vector(
    f.direction(((r4 - r2)/slant, 0.0, 2.0/slant)), slant)))

cone_loop = f.edge_loop([
    f.oriented_edge(e_AB, True),
    f.oriented_edge(e_BC, True),
    f.oriented_edge(e_CD, True),
    f.oriented_edge(e_DA, True),
])
cone_face = f.advanced_face([f.face_outer_bound(cone_loop)], cone)

# ── Cap: flat rectangle at z=2, y ∈ [0, 0.5], x ∈ [-r2, r2] ──────────────────
p_C2 = f.cartesian_point((-r2, 0.0, 2.0))
p_D2 = f.cartesian_point(( r2, 0.0, 2.0))
p_E  = f.cartesian_point(( r2, 0.5, 2.0))
p_F  = f.cartesian_point((-r2, 0.5, 2.0))

v_C2 = f.vertex_point(p_C2)
v_D2 = f.vertex_point(p_D2)
v_E  = f.vertex_point(p_E)
v_F  = f.vertex_point(p_F)

e_D2E = f.edge_curve(v_D2, v_E,  f.line(p_D2, f.vector(f.direction((0.0, 1.0, 0.0)), 0.5)))
e_EF  = f.edge_curve(v_E,  v_F,  f.line(p_E,  f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0 * r2)))
e_FC2 = f.edge_curve(v_F,  v_C2, f.line(p_F,  f.vector(f.direction((0.0, -1.0, 0.0)), 0.5)))
e_C2D2= f.edge_curve(v_C2, v_D2, f.line(p_C2, f.vector(f.direction((1.0, 0.0, 0.0)), 2.0 * r2)))

cap_loop = f.edge_loop([
    f.oriented_edge(e_C2D2, True),
    f.oriented_edge(e_D2E,  True),
    f.oriented_edge(e_EF,   True),
    f.oriented_edge(e_FC2,  True),
])
cap_plc  = f.axis2_placement_3d(p_C2, f.direction((0.0, 0.0, -1.0)),
                                  f.direction((1.0, 0.0, 0.0)))
cap_face = f.advanced_face([f.face_outer_bound(cap_loop)], f.plane(cap_plc))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([cone_face, cap_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa099.stp")
