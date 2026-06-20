"""Tfa054 — Face has no underlying surface.

Catalog claim: An ADVANCED_FACE is declared but its face_geometry slot is null
or references a non-existent entity. The face has bounding wires but no surface
to lie on; the kernel cannot compute face area.

Mechanism: OPEN_SHELL with TWO faces:
  face[0] (defective): ADVANCED_FACE with face_geometry = $ (NULL) but a valid
    outer EDGE_LOOP. The face is on the live traversal path. OCC's lenient
    reader heals the shell and loads shape(1).
  face[1] (valid): 100×100 plane at z=1 so OCC has a real face to load.

The NULL face_geometry IS the defect: no surface in 3D for the face to lie on.
Bug-reporter language: "face has no surface", "face_geometry missing",
"kernel can't compute face area".

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: brepcheck.valid == False

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa054",
    defect=(
        "OPEN_SHELL: face[0] is ADVANCED_FACE with face_geometry = $ (NULL); "
        "valid FACE_OUTER_BOUND and EDGE_LOOP on the traversal path but no surface; "
        "OCC heals and loads shape(1) from face[1]; "
        "defect IS live: NULL face_geometry means no surface for face[0]; "
        "brepcheck.valid must be False"
    ),
)


def make_rect_loop(x0, y0, x1, y1, z=0.0):
    """Return an EDGE_LOOP for a rectangle at given z level."""
    p_bl = f.cartesian_point((x0, y0, z))
    p_br = f.cartesian_point((x1, y0, z))
    p_tr = f.cartesian_point((x1, y1, z))
    p_tl = f.cartesian_point((x0, y1, z))

    v_bl = f.vertex_point(p_bl)
    v_br = f.vertex_point(p_br)
    v_tr = f.vertex_point(p_tr)
    v_tl = f.vertex_point(p_tl)

    dx = x1 - x0
    dy = y1 - y0

    ec_b = f.edge_curve(v_bl, v_br, f.line(p_bl, f.vector(f.direction(( 1.0, 0.0, 0.0)), dx)))
    ec_r = f.edge_curve(v_br, v_tr, f.line(p_br, f.vector(f.direction(( 0.0, 1.0, 0.0)), dy)))
    ec_t = f.edge_curve(v_tr, v_tl, f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), dx)))
    ec_l = f.edge_curve(v_tl, v_bl, f.line(p_tl, f.vector(f.direction(( 0.0,-1.0, 0.0)), dy)))

    return f.edge_loop([
        f.oriented_edge(ec_b, True),
        f.oriented_edge(ec_r, True),
        f.oriented_edge(ec_t, True),
        f.oriented_edge(ec_l, True),
    ])


# ── DEFECTIVE face: ADVANCED_FACE with face_geometry = $ ─────────────────────
defect_loop = make_rect_loop(0.0, 0.0, 10.0, 10.0, z=0.0)
defect_fob  = f.face_outer_bound(defect_loop)
# Emit directly with $ for face_geometry (NULL)
defect_face = f._emit_raw(
    f"ADVANCED_FACE('no_surface',(#{defect_fob.eid}),$,.T.)"
)

# ── VALID reference face: 100×100 plane at z=1 ───────────────────────────────
ref_loop  = make_rect_loop(0.0, 0.0, 100.0, 100.0, z=1.0)
ref_orig  = f.cartesian_point((0.0, 0.0, 1.0))
ref_zdir  = f.direction((0.0, 0.0, 1.0))
ref_xdir  = f.direction((1.0, 0.0, 0.0))
ref_plc   = f.axis2_placement_3d(ref_orig, ref_zdir, ref_xdir)
ref_plane = f.plane(ref_plc)
ref_face  = f.advanced_face([f.face_outer_bound(ref_loop)], ref_plane)

# ── Wire both faces into an OPEN_SHELL → SBSM → product chain ────────────────
shell = f.open_shell([defect_face, ref_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa054.stp")
