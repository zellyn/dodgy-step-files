"""Twi190 — ShapeAnalysis_Wire.CheckShapeConnect three-edge-fan.

Catalog claim: Three edges meeting at single shared vertex (fan);
CheckShapeConnect expects two-edge sharing and produces wrong verdict for fan.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on a
PLANE. Three edges (e0, e1, e2) all share a single hub vertex H at (2,1,0) as
their end-point, with one outgoing edge e3 from H to close the loop. This
creates a 3-edge fan at H: edges e0 (A->H), e1 (B->H), e2 (C->H) all terminate
at H, and e3 (H->A) departs from H. CheckShapeConnect expects exactly two edges
per vertex (one incoming, one outgoing) and produces a wrong verdict for this
fan topology. The hub vertex edges are labelled 'fan_spoke_0', 'fan_spoke_1',
'fan_spoke_2' to make the defect explicit in bytes.

Byte assertions:
  - contains(b'fan_spoke_0')
  - contains(b'fan_spoke_2')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi190",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "hub vertex H(2,1,0) shared by 3 incoming edges and 1 outgoing edge; "
        "fan_spoke_0: A(0,0)->H(2,1) first incoming edge; "
        "fan_spoke_1: B(4,0)->H(2,1) second incoming edge; "
        "fan_spoke_2: C(2,3)->H(2,1) third incoming edge; "
        "fan_hub_out: H(2,1)->A(0,0) outgoing edge; "
        "three-edge fan at H IS mechanism: CheckShapeConnect expects 2-edge sharing; "
        "CheckShapeConnect IS mechanism — wrong verdict for n-way fan topology; "
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

PA = (0.0, 0.0, 0.0)   # spoke 0 start / outgoing edge end
PB = (4.0, 0.0, 0.0)   # spoke 1 start
PC = (2.0, 3.0, 0.0)   # spoke 2 start
PH = (2.0, 1.0, 0.0)   # hub vertex — 3 edges terminate here

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vH = f.vertex_point(f.cartesian_point(PH))


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


# e0: A->H (fan_spoke_0)
ec0 = _line_sc(vA, vH, PA, PH, name="fan_spoke_0")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: B->H (fan_spoke_1)
ec1 = _line_sc(vB, vH, PB, PH, name="fan_spoke_1")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: C->H (fan_spoke_2)
ec2 = _line_sc(vC, vH, PC, PH, name="fan_spoke_2")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: H->A (fan_hub_out — outgoing edge from hub)
ec3 = _line_sc(vH, vA, PH, PA, name="fan_hub_out")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi190.stp")
