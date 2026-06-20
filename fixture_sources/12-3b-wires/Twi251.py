"""Twi251 — ShapeFix_IntersectionTool FixIntersectingWires null input guard.

Catalog claim: Method receives null context or face argument. Returns false
without processing at line 1837. No diagnostic output distinguishes null-input
condition from healing-success.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with no carrier face
context — the wire is a naked edge loop not embedded in a FACE. When
ShapeFix_IntersectionTool::FixIntersectingWires is invoked it receives a null
face/context argument because no ADVANCED_FACE wraps the wire. The method
returns false at line 1837 without any diagnostic output. The silent false
return is indistinguishable from a successful no-op IS the defect. Named edge
'null_ctx_e' marks the defect-carrying edge.

Byte assertions:
  - contains(b'null_ctx_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi251",
    defect=(
        "GEOMETRIC_CURVE_SET containing bare EDGE_LOOP with no carrier FACE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "Rectangle: V0(0,0,0)->V1(6,0,0)->V2(6,6,0)->V3(0,6,0)->V0; "
        "null_ctx_e: first edge of EDGE_LOOP — marks the null-context carrier; "
        "FixIntersectingWires receives null face context (no ADVANCED_FACE) IS condition; "
        "method returns false at line 1837 without processing IS silent false return; "
        "no diagnostic distinguishes null-input from healing-success IS defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "EDGE_LOOP has no wrapping FACE — null context guaranteed at healing time; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# PLANE: normal +Z (used for surface curves but no ADVANCED_FACE wraps the loop)
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# Vertices
PV0 = (0.0, 0.0, 0.0)
PV1 = (6.0, 0.0, 0.0)
PV2 = (6.0, 6.0, 0.0)
PV3 = (0.0, 6.0, 0.0)

vV0 = f.vertex_point(f.cartesian_point(PV0))
vV1 = f.vertex_point(f.cartesian_point(PV1))
vV2 = f.vertex_point(f.cartesian_point(PV2))
vV3 = f.vertex_point(f.cartesian_point(PV3))


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


# null_ctx_e: first edge; marks the null-context carrier IS defect
ec_nc = _line_sc(vV0, vV1, PV0, PV1, name="null_ctx_e")
ec_e1 = _line_sc(vV1, vV2, PV1, PV2, name="e1")
ec_e2 = _line_sc(vV2, vV3, PV2, PV3, name="e2")
ec_e3 = _line_sc(vV3, vV0, PV3, PV0, name="e3")

oe_nc = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_nc.eid},.T.)")
oe_e1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

# Bare EDGE_LOOP — no ADVANCED_FACE wrapping IS the null-context condition
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_nc.eid},#{oe_e1.eid},#{oe_e2.eid},#{oe_e3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi251.stp")
