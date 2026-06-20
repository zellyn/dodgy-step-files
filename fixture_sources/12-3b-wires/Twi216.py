"""Twi216 — ShapeFix_Wire.FixDegenerated removal-cascade.

Catalog claim: Wire with multiple degenerate edges. FixDegenerated removes
sequentially but removal changes vertex map, invalidating subsequent removals.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP representing an open
chain alternating normal and degenerate (zero-length) edges. Pattern:
normal(e0) → degen(d1) → normal(e2) → degen(d3) → normal(e4).
Degenerate edges 'd1' and 'd3' have coincident start and end vertices (zero
length). FixDegenerated removes d1 first; the vertex map changes, making the
index for d3 stale; cascade fails IS the defect mechanism.

Byte assertions:
  - contains(b'degen_d1')
  - contains(b'degen_d3')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi216",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with alternating normal and "
        "degenerate edges on PLANE; PLANE: normal +Z, origin (0,0,0); "
        "e0: normal LINE V0(0,0,0)->V1(3,0,0); "
        "degen_d1: zero-length degenerate edge at V1(3,0,0)->V1(3,0,0) IS first degen; "
        "e2: normal LINE V1(3,0,0)->V2(6,0,0); "
        "degen_d3: zero-length degenerate edge at V2(6,0,0)->V2(6,0,0) IS second degen; "
        "e4: normal LINE V2(6,0,0)->V3(9,0,0); "
        "FixDegenerated removes degen_d1 first changing vertex map IS cascade defect; "
        "stale index for degen_d3 causes second removal to fail IS mechanism; "
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
PV0 = (0.0, 0.0, 0.0)
PV1 = (3.0, 0.0, 0.0)
PV2 = (6.0, 0.0, 0.0)
PV3 = (9.0, 0.0, 0.0)

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


def _degen_edge(v_pt, pt, name=""):
    """Zero-length degenerate edge: same vertex at start and end, line of zero extent."""
    # Use a degenerate line pointing +X but parameterized to zero length
    ln3 = f.line(f.cartesian_point(pt),
                 f.vector(f.direction((1.0, 0.0, 0.0)), 0.0))
    uv_orig = f.cartesian_point((pt[0], pt[1]))
    uv_dir  = f.direction((1.0, 0.0))
    uv_vec  = f.vector(uv_dir, 0.0)
    uv_ln   = f.line(uv_orig, uv_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc      = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_pt.eid},#{v_pt.eid},#{sc.eid},.T.)")


# e0: normal V0 -> V1
ec_e0 = _line_sc(vV0, vV1, PV0, PV1, name="e0")
oe_e0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e0.eid},.T.)")

# degen_d1: zero-length at V1
ec_d1 = _degen_edge(vV1, PV1, name="degen_d1")
oe_d1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_d1.eid},.T.)")

# e2: normal V1 -> V2
ec_e2 = _line_sc(vV1, vV2, PV1, PV2, name="e2")
oe_e2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")

# degen_d3: zero-length at V2
ec_d3 = _degen_edge(vV2, PV2, name="degen_d3")
oe_d3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_d3.eid},.T.)")

# e4: normal V2 -> V3
ec_e4 = _line_sc(vV2, vV3, PV2, PV3, name="e4")
oe_e4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e4.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_e0.eid},#{oe_d1.eid},#{oe_e2.eid},#{oe_d3.eid},#{oe_e4.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi216.stp")
