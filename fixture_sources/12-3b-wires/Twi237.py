"""Twi237 — ShapeFix_Wire.FixSmall edge-coalescing tolerance.

Catalog claim: Wire contains a segment smaller than the tolerance threshold.
FixSmall detects sub-tolerance edges and coalesces them into adjacent geometry,
requiring proper endpoint merging and curve reparametrization.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP representing a
triangular wire with one sub-tolerance micro-edge 'micro_e' of length 0.001
between two nearly-coincident vertices. The main triangle has legs of ~10 units
so the micro-edge (0.001) is far below any reasonable healing threshold.
FixSmall must detect 'micro_e' and coalesce it with the adjacent edge, merging
the nearly-coincident vertices IS the mechanism.

Byte assertions:
  - contains(b'micro_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi237",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP representing triangular wire on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "P0=(0,0,0), P0b=(0.001,0,0) — sub-tolerance gap of 0.001 IS the micro-edge; "
        "P1=(10,0,0), P2=(5,8,0) — normal triangle vertices; "
        "micro_e: LINE from P0 to P0b, length=0.001 — far below tolerance IS defect edge; "
        "adjacent edge E1 from P0b to P1 length=9.999 — coalescing target; "
        "FixSmall must detect micro_e, merge P0/P0b, reparametrize E1 IS mechanism; "
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
P0  = (0.0,    0.0, 0.0)   # start
P0b = (0.001,  0.0, 0.0)   # nearly-coincident with P0 — micro-edge endpoint
P1  = (10.0,   0.0, 0.0)   # normal vertex
P2  = (5.0,    8.0, 0.0)   # apex

vP0  = f.vertex_point(f.cartesian_point(P0))
vP0b = f.vertex_point(f.cartesian_point(P0b))
vP1  = f.vertex_point(f.cartesian_point(P1))
vP2  = f.vertex_point(f.cartesian_point(P2))


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


# micro_e: sub-tolerance edge P0->P0b (length=0.001)
ec_micro = _line_sc(vP0, vP0b, P0, P0b, name="micro_e")

# E1: P0b -> P1
ec_e1 = _line_sc(vP0b, vP1, P0b, P1, name="e1")

# E2: P1 -> P2
ec_e2 = _line_sc(vP1, vP2, P1, P2, name="e2")

# E3: P2 -> P0 (closing)
ec_e3 = _line_sc(vP2, vP0, P2, P0, name="e3")

oe_micro = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_micro.eid},.T.)")
oe_e1    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_micro.eid},#{oe_e1.eid},#{oe_e2.eid},#{oe_e3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi237.stp")
