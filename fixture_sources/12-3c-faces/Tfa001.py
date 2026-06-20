"""Tfa001 — FACE_SURFACE.face_geometry is null.

Catalog claim: An ADVANCED_FACE / FACE_SURFACE entity carries $ (NULL) or an
unresolved reference for face_geometry. The parent shell loses one face
entirely; downstream solids fail to close.

Mechanism: SHELL_BASED_SURFACE_MODEL with TWO ADVANCED_FACEs. The defective
face has face_geometry = $ (NULL). The good face is a valid 1×1 square on a
PLANE so OCC loads the shell as shape(1). The NULL face_geometry IS wired into
the FACE_OUTER_BOUND / EDGE_LOOP / ADVANCED_FACE topology path that OCC
traverses, so the defect is live on the face traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: brepcheck.valid == False

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa001",
    defect=(
        "ADVANCED_FACE with face_geometry = $ (NULL); "
        "defective face IS on the live CLOSED_SHELL traversal path; "
        "good companion face (1×1 square on PLANE) ensures OCC loads shape(1); "
        "NULL face_geometry slot IS the defect: kernel loses one face, "
        "resulting shell is open; brepcheck.valid must be False"
    ),
)

# ── Helper: build a 4-edge rectangular EDGE_LOOP on the XY plane ─────────────
def make_rect_loop(x0, y0, x1, y1):
    """Return (edge_loop entity, [oriented_edge entities]) for a rectangle."""
    p_bl = f.cartesian_point((x0, y0, 0.0))
    p_br = f.cartesian_point((x1, y0, 0.0))
    p_tr = f.cartesian_point((x1, y1, 0.0))
    p_tl = f.cartesian_point((x0, y1, 0.0))

    v_bl = f.vertex_point(p_bl)
    v_br = f.vertex_point(p_br)
    v_tr = f.vertex_point(p_tr)
    v_tl = f.vertex_point(p_tl)

    dx = x1 - x0
    dy = y1 - y0

    ln_b = f.line(p_bl, f.vector(f.direction((1.0, 0.0, 0.0)), dx))
    ln_r = f.line(p_br, f.vector(f.direction((0.0, 1.0, 0.0)), dy))
    ln_t = f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), dx))
    ln_l = f.line(p_tl, f.vector(f.direction((0.0, -1.0, 0.0)), dy))

    ec_b = f.edge_curve(v_bl, v_br, ln_b)
    ec_r = f.edge_curve(v_br, v_tr, ln_r)
    ec_t = f.edge_curve(v_tr, v_tl, ln_t)
    ec_l = f.edge_curve(v_tl, v_bl, ln_l)

    loop = f.edge_loop([
        f.oriented_edge(ec_b, True),
        f.oriented_edge(ec_r, True),
        f.oriented_edge(ec_t, True),
        f.oriented_edge(ec_l, True),
    ])
    return loop

# ── DEFECTIVE face: ADVANCED_FACE with face_geometry = $ ─────────────────────
# The face has a valid outer wire on a 1×1 square but the surface slot is NULL.
defect_loop = make_rect_loop(0.0, 0.0, 1.0, 1.0)
defect_fob  = f.face_outer_bound(defect_loop)
# Emit the defective ADVANCED_FACE with $ as face_geometry (NULL)
defect_face = f._emit_raw(
    f"ADVANCED_FACE('null_geom',(#{defect_fob.eid}),$,.T.)"
)

# ── GOOD face: valid 1×1 square on PLANE to give OCC something to load ───────
good_orig = f.cartesian_point((2.0, 0.0, 0.0))
good_zdir = f.direction((0.0, 0.0, 1.0))
good_xdir = f.direction((1.0, 0.0, 0.0))
good_plc  = f.axis2_placement_3d(good_orig, good_zdir, good_xdir)
good_plane = f.plane(good_plc)

good_loop = make_rect_loop(2.0, 0.0, 3.0, 1.0)
good_fob  = f.face_outer_bound(good_loop)
good_face = f.advanced_face([good_fob], good_plane)

# ── Wire both faces into an OPEN_SHELL → SBSM → product chain ────────────────
shell = f.open_shell([defect_face, good_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa001.stp")
