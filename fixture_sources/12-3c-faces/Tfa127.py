"""Tfa127 — CheckPin: oversized-pin.

Catalog claim: Face with pin-like morphology (very thin rectangle: 10×1.5)
where width exceeds CheckPin's maximum pin-width threshold. Algorithm reports
face is not a pin despite pin structure. Rectangular plane face with aspect
ratio triggering false negative.

Mechanism: OPEN_SHELL with a single PLANE ADVANCED_FACE that is a 10×1.5
rectangle. The face has pin-like morphology (high aspect ratio: 10/1.5 ≈ 6.67)
but its width of 1.5 units exceeds CheckPin's maximum pin-width threshold
(~1.0 unit). ShapeAnalysis_CheckSmallFace::CheckPin returns false (not a pin)
despite the pin structure — a false negative triggered by the oversized width.

The face IS on the live OPEN_SHELL traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa127",
    defect=(
        "OPEN_SHELL: single PLANE ADVANCED_FACE; 10×1.5 rectangle with pin-like "
        "morphology (aspect ratio ≈ 6.67); width 1.5 exceeds CheckPin maximum "
        "pin-width threshold (~1.0); "
        "ShapeAnalysis_CheckSmallFace::CheckPin returns false (not a pin) despite "
        "pin structure — false negative triggered by oversized width; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# Single 10×1.5 rectangular face at z=0
# L=10 (long dimension), W=1.5 (width, exceeds pin threshold of ~1.0)
L = 10.0
W = 1.5

p_bl = f.cartesian_point((0.0, 0.0, 0.0))
p_br = f.cartesian_point(( L,  0.0, 0.0))
p_tr = f.cartesian_point(( L,   W,  0.0))
p_tl = f.cartesian_point((0.0,  W,  0.0))

v_bl = f.vertex_point(p_bl); v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr); v_tl = f.vertex_point(p_tl)

e_bot = f.edge_curve(v_bl, v_br, f.line(p_bl, f.vector(f.direction(( 1.0, 0.0, 0.0)), L)))
e_rgt = f.edge_curve(v_br, v_tr, f.line(p_br, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
e_top = f.edge_curve(v_tr, v_tl, f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), L)))
e_lft = f.edge_curve(v_tl, v_bl, f.line(p_tl, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

pin_loop = f.edge_loop([
    f.oriented_edge(e_bot, True), f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True), f.oriented_edge(e_lft, True),
])
pin_plc  = f.axis2_placement_3d(p_bl, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
pin_face = f.advanced_face([f.face_outer_bound(pin_loop)], f.plane(pin_plc))

# OPEN_SHELL: single face
open_sh = f.open_shell([pin_face])
sbsm    = f.shell_based_surface_model([open_sh])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa127.stp")
