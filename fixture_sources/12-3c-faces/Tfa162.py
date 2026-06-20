"""Tfa162 — ShapeAnalysis_CheckSmallFace.CheckSpotFace negative-area-detection.

Catalog claim: Face with vertices ordered to produce negative signed area
(CCW instead of CW on plane-like surface). CheckSpotFace calculates
bounding-box area and applies absolute-value masking, hiding the orientation
error. Minimal reproducer uses PLANE surface, reversed face orientation (.F.),
quad loop with swapped point order to trigger negative area calculation.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE on a PLANE. The outer loop
traverses the rectangle CCW when viewed from above (the "wrong" winding for
the standard CW-outer convention), producing a negative signed area.
The face orientation flag is .F. (reversed) to compound the ambiguity.
CheckSpotFace masks negative area with abs(), hiding the orientation defect.
Defect IS on live face traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa162",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE with face orientation .F. (reversed); "
        "outer loop traverses CCW from above (+Z normal) — swapped point order; "
        "signed area is negative; "
        "CheckSpotFace applies abs() masking and misses the orientation error; "
        "FACE_OUTER_BOUND loop: CCW (BL→TL→TR→BR) producing negative area; "
        "defect IS on live OPEN_SHELL traversal path; "
        "no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
plane   = f.plane(f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir))

# ── Points: swapped order for CCW (negative-area) traversal ───────────────────
# Standard CW from above: BL→BR→TR→TL
# Negative-area CCW: BL→TL→TR→BR  (swap middle two)
p_bl = f.cartesian_point((0.0, 0.0, 0.0))
p_br = f.cartesian_point((5.0, 0.0, 0.0))
p_tr = f.cartesian_point((5.0, 4.0, 0.0))
p_tl = f.cartesian_point((0.0, 4.0, 0.0))

v_bl = f.vertex_point(p_bl)
v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr)
v_tl = f.vertex_point(p_tl)

# CCW order: BL → TL → TR → BR → BL  (negative signed area)
ec_left  = f.edge_curve(v_bl, v_tl, f.line(p_bl, f.vector(f.direction((0.0,  1.0, 0.0)), 4.0)))
ec_top   = f.edge_curve(v_tl, v_tr, f.line(p_tl, f.vector(f.direction((1.0,  0.0, 0.0)), 5.0)))
ec_right = f.edge_curve(v_tr, v_br, f.line(p_tr, f.vector(f.direction((0.0, -1.0, 0.0)), 4.0)))
ec_bot   = f.edge_curve(v_br, v_bl, f.line(p_br, f.vector(f.direction((-1.0, 0.0, 0.0)), 5.0)))

outer_loop = f.edge_loop([
    f.oriented_edge(ec_left,  True),
    f.oriented_edge(ec_top,   True),
    f.oriented_edge(ec_right, True),
    f.oriented_edge(ec_bot,   True),
])

# Face with orientation .F. to compound ambiguity; emit via _emit_raw for .F.
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{outer_loop.eid},.T.)")
# .F. on ADVANCED_FACE: reversed face orientation → negative-area trigger
af = f._emit_raw(
    f"ADVANCED_FACE('neg_area_face',(#{fob.eid}),#{plane.eid},.F.)"
)

shell = f._emit_raw(f"OPEN_SHELL('spot_face_shell',( #{af.eid}))")
sbsm  = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('',( #{shell.eid}))")
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa162.stp")
