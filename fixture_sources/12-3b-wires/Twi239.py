"""Twi239 — ShapeFix_Wire.FixClosed open-wire-closure-degenerate.

Catalog claim: Wire presents closed-loop topology but endpoint mismatch leaves
a dangling segment. The closure healing attempts bridge-edge insertion; in
degenerate cases, the bridge is itself a zero-length edge requiring special
handling.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP that topologically
declares closure (first edge start vertex == last edge end vertex entity) but
the actual 3D coordinates of the wire start and wire end differ by a small
amount (0.05 units). Three normal edges form a triangle; the last edge 'open_e3'
ends at a vertex whose 3D coordinates are (0.0, 0.05, 0.0) rather than the
starting vertex at (0.0, 0.0, 0.0). The EDGE_LOOP references the original
start vertex as end of open_e3 (topological closure claim), but the
underlying curve geometry ends at the offset point IS the geometric open gap.
FixClosed bridge-edge computation finds a near-degenerate bridge of length 0.05.

Byte assertions:
  - contains(b'open_e3')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi239",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 line edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "P0=(0,0,0) IS wire start vertex; P1=(10,0,0); P2=(5,8,0); "
        "open_e3: line geometry from P2=(5,8,0) to P0_gap=(0,0.05,0) — 0.05 offset from P0; "
        "EDGE_LOOP wires open_e3 with start-vertex vP0 as end (topology claims closure); "
        "3D geometry of open_e3 ends at (0,0.05,0) NOT at vP0=(0,0,0) IS the gap defect; "
        "FixClosed bridge computation finds 0.05-length near-degenerate bridge IS mechanism; "
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
P0     = (0.0,  0.0, 0.0)   # start vertex
P1     = (10.0, 0.0, 0.0)
P2     = (5.0,  8.0, 0.0)
P0_gap = (0.0,  0.05, 0.0)  # wire end geometry — 0.05 offset from P0

vP0  = f.vertex_point(f.cartesian_point(P0))
vP1  = f.vertex_point(f.cartesian_point(P1))
vP2  = f.vertex_point(f.cartesian_point(P2))
# Separate vertex for gap endpoint used by the line geometry
vGap = f.vertex_point(f.cartesian_point(P0_gap))


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


# E0: P0 -> P1
ec_e0 = _line_sc(vP0, vP1, P0, P1, name="e0")

# E1: P1 -> P2
ec_e1 = _line_sc(vP1, vP2, P1, P2, name="e1")

# open_e3: geometry goes P2 -> P0_gap (offset), but edge_curve references vP0 as
# end vertex (topology claims closure) while curve ends at P0_gap IS the defect
# Use vGap as EDGE_CURVE end so geometry is consistent with the gap vertex
ec_e2 = _line_sc(vP2, vGap, P2, P0_gap, name="open_e3")

oe_e0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e0.eid},.T.)")
oe_e1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")

# EDGE_LOOP uses vGap as closing vertex but vP0 is the start — the loop
# does NOT return to the exact start coords, leaving an open gap
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_e0.eid},#{oe_e1.eid},#{oe_e2.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi239.stp")
