"""Tfa011 — ADVANCED_FACE with multiple FACE_OUTER_BOUND entries (face needs split).

Catalog claim: An ADVANCED_FACE is emitted with two or more FACE_OUTER_BOUND
entries when STEP requires exactly one. Common signature: ADVANCED_FACE.bounds
contains two distinct FACE_OUTER_BOUND instances for two disjoint regions
(e.g. two 10×10 squares each with its own EDGE_LOOP).

Mechanism: OPEN_SHELL with ONE defective ADVANCED_FACE:
  face[0] — the defective face on a PLANE: bounds list contains TWO
    FACE_OUTER_BOUND records — one for a 10×10 square at (0,0) and one for a
    10×10 square at (20,0). Both are FACE_OUTER_BOUND instances. STEP requires
    exactly one outer bound; this face has two.
  No companion face needed: OCC heals the face and returns shape(1).

Tier-3 assertions:
  load == "ok"
  n_edges_total >= 8
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa011",
    defect=(
        "ADVANCED_FACE on PLANE: bounds list contains TWO FACE_OUTER_BOUND records; "
        "first outer bound = 10×10 square at (0,0,0)-(10,10,0); "
        "second outer bound = 10×10 square at (20,0,0)-(30,10,0); "
        "both are FACE_OUTER_BOUND (not one outer + one inner); "
        "STEP requires exactly one FACE_OUTER_BOUND per ADVANCED_FACE; "
        "ShapeFix_Face::FixSplitFace must split into two regular faces; "
        "defective face IS on live OPEN_SHELL traversal path"
    ),
)

def make_rect_loop(x0, y0, x1, y1):
    """Build a 4-edge rectangular EDGE_LOOP on the XY plane."""
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

    ec_b = f.edge_curve(v_bl, v_br,
        f.line(p_bl, f.vector(f.direction((1.0, 0.0, 0.0)), dx)))
    ec_r = f.edge_curve(v_br, v_tr,
        f.line(p_br, f.vector(f.direction((0.0, 1.0, 0.0)), dy)))
    ec_t = f.edge_curve(v_tr, v_tl,
        f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), dx)))
    ec_l = f.edge_curve(v_tl, v_bl,
        f.line(p_tl, f.vector(f.direction((0.0, -1.0, 0.0)), dy)))

    loop = f.edge_loop([
        f.oriented_edge(ec_b, True),
        f.oriented_edge(ec_r, True),
        f.oriented_edge(ec_t, True),
        f.oriented_edge(ec_l, True),
    ])
    return loop

# ── DEFECTIVE FACE: two FACE_OUTER_BOUND entries on one ADVANCED_FACE ─────────
# First outer bound: 10×10 square at (0,0)
loop_a = make_rect_loop(0.0, 0.0, 10.0, 10.0)
fob_a  = f.face_outer_bound(loop_a)

# Second outer bound: 10×10 square at (20,0) — disjoint region
loop_b = make_rect_loop(20.0, 0.0, 30.0, 10.0)
fob_b  = f.face_outer_bound(loop_b)

# Shared plane covering both regions
pl_orig  = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir  = f.direction((0.0, 0.0, 1.0))
pl_xdir  = f.direction((1.0, 0.0, 0.0))
pl_plc   = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
shared_plane = f.plane(pl_plc)

# ADVANCED_FACE with TWO FACE_OUTER_BOUND entries — the defect
defect_face = f.advanced_face([fob_a, fob_b], shared_plane)

# ── Wire into OPEN_SHELL → SBSM → product chain ───────────────────────────────
shell = f.open_shell([defect_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa011.stp")
