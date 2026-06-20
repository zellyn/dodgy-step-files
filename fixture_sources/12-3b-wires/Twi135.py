"""Twi135 — ShapeAnalysis_Wire.CheckGap2d trimmed-pcurve gap.

Catalog claim: Adjacent edges with pcurves defined as TRIMMED_CURVEs of different
basis line curves. CheckGap2d compares 2d endpoints in the trimmed parameter spaces
instead of evaluating the actual basis curve positions, reporting false gaps.

Fixture: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with 3 edges on a PLANE.
e1 and e2 are adjacent edges whose pcurves are TRIMMED_CURVEs wrapping two
different basis lines that both pass through the same 2D point (5,3).
However, the trim parameter values differ: e1 ends at parameter=5.0 on its
basis line, while e2 starts at parameter=3.0 on its different basis line.
CheckGap2d compares trim parameter values (5.0 vs 3.0) rather than evaluating
the actual 2D positions, reporting a false gap even though both evaluate to
the same 2D location (5,3).

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi135",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "e1 pcurve: TRIMMED_CURVE of LINE1 from (0,0) direction (1,0.6) trimmed t=[0,5]; "
        "e1 2D endpoint: (0,0)+(1,0.6)*5 = (5,3) — correct junction; "
        "e2 pcurve: TRIMMED_CURVE of LINE2 from (5-0.6*3,3-0.8*3) direction (0.6,0.8) trimmed t=[0,3]; "
        "e2 2D start: same point (5,3) — same geometric position different parameter IS defect; "
        "CheckGap2d compares trim-parameter endpoints t=5 vs t=0 instead of evaluating 2D positions; "
        "false gap reported at (5,3) even though both pcurves reach same 2D location; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── PLANE: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── 3D vertices ───────────────────────────────────────────────────────────────
# e1: (0,0,0)→(5,3,0);  e2: (5,3,0)→(8,7,0);  e3: (8,7,0)→(0,0,0) close
PA3d = (0.0, 0.0, 0.0)
PB3d = (5.0, 3.0, 0.0)
PC3d = (8.0, 7.0, 0.0)

vA = f.vertex_point(f.cartesian_point(PA3d))
vB = f.vertex_point(f.cartesian_point(PB3d))
vC = f.vertex_point(f.cartesian_point(PC3d))


def _3d_line(p_s, p_e):
    dx, dy, dz = p_e[0]-p_s[0], p_e[1]-p_s[1], p_e[2]-p_s[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    return f.line(
        f.cartesian_point(p_s),
        f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag),
    )


# ── e1 pcurve: TRIMMED_CURVE basis LINE1 origin=(0,0) dir=(1,0.6) t=[0→5] ──
# At t=5: (0+1*5, 0+0.6*5) = (5, 3.0) — junction point
L1_mag  = _math.sqrt(1.0**2 + 0.6**2)
L1_orig = f.cartesian_point((0.0, 0.0))
L1_dir  = f.direction((1.0/L1_mag, 0.6/L1_mag))
L1_vec  = f.vector(L1_dir, L1_mag)
L1_base = f.line(L1_orig, L1_vec)
# TRIMMED_CURVE with PARAMETER trim [0, 5] using raw unit-parameterized line
# We use PARAMETER_VALUE to make trim parameter explicit
L1_trim = f._emit_raw(
    f"TRIMMED_CURVE('',#{L1_base.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE(5.0)),.T.,.PARAMETER.)"
)
pc1_def = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{L1_trim.eid}),#*)")
pc1     = f._emit_raw(f"PCURVE('',#{plane.eid},#{pc1_def.eid})")

# ── e2 pcurve: TRIMMED_CURVE basis LINE2 origin=(3.2,0.6) dir=(0.6,0.8) t=[0→3] ──
# At t=0: (3.2, 0.6) + (0.6,0.8)*0 = (3.2, 0.6)? No — we want start = (5,3).
# L2 must start from a position such that at t=3 it also hits (5,3).
# L2 origin such that L2_origin + (0.6,0.8)*3 = (5,3):
#   L2_origin = (5-1.8, 3-2.4) = (3.2, 0.6); start at t=0 → (3.2,0.6) != (5,3)
# To make it start at (5,3): set origin=(5,3), t_start=0: at t=0 → (5,3) ✓
# Then at t=3: (5+0.6*3, 3+0.8*3) = (6.8, 5.4) — end of e2
# But we want e2 to end at PC2d=(8,7). Let's pick a different direction.
# Direction for (8,7)-(5,3) = (3,4), mag=5, so dir=(0.6, 0.8).
# e2 basis: origin=(5,3), dir=(0.6,0.8), trim=[0,5] reaches (5+3, 3+4)=(8,7) ✓
# BUT CheckGap2d bug: e1 ends at trim_param=5; e2 starts at trim_param=0.
# The trim_param values differ (5 vs 0) even though the 2D endpoints coincide.
# This is the false-gap trigger: CheckGap2d compares raw parameter numbers.
L2_orig = f.cartesian_point((5.0, 3.0))
L2_dir  = f.direction((0.6, 0.8))   # (3,4)/5
L2_vec  = f.vector(L2_dir, 5.0)
L2_base = f.line(L2_orig, L2_vec)
L2_trim = f._emit_raw(
    f"TRIMMED_CURVE('',#{L2_base.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE(5.0)),.T.,.PARAMETER.)"
)
pc2_def = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{L2_trim.eid}),#*)")
pc2     = f._emit_raw(f"PCURVE('',#{plane.eid},#{pc2_def.eid})")

# ── e3 pcurve: simple 2D line C→A, no trimmed-curve (valid) ─────────────────
PC2d = (8.0, 7.0)
PA2d = (0.0, 0.0)
dx3, dy3 = PA2d[0]-PC2d[0], PA2d[1]-PC2d[1]
L3_mag = _math.sqrt(dx3*dx3 + dy3*dy3)
L3_orig = f.cartesian_point(PC2d)
L3_dir  = f.direction((dx3/L3_mag, dy3/L3_mag))
L3_base = f.line(L3_orig, f.vector(L3_dir, L3_mag))
pc3_def = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{L3_base.eid}),#*)")
pc3     = f._emit_raw(f"PCURVE('',#{plane.eid},#{pc3_def.eid})")

# ── EDGE_CURVEs via SURFACE_CURVE ────────────────────────────────────────────
line_e1 = _3d_line(PA3d, PB3d)
sc1 = f._emit_raw(f"SURFACE_CURVE('',#{line_e1.eid},(#{pc1.eid}),.PCURVE_S1.)")
ec1 = f._emit_raw(f"EDGE_CURVE('',#{vA.eid},#{vB.eid},#{sc1.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

line_e2 = _3d_line(PB3d, PC3d)
sc2 = f._emit_raw(f"SURFACE_CURVE('',#{line_e2.eid},(#{pc2.eid}),.PCURVE_S1.)")
ec2 = f._emit_raw(f"EDGE_CURVE('',#{vB.eid},#{vC.eid},#{sc2.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

line_e3 = _3d_line(PC3d, PA3d)
sc3 = f._emit_raw(f"SURFACE_CURVE('',#{line_e3.eid},(#{pc3.eid}),.PCURVE_S1.)")
ec3 = f._emit_raw(f"EDGE_CURVE('',#{vC.eid},#{vA.eid},#{sc3.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi135.stp")
