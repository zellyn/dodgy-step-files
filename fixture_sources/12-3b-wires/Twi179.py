"""Twi179 — ShapeAnalysis_Wire.CheckGap2d on-trimmed-pcurve.

Catalog claim: Adjacent edges with TRIMMED_CURVE pcurves. CheckGap2d compares
trim bounds against untrimmed parameters and incorrectly reports gap values
when both edges are trimmed.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on
a PLANE. Two adjacent edges (e0 and e1) use TRIMMED_CURVE pcurves instead of
plain pcurves. The trimming of the underlying parametric line means CheckGap2d
compares the trim-end parameter of e0's pcurve against the trim-start parameter
of e1's pcurve using the full untrimmed-curve parametric range, producing a
spurious gap report. The trimmed edges are labelled 'trimmed_pcurve_gap_A' and
'trimmed_pcurve_gap_B' to make the defect explicit in bytes.

Byte assertions:
  - contains(b'trimmed_pcurve_gap_A')
  - contains(b'trimmed_pcurve_gap_B')
  - contains(b'TRIMMED_CURVE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi179",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "unit square A(0,0)->B(1,0)->C(1,1)->D(0,1)->A; "
        "edges e0 (A->B, trimmed_pcurve_gap_A) and e1 (B->C, trimmed_pcurve_gap_B) "
        "use SURFACE_CURVE where pcurve basis is a TRIMMED_CURVE wrapping a LINE; "
        "trim_1=0.0 trim_2=0.5 on underlying unit-length line, then TRIMMED_CURVE "
        "re-parameterises to [0,1]; CheckGap2d IS mechanism — compares pcurve end "
        "parameter against untrimmed-line start parameter of next edge, reporting "
        "a false gap of 0.5 because it ignores the TRIMMED_CURVE re-parameterisation; "
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


def _line_sc_plain(v_s, v_e, ps, pe):
    """Plain SURFACE_CURVE (no TRIMMED_CURVE) for regular edges."""
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
    return f._emit_raw(f"EDGE_CURVE('',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


def _line_sc_trimmed(v_s, v_e, ps, pe, name=""):
    """SURFACE_CURVE where the pcurve basis is a TRIMMED_CURVE wrapping a LINE.

    The underlying parametric line is twice as long as the edge; TRIMMED_CURVE
    covers [0, 0.5] of it. CheckGap2d compares pcurve trim bounds against
    untrimmed parameters and produces a false gap.
    """
    dx = pe[0]-ps[0]; dy = pe[1]-ps[1]; dz = pe[2]-ps[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    # 3-D line (correct length)
    ln3 = f.line(f.cartesian_point(ps),
                 f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))
    # UV: underlying line is 2x as long (so trim [0,0.5] covers the edge)
    uv_orig = f.cartesian_point((ps[0], ps[1]))
    uv_dir  = f.direction((dx/mag, dy/mag))
    uv_long_vec = f.vector(uv_dir, mag * 2.0)   # 2x long
    uv_long_ln  = f.line(uv_orig, uv_long_vec)
    # TRIMMED_CURVE: [0, 0.5] on the long line (= [0, mag] parametrically)
    p_trim_start = f.cartesian_point((ps[0], ps[1]))
    p_trim_end   = f.cartesian_point((pe[0], pe[1]))
    tc = f._emit_raw(
        f"TRIMMED_CURVE('',#{uv_long_ln.eid},"
        f"(PARAMETER_VALUE(0.0),#{p_trim_start.eid}),"
        f"(PARAMETER_VALUE(0.5),#{p_trim_end.eid}),.T.,.PARAMETER.)"
    )
    drep = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{tc.eid}),#*)")
    pc   = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc   = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# e0: A->B — trimmed pcurve edge (mechanism)
ec0 = _line_sc_trimmed(vA, vB, PA, PB, name="trimmed_pcurve_gap_A")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: B->C — trimmed pcurve edge (mechanism)
ec1 = _line_sc_trimmed(vB, vC, PB, PC, name="trimmed_pcurve_gap_B")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: C->D — plain edge
ec2 = _line_sc_plain(vC, vD, PC, PD)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: D->A — plain edge (closes loop)
ec3 = _line_sc_plain(vD, vA, PD, PA)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi179.stp")
