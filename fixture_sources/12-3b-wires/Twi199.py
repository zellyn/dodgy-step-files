"""Twi199 — ShapeFix_Wire.FixGaps3d gap-larger-than-Confusion-but-less-than-vertex-tolerance.

Catalog claim: Gap treated as "real gap" by Confusion threshold but
"essentially closed" by vertex-tolerance test; FixGaps3d uses wrong threshold.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on a
PLANE. Two edges named 'gap_e0' and 'gap_e1' are separated by a gap of ~1e-6
at their junction — larger than Precision::Confusion (~1e-7) but smaller than
vertex tolerance (~1e-4). FixGaps3d's Confusion-based logic flags this as a
real gap but the tolerance-based test would close it. The threshold mismatch
between Precision::Confusion and vertex tolerance IS the mechanism.

Byte assertions:
  - contains(b'gap_e0')
  - contains(b'gap_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi199",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "gap_e0: A(0,0,0)->B(2,0,0), endpoint at exactly (2,0,0); "
        "gap_e1: start vertex at (2.000001,0,0) — 1e-6 gap from B; "
        "gap 1e-6 > Precision::Confusion(~1e-7) but < vertex tolerance(~1e-4); "
        "FixGaps3d Confusion-based logic flags real gap; tolerance logic would close; "
        "threshold mismatch between Confusion and vertex tolerance IS mechanism; "
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

# Vertices — gap_e1 starts 1e-6 away from where gap_e0 ends
PA  = (0.0,       0.0,  0.0)
PB  = (2.0,       0.0,  0.0)   # end of gap_e0
PB2 = (2.000001,  0.0,  0.0)   # start of gap_e1 — 1e-6 gap
PC  = (2.000001,  2.0,  0.0)
PD  = (0.0,       2.0,  0.0)

vA  = f.vertex_point(f.cartesian_point(PA))
vB  = f.vertex_point(f.cartesian_point(PB))
vB2 = f.vertex_point(f.cartesian_point(PB2))
vC  = f.vertex_point(f.cartesian_point(PC))
vD  = f.vertex_point(f.cartesian_point(PD))


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


# gap_e0: A->B, ends at exact (2,0,0)
ec0 = _line_sc(vA, vB, PA, PB, name="gap_e0")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# gap_e1: B2->C, starts at (2.000001,0,0) — 1e-6 gap IS the defect
ec1 = _line_sc(vB2, vC, PB2, PC, name="gap_e1")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# Closing edges: C->D->A
ec2 = _line_sc(vC, vD, PC, PD, name="close_e2")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

ec3 = _line_sc(vD, vA, PD, PA, name="close_e3")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi199.stp")
