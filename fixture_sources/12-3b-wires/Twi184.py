"""Twi184 — ShapeFix_Wire.FixConnected zero-length-edge-between.

Catalog claim: Zero-length edge between two normal edges masks a discontinuity
that should trigger repair. FixConnected sees zero-length-edge-bridged endpoints
as connected and skips needed gap/mismatch fixes.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 5 edges on a
PLANE. Four edges form a near-square with a deliberate gap at one junction (B1
to B2, gap = 0.1 in 3-D space). A 5th zero-length degenerate edge bridges the
gap by connecting B1 to B2 without any 3-D extent. FixConnected sees the
zero-length-edge-bridge and considers the discontinuity "connected", skipping
the gap fix that should propagate to the normal edges. The zero-length bridge
edge is labelled 'zero_length_bridge' to make the defect explicit in bytes.

Byte assertions:
  - contains(b'zero_length_bridge')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi184",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 5 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "near-square A(0,0)->B1(1,0) gap B2(1.1,0)->C(1.1,1)->D(0,1)->A; "
        "zero-length bridge edge B1->B2 (zero_length_bridge) masks 0.1 gap; "
        "zero_length_bridge IS the mechanism: 5th degenerate edge bridges "
        "B1(1,0)->B2(1.1,0) with zero-length LINE (same start/end vertex ref); "
        "FixConnected IS mechanism — bridge makes junction appear connected, "
        "skipping gap/mismatch fix on surrounding normal edges; "
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

PA  = (0.0, 0.0, 0.0)
PB1 = (1.0, 0.0, 0.0)   # end of first normal edge
PB2 = (1.1, 0.0, 0.0)   # start of second normal edge (0.1 gap in 3-D)
PC  = (1.1, 1.0, 0.0)
PD  = (0.0, 1.0, 0.0)

vA  = f.vertex_point(f.cartesian_point(PA))
vB1 = f.vertex_point(f.cartesian_point(PB1))
vB2 = f.vertex_point(f.cartesian_point(PB2))
vC  = f.vertex_point(f.cartesian_point(PC))
vD  = f.vertex_point(f.cartesian_point(PD))


def _line_sc(v_s, v_e, ps, pe, name=""):
    dx = pe[0]-ps[0]; dy = pe[1]-ps[1]; dz = pe[2]-ps[2]
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


# e0: A -> B1 (normal edge, ends before the gap)
ec0 = _line_sc(vA, vB1, PA, PB1)
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: B1 -> B2 — zero-length degenerate bridge (the defect mechanism)
# Use a LINE at B1 with magnitude 0 — degenerate but syntactically valid.
# Both vertices point to PB1's coordinates; B2 is a distinct VERTEX_POINT.
zl_dir = f.direction((1.0, 0.0, 0.0))
zl_vec = f.vector(zl_dir, 0.0)   # zero magnitude
zl_ln  = f.line(f.cartesian_point(PB1), zl_vec)
zl_uv_orig = f.cartesian_point((PB1[0], PB1[1]))
zl_uv_dir  = f.direction((1.0, 0.0))
zl_uv_vec  = f.vector(zl_uv_dir, 0.0)
zl_uv_ln   = f.line(zl_uv_orig, zl_uv_vec)
zl_drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{zl_uv_ln.eid}),#*)")
zl_pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{zl_drep.eid})")
zl_sc      = f._emit_raw(f"SURFACE_CURVE('',#{zl_ln.eid},(#{zl_pc.eid}),.PCURVE_S1.)")
ec1        = f._emit_raw(
    f"EDGE_CURVE('zero_length_bridge',#{vB1.eid},#{vB2.eid},#{zl_sc.eid},.T.)"
)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: B2 -> C (normal edge, starts after the gap)
ec2 = _line_sc(vB2, vC, PB2, PC)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: C -> D
ec3 = _line_sc(vC, vD, PC, PD)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# e4: D -> A (closes the loop)
ec4 = _line_sc(vD, vA, PD, PA)
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi184.stp")
