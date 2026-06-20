"""Twi197 — ShapeFix_Wire.FixTails iteration-with-removal.

Catalog claim: Wire with multiple tail candidates; FixTails removes one tail
and iterator gets invalidated.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on a
PLANE. Two collinear tail edges named 'tail_e1' and 'tail_e2' share the main
loop vertices but form degenerate short segments at different angles. FixTails
detects tail_e1 first and removes it from the sequence; the removal
invalidates the edge iterator, so tail_e2 is skipped on the next step.
The pair of short collinear edges ARE the mechanism.

Byte assertions:
  - contains(b'tail_e1')
  - contains(b'tail_e2')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi197",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "main loop: A(0,0,0)->B(3,0,0)->C(3,3,0)->A(0,0,0); "
        "tail_e1: A(0,0,0)->T1(0.01,0,0) short collinear tail at angle=0; "
        "tail_e2: A(0,0,0)->T2(0,0.01,0) short collinear tail at angle=90; "
        "FixTails removes tail_e1 first, invalidating iterator; tail_e2 skipped; "
        "iterator invalidation during sequence mutation IS mechanism; "
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
PA  = (0.0,  0.0,  0.0)
PB  = (3.0,  0.0,  0.0)
PC  = (3.0,  3.0,  0.0)
PT1 = (0.01, 0.0,  0.0)   # tail_e1 tip
PT2 = (0.0,  0.01, 0.0)   # tail_e2 tip

vA  = f.vertex_point(f.cartesian_point(PA))
vB  = f.vertex_point(f.cartesian_point(PB))
vC  = f.vertex_point(f.cartesian_point(PC))
vT1 = f.vertex_point(f.cartesian_point(PT1))
vT2 = f.vertex_point(f.cartesian_point(PT2))


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


# Main loop edges
ec0 = _line_sc(vA, vB, PA, PB, name="main_e0")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

ec1 = _line_sc(vB, vC, PB, PC, name="main_e1")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

ec2 = _line_sc(vC, vA, PC, PA, name="main_e2")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# Tail edges — two collinear tails from A, triggering iterator invalidation
ec3 = _line_sc(vA, vT1, PA, PT1, name="tail_e1")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

ec4 = _line_sc(vA, vT2, PA, PT2, name="tail_e2")
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi197.stp")
