"""Twi298 — Two NON-ADJACENT edges of one wire share a large (>50%)
collinear overlap on the same underlying LINE, forcing the 3-edge
reconstruction path (missing subvariant of
tkshh-wire-nonadjacent-edges-intersect, distinct from Twi063's small
(<50%) 2-edge trim/split overlap).

Catalog claim (occt-coverage/tkshhealing/problems.json,
tkshh-wire-nonadjacent-edges-intersect, subvariant "collinear overlap over
a large (>50%) range (3-edge reconstruction sharing the overlap segment)"
— evidence: ShapeFix_IntersectionTool::FixSelfIntersectWire,
ShapeFix_IntersectionTool.cxx:1202-1456). Twi063 already covers a SMALL
(<50%) collinear overlap between two edges of one EDGE_LOOP (edge_a [0,5],
edge_b [2,7], overlap [2,5] = 60% of the loop's *own* two edges but
reached via a degenerate quasi-adjacent connector in that fixture's wire
ordering, matching the small-overlap 2-edge cut/trim path at
ShapeFix_IntersectionTool.cxx:1163-1196). This fixture instead makes the
overlap large (90% of each edge's own length) AND puts three ordinary
closure edges between edge_a and edge_b on EACH side of the cyclic wire
(genuinely non-adjacent, not merely separated by one degenerate connector)
— forcing the large-overlap branch, which must reconstruct THREE edges
sharing the overlap segment (the pre-overlap remainder of one edge, the
shared overlap segment itself, and the post-overlap remainder of the
other) rather than a simple two-edge cut.

Mechanism IS the ADVANCED_FACE on a PLANE whose EDGE_LOOP is: edge_a
(0,0,0)->(10,0,0), a 3-edge detour up and over to (11,0,0), edge_b
REVERSED (11,0,0)->(1,0,0) [edge_b itself runs (1,0,0)->(11,0,0), the
same underlying LINE as edge_a], a 3-edge detour down and back to
(0,0,0). edge_a and edge_b's interiors overlap over [1,10] — 9 units out
of each edge's own 10-unit length, i.e. 90% — while being separated by
three ordinary edges on both sides of the wire, genuinely non-adjacent.
The overlapping pair IS referenced by the wire's EDGE_LOOP, which IS
referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL;
never orphaned.

Byte assertions:
  - contains(b'large_overlap_edge_a')
  - contains(b'large_overlap_edge_b')
  - count_entity_def(b'EDGE_CURVE') == 8

Tier-3 assertions:
  - face[0].surface_type == "plane"
  - n_edges_total >= 9
  - n_vertices_total >= 10
  - brepcheck.valid == False

Live finding: OCCT 7.8.1 does NOT collapse the pair back down to a clean
merged wire the way it does for Twi063's small (60%-of-declared, but
quasi-adjacent-via-degenerate-connector) overlap, where n_edges_total
comes back as 5 (down from 6 declared) with brepcheck.valid==True. Here,
with the overlap genuinely large (90%) AND the two edges genuinely
non-adjacent, OCCT instead SPLITS both edge_a and edge_b at the junction
parameters (1 and 10) -- n_edges_total comes back as 10 (up from 8
declared: two ~1-unit remainder edges plus two ~9-unit segments spanning
the shared [1,10] overlap, kept as separate coincident edges rather than
merged into one shared edge) -- and brepcheck.valid comes back False (the
duplicated overlap segments leave the result topologically inconsistent).
This is a clearly different, and clearly WORSE, outcome than Twi063's,
confirming a distinct handling path is exercised for the large/
non-adjacent case.

live oracle: occt=shape(1)/shape(1) gmsh=shape(19) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi298",
    defect=(
        "ADVANCED_FACE on a PLANE; EDGE_LOOP with 8 EDGE_CURVEs; "
        "'large_overlap_edge_a' runs (0,0,0)->(10,0,0) along the X-axis (length 10); "
        "'large_overlap_edge_b' runs (1,0,0)->(11,0,0) along the SAME X-axis "
        "(length 10); their interiors overlap over [1,10] -- 9 out of each "
        "edge's own 10-unit length, i.e. 90%, well above the 50% large-overlap "
        "threshold; "
        "edge_a and edge_b are separated by THREE ordinary closure edges on "
        "EACH side of the cyclic wire (an up-across-down detour to (11,0,0) on "
        "one side, a down-across-up detour back to (0,0,0) on the other) -- "
        "genuinely non-adjacent, not merely separated by one degenerate "
        "connector (Twi063's pattern); "
        "ShapeFix_IntersectionTool::FixSelfIntersectWire must reconstruct THREE "
        "edges sharing the overlap segment (pre-overlap remainder, shared "
        "overlap segment, post-overlap remainder) rather than a simple two-edge "
        "cut; "
        "the overlapping pair IS wired into EDGE_LOOP, FACE_OUTER_BOUND, "
        "ADVANCED_FACE, OPEN_SHELL; never orphaned"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane = f.plane(pl_plc)

# ── Vertices for the two large-overlap collinear edges ───────────────────────
v_a0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_a1 = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0)))
v_b0 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
v_b1 = f.vertex_point(f.cartesian_point((11.0, 0.0, 0.0)))

# edge_a: (0,0,0) -> (10,0,0)
edge_a = f._emit_raw(
    f"EDGE_CURVE('large_overlap_edge_a',#{v_a0.eid},#{v_a1.eid},"
    f"#{f.line(f.cartesian_point((0.0,0.0,0.0)), f.vector(f.direction((1.0,0.0,0.0)),10.0)).eid},.T.)"
)
oe_a = f.oriented_edge(edge_a, True)

# edge_b: (1,0,0) -> (11,0,0) -- SAME underlying line, 90% overlap with edge_a
edge_b = f._emit_raw(
    f"EDGE_CURVE('large_overlap_edge_b',#{v_b0.eid},#{v_b1.eid},"
    f"#{f.line(f.cartesian_point((1.0,0.0,0.0)), f.vector(f.direction((1.0,0.0,0.0)),10.0)).eid},.T.)"
)

# ── Top detour: v_a1(10,0,0) -> (10,3,0) -> (11,3,0) -> v_b1(11,0,0) ─────────
v_top1 = f.vertex_point(f.cartesian_point((10.0, 3.0, 0.0)))
v_top2 = f.vertex_point(f.cartesian_point((11.0, 3.0, 0.0)))

e_up = f.edge_curve(v_a1, v_top1,
                     f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                            f.vector(f.direction((0.0, 1.0, 0.0)), 3.0)))
e_across_top = f.edge_curve(v_top1, v_top2,
                             f.line(f.cartesian_point((10.0, 3.0, 0.0)),
                                    f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
e_down = f.edge_curve(v_top2, v_b1,
                       f.line(f.cartesian_point((11.0, 3.0, 0.0)),
                              f.vector(f.direction((0.0, -1.0, 0.0)), 3.0)))

# ── Bottom detour: v_b0(1,0,0) -> (1,-2,0) -> (0,-2,0) -> v_a0(0,0,0) ────────
v_bot1 = f.vertex_point(f.cartesian_point((1.0, -2.0, 0.0)))
v_bot2 = f.vertex_point(f.cartesian_point((0.0, -2.0, 0.0)))

e_down2 = f.edge_curve(v_b0, v_bot1,
                        f.line(f.cartesian_point((1.0, 0.0, 0.0)),
                               f.vector(f.direction((0.0, -1.0, 0.0)), 2.0)))
e_across_bot = f.edge_curve(v_bot1, v_bot2,
                             f.line(f.cartesian_point((1.0, -2.0, 0.0)),
                                    f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_up2 = f.edge_curve(v_bot2, v_a0,
                      f.line(f.cartesian_point((0.0, -2.0, 0.0)),
                             f.vector(f.direction((0.0, 1.0, 0.0)), 2.0)))

# ── EDGE_LOOP: a -> up -> across_top -> down -> b(reversed) -> down2 ->
#    across_bot -> up2 -> (closes back to a's start) ─────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_a.eid},"
    f"#{f.oriented_edge(e_up, True).eid},"
    f"#{f.oriented_edge(e_across_top, True).eid},"
    f"#{f.oriented_edge(e_down, True).eid},"
    f"#{f.oriented_edge(edge_b, False).eid},"
    f"#{f.oriented_edge(e_down2, True).eid},"
    f"#{f.oriented_edge(e_across_bot, True).eid},"
    f"#{f.oriented_edge(e_up2, True).eid}))"
)

fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
