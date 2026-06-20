"""Tfa043 — Single-face dispatcher: classify-and-heal small face.

Catalog claim: A standalone ADVANCED_FACE supplied without context. The
dispatcher must classify it as spot, strip, or pin (or none), and then call
the specific fixer. The classification is the entry-point for any small-face
workflow.

Reproducer recipe (from catalog): A near-zero-area face supplied as the only
face of a fixture.

Mechanism: face[0] is a 0.001 × 0.000001 ADVANCED_FACE on a PLANE at z=0.
  - area = 1e-9 < 1e-3 (spot-face criterion)
  - aspect = 0.001 / 0.000001 = 1000 > 1e3 (strip-face criterion)
The dispatcher (FixFace) must classify before applying any fixer.
A valid 10×10 reference face is face[1] to ensure shape(1).

Tier-3 assertions:
  face[0].area < 1e-3
  face[0].sliver_aspect_max_min > 1e3
  n_edges_total >= 4

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa043",
    defect=(
        "OPEN_SHELL: face[0] is 0.001×0.000001 ADVANCED_FACE on PLANE at z=0; "
        "area ≈ 1e-9 < 1e-3 (spot face criterion); "
        "aspect = 0.001/0.000001 = 1000 > 1e3 (strip face criterion); "
        "ShapeFix_FixSmallFace::FixFace must classify (spot vs strip vs pin) "
        "before dispatching; "
        "face[1] is valid 10×10 plane to ensure shape(1); "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# ── face[0]: small face satisfying both area<1e-3 and aspect>1e3 ──────────────
W = 0.001       # width
H = 0.000001    # height (1e-6) → aspect = W/H = 1000 > 1e3

pa = f.cartesian_point((0.0, 0.0, 0.0))
pb = f.cartesian_point((W,   0.0, 0.0))
pc = f.cartesian_point((W,   H,   0.0))
pd = f.cartesian_point((0.0, H,   0.0))
va = f.vertex_point(pa); vb = f.vertex_point(pb)
vc = f.vertex_point(pc); vd = f.vertex_point(pd)

ec0 = f.edge_curve(va, vb, f.line(pa, f.vector(f.direction(( 1.0, 0.0, 0.0)), W)))
ec1 = f.edge_curve(vb, vc, f.line(pb, f.vector(f.direction(( 0.0, 1.0, 0.0)), H)))
ec2 = f.edge_curve(vc, vd, f.line(pc, f.vector(f.direction((-1.0, 0.0, 0.0)), W)))
ec3 = f.edge_curve(vd, va, f.line(pd, f.vector(f.direction(( 0.0,-1.0, 0.0)), H)))

small_loop = f.edge_loop([
    f.oriented_edge(ec0, True), f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True), f.oriented_edge(ec3, True),
])

small_orig  = f.cartesian_point((0.0, 0.0, 0.0))
small_zdir  = f.direction((0.0, 0.0, 1.0))
small_xdir  = f.direction((1.0, 0.0, 0.0))
small_plc   = f.axis2_placement_3d(small_orig, small_zdir, small_xdir)
small_plane = f.plane(small_plc)
face0 = f.advanced_face([f.face_outer_bound(small_loop)], small_plane)

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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa043.stp")
