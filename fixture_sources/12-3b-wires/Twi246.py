"""Twi246 — ShapeAnalysis_Wire.CheckSameParameter overlapping edges.

Catalog claim: Multiple edges share same curve (overlapping geometry). Edges
'ov_e0', 'ov_e1', and 'ov_e2' all reference the same LINE; they share
overlapping 3D segments. CheckSameParameter or topological analysis flags edge
multiplicity; ambiguous parametrization is the defect.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP where two additional
edges (ov_e1 and ov_e2) reference the same underlying LINE entity as ov_e0.
All three map to the same parametric space on the same curve — overlapping
parametrization IS the defect. FixSameParameter or merge logic must detect the
shared-curve ambiguity.

Byte assertions:
  - contains(b'ov_e0')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi246",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "Rectangle base: V0(0,0,0)->V1(6,0,0)->V2(6,6,0)->V3(0,6,0)->V0; "
        "ov_e0: LINE from (0,0,0) dir +X length 6; "
        "ov_e1: references same LINE as ov_e0 for V0->mid(3,0,0); "
        "ov_e2: references same LINE as ov_e0 for mid(3,0,0)->V1; "
        "ov_e0, ov_e1, ov_e2 share overlapping LINE entity IS ambiguous parametrization; "
        "CheckSameParameter flags shared-curve edge multiplicity IS defect; "
        "FixSameParameter or Merging must detect and resolve overlapped curve IS repair; "
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
PV0   = (0.0, 0.0, 0.0)
PV1   = (6.0, 0.0, 0.0)
PV2   = (6.0, 6.0, 0.0)
PV3   = (0.0, 6.0, 0.0)
PVmid = (3.0, 0.0, 0.0)   # midpoint of V0->V1

vV0   = f.vertex_point(f.cartesian_point(PV0))
vV1   = f.vertex_point(f.cartesian_point(PV1))
vV2   = f.vertex_point(f.cartesian_point(PV2))
vV3   = f.vertex_point(f.cartesian_point(PV3))
vVmid = f.vertex_point(f.cartesian_point(PVmid))

# Shared LINE for the bottom segment — used by ov_e0, ov_e1, ov_e2 IS defect
shared_ln3 = f.line(
    f.cartesian_point(PV0),
    f.vector(f.direction((1.0, 0.0, 0.0)), 6.0)
)
uv_orig_sh = f.cartesian_point((PV0[0], PV0[1]))
uv_dir_sh  = f.direction((1.0, 0.0))
uv_vec_sh  = f.vector(uv_dir_sh, 6.0)
uv_ln_sh   = f.line(uv_orig_sh, uv_vec_sh)
drep_sh    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln_sh.eid}),#*)")
pc_sh      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep_sh.eid})")
sc_sh      = f._emit_raw(f"SURFACE_CURVE('',#{shared_ln3.eid},(#{pc_sh.eid}),.PCURVE_S1.)")

# ov_e0: full V0->V1 using shared_ln3
ec_ov0 = f._emit_raw(
    f"EDGE_CURVE('ov_e0',#{vV0.eid},#{vV1.eid},#{sc_sh.eid},.T.)"
)
# ov_e1: V0->mid using same sc_sh — overlap IS defect
ec_ov1 = f._emit_raw(
    f"EDGE_CURVE('ov_e1',#{vV0.eid},#{vVmid.eid},#{sc_sh.eid},.T.)"
)
# ov_e2: mid->V1 using same sc_sh — overlap IS defect
ec_ov2 = f._emit_raw(
    f"EDGE_CURVE('ov_e2',#{vVmid.eid},#{vV1.eid},#{sc_sh.eid},.T.)"
)


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


# Remaining rectangle edges (no overlap)
ec_e1 = _line_sc(vV1, vV2, PV1, PV2, name="e1")
ec_e2 = _line_sc(vV2, vV3, PV2, PV3, name="e2")
ec_e3 = _line_sc(vV3, vV0, PV3, PV0, name="e3")

# Loop: ov_e0 (full bottom), ov_e1 (half bottom), ov_e2 (half bottom) then rest
oe_ov0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_ov0.eid},.T.)")
oe_ov1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_ov1.eid},.T.)")
oe_ov2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_ov2.eid},.T.)")
oe_e1  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_ov0.eid},#{oe_ov1.eid},#{oe_ov2.eid},"
    f"#{oe_e1.eid},#{oe_e2.eid},#{oe_e3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi246.stp")
