"""Twi187 — ShapeFix_Wire.FixLacking insertion-cascade.

Catalog claim: Wire missing 2 consecutive edges; FixLacking inserts the first,
then the second's position depends on the first's result, but no re-evaluation
happens.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 3 edges on a
PLANE. The wire has edges e0 (A->B), e1 (D->E) and e2 (E->A), creating two
consecutive gaps: B->D (first gap, labelled 'gap_before_cascade') and D->(D is
already e1 start, so gap B->D). The missing edges span B(1,0)->C(2,0)->D(3,0);
FixLacking inserts the first missing edge but doesn't re-scan for the second,
leaving the cascade gap unfixed. The gap-straddling edges are labelled
'cascade_gap_start' and 'cascade_gap_end' to make the defect explicit in bytes.

Byte assertions:
  - contains(b'cascade_gap_start')
  - contains(b'cascade_gap_end')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi187",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "A(0,0)->B(1,0) then gap to D(3,0)->E(3,1)->A(0,0); "
        "two consecutive missing edges B->C(2,0) and C->D in the wire; "
        "cascade_gap_start (A->B) IS the edge before first gap; "
        "cascade_gap_end (D->E) IS the edge after second gap; "
        "FixLacking IS mechanism — inserts first missing edge but no re-evaluation "
        "occurs to catch second cascading gap; "
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
PB = (1.0, 0.0, 0.0)   # end of first present edge — gap starts here
PD = (3.0, 0.0, 0.0)   # start of next present edge — two edges missing (B->C, C->D)
PE = (3.0, 1.0, 0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vD = f.vertex_point(f.cartesian_point(PD))
vE = f.vertex_point(f.cartesian_point(PE))


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


# e0: A->B (cascade_gap_start — edge before first gap)
ec0 = _line_sc(vA, vB, PA, PB, name="cascade_gap_start")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# e1: D->E (cascade_gap_end — edge after second gap; two edges missing before it)
ec1 = _line_sc(vD, vE, PD, PE, name="cascade_gap_end")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: E->A (closes the loop)
ec2 = _line_sc(vE, vA, PE, PA)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi187.stp")
