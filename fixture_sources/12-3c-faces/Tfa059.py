"""Tfa059 — Pcurve projection failed: 3D edge curve cannot be lifted onto host surface.

Catalog claim: A face's bounding edge has a 3D curve that does not lie on the
face's surface; the 3D curve is significantly off-surface. The kernel cannot
project the curve into UV to build a pcurve because the projection diverges or
is multi-valued. Bug-reporter language: "edge not on surface", "pcurve
construction failed", "edge floats above face".

Mechanism: OPEN_SHELL with TWO faces:
  face[0] (defective): ADVANCED_FACE on a PLANE at z=0 (XY plane, z_normal=(0,0,1)).
    The outer EDGE_LOOP references an EDGE_CURVE whose LINE runs at z=0.5 —
    well above the declared plane. The 3D curve cannot be projected onto z=0
    without a large residual deviation (0.5mm >> tolerance).
    Vertices are at z=0.5 (off the plane surface).
  face[1] (reference): valid 100×100 plane at z=-10 to ensure shape(1) loads.

OCC heals the shape (accepts the off-surface edge); brepcheck.valid == False.

Tier-3 assertions:
  face[0].surface_type == "plane"
  n_edges_total >= 1
  n_vertices_total >= 2
  brepcheck.valid == False

Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa059",
    defect=(
        "OPEN_SHELL: face[0] on PLANE at z=0; "
        "outer EDGE_LOOP edge curves all at z=0.5 — 0.5mm above the declared plane; "
        "3D curve cannot be projected onto z=0 surface without residual of 0.5mm >> tol; "
        "BRepLib_MakeFace::CurveProjectionFailed condition; "
        "face[1] valid 100×100 plane at z=-10 ensures shape(1); "
        "brepcheck.valid must be False; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# ── DEFECTIVE face[0]: outer wire at z=0.5, PLANE declared at z=0 ─────────────
# Vertices are at z=0.5 (off the z=0 plane)
OFF = 0.5  # z offset for the off-surface curve

p0 = f.cartesian_point((  0.0,   0.0, OFF))
p1 = f.cartesian_point((100.0,   0.0, OFF))
p2 = f.cartesian_point((100.0, 100.0, OFF))
p3 = f.cartesian_point((  0.0, 100.0, OFF))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# Edge curves all at z=0.5 (off-surface — DEFECT)
ec0 = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 100.0)))
ec1 = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 100.0)))
ec2 = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 100.0)))
ec3 = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 100.0)))

defect_loop = f.edge_loop([
    f.oriented_edge(ec0, True),
    f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True),
    f.oriented_edge(ec3, True),
])

# PLANE at z=0 — the 3D curves at z=0.5 cannot be projected onto this plane
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
plane0   = f.plane(f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir))

face0 = f.advanced_face([f.face_outer_bound(defect_loop)], plane0)

# ── VALID reference face[1]: 100×100 plane at z=-10 ──────────────────────────
r0 = f.cartesian_point((  0.0,   0.0, -10.0))
r1 = f.cartesian_point((100.0,   0.0, -10.0))
r2 = f.cartesian_point((100.0, 100.0, -10.0))
r3 = f.cartesian_point((  0.0, 100.0, -10.0))

rv0 = f.vertex_point(r0)
rv1 = f.vertex_point(r1)
rv2 = f.vertex_point(r2)
rv3 = f.vertex_point(r3)

re0 = f.edge_curve(rv0, rv1, f.line(r0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 100.0)))
re1 = f.edge_curve(rv1, rv2, f.line(r1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 100.0)))
re2 = f.edge_curve(rv2, rv3, f.line(r2, f.vector(f.direction((-1.0, 0.0, 0.0)), 100.0)))
re3 = f.edge_curve(rv3, rv0, f.line(r3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 100.0)))

ref_loop  = f.edge_loop([
    f.oriented_edge(re0, True),
    f.oriented_edge(re1, True),
    f.oriented_edge(re2, True),
    f.oriented_edge(re3, True),
])
pl1_orig  = f.cartesian_point((0.0, 0.0, -10.0))
pl1_zdir  = f.direction((0.0, 0.0, 1.0))
pl1_xdir  = f.direction((1.0, 0.0, 0.0))
plane1    = f.plane(f.axis2_placement_3d(pl1_orig, pl1_zdir, pl1_xdir))
face1     = f.advanced_face([f.face_outer_bound(ref_loop)], plane1)

# ── OPEN_SHELL ────────────────────────────────────────────────────────────────
shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa059.stp")
