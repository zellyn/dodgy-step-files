"""Twi170 — ShapeAnalysis_Wire.CheckGap3d 3D-vs-pcurve-disagreement.

Catalog claim: CheckGap3d on wire where 3D gap and parametric curve gap
disagree. Only one metric tested; alternative gap perspective unreported.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on
a PLANE (rectangular wire). The defect: one edge uses a SURFACE_CURVE where
the 3D LINE endpoint and the PCURVE endpoint disagree. Specifically, e2's
3D LINE ends at (10.0, 0.0, 0.0) while its PCURVE ends at (10.05, 0.0) —
0.05 discrepancy in U. CheckGap3d checks the 3D gap (which may appear closed
due to vertex snapping) but fails to report the pcurve-space gap, leaving the
discrepancy unreported. The disagreement between 3D and pcurve coordinates
IS the defect.

The mismatched pcurve endpoint is labelled 'pcurve_gap_disagreement'.

Byte assertions:
  - contains(b'pcurve_gap_disagreement')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi170",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "rectangular wire: A(0,0,0)→B(10,0,0)→C(10,8,0)→D(0,8,0)→A; "
        "e1 (A→B): SURFACE_CURVE 3D LINE ends at B=(10,0,0), "
        "PCURVE (labelled pcurve_gap_disagreement) ends at UV (10.05,0.0) — "
        "0.05 discrepancy in U parameter IS the defect; "
        "3D gap appears closed by vertex snapping but pcurve gap is real; "
        "CheckGap3d checks only 3D metric; pcurve-space gap unreported IS mechanism; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── PLANE: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
PA = (0.0,  0.0, 0.0)
PB = (10.0, 0.0, 0.0)
PC = (10.0, 8.0, 0.0)
PD = (0.0,  8.0, 0.0)

vA = f.vertex_point(f.cartesian_point(PA))
vB = f.vertex_point(f.cartesian_point(PB))
vC = f.vertex_point(f.cartesian_point(PC))
vD = f.vertex_point(f.cartesian_point(PD))


def _normal_sc(v_s, v_e, ps, pe):
    """Normal SURFACE_CURVE + EDGE_CURVE with matching 3D and pcurve endpoints."""
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


# ── e1: A→B with mismatched pcurve endpoint (the defect) ─────────────────────
# 3D LINE: (0,0,0) → (10,0,0)  [correct]
# PCURVE:  starts at UV (0,0), direction (1,0), but labelled end extends to
#          UV (10.05, 0) — the pcurve_gap_disagreement IS here.
PA3 = PA; PB3 = PB
dx1 = PB3[0]-PA3[0]; dy1 = PB3[1]-PA3[1]; dz1 = PB3[2]-PA3[2]
mag1 = _math.sqrt(dx1*dx1+dy1*dy1+dz1*dz1)
ln3_e1 = f.line(f.cartesian_point(PA3),
                f.vector(f.direction((dx1/mag1, dy1/mag1, dz1/mag1)), mag1))
# Pcurve: origin (0,0), direction (1,0), length 10.05 — ends at UV (10.05,0)
# This creates the 3D-vs-pcurve discrepancy.
uv_orig1 = f.cartesian_point((0.0, 0.0))
uv_dir1  = f.direction((1.0, 0.0))
uv_vec1  = f.vector(uv_dir1, 10.05)  # pcurve reaches 10.05, 3D ends at 10.0
uv_ln1   = f.line(uv_orig1, uv_vec1)
drep1    = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcurve_gap_disagreement',(#{uv_ln1.eid}),#*)"
)
pc1 = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep1.eid})")
sc1 = f._emit_raw(f"SURFACE_CURVE('',#{ln3_e1.eid},(#{pc1.eid}),.PCURVE_S1.)")
ec1 = f._emit_raw(f"EDGE_CURVE('',#{vA.eid},#{vB.eid},#{sc1.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# e2: B→C (normal)
ec2 = _normal_sc(vB, vC, PB, PC)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

# e3: C→D (normal)
ec3 = _normal_sc(vC, vD, PC, PD)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec3.eid},.T.)")

# e4: D→A (normal)
ec4 = _normal_sc(vD, vA, PD, PA)
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec4.eid},.T.)")

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi170.stp")
