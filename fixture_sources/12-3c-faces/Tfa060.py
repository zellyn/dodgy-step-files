"""Tfa060 — Shell parametric coverage exceeds host surface bounds.

Catalog claim: A face within a shell has a bounding wire whose pcurve excursion
in UV exceeds the u_min/u_max of the underlying surface. The face "wraps around"
or "overshoots" the surface. Bug-reporter language: "face parameters out of range",
"wire goes off surface".

Mechanism: OPEN_SHELL with TWO faces:
  face[0] (defective): ADVANCED_FACE on a RECTANGULAR_TRIMMED_SURFACE of a PLANE
    with u1=0, u2=1, v1=0, v2=1 (unit square). The 3D wire overshoot defect is
    introduced by placing the wire vertices at x=[0..1.5] in 3D — corresponding
    to a pcurve that would run from u=0 to u=1.5, exceeding the surface bound of
    u_max=1. OCC heals by clamping; brepcheck.valid == False.
  face[1] (reference): valid 100x100 plane at z=-10 to ensure shape(1).

OCC heals (silently accepts); brepcheck.valid == False.

Tier-3 assertions:
  brepcheck.valid == False

Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa060",
    defect=(
        "OPEN_SHELL: face[0] on RECTANGULAR_TRIMMED_SURFACE(PLANE) with u1=0, u2=1; "
        "3D wire runs from x=0 to x=1.5 — pcurve excursion u=0..1.5 > u_max=1; "
        "face 'wraps around' / 'overshoots' surface parameter domain; "
        "ShapeAnalysis_Surface::IsUClosed detects parametric overshoot; "
        "brepcheck.valid must be False; "
        "face[1] valid 100x100 plane at z=-10 ensures shape(1); "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# ── Defective face[0]: wire overshoots RECTANGULAR_TRIMMED_SURFACE domain ─────
# Underlying plane at z=0, x-axis along X, y-axis along Y
# Trimmed surface: u=[0,1], v=[0,1] — so u_max=1.0
# 3D wire runs to x=1.5, which maps to u=1.5 on the plane (exceeds u_max=1.0)
OVER = 1.5  # x goes to 1.5 but surface only covers u=[0,1]

# Underlying plane surface
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
plane_basis = f.plane(f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir))

# RECTANGULAR_TRIMMED_SURFACE: u=[0,1], v=[0,1]
rts = f.rectangular_trimmed_surface(plane_basis, 0.0, 1.0, 0.0, 1.0)

# 3D wire vertices — x goes to 1.5 (exceeds u_max=1)
p0 = f.cartesian_point((0.0,  0.0, 0.0))
p1 = f.cartesian_point((OVER, 0.0, 0.0))   # x=1.5 > u_max=1.0 — DEFECT
p2 = f.cartesian_point((OVER, 1.0, 0.0))
p3 = f.cartesian_point((0.0,  1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

ec0 = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), OVER)))
ec1 = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
ec2 = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), OVER)))
ec3 = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

defect_loop = f.edge_loop([
    f.oriented_edge(ec0, True),
    f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True),
    f.oriented_edge(ec3, True),
])

face0 = f.advanced_face([f.face_outer_bound(defect_loop)], rts)

# ── Valid reference face[1]: 100×100 plane at z=-10 ───────────────────────────
r0 = f.cartesian_point((  0.0,   0.0, -10.0))
r1 = f.cartesian_point((100.0,   0.0, -10.0))
r2 = f.cartesian_point((100.0, 100.0, -10.0))
r3 = f.cartesian_point((  0.0, 100.0, -10.0))

rv0 = f.vertex_point(r0); rv1 = f.vertex_point(r1)
rv2 = f.vertex_point(r2); rv3 = f.vertex_point(r3)

re0 = f.edge_curve(rv0, rv1, f.line(r0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 100.0)))
re1 = f.edge_curve(rv1, rv2, f.line(r1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 100.0)))
re2 = f.edge_curve(rv2, rv3, f.line(r2, f.vector(f.direction((-1.0, 0.0, 0.0)), 100.0)))
re3 = f.edge_curve(rv3, rv0, f.line(r3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 100.0)))

ref_loop = f.edge_loop([
    f.oriented_edge(re0, True), f.oriented_edge(re1, True),
    f.oriented_edge(re2, True), f.oriented_edge(re3, True),
])
pl1_orig = f.cartesian_point((0.0, 0.0, -10.0))
plane1   = f.plane(f.axis2_placement_3d(pl1_orig, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))))
face1    = f.advanced_face([f.face_outer_bound(ref_loop)], plane1)

# ── OPEN_SHELL ────────────────────────────────────────────────────────────────
shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa060.stp")
