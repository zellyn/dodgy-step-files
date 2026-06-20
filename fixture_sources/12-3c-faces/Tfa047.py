"""Tfa047 — Single-strip ADVANCED_FACE detection with U/V direction classification.

Catalog claim: A face is a single strip (two long confused edges) but the
diagnostic must additionally report whether the strip extends in the U or V
direction of the host surface. Without that, the strip cannot be unfolded or
merged into a neighbor.

Reproducer recipe (from catalog): As Tfa042 — long thin 100 × 0.001 face.
The diagnostic should return "strip in U" because the long edges run along U.

Mechanism: face[0] is a 100 × 0.001 mm ADVANCED_FACE on a PLANE at z=0.
  - Long edges run along X (the U parameter direction of the plane)
  - Two long edges (length=100) at y=0 and y=0.001 are confused (width < tol)
  - Two short end edges (length=0.001) close the strip
  - aspect ratio = 100/0.001 = 1e5 > 1e3
  - diagnostic must classify: strip_in_U (long axis aligns with surface U)
A valid 10×10 reference face is face[1] to ensure shape(1).

Tier-3 assertions:
  face[0].sliver_aspect_max_min > 1e3
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa047",
    defect=(
        "OPEN_SHELL: face[0] is 100×0.001 strip ADVANCED_FACE on PLANE at z=0; "
        "long edges run along X (= U direction of plane surface); "
        "two confused long edges (length=100) separated by width=0.001 < tolerance; "
        "aspect ratio = 100/0.001 = 1e5 > 1e3 (strip-face criterion); "
        "ShapeAnalysis_CheckSmallFace::CheckSingleStrip must classify as strip-in-U; "
        "direction tag (0=none/1=U/2=V) needed for absorbing-face alignment; "
        "face[1] is valid 10×10 plane to ensure shape(1); "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# ── face[0]: 100×0.001 strip in U direction ────────────────────────────────────
L = 100.0     # long dimension (U axis)
W = 0.001     # short dimension (V axis, sub-tolerance)

pa = f.cartesian_point((0.0, 0.0, 0.0))
pb = f.cartesian_point((L,   0.0, 0.0))
pc = f.cartesian_point((L,   W,   0.0))
pd = f.cartesian_point((0.0, W,   0.0))
va = f.vertex_point(pa); vb = f.vertex_point(pb)
vc = f.vertex_point(pc); vd = f.vertex_point(pd)

ec0 = f.edge_curve(va, vb, f.line(pa, f.vector(f.direction(( 1.0, 0.0, 0.0)), L)))
ec1 = f.edge_curve(vb, vc, f.line(pb, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
ec2 = f.edge_curve(vc, vd, f.line(pc, f.vector(f.direction((-1.0, 0.0, 0.0)), L)))
ec3 = f.edge_curve(vd, va, f.line(pd, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

strip_loop = f.edge_loop([
    f.oriented_edge(ec0, True), f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True), f.oriented_edge(ec3, True),
])

strip_orig  = f.cartesian_point((0.0, 0.0, 0.0))
strip_zdir  = f.direction((0.0, 0.0, 1.0))
strip_xdir  = f.direction((1.0, 0.0, 0.0))
strip_plc   = f.axis2_placement_3d(strip_orig, strip_zdir, strip_xdir)
strip_plane = f.plane(strip_plc)
face0 = f.advanced_face([f.face_outer_bound(strip_loop)], strip_plane)

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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa047.stp")
