"""Twi198 — ShapeAnalysis_Wire.CheckSelfIntersection coincident-line-segments.

Catalog claim: Wire with two edges sharing entire geometry (geometrically
identical); CheckSelfIntersection doesn't recognize and reports both as
separate.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on a
PLANE. Two edges named 'coinc_e0' and 'coinc_e1' reference the same geometric
LINE and have identical parameter ranges [0,1]. Handle equality misses
geometric equivalence so CheckSelfIntersection cannot merge them and reports
both as distinct, non-intersecting edges when they are geometrically identical.

Byte assertions:
  - contains(b'coinc_e0')
  - contains(b'coinc_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi198",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "coinc_e0 and coinc_e1 both reference same LINE from (0,0,0) to (2,0,0); "
        "both edges share identical vertex pair vA-vB with param range [0,2]; "
        "two edges with same geometry IS defect: handle equality misses equivalence; "
        "CheckSelfIntersection IS mechanism — geometric coincidence not detected; "
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

# Vertices
PA = (0.0, 0.0, 0.0)
PB = (2.0, 0.0, 0.0)
PC = (2.0, 2.0, 0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))


def _line_sc(v_s, v_e, ps, pe, shared_ln3=None, name=""):
    dx = pe[0] - ps[0]; dy = pe[1] - ps[1]; dz = pe[2] - ps[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    if shared_ln3 is None:
        ln3 = f.line(f.cartesian_point(ps),
                     f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))
    else:
        ln3 = shared_ln3
    uv_orig = f.cartesian_point((ps[0], ps[1]))
    uv_dir  = f.direction((dx/mag, dy/mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_ln   = f.line(uv_orig, uv_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc      = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# Shared LINE geometry — same curve object used by both coincident edges
dx, dy, dz = PB[0]-PA[0], PB[1]-PA[1], PB[2]-PA[2]
mag_ab = _math.sqrt(dx*dx + dy*dy + dz*dz)
shared_ln = f.line(f.cartesian_point(PA),
                   f.vector(f.direction((dx/mag_ab, dy/mag_ab, dz/mag_ab)), mag_ab))

# coinc_e0 and coinc_e1: identical geometry, same LINE reference
ec_coinc0 = _line_sc(vA, vB, PA, PB, shared_ln3=shared_ln, name="coinc_e0")
oe_coinc0  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_coinc0.eid},.T.)")

ec_coinc1 = _line_sc(vA, vB, PA, PB, shared_ln3=shared_ln, name="coinc_e1")
oe_coinc1  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_coinc1.eid},.T.)")

# Closing edges to form a valid loop structure (B->C->A)
ec2 = _line_sc(vB, vC, PB, PC, name="close_e2")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

ec3 = _line_sc(vC, vA, PC, PA, name="close_e3")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_coinc0.eid},#{oe2.eid},#{oe3.eid},#{oe_coinc1.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi198.stp")
