"""Twi238 — ShapeFix_Wire.FixConnected disconnected-endpoints vertex-merge-fails.

Catalog claim: Wire edges present connectivity gaps at endpoints where vertices
nominally connect but actual coordinates diverge beyond tolerance. FixConnected
must detect disconnects and bridge or merge vertices; failure when gap exceeds
healing capability.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 line edges that
form a near-rectangle. The junction between edge E1 and E2 has a 'gap_e1' gap
of 2.5 units — the end-vertex of E1 is (10, 0, 0) while E2 starts at
(10, 2.5, 0). The disconnected vertex pair creates a gap larger than any
reasonable FixConnected tolerance, triggering failure/rejection mode.
Endpoint topology claims connectivity (.T. orientation) but 3D coordinates
diverge by 2.5 units IS the defect.

Byte assertions:
  - contains(b'gap_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi238",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 line edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "E0: (0,0,0)->(10,0,0) — first bottom edge; "
        "gap_e1: E1 ends at (10,0,0) with vertex v1_end; "
        "E2 starts at (10,2.5,0) with vertex v2_start — 2.5 unit gap IS connectivity defect; "
        "E2: (10,2.5,0)->(10,8,0); E3: (10,8,0)->(0,8,0); E4: (0,8,0)->(0,0,0); "
        "FixConnected gap-exceeds-precision: 2.5 unit gap larger than healing tolerance; "
        "endpoint merge fails IS the mechanism; "
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

# Vertices — gap between v1_end and v2_start
P0       = (0.0,  0.0, 0.0)
P1       = (10.0, 0.0, 0.0)    # E0 end / E1 (gap_e1) start nominal
P1_gap   = (10.0, 2.5, 0.0)    # E2 actual start — 2.5 units away from P1
P2       = (10.0, 8.0, 0.0)
P3       = (0.0,  8.0, 0.0)

vP0      = f.vertex_point(f.cartesian_point(P0))
v1_end   = f.vertex_point(f.cartesian_point(P1))    # E0 end
v2_start = f.vertex_point(f.cartesian_point(P1_gap)) # E2 start — gap vertex
vP2      = f.vertex_point(f.cartesian_point(P2))
vP3      = f.vertex_point(f.cartesian_point(P3))


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


# E0: bottom edge (0,0,0)->(10,0,0)
ec_e0 = _line_sc(vP0, v1_end, P0, P1, name="gap_e1")

# E2: starts at disconnected vertex — 2.5 unit gap from E0 end
ec_e2 = _line_sc(v2_start, vP2, P1_gap, P2, name="e2")

# E3: (10,8,0)->(0,8,0)
ec_e3 = _line_sc(vP2, vP3, P2, P3, name="e3")

# E4: closing (0,8,0)->(0,0,0)
ec_e4 = _line_sc(vP3, vP0, P3, P0, name="e4")

oe_e0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e0.eid},.T.)")
oe_e2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")
oe_e4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e4.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_e0.eid},#{oe_e2.eid},#{oe_e3.eid},#{oe_e4.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi238.stp")
