"""Twi294 — Open chain of two arcs of the same circle (not yet closing to a
full circle) that should be fused into one arc (missing subvariant of
tkshh-same-curve-fragmented-edges, distinct from Twi089's collinear-LINE
case).

Catalog claim (occt-coverage/tkshhealing/problems.json,
tkshh-same-curve-fragmented-edges, subvariant "arcs of the same circle
fused into one arc (open chain)"): a chain of edges joined at a degree-2
vertex lies on the SAME geometric curve, so the interior vertex is
topologically unnecessary fragmentation. ShapeUpgrade_UnifySameDomain
validates co-curve geometry (here: literally the identical CIRCLE
entity — the strongest possible "same curve" signal, since both edges
reference the SAME #id, not merely two circles with coincident
parameters) and fuses the chain into a single arc edge. Twi089 already
covers the analogous LINE case (two collinear line segments); this
fixture covers the ARC case explicitly named as still missing in the
problem record's notes. The chain is deliberately left OPEN (spanning
90 degrees total, not the full 360) so this is distinct from Twi019's
closed-full-period-edge mechanism.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP (mirrors
Twi089's structure): two EDGE_CURVEs, BOTH referencing the identical
CIRCLE entity (radius 5, XY plane, centred at the origin), meeting at a
shared degree-2 VERTEX_POINT at angle 45 degrees that is not used by any
other wire/face — arc 1 spans 0-45 degrees, arc 2 spans 45-90 degrees,
together an open 90-degree chain (never closing to a full circle).
GEOMETRIC_CURVE_SET IS the model entity — OCC returns empty for this
container type (same convention as Twi089/Twi253).

Byte assertions:
  - contains(b'arc_chain_loop')
  - contains(b'mid_arc_vertex')
  - count_entity_def(b'EDGE_CURVE') == 2
  - count_entity_def(b'CIRCLE') == 1

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi294",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP 'arc_chain_loop'; exactly TWO "
        "EDGE_CURVEs, BOTH referencing the SAME CIRCLE entity (radius 5, centre "
        "origin, XY plane) — the strongest same-curve signal (identical entity, "
        "not just coincident parameters); "
        "e1: 0deg->45deg arc; e2: 45deg->90deg arc; "
        "shared VERTEX_POINT 'mid_arc_vertex' at 45deg — degree-2 vertex not used "
        "by any other face; chain is OPEN (90deg total, never closes to a full "
        "circle, distinct from Twi019's closed-edge mechanism); "
        "the midpoint vertex is topologically redundant: ShapeUpgrade_UnifySameDomain "
        "should fuse e1+e2 into one 90-degree arc edge; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

RADIUS = 5.0

def pt_at(deg):
    th = math.radians(deg)
    return (RADIUS * math.cos(th), RADIUS * math.sin(th), 0.0)

v_start = f.vertex_point(f.cartesian_point(pt_at(0.0)))
# Byte assertion: contains(b'mid_arc_vertex') — degree-2, unused-elsewhere vertex
v_mid = f.vertex_point(f.cartesian_point(pt_at(45.0)), name="mid_arc_vertex")
v_end = f.vertex_point(f.cartesian_point(pt_at(90.0)))

circ_orig = f.cartesian_point((0.0, 0.0, 0.0))
circ_zdir = f.direction((0.0, 0.0, 1.0))
circ_xdir = f.direction((1.0, 0.0, 0.0))
circ_plc = f.axis2_placement_3d(circ_orig, circ_zdir, circ_xdir)
# Single CIRCLE entity — byte assertion: count_entity_def(b'CIRCLE') == 1
circle = f._emit_raw(f"CIRCLE('',#{circ_plc.eid},{RADIUS:.10f})")

# e1: 0deg -> 45deg, on the shared CIRCLE
e1 = f._emit_raw(f"EDGE_CURVE('',#{v_start.eid},#{v_mid.eid},#{circle.eid},.T.)")
oe1 = f.oriented_edge(e1, True)

# e2: 45deg -> 90deg, SAME CIRCLE entity reference
e2 = f._emit_raw(f"EDGE_CURVE('',#{v_mid.eid},#{v_end.eid},#{circle.eid},.T.)")
oe2 = f.oriented_edge(e2, True)

# EDGE_LOOP 'arc_chain_loop' — byte assertion
loop = f._emit_raw(f"EDGE_LOOP('arc_chain_loop',(#{oe1.eid},#{oe2.eid}))")

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
