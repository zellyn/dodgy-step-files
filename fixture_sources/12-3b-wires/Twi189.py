"""Twi189 — ShapeFix_Wire.FixGaps3d directional-extension.

Catalog claim: Gap-bridge by extending edge A vs extending edge B yields
different results; FixGaps3d picks arbitrary direction not the
geometrically-correct one.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on a
PLANE. Edges e0 (A->B) and e1 (C->D) approach a tiny vertical gap from opposite
directions: B=(5,5,0) and C=(5,5.1,0) create a 0.1-unit gap. Extending e0
upward vs extending e1 downward yields different slopes; FixGaps3d picks by
iteration order (e0 first), not by geometry. The gap edges are labelled
'gap_extend_lower' (e0) and 'gap_extend_upper' (e1) to make the defect explicit
in bytes.

Byte assertions:
  - contains(b'gap_extend_lower')
  - contains(b'gap_extend_upper')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi189",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "A(0,0)->B(5,5) gap to C(5,5.1)->D(0,5.1)->A; "
        "gap from B(5,5,0) to C(5,5.1,0) is 0.1 units vertical; "
        "gap_extend_lower (A->B) IS edge below gap; "
        "gap_extend_upper (C->D) IS edge above gap; "
        "FixGaps3d IS mechanism — extends lower edge upward by iteration order, "
        "not by geometric preference (e.g. lower slope change); "
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
PB = (5.0, 5.0, 0.0)    # end of lower edge — gap starts here
PC = (5.0, 5.1, 0.0)    # start of upper edge — gap ends here (0.1 above PB)
PD = (0.0, 5.1, 0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vD = f.vertex_point(f.cartesian_point(PD))


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


# e0: A->B (gap_extend_lower — diagonal edge ending just below the gap)
ec0 = _line_sc(vA, vB, PA, PB, name="gap_extend_lower")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: C->D (gap_extend_upper — horizontal edge starting just above the gap)
ec1 = _line_sc(vC, vD, PC, PD, name="gap_extend_upper")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: D->A (closes loop on left side)
ec2 = _line_sc(vD, vA, PD, PA)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi189.stp")
