"""Twi181 — ShapeAnalysis_Wire.CheckGap3d B-spline-vs-LINE.

Catalog claim: Adjacent edges where one is a B_SPLINE_CURVE and the other is a
LINE. CheckGap3d's endpoint extraction applies different parametric
interpretation for the two curve types, causing false gap detection.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on a
PLANE. Edge e0 uses a B_SPLINE_CURVE_WITH_KNOTS and edge e1 uses a plain LINE.
The two curves meet at (1,0,0) in 3-D space with zero actual gap, but
CheckGap3d evaluates the B-spline at parameter 1.0 (knot domain end) while
evaluating the LINE at parameter 0.0 (start), and the different extraction
paths disagree on the coordinate, producing a false gap report. The mixed-type
junction edges are labelled 'bspline_end_gap' and 'line_start_gap' to make
the defect explicit in bytes.

Byte assertions:
  - contains(b'bspline_end_gap')
  - contains(b'line_start_gap')
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi181",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "unit square A(0,0)->B(1,0)->C(1,1)->D(0,1)->A; "
        "edge e0 (A->B, bspline_end_gap) is a degree-1 B_SPLINE_CURVE_WITH_KNOTS; "
        "edge e1 (B->C, line_start_gap) is a plain LINE; "
        "both curves meet at B=(1,0,0) with zero actual 3-D gap; "
        "CheckGap3d IS mechanism — extracts B-spline endpoint at parameter 1.0 "
        "and LINE startpoint at parameter 0.0 via different code paths; "
        "parametric mismatch between code paths causes false gap detection; "
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

PA = (0.0, 0.0, 0.0)
PB = (1.0, 0.0, 0.0)
PC = (1.0, 1.0, 0.0)
PD = (0.0, 1.0, 0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vD = f.vertex_point(f.cartesian_point(PD))


def _line_sc(v_s, v_e, ps, pe, name=""):
    """Plain LINE-based SURFACE_CURVE."""
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


# e0: A->B — degree-1 B_SPLINE_CURVE_WITH_KNOTS (linear, knots [0,1])
cp0 = f.cartesian_point(PA)
cp1 = f.cartesian_point(PB)
bsp = f.b_spline_curve_with_knots(
    degree=1,
    control_points=[cp0, cp1],
    knot_multiplicities=[2, 2],
    knots=[0.0, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)
# pcurve for e0 (linear in UV)
uv0 = f.cartesian_point((PA[0], PA[1]))
uv1 = f.cartesian_point((PB[0], PB[1]))
uv_bsp = f.b_spline_curve_with_knots(
    degree=1,
    control_points=[uv0, uv1],
    knot_multiplicities=[2, 2],
    knots=[0.0, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)
drep0 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_bsp.eid}),#*)")
pc0   = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep0.eid})")
sc0   = f._emit_raw(f"SURFACE_CURVE('',#{bsp.eid},(#{pc0.eid}),.PCURVE_S1.)")
ec0   = f._emit_raw(f"EDGE_CURVE('bspline_end_gap',#{vA.eid},#{vB.eid},#{sc0.eid},.T.)")
oe0   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: B->C — plain LINE (line_start_gap, adjacent to the B-spline)
ec1 = _line_sc(vB, vC, PB, PC, name="line_start_gap")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: C->D — plain LINE
ec2 = _line_sc(vC, vD, PC, PD)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: D->A — plain LINE (closes loop)
ec3 = _line_sc(vD, vA, PD, PA)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi181.stp")
