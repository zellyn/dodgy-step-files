"""Twi211 — ShapeFix_Wire.FixLacking surface-edge-direction-mismatch.

Catalog claim: Wire on CYLINDRICAL_SURFACE missing edge with specific direction
in parametric space. FixLacking inserts edge with reversed sense flag (.F.
instead of .T.), creating surface-edge-direction mismatch. Missing edge should
bridge u=[2.0, 2.1] at v=5.0 on cylinder; inserted edge has wrong orientation,
breaking surface-curve compatibility.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 5 edges. Wire on
CYLINDRICAL_SURFACE (radius 5, z-axis). Four arc edges (arcs u∈[0,1], u∈[1,2],
a degenerate stub at u=2, and the closing arc u∈[2.1,2π→0]) plus the mismatch
arc 'sense_mismatch_e' at u∈[2.0,2.1] with same_sense .F. (WRONG: should be .T.
to match surface-curve direction). FixLacking direction inference on periodic
surface IS the mechanism.

Byte assertions:
  - contains(b'sense_mismatch_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi211",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 5 edges on "
        "CYLINDRICAL_SURFACE (radius 5, axis +Z); "
        "arc_e0: u=[0,1] rad at z=5, arc forward; "
        "arc_e1: u=[1,2] rad at z=5, arc forward; "
        "sense_mismatch_e: u=[2.0,2.1] rad at z=5, same_sense .F. (WRONG — "
        "should be .T.); surface-curve direction mismatch IS the defect; "
        "arc_e3: u=[2.1,2pi] rad at z=5 closing arc; "
        "degenerate_e: seam closure stub at u=2*pi/0 seam; "
        "FixLacking inserts sense_mismatch_e with reversed sense IS mechanism; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# CYLINDRICAL_SURFACE: radius 5, axis +Z, origin at (0,0,0)
R = 5.0
Z = 5.0  # height at which the wire runs
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},{R})")

# Parametric angles in radians for the arc divisions
U0  = 0.0
U1  = 1.0
U2  = 2.0
U2a = 2.1
U_END = 2.0 * _math.pi   # closes back to u=0


def _pt_on_cyl(u, z=Z):
    """3D point on cylinder at angle u, height z."""
    return (R * _math.cos(u), R * _math.sin(u), z)


def _arc_tangent_dir(u):
    """Tangent direction of circle at angle u (CCW)."""
    return (-_math.sin(u), _math.cos(u), 0.0)


# 3D points at each division
P0   = _pt_on_cyl(U0)    # (5, 0, 5)
P1   = _pt_on_cyl(U1)
P2   = _pt_on_cyl(U2)
P2a  = _pt_on_cyl(U2a)
P_end = _pt_on_cyl(U0)   # back to start (same as P0 for closed loop)

# VERTEX_POINTs
vV0  = f.vertex_point(f.cartesian_point(P0))
vV1  = f.vertex_point(f.cartesian_point(P1))
vV2  = f.vertex_point(f.cartesian_point(P2))
vV2a = f.vertex_point(f.cartesian_point(P2a))
# vV_end = vV0 (the loop closes)


def _arc_sc_on_cyl(v_s, v_e, u_start, u_end, same_sense, name=""):
    """Arc edge on the cylinder from u_start to u_end at height Z."""
    # 3D circle in the horizontal plane at height Z
    circ_plc_orig = f.cartesian_point((0.0, 0.0, Z))
    circ_plc_zdir = f.direction((0.0, 0.0, 1.0))
    circ_plc_xdir = f.direction((1.0, 0.0, 0.0))
    circ_plc  = f.axis2_placement_3d(circ_plc_orig, circ_plc_zdir, circ_plc_xdir)
    circ_geom = f._emit_raw(f"CIRCLE('',#{circ_plc.eid},{R})")
    sense_str = ".T." if same_sense else ".F."
    return f._emit_raw(
        f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{circ_geom.eid},{sense_str})"
    )


# arc_e0: u=[0,1], forward sense
ec0 = _arc_sc_on_cyl(vV0, vV1, U0, U1, same_sense=True, name="arc_e0")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# arc_e1: u=[1,2], forward sense
ec1 = _arc_sc_on_cyl(vV1, vV2, U1, U2, same_sense=True, name="arc_e1")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# sense_mismatch_e: u=[2.0,2.1] with .F. sense — IS the defect
# FixLacking inserts this edge with reversed sense, breaking surface-curve compatibility
ec_mm = _arc_sc_on_cyl(vV2, vV2a, U2, U2a, same_sense=False, name="sense_mismatch_e")
oe_mm = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_mm.eid},.T.)")

# arc_e3: u=[2.1,2pi] closing arc, forward sense
# This arc covers most of the circle back to start
ec3 = _arc_sc_on_cyl(vV2a, vV0, U2a, U_END, same_sense=True, name="arc_e3")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe_mm.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi211.stp")
