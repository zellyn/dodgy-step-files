"""Tfa128 — FixOrientation: already-correct.

Catalog claim: Face whose normal orientation is already correct according to
the face geometry and bounds. FixOrientation runs the correction algorithm and
produces identical output but marks myStatus as "fixed" even though no change
occurred. Reproducer: simple 5×5 square with correct CCW outer boundary and
correct normal.

Mechanism: OPEN_SHELL with a single PLANE ADVANCED_FACE (5×5 square) with
same_sense=True (correct) and a CCW outer boundary winding when viewed from
the +Z normal. The face orientation is already correct; FixOrientation should
detect no change needed. However, due to an api-contract defect, FixOrientation
marks myStatus as "modified/fixed" despite making no actual change.

The face IS on the live OPEN_SHELL traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa128",
    defect=(
        "OPEN_SHELL: single PLANE ADVANCED_FACE; 5×5 square at z=0 with correct "
        "CCW outer boundary winding (bl→br→tr→tl) and same_sense=.T. (normal = +Z); "
        "ShapeFix_Face::FixOrientation finds orientation already correct but "
        "incorrectly marks myStatus as 'fixed' (api-contract defect); "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# Single 5×5 square face at z=0 with correct CCW winding and +Z normal
S = 5.0

p_bl = f.cartesian_point((0.0, 0.0, 0.0))
p_br = f.cartesian_point(( S,  0.0, 0.0))
p_tr = f.cartesian_point(( S,   S,  0.0))
p_tl = f.cartesian_point((0.0,  S,  0.0))

v_bl = f.vertex_point(p_bl); v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr); v_tl = f.vertex_point(p_tl)

e_bot = f.edge_curve(v_bl, v_br, f.line(p_bl, f.vector(f.direction(( 1.0, 0.0, 0.0)), S)))
e_rgt = f.edge_curve(v_br, v_tr, f.line(p_br, f.vector(f.direction(( 0.0, 1.0, 0.0)), S)))
e_top = f.edge_curve(v_tr, v_tl, f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), S)))
e_lft = f.edge_curve(v_tl, v_bl, f.line(p_tl, f.vector(f.direction(( 0.0,-1.0, 0.0)), S)))

# CCW loop from +Z: bl→br→tr→tl→bl
sq_loop = f.edge_loop([
    f.oriented_edge(e_bot, True), f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True), f.oriented_edge(e_lft, True),
])
sq_plc   = f.axis2_placement_3d(p_bl, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
sq_face  = f.advanced_face([f.face_outer_bound(sq_loop)], f.plane(sq_plc), same_sense=True)

# OPEN_SHELL: single face — orientation is already correct
open_sh = f.open_shell([sq_face])
sbsm    = f.shell_based_surface_model([open_sh])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa128.stp")
