"""Tfa040 — Small-face dispatcher orchestrates spot/strip/pin classification.

Catalog claim: An ADVANCED_FACE that simultaneously satisfies multiple "small
face" heuristics; bounding box below precision (sub-tolerance spot face, e.g.,
a 0.001 x 0.001 mm square outer EDGE_LOOP at the origin), aspect ratio extreme
in one direction (strip), and a sharp single-vertex pinch (pin). The pipeline
must classify before applying a removal/healing strategy.

Mechanism: A near-zero-area ADVANCED_FACE whose outer EDGE_LOOP vertices are
all within 1e-3 of (0,0) — a sub-tolerance spot face:
  face[0]: tiny 0.001 × 0.0001 rectangle at origin (area = 1e-7, aspect = 10)
    Both bounding box dimensions are sub-tolerance (< global uncertainty 1e-7
    expressed differently: the face is truly sub-tolerance in area terms).

To satisfy face[0].area < 1e-3 and sliver_aspect_max_min > 1e3, we use a
0.001 × 0.000001 rectangle:
  - area = 1e-9 < 1e-3
  - aspect = 0.001 / 0.000001 = 1000 > 1e3

A valid 10×10 face is added as face[1] so the shell loads as shape(1).

Tier-3 assertions:
  face[0].area < 1e-3
  face[0].sliver_aspect_max_min > 1e3
  n_edges_total >= 4

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa040",
    defect=(
        "OPEN_SHELL: face[0] is a 0.001×0.000001 sub-tolerance ADVANCED_FACE on PLANE; "
        "outer EDGE_LOOP vertices all within 1e-3 of origin; "
        "area ≈ 1e-9 < 1e-3 (spot face criterion); "
        "aspect ratio = 0.001/0.000001 = 1000 > 1e3 (strip face criterion); "
        "satisfies both spot and strip heuristics simultaneously; "
        "ShapeFix_FixSmallFace::Perform must classify (spot beats strip beats pin) "
        "before dispatching to the correct fixer; "
        "face[1] is valid 10×10 plane to ensure shape(1); "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# ── face[0]: sub-tolerance tiny face (spot + extreme aspect ratio) ─────────────
# 0.001 wide × 0.000001 tall — satisfies area < 1e-3 AND aspect > 1e3
W = 0.001      # width
H = 0.000001   # height (1e-6)

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

tiny_loop = f.edge_loop([
    f.oriented_edge(ec0, True), f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True), f.oriented_edge(ec3, True),
])

tiny_orig = f.cartesian_point((0.0, 0.0, 0.0))
tiny_zdir = f.direction((0.0, 0.0, 1.0))
tiny_xdir = f.direction((1.0, 0.0, 0.0))
tiny_plc  = f.axis2_placement_3d(tiny_orig, tiny_zdir, tiny_xdir)
tiny_plane = f.plane(tiny_plc)
face0 = f.advanced_face([f.face_outer_bound(tiny_loop)], tiny_plane)

# ── face[1]: valid 10×10 reference plane at z=0, offset at y=1 ────────────────
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

ref_loop = f.edge_loop([
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa040.stp")
