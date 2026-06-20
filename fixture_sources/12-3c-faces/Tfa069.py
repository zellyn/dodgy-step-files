"""Tfa069 — Lettering bottoms not closed in exported STEP (text-on-surface non-solid result).

Catalog claim: A body with embossed lettering emits a STEP where the bottom
faces of each letter pocket — the inner-floor planar faces — are missing from
the shell. The receiver loads but reports "shell has free edges" (open shell).
The on-disk symptom: a face's FACE_OUTER_BOUND EDGE_LOOP is missing one of the
boundary edges, leaving a partial floor (open bound).

Mechanism: OPEN_SHELL with a single ADVANCED_FACE on a PLANE. The outer
EDGE_LOOP has only 3 edges instead of the required 4 for a rectangular face.
The fourth edge (the "bottom" closing edge) is missing — this represents the
missing floor boundary in the lettering pocket. OCC loads the face (heals
the open bound by clamping or closing), yielding shape(1) with 1 face.

Byte assertions:
  count_entity_def(b'EDGE_LOOP') >= 1
  contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa069",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE with FACE_OUTER_BOUND; "
        "EDGE_LOOP has only 3 edges (3 sides of a rectangle) — "
        "the fourth closing edge (bottom of pocket floor) is missing; "
        "open-bound floor: wire goes BL→BR→TR→TL but not TL→BL; "
        "represents FreeCAD text-on-surface STEP export defect: "
        "EDGE_LOOP one edge short on STEP export; "
        "OCC heals open bound — loads as shape(1) with n_faces_total==1; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# ── Single rectangular pocket-floor face with 3-edge (open) EDGE_LOOP ─────────
# A 10mm × 5mm rectangular pocket floor. The wire is missing the left closing
# edge (TL → BL), making it an open boundary.
W = 10.0   # width
H = 5.0    # height

p_bl = f.cartesian_point((0.0, 0.0, 0.0))   # bottom-left
p_br = f.cartesian_point(( W,  0.0, 0.0))   # bottom-right
p_tr = f.cartesian_point(( W,   H,  0.0))   # top-right
p_tl = f.cartesian_point((0.0,  H,  0.0))   # top-left

v_bl = f.vertex_point(p_bl)
v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr)
v_tl = f.vertex_point(p_tl)

# Three edges forming a U-shape (missing the left closing edge TL→BL)
ec_bottom = f.edge_curve(v_bl, v_br, f.line(p_bl, f.vector(f.direction(( 1.0, 0.0, 0.0)), W)))
ec_right  = f.edge_curve(v_br, v_tr, f.line(p_br, f.vector(f.direction(( 0.0, 1.0, 0.0)), H)))
ec_top    = f.edge_curve(v_tr, v_tl, f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), W)))
# MISSING: ec_left would be v_tl → v_bl — THIS IS THE DEFECT

# EDGE_LOOP with only 3 edges — the defective open bound
defect_loop = f.edge_loop([
    f.oriented_edge(ec_bottom, True),
    f.oriented_edge(ec_right,  True),
    f.oriented_edge(ec_top,    True),
    # ec_left is missing — open bound! (floor edge absent)
])

# PLANE surface at z=0 (the pocket floor)
plane = f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0))
))

face0 = f.advanced_face([f.face_outer_bound(defect_loop)], plane)

# ── OPEN_SHELL with one face ───────────────────────────────────────────────────
shell = f.open_shell([face0])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa069.stp")
