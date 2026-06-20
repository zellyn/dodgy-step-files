"""Twi212 — ShapeFix_Wire.FixIntersectingEdges trim-aware-intersection.

Catalog claim: Two TRIMMED_CURVE edges geometrically don't intersect (different
trim ranges) but their base curves do. FixIntersectingEdges incorrectly splits at
base-curve intersection, producing erroneous split point in trimmed domain.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges on a
PLANE. Two collinear line edges share the same base LINE geometry but have
non-overlapping trim ranges. Edge 'trim_e0' covers t=[1,5] (avoids origin).
Edge 'trim_e1' covers t=[6,10] (starts after gap). The base LINE passes through
the origin at t=0, which is outside both trim ranges — but FixIntersectingEdges
tests base-curve intersection and finds t=0 (outside both trimmed ranges) and
incorrectly splits there. Non-overlapping trim ranges IS the defect.

Byte assertions:
  - contains(b'trim_e0')
  - contains(b'trim_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi212",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "base LINE: origin (0,0,0), direction +X (unit), length parameter t in [0,10]; "
        "trim_e0: EDGE_CURVE V0(1,0,0)->V1(5,0,0) using base LINE TRIMMED to t=[1,5]; "
        "trim_e1: EDGE_CURVE V2(6,0,0)->V3(10,0,0) using base LINE TRIMMED to t=[6,10]; "
        "base LINE passes through t=0 (origin) outside both trim ranges; "
        "FixIntersectingEdges splits at base-curve intersection t=0 outside "
        "trimmed domains IS the defect — erroneous split in non-overlapping trims; "
        "close_e2 (V1->V2) and close_e3 (V3->V0via loop) close the wire; "
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

# Base LINE along +X from origin (the shared base curve)
base_ln_orig = f.cartesian_point((0.0, 0.0, 0.0))
base_ln_dir  = f.direction((1.0, 0.0, 0.0))
base_ln_vec  = f.vector(base_ln_dir, 1.0)   # unit parameterized
base_ln      = f.line(base_ln_orig, base_ln_vec)

# Key 3D points
PV0 = (1.0,  0.0, 0.0)   # trim_e0 start (t=1)
PV1 = (5.0,  0.0, 0.0)   # trim_e0 end   (t=5)
PV2 = (6.0,  0.0, 0.0)   # trim_e1 start (t=6)
PV3 = (10.0, 0.0, 0.0)   # trim_e1 end   (t=10)

vV0 = f.vertex_point(f.cartesian_point(PV0))
vV1 = f.vertex_point(f.cartesian_point(PV1))
vV2 = f.vertex_point(f.cartesian_point(PV2))
vV3 = f.vertex_point(f.cartesian_point(PV3))


def _line_sc_plain(v_s, v_e, ps, pe, name=""):
    """Plain LINE SURFACE_CURVE (not using base_ln)."""
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


# Build TRIMMED_CURVE edges for trim_e0 and trim_e1 sharing the same base LINE.
# Both edges use TRIMMED_CURVE of base_ln as the edge geometry.
# TRIMMED_CURVE: ('', basis_curve, trim1, trim2, sense_agreement, master_representation)
tc0 = f._emit_raw(
    f"TRIMMED_CURVE('',#{base_ln.eid},"
    f"(PARAMETER_VALUE(1.0)),(PARAMETER_VALUE(5.0)),.T.,.PARAMETER.)"
)
ec_t0 = f._emit_raw(
    f"EDGE_CURVE('trim_e0',#{vV0.eid},#{vV1.eid},#{tc0.eid},.T.)"
)
oe_t0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_t0.eid},.T.)")

tc1 = f._emit_raw(
    f"TRIMMED_CURVE('',#{base_ln.eid},"
    f"(PARAMETER_VALUE(6.0)),(PARAMETER_VALUE(10.0)),.T.,.PARAMETER.)"
)
ec_t1 = f._emit_raw(
    f"EDGE_CURVE('trim_e1',#{vV2.eid},#{vV3.eid},#{tc1.eid},.T.)"
)
oe_t1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_t1.eid},.T.)")

# Closing edges: V1->V2 (gap bridge) and V3->V0 (return to start)
# We need a closed EDGE_LOOP. Route: trim_e0 (V0->V1), close_e2 (V1->V2),
# trim_e1 (V2->V3), close_e3 (V3->V0)
# close_e2: bridge from (5,0,0) to (6,0,0) along +X
ec_c2 = _line_sc_plain(vV1, vV2, PV1, PV2, name="close_e2")
oe_c2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_c2.eid},.T.)")

# close_e3: from V3(10,0,0) back to V0(1,0,0) — diagonal return
ec_c3 = _line_sc_plain(vV3, vV0, PV3, PV0, name="close_e3")
oe_c3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_c3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_t0.eid},#{oe_c2.eid},#{oe_t1.eid},#{oe_c3.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi212.stp")
