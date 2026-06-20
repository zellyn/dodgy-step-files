"""Twi182 — ShapeFix_Wire.FixTails very-small-tail.

Catalog claim: Wire with trailing edge length ~1e-15; FixTails removal breaks
closure semantics.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 5 edges on a
PLANE. Four edges form a unit square A->B->C->D; the 5th edge is an
ultra-short tail: D->(D+epsilon) where epsilon ~ 1e-15. When FixTails removes
the tail, the wire endpoint reverts to D's coordinates instead of the intended
closing vertex (A), breaking wire closure. The tail edge is labelled
'very_small_tail' to make the defect explicit in bytes.

Byte assertions:
  - contains(b'very_small_tail')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi182",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 5 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "unit square A(0,0)->B(1,0)->C(1,1)->D(0,1) plus ultra-short tail "
        "D->Dt where Dt=(1e-15,1.0,0.0), tail length~1e-15; "
        "very_small_tail edge IS the mechanism: removing tail with length<tolerance "
        "causes wire endpoint to revert to D instead of closing at A; "
        "FixTails IS mechanism — tail removal breaks closure semantics; "
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

TAIL = 1e-15

PA  = (0.0,  0.0, 0.0)
PB  = (1.0,  0.0, 0.0)
PC  = (1.0,  1.0, 0.0)
PD  = (0.0,  1.0, 0.0)
PDt = (TAIL, 1.0, 0.0)   # D + epsilon (ultra-short tail endpoint)

vA  = f.vertex_point(f.cartesian_point(PA))
vB  = f.vertex_point(f.cartesian_point(PB))
vC  = f.vertex_point(f.cartesian_point(PC))
vD  = f.vertex_point(f.cartesian_point(PD))
vDt = f.vertex_point(f.cartesian_point(PDt))


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


# Square edges
ec0 = _line_sc(vA, vB, PA, PB)
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

ec1 = _line_sc(vB, vC, PB, PC)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

ec2 = _line_sc(vC, vD, PC, PD)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

ec3 = _line_sc(vD, vA, PD, PA)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# Ultra-short tail edge: D -> Dt (length ~ 1e-15)
ec4 = _line_sc(vD, vDt, PD, PDt, name="very_small_tail")
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi182.stp")
