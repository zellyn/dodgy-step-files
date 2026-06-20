"""Twi242 — ShapeAnalysis_Wire.CheckOrder edge orientation reversal.

Catalog claim: Edge orientation reversal breaks traversal order in a closed
wire. CheckOrder detects non-linear topology in wire where one edge opposes
the expected direction.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP representing a
rectangular wire. Three edges traverse counter-clockwise (forward orientation
.T.); one edge 'rev_e' is inserted with reversed orientation (.F.), meaning
the ORIENTED_EDGE references the EDGE_CURVE with orientation False. This causes
the wire traversal to oppose the expected direction at that edge, breaking
sequential order. CheckOrder detects the non-linear topology (traversal
direction mismatch) and marks the wire as disordered.

Byte assertions:
  - contains(b'rev_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi242",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 line edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "V0(0,0,0)->V1(8,0,0)->V2(8,6,0)->V3(0,6,0)->V0 rectangular wire; "
        "rev_e: EDGE_CURVE from V2(8,6,0)->V3(0,6,0) used with .F. orientation; "
        "ORIENTED_EDGE for rev_e has orientation=.F. — traversal reverses at that edge; "
        "sequential order broken: after V2 the traversal goes backward toward V3 IS defect; "
        "CheckOrder detects non-linear topology (direction inversion) in wire traversal; "
        "FixReorder must reorient edges to restore consistency IS repair mechanism; "
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

# Vertices for rectangle
PV0 = (0.0, 0.0, 0.0)
PV1 = (8.0, 0.0, 0.0)
PV2 = (8.0, 6.0, 0.0)
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


# E0: V0->V1 (forward, normal)
ec_e0 = _line_sc(vV0, vV1, PV0, PV1, name="e0")

# E1: V1->V2 (forward, normal)
ec_e1 = _line_sc(vV1, vV2, PV1, PV2, name="e1")

# rev_e: EDGE_CURVE defined V2->V3 but inserted with .F. orientation
# This means in the EDGE_LOOP traversal the edge runs V3->V2 (backward) IS defect
ec_rev = _line_sc(vV2, vV3, PV2, PV3, name="rev_e")

# E3: V3->V0 (closing, forward)
ec_e3 = _line_sc(vV3, vV0, PV3, PV0, name="e3")

oe_e0  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e0.eid},.T.)")
oe_e1  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
# rev_e inserted with .F. — orientation reversal IS the defect
oe_rev = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_rev.eid},.F.)")
oe_e3  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_e0.eid},#{oe_e1.eid},#{oe_rev.eid},#{oe_e3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi242.stp")
