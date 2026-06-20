"""Tfa183 — ShapeFix_Face.FixSplitFace splitter-extends-beyond-face

Catalog claim: Rectangular face with LINE splitter whose endpoints
(-2,5,0)→(12,5,0) extend outside face bounds (0-10,0-10). FixSplitFace clips
to face boundary but mishandles clip-point determination. Tests robustness of
clipping logic when splitter extends beyond face extent.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE on a PLANE. The 10×10 outer
boundary (x: 0-10, y: 0-10) has an inner FACE_BOUND whose edge traces the
splitter line y=5 using endpoints extended beyond the face: from (-2,5,0) to
(12,5,0). This inner line-wire crosses the outer boundary from left to right at
y=5, with both endpoints lying outside the face. FixSplitFace encounters this
wire and must clip its endpoints to the face boundary at (0,5) and (10,5);
the clip-point determination is mishandled, producing incorrect split topology.
Defect IS on live face traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa183",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE (10×10, x:0-10 y:0-10); "
        "inner FACE_BOUND is a degenerate 2-edge 'splitter' wire along y=5 "
        "with endpoints extended to x=-2 and x=12 (outside face bounds); "
        "FixSplitFace must clip extended line to face boundary at (0,5)/(10,5); "
        "clip-point determination fails when splitter extends beyond face extent; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ────────────────────────────────────
plane = f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
))

# ── Outer boundary: 10×10 rectangle CCW ────────────────────────────────────
op0 = f.cartesian_point(( 0.0,  0.0, 0.0))
op1 = f.cartesian_point((10.0,  0.0, 0.0))
op2 = f.cartesian_point((10.0, 10.0, 0.0))
op3 = f.cartesian_point(( 0.0, 10.0, 0.0))

ov0 = f.vertex_point(op0); ov1 = f.vertex_point(op1)
ov2 = f.vertex_point(op2); ov3 = f.vertex_point(op3)

oe_b = f.edge_curve(ov0, ov1, f.line(op0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
oe_r = f.edge_curve(ov1, ov2, f.line(op1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
oe_t = f.edge_curve(ov2, ov3, f.line(op2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
oe_l = f.edge_curve(ov3, ov0, f.line(op3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

outer_loop = f.edge_loop([
    f.oriented_edge(oe_b, True), f.oriented_edge(oe_r, True),
    f.oriented_edge(oe_t, True), f.oriented_edge(oe_l, True),
])
outer_fob = f.face_outer_bound(outer_loop)

# ── Splitter wire: line from (-2,5,0) to (12,5,0), beyond face bounds ──────
# Two vertices at extended positions
sp_L = f.cartesian_point((-2.0, 5.0, 0.0))   # left: x=-2 (outside face)
sp_R = f.cartesian_point((12.0, 5.0, 0.0))   # right: x=12 (outside face)

sv_L = f.vertex_point(sp_L)
sv_R = f.vertex_point(sp_R)

# Single edge: L → R, length 14
se_LR = f.edge_curve(sv_L, sv_R,
    f.line(sp_L, f.vector(f.direction((1.0, 0.0, 0.0)), 14.0)))
# Return edge: R → L (to close the degenerate wire as a 2-edge loop)
se_RL = f.edge_curve(sv_R, sv_L,
    f.line(sp_R, f.vector(f.direction((-1.0, 0.0, 0.0)), 14.0)))

splitter_loop = f.edge_loop([
    f.oriented_edge(se_LR, True),
    f.oriented_edge(se_RL, True),
])
splitter_fb = f.face_bound(splitter_loop, True)

face = f.advanced_face([outer_fob, splitter_fb], plane)

shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa183.stp")
