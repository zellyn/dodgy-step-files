"""Twi243 — ShapeAnalysis_Wire.CheckConnected sharp-tangent-discontinuity.

Catalog claim: Closed EDGE_LOOP with 90° kink at shared vertex (edges form a
square; tangent direction inverts at each corner). CheckConnected flags the
discontinuous tangent; FixConnected may blend or split at the sharp angle.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP representing a square
wire. Four line edges meet at 90° corners. At each corner the arriving tangent
(e.g. +X) is perpendicular to the departing tangent (+Y), creating a sharp
C0-continuous but G1-discontinuous junction. CheckConnected's tangent-
continuity test detects these 90° kinks as tangent discontinuities and flags
all four corners. The wire is geometrically connected (vertices share 3D
coordinates) but tangentially discontinuous IS the defect.

Byte assertions:
  - contains(b'sq_e0')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi243",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP forming a square wire on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "Square corners: V0(0,0,0)->V1(6,0,0)->V2(6,6,0)->V3(0,6,0)->V0; "
        "sq_e0: (0,0,0)->(6,0,0) tangent +X; sq_e1: (6,0,0)->(6,6,0) tangent +Y; "
        "sq_e2: (6,6,0)->(0,6,0) tangent -X; sq_e3: (0,6,0)->(0,0,0) tangent -Y; "
        "at V1: arriving +X meets departing +Y — 90° tangent kink IS discontinuity; "
        "at V2: arriving +Y meets departing -X — 90° tangent kink IS discontinuity; "
        "at V3: arriving -X meets departing -Y — 90° tangent kink IS discontinuity; "
        "at V0: arriving -Y meets departing +X — 90° tangent kink IS discontinuity; "
        "CheckConnected flags all four 90° kinks as tangent discontinuities IS defect; "
        "wire IS geometrically connected (vertices share 3D coords) but G1-discontinuous; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# PLANE: normal +Z
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# Square vertices — geometrically connected, G1-discontinuous at each corner
PV0 = (0.0, 0.0, 0.0)
PV1 = (6.0, 0.0, 0.0)
PV2 = (6.0, 6.0, 0.0)
PV3 = (0.0, 6.0, 0.0)

vV0 = f.vertex_point(f.cartesian_point(PV0))
vV1 = f.vertex_point(f.cartesian_point(PV1))
vV2 = f.vertex_point(f.cartesian_point(PV2))
vV3 = f.vertex_point(f.cartesian_point(PV3))


def _line_sc(v_s, v_e, ps, pe, name=""):
    dx = pe[0] - ps[0]; dy = pe[1] - ps[1]; dz = pe[2] - ps[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    ln3 = f.line(f.cartesian_point(ps),
                 f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))
    uv_orig = f.cartesian_point((ps[0], ps[1]))
    uv_dir  = f.direction((dx/mag, dy/mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_ln   = f.line(uv_orig, uv_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc      = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# Four square edges — each pair meets at 90° kink (G1-discontinuous)
ec_e0 = _line_sc(vV0, vV1, PV0, PV1, name="sq_e0")   # +X tangent
ec_e1 = _line_sc(vV1, vV2, PV1, PV2, name="sq_e1")   # +Y tangent (90° from e0)
ec_e2 = _line_sc(vV2, vV3, PV2, PV3, name="sq_e2")   # -X tangent (90° from e1)
ec_e3 = _line_sc(vV3, vV0, PV3, PV0, name="sq_e3")   # -Y tangent (90° from e2)

oe_e0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e0.eid},.T.)")
oe_e1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_e0.eid},#{oe_e1.eid},#{oe_e2.eid},#{oe_e3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi243.stp")
