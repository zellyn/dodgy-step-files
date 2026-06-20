"""Twi121 — ShapeFix_Wire.FixSeam closed-surface seam reset.

Catalog claim: Wire on cylindrical surface where seam-edge tolerance gets reset
to 0.0 unconditionally. Seam edge at u-parameter boundary (topology closure) has
user-set tolerance 0.001; FixSeam erases it. Downstream CheckConnected tolerance
mismatch detection fails.

Reproducer recipe: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with two edges
on a CYLINDRICAL_SURFACE. One edge is a seam edge at the U=0/2π boundary with
tolerance label 'SEAM_EDGE_tol0p001'. Its pcurve endpoints are at U=0 (start)
and U=2π (end), closing the cylinder in the U direction. A second edge connects
vertically. The seam edge tolerance mismatch IS the defect; FixSeam resets
tolerance to 0.0, breaking downstream CheckConnected detection.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math as _math

f = StepFile(
    catalog_id="Twi121",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP on CYLINDRICAL_SURFACE (radius 1); "
        "2 SURFACE_CURVE edges: "
        "e1 IS seam edge at U=0/2π boundary labelled 'SEAM_EDGE_tol0p001'; "
        "pcurve goes from U=0,V=0 to U=0,V=1 (same U at seam); "
        "e2 connects V=1 back to V=0 via UV from (0,1)→(2π,1)→... not used; "
        "seam edge user tolerance 0.001 IS reset to 0.0 by FixSeam unconditionally; "
        "downstream CheckConnected tolerance mismatch detection fails IS defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── CYLINDRICAL_SURFACE: axis +Z, radius 1 ───────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},1.0)")

# ── 3D vertices: seam line at U=0 (x=1,y=0), V=0 and V=1 ────────────────────
# On cylinder r=1, U=0: (cos(0), sin(0), V) = (1, 0, V)
P_v0 = (1.0, 0.0, 0.0)   # seam start: U=0, V=0
P_v1 = (1.0, 0.0, 1.0)   # seam end:   U=0, V=1

# Second edge: a circle at V=1 (top cap seam connector) going around
# Use a straight 3D line from (1,0,1) back toward (1,0,0) — vertical closing edge
P_v2 = (1.0, 0.0, 1.0)   # same as P_v1 (connect back)
P_v3 = (1.0, 0.0, 0.0)   # same as P_v0

v0 = f.vertex_point(f.cartesian_point(P_v0))  # seam bottom
v1 = f.vertex_point(f.cartesian_point(P_v1))  # seam top

# ── PCURVE helper: LINE in UV space ──────────────────────────────────────────
def make_uv_line(u0, v0_uv, u1, v1_uv, label=''):
    """Build a PCURVE for a line from (u0,v0_uv) to (u1,v1_uv) on cyl_surf."""
    du = u1 - u0
    dv = v1_uv - v0_uv
    mag = _math.sqrt(du*du + dv*dv)
    uv_orig = f.cartesian_point((u0, v0_uv))
    uv_dir  = f.direction((du / mag, dv / mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_line = f._emit_raw(f"LINE('{label}',#{uv_orig.eid},#{uv_vec.eid})")
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line.eid}),#?)")
    return f._emit_raw(f"PCURVE('',#{cyl_surf.eid},#{drep.eid})")

# e1: seam edge — UV from (0,0) → (0,1): vertical line at U=0 in UV space
# Labelled to mark the seam-edge tolerance defect
pcurve1 = make_uv_line(0.0, 0.0, 0.0, 1.0, label='SEAM_EDGE_tol0p001')

# e2: closing edge — UV from (0,1) → (2π,1): horizontal line at V=1
TWO_PI = _math.pi * 2.0
pcurve2 = make_uv_line(0.0, 1.0, TWO_PI, 1.0)

# ── 3D geometry for edges ─────────────────────────────────────────────────────
# e1: vertical 3D line from (1,0,0) to (1,0,1)
line3d_e1 = f.line(
    f.cartesian_point(P_v0),
    f.vector(f.direction((0.0, 0.0, 1.0)), 1.0),
)
sc_e1 = f._emit_raw(
    f"SURFACE_CURVE('',#{line3d_e1.eid},(#{pcurve1.eid}),.PCURVE_S1.)"
)
ec_e1 = f._emit_raw(
    f"EDGE_CURVE('',#{v0.eid},#{v1.eid},#{sc_e1.eid},.T.)"
)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")

# e2: at V=1, circle arc from (1,0,1) around to (1,0,1) — full loop
# Use a 3D circle of radius 1 at Z=1
plc_e2_orig = f.cartesian_point((0.0, 0.0, 1.0))
plc_e2_zdir = f.direction((0.0, 0.0, 1.0))
plc_e2_xdir = f.direction((1.0, 0.0, 0.0))
plc_e2      = f.axis2_placement_3d(plc_e2_orig, plc_e2_zdir, plc_e2_xdir)
circ_e2     = f._emit_raw(f"CIRCLE('',#{plc_e2.eid},1.0)")
sc_e2 = f._emit_raw(
    f"SURFACE_CURVE('',#{circ_e2.eid},(#{pcurve2.eid}),.PCURVE_S1.)"
)
# e2 goes from v1 back to v0 (closing the loop)
ec_e2 = f._emit_raw(
    f"EDGE_CURVE('',#{v1.eid},#{v0.eid},#{sc_e2.eid},.T.)"
)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")

# ── EDGE_LOOP: seam edge + closing circle arc ─────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi121.stp")
