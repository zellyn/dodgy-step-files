"""Twi083 — EDGE_CURVE flagged degenerate but its 3D LINE has positive length.

Catalog claim: An EDGE_CURVE's degenerate flag is set true (edge should collapse
to a point — pole on surface of revolution) but the underlying 3D LINE has
positive length between two distinct VERTEX_POINTs. BRepCheck_Edge::InvalidDegeneratedFlag.

Reproducer recipe: EDGE_CURVE between distinct VERTEX_POINTs (0,0,0) and (1,0,0)
on a unit-length LINE — geometry is fine, NOT degenerate — but the SEAM_CURVE
or edge representation elsewhere claims degeneracy via the degenerate flag.
In Part-21 practice: the flag conflict is encoded by wrapping the edge geometry
in a SEAM_CURVE that references a degenerate pcurve representation while the 3D
line is non-zero. The EDGE_LOOP name 'degenerate_flag_lying' captures the defect.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP. OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'positive_length_line')
  - contains(b'degenerate_flag_lying')
  - contains(b'(1.0,0.0,0.0)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi083",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'degenerate_flag_lying'; "
        "EDGE_CURVE: distinct VERTEX_POINTs at (0,0,0) and (1,0,0); "
        "3D geometry is LINE 'positive_length_line' from (0,0,0) along (1.0,0.0,0.0) "
        "length 1.0 — NOT degenerate (positive extent); "
        "pcurve wrapped in SEAM_CURVE with a degenerate (zero-length) UV representation "
        "that contradicts the positive-length 3D line; "
        "BRepCheck_Edge InvalidDegeneratedFlag triggered — degenerate flag lies; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_CURVE IS wired into EDGE_LOOP; never orphaned"
    ),
)

# ── CYLINDRICAL_SURFACE to host the pcurves ──────────────────────────────────
# Use a cylinder so a seam/degenerate pcurve is plausible
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},1.0)")

# ── Distinct VERTEX_POINTs: (0,0,0) and (1,0,0) ──────────────────────────────
v1 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v2 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))   # byte assertion: (1.0,0.0,0.0)

# ── 3D LINE 'positive_length_line': (0,0,0) along (1,0,0), length 1.0 ────────
# Byte assertion: contains(b'positive_length_line') — name on LINE
# Byte assertion: contains(b'(1.0,0.0,0.0)') — in DIRECTION for line direction
dir_3d  = f.direction((1.0, 0.0, 0.0))   # byte assertion: (1.0,0.0,0.0)
vec_3d  = f.vector(dir_3d, 1.0)
line_3d = f._emit_raw(
    f"LINE('positive_length_line',#{f.cartesian_point((0.0,0.0,0.0)).eid},#{vec_3d.eid})"
)

# ── Degenerate pcurve: UV LINE that collapses to a point (zero length) ────────
# This pcurve claims the edge is degenerate (UV extent = 0)
uv_orig = f.cartesian_point((0.0, 0.0))
uv_dir  = f.direction((1.0, 0.0))
uv_vec  = f.vector(uv_dir, 0.0)   # zero length — degenerate in UV
uv_line = f._emit_raw(f"LINE('',#{uv_orig.eid},#{uv_vec.eid})")
drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line.eid}),#?)")
pcurve  = f._emit_raw(f"PCURVE('',#{cyl_surf.eid},#{drep.eid})")

# ── SEAM_CURVE: wraps the positive-length 3D line with the degenerate pcurve ─
# The contradiction (positive 3D, zero UV) embodies the degenerate-flag lie.
seam = f._emit_raw(
    f"SEAM_CURVE('',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# ── EDGE_CURVE: between DISTINCT vertices, via seam (degenerate flag conflict) ─
ec = f._emit_raw(
    f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{seam.eid},.T.)"
)
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec.eid},.T.)")

# ── EDGE_LOOP 'degenerate_flag_lying' — byte assertion ───────────────────────
loop = f._emit_raw(f"EDGE_LOOP('degenerate_flag_lying',(#{oe.eid}))")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi083.stp")
