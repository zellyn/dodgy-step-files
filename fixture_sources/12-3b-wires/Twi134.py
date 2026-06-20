"""Twi134 — ShapeFix_Wire.FixShifted non-2π shift.

Catalog claim: Wire on SURFACE_OF_REVOLUTION (periodic in θ) with pcurves
shifted by π (half period). FixShifted assumes all periodic shifts are multiples
of 2π and skips correction for odd multiples.

Fixture: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with 3 edges on a
SURFACE_OF_REVOLUTION (cylinder-like profile, periodic in θ with period 2π).
Two edges have pcurves that are correctly positioned in [0,2π], but a third
edge's pcurve is shifted by exactly π (half-period): its u-coordinate is in
[π, 3π] instead of [-π, π]. FixShifted detects the shift but only attempts
corrections that are multiples of 2π, leaving the π-shifted edge uncorrected.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi134",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges; "
        "SURFACE_OF_REVOLUTION: revolves straight line profile around Z axis, radius=5; "
        "3D circle at z=0, radius=5; edges span θ=[0,2π/3], [2π/3,4π/3], [4π/3,2π]; "
        "e1 pcurve: u=[0,2π/3] — correctly positioned; "
        "e2 pcurve: u=[π+2π/3, π+4π/3] — shifted by π IS defect (half-period shift); "
        "e3 pcurve: u=[4π/3,2π] — correctly positioned; "
        "FixShifted corrects only 2π-multiple shifts; π-shift on e2 is skipped IS defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

PI   = _math.pi
R    = 5.0   # revolution radius

# ── SURFACE_OF_REVOLUTION: profile = vertical line at x=R, revolve around Z ──
# Profile: LINE at x=R from z=-1 to z=1
profile_orig = f.cartesian_point((R, 0.0, -1.0))
profile_dir  = f.direction((0.0, 0.0, 1.0))
profile_vec  = f.vector(profile_dir, 2.0)
profile_line = f.line(profile_orig, profile_vec)

# Axis of revolution: Z-axis through origin
rev_orig = f.cartesian_point((0.0, 0.0, 0.0))
rev_dir  = f.direction((0.0, 0.0, 1.0))
rev_axis = f._emit_raw(f"AXIS1_PLACEMENT('',#{rev_orig.eid},#{rev_dir.eid})")
surf = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('',#{profile_line.eid},#{rev_axis.eid})"
)

# ── 3D circle at z=0, radius=R ───────────────────────────────────────────────
circ_orig = f.cartesian_point((0.0, 0.0, 0.0))
circ_zdir = f.direction((0.0, 0.0, 1.0))
circ_xdir = f.direction((1.0, 0.0, 0.0))
circ_plc  = f.axis2_placement_3d(circ_orig, circ_zdir, circ_xdir)
circle3d  = f.circle(circ_plc, R)

# ── 3D vertex positions at angles 0, 2π/3, 4π/3 ─────────────────────────────
def pt3d(theta):
    return (R*_math.cos(theta), R*_math.sin(theta), 0.0)

T0 = 0.0
T1 = 2.0*PI/3.0    # 120°
T2 = 4.0*PI/3.0    # 240°

vA = f.vertex_point(f.cartesian_point(pt3d(T0)))
vB = f.vertex_point(f.cartesian_point(pt3d(T1)))
vC = f.vertex_point(f.cartesian_point(pt3d(T2)))


def _pcurve_uv(u0, v0, du, dv, length):
    """2D line pcurve on the surface_of_revolution (u=θ, v=height param)."""
    pc_orig = f.cartesian_point((u0, v0))
    mag = _math.sqrt(du*du + dv*dv)
    pc_dir  = f.direction((du/mag, dv/mag))
    pc_line = f.line(pc_orig, f.vector(pc_dir, length))
    pc_def  = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{pc_line.eid}),#*)")
    return f._emit_raw(f"PCURVE('',#{surf.eid},#{pc_def.eid})")


def _sc_edge(v_s, p_s, v_e, p_e, pc):
    """SURFACE_CURVE + EDGE_CURVE for a circular arc."""
    sc = f._emit_raw(f"SURFACE_CURVE('',#{circle3d.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# e1: vA→vB, pcurve u:[0, 2π/3] at v=0.5 — correctly positioned
pc1 = _pcurve_uv(T0, 0.5, 1.0, 0.0, T1-T0)
ec1 = _sc_edge(vA, pt3d(T0), vB, pt3d(T1), pc1)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: vB→vC, pcurve u:[π+2π/3, π+4π/3] — shifted by π IS THE DEFECT
# Correct would be [2π/3, 4π/3]; this adds π to simulate half-period shift
pc2 = _pcurve_uv(PI + T1, 0.5, 1.0, 0.0, T2-T1)
ec2 = _sc_edge(vB, pt3d(T1), vC, pt3d(T2), pc2)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: vC→vA, pcurve u:[4π/3, 2π] at v=0.5 — correctly positioned
pc3 = _pcurve_uv(T2, 0.5, 1.0, 0.0, 2.0*PI-T2)
ec3 = _sc_edge(vC, pt3d(T2), vA, pt3d(T0), pc3)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# ── EDGE_LOOP: 3 edges ────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi134.stp")
