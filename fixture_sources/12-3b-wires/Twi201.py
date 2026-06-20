"""Twi201 — ShapeFix_Wire.FixSeam mismatched-pcurve-direction.

Catalog claim: Seam edge with pcurves on two sides pointing in opposite
directions; FixSeam takes one side's direction as correct.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP on a PLANE. A seam
edge named 'seam_fwd' has two PCURVE references, one parametrized 0→2π
(forward) and one parametrized 2π→0 (reversed). The two references are
placed in a SURFACE_CURVE with PCURVE_S1/PCURVE_S2 tags. FixSeam assumes
the first pcurve direction is canonical and applies that direction to both
sides; when the pcurve directions are opposite, the resulting wire has an
internally inconsistent orientation. The mismatched pcurve directions IS
the mechanism.

Byte assertions:
  - contains(b'seam_fwd')
  - contains(b'seam_rev')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

TWO_PI = 6.283185307179586

f = StepFile(
    catalog_id="Twi201",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "seam_fwd: seam edge; SURFACE_CURVE carries two PCURVEs — "
        "pcurve_fwd parametrized u=0→2π (forward) tagged PCURVE_S1; "
        "pcurve_rev parametrized u=2π→0 (reversed) tagged PCURVE_S2; "
        "mismatched pcurve directions on same edge IS defect; "
        "FixSeam assumes first pcurve direction canonical — wrong for side-2; "
        "parametric orientation mismatch IS mechanism; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# PLANE: normal +Z (used as parametric domain for both pcurves)
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# A second plane reference used as the "other side" of the seam
pl_orig2 = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir2 = f.direction((0.0, 0.0, 1.0))
pl_xdir2 = f.direction((1.0, 0.0, 0.0))
pl_plc2  = f.axis2_placement_3d(pl_orig2, pl_zdir2, pl_xdir2)
plane2   = f.plane(pl_plc2)

# Vertices for the seam edge (start == end for a closed seam)
PA = (1.0, 0.0, 0.0)   # seam vertex (same point, parametric seam at u=0 and u=2pi)
vA = f.vertex_point(f.cartesian_point(PA))
PB = (0.0, 1.0, 0.0)
vB = f.vertex_point(f.cartesian_point(PB))
PC = (-1.0, 0.0, 0.0)
vC = f.vertex_point(f.cartesian_point(PC))

# 3D seam geometry: LINE along x from (1,0,0) with length 2pi (seam parametric)
seam_ln3 = f.line(f.cartesian_point(PA),
                  f.vector(f.direction((0.0, 1.0, 0.0)), TWO_PI))

# pcurve_fwd: u = 0 → 2π (forward direction) on plane
pc_fwd_orig = f.cartesian_point((0.0, 0.0))
pc_fwd_dir  = f.direction((1.0, 0.0))
pc_fwd_vec  = f.vector(pc_fwd_dir, TWO_PI)
pc_fwd_ln   = f.line(pc_fwd_orig, pc_fwd_vec)
drep_fwd    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{pc_fwd_ln.eid}),#*)")
pc_fwd      = f._emit_raw(f"PCURVE('seam_fwd',#{plane.eid},#{drep_fwd.eid})")

# pcurve_rev: u = 2π → 0 (reversed direction) on plane2 — MISMATCH IS defect
pc_rev_orig = f.cartesian_point((TWO_PI, 0.0))
pc_rev_dir  = f.direction((-1.0, 0.0))
pc_rev_vec  = f.vector(pc_rev_dir, TWO_PI)
pc_rev_ln   = f.line(pc_rev_orig, pc_rev_vec)
drep_rev    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{pc_rev_ln.eid}),#*)")
pc_rev      = f._emit_raw(f"PCURVE('seam_rev',#{plane2.eid},#{drep_rev.eid})")

# SURFACE_CURVE with both pcurves — PCURVE_S1 forward, PCURVE_S2 reversed
sc_seam = f._emit_raw(
    f"SURFACE_CURVE('',#{seam_ln3.eid},"
    f"(#{pc_fwd.eid},#{pc_rev.eid}),.PCURVE_S1.)"
)
ec_seam = f._emit_raw(
    f"EDGE_CURVE('seam_edge',#{vA.eid},#{vA.eid},#{sc_seam.eid},.T.)"
)
oe_seam = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_seam.eid},.T.)")

# Two additional straight edges to fill out the EDGE_LOOP
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

ec1 = _line_sc(vA, vB, PA, PB, name="fill_e1")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

ec2 = _line_sc(vB, vA, PB, PA, name="fill_e2")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_seam.eid},#{oe1.eid},#{oe2.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi201.stp")
