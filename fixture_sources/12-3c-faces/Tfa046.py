"""Tfa046 — Spot-face diagnostic emits Pnt-located warning before healing.

Catalog claim: As Tfa041 but emphasizing the diagnostic-only phase: the
analyzer must detect the spot classification and emit a structured warning
containing the spot's 3D location (Pnt) before any healer is invoked.

Reproducer recipe (from catalog): As Tfa041 — a sub-precision spot
ADVANCED_FACE (0.001 × 0.001 mm square at origin).

Mechanism: face[0] is a 0.001×0.001 ADVANCED_FACE on a PLANE at z=0.
  - All 4 vertices within 1e-3 of origin
  - area = (0.001)^2 = 1e-6 < 1e-3 (spot-face criterion)
  - Surface type: plane
A valid 10×10 reference face is face[1] to ensure shape(1).

Tier-3 assertions:
  face[0].area < 1e-3
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa046",
    defect=(
        "OPEN_SHELL: face[0] is 0.001×0.001 spot ADVANCED_FACE on PLANE at z=0; "
        "vertices at (0,0,0),(0.001,0,0),(0.001,0.001,0),(0,0.001,0); "
        "area = 1e-6 < 1e-3 (spot-face criterion); "
        "ShapeAnalysis_CheckSmallFace::CheckSpotFace must emit diagnostic with 3D Pnt; "
        "diagnostic must fire before any healing is invoked; "
        "face[1] is valid 10×10 plane to ensure shape(1); "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# ── face[0]: spot face 0.001×0.001 at origin ─────────────────────────────────
S = 0.001   # side length (sub-tolerance spot face)

pa = f.cartesian_point((0.0, 0.0, 0.0))
pb = f.cartesian_point((S,   0.0, 0.0))
pc = f.cartesian_point((S,   S,   0.0))
pd = f.cartesian_point((0.0, S,   0.0))
va = f.vertex_point(pa); vb = f.vertex_point(pb)
vc = f.vertex_point(pc); vd = f.vertex_point(pd)

ec0 = f.edge_curve(va, vb, f.line(pa, f.vector(f.direction(( 1.0, 0.0, 0.0)), S)))
ec1 = f.edge_curve(vb, vc, f.line(pb, f.vector(f.direction(( 0.0, 1.0, 0.0)), S)))
ec2 = f.edge_curve(vc, vd, f.line(pc, f.vector(f.direction((-1.0, 0.0, 0.0)), S)))
ec3 = f.edge_curve(vd, va, f.line(pd, f.vector(f.direction(( 0.0,-1.0, 0.0)), S)))

spot_loop = f.edge_loop([
    f.oriented_edge(ec0, True), f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True), f.oriented_edge(ec3, True),
])

spot_orig  = f.cartesian_point((0.0, 0.0, 0.0))
spot_zdir  = f.direction((0.0, 0.0, 1.0))
spot_xdir  = f.direction((1.0, 0.0, 0.0))
spot_plc   = f.axis2_placement_3d(spot_orig, spot_zdir, spot_xdir)
spot_plane = f.plane(spot_plc)
face0 = f.advanced_face([f.face_outer_bound(spot_loop)], spot_plane)

# ── face[1]: valid 10×10 reference plane at y=1 ───────────────────────────────
p0 = f.cartesian_point((  0.0, 1.0, 0.0))
p1 = f.cartesian_point(( 10.0, 1.0, 0.0))
p2 = f.cartesian_point(( 10.0,11.0, 0.0))
p3 = f.cartesian_point((  0.0,11.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
e2 = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
e3 = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

ref_loop  = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
ref_orig  = f.cartesian_point((0.0, 0.0, 0.0))
ref_zdir  = f.direction((0.0, 0.0, 1.0))
ref_xdir  = f.direction((1.0, 0.0, 0.0))
ref_plc   = f.axis2_placement_3d(ref_orig, ref_zdir, ref_xdir)
ref_plane = f.plane(ref_plc)
face1 = f.advanced_face([f.face_outer_bound(ref_loop)], ref_plane)

# ── OPEN_SHELL ────────────────────────────────────────────────────────────────
shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa046.stp")
