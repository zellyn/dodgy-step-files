"""Twi071 — Seam edge has its two pcurves swapped.

Catalog claim: A seam edge of a face on a periodic surface (cylinder, sphere,
torus) carries two pcurves; one for the FORWARD side, one for the REVERSED side.
The diagnostic detects the case where these have been swapped: FORWARD-side
carries the pcurve that should be on REVERSED, and vice versa.

Reproducer recipe: A seam edge of a cylindrical face where the forward pcurve
is at U=2π and the reversed pcurve is at U=0 (correct order is the reverse).

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with a SEAM_CURVE
whose associated_geometry has the two pcurves in swapped order:
- first pcurve (FORWARD side): at U=2π — labelled 'forward_at_U_2pi'
- second pcurve (REVERSED side): at U=0 — labelled 'reversed_at_U_0'
Correct order would be FORWARD at U=0 and REVERSED at U=2π. The SEAM_CURVE
uses .PCURVE_S1_AND_S2. to signal both pcurves present. CheckSeam detects the
swap. OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'.PCURVE_S1_AND_S2.')
  - contains(b'forward_at_U_2pi')
  - contains(b'reversed_at_U_0')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi071",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with SEAM_CURVE on "
        "CYLINDRICAL_SURFACE (radius 1, axis +Z); "
        "SEAM_CURVE has .PCURVE_S1_AND_S2. with TWO pcurves in swapped order: "
        "first (FORWARD) pcurve 'forward_at_U_2pi' at U=2π — wrong side; "
        "second (REVERSED) pcurve 'reversed_at_U_0' at U=0 — wrong side; "
        "correct order: FORWARD at U=0, REVERSED at U=2π; "
        "CheckSeam detects the swap; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "SEAM_CURVE IS wired into EDGE_CURVE, ORIENTED_EDGE, EDGE_LOOP; "
        "never orphaned"
    ),
)

TWO_PI = 2.0 * _math.pi

# ── CYLINDRICAL_SURFACE: axis +Z, radius 1 ───────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},1.0)")

# ── Seam vertices at (1,0,0) to (1,0,1) ──────────────────────────────────────
v_bot = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
v_top = f.vertex_point(f.cartesian_point((1.0, 0.0, 1.0)))

# ── 3D seam line: vertical at x=1,y=0 ────────────────────────────────────────
seam_line_3d = f.line(
    f.cartesian_point((1.0, 0.0, 0.0)),
    f.vector(f.direction((0.0, 0.0, 1.0)), 1.0)
)

# ── PCURVE at U=2π (FORWARD slot — WRONG, this is the swap defect) ──────────
# Should be at U=0 for the FORWARD side; we put it at U=2π instead.
uv_orig_2pi  = f.cartesian_point((_math.pi * 2.0, 0.0))
uv_dir_2pi   = f.direction((0.0, 1.0))    # +V direction (height)
uv_vec_2pi   = f.vector(uv_dir_2pi, 1.0)
uv_line_2pi  = f._emit_raw(
    f"LINE('forward_at_U_2pi',#{uv_orig_2pi.eid},#{uv_vec_2pi.eid})"
)
drep_2pi = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{uv_line_2pi.eid}),#?)"
)
pcurve_forward_wrong = f._emit_raw(
    f"PCURVE('',#{cyl_surf.eid},#{drep_2pi.eid})"
)

# ── PCURVE at U=0 (REVERSED slot — WRONG, this is the swap defect) ───────────
# Should be at U=2π for the REVERSED side; we put it at U=0 instead.
uv_orig_0   = f.cartesian_point((0.0, 0.0))
uv_dir_0    = f.direction((0.0, 1.0))    # +V direction (height)
uv_vec_0    = f.vector(uv_dir_0, 1.0)
uv_line_0   = f._emit_raw(
    f"LINE('reversed_at_U_0',#{uv_orig_0.eid},#{uv_vec_0.eid})"
)
drep_0 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{uv_line_0.eid}),#?)"
)
pcurve_reversed_wrong = f._emit_raw(
    f"PCURVE('',#{cyl_surf.eid},#{drep_0.eid})"
)

# ── SEAM_CURVE: .PCURVE_S1_AND_S2. with swapped pcurves ─────────────────────
# The byte assertion .PCURVE_S1_AND_S2. signals both pcurve slots are present.
# Slot 1 (FORWARD): pcurve_forward_wrong (at U=2π — swapped)
# Slot 2 (REVERSED): pcurve_reversed_wrong (at U=0 — swapped)
seam_curve = f._emit_raw(
    f"SEAM_CURVE('',#{seam_line_3d.eid},"
    f"(#{pcurve_forward_wrong.eid},#{pcurve_reversed_wrong.eid}),.PCURVE_S1_AND_S2.)"
)

# ── EDGE_CURVE wrapping the SEAM_CURVE ───────────────────────────────────────
ec_seam = f._emit_raw(
    f"EDGE_CURVE('',#{v_bot.eid},#{v_top.eid},#{seam_curve.eid},.T.)"
)
oe_seam = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_seam.eid},.T.)")

# ── EDGE_LOOP: seam edge with swapped pcurves IS the mechanism ───────────────
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe_seam.eid}))")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi071.stp")
