"""Gp195 — COMPOSITE_CURVE whose segments are listed out of connected order,
in a configuration where the reorder repair is actually observable
(stp-compcurve-reorder, PARTIAL: "the reorder-repair mechanism (FixReorder)
cannot be observed actually firing ... Kept PARTIAL, not COVERED, pending a
config where COMPOSITE_CURVE wires actually translate to a bounded wire").

Catalog claim: StepToTopoDS_TranslateCompositeCurve::Init
(StepToTopoDS_TranslateCompositeCurve.cxx:265-274) runs `sfw->FixReorder()`
over the segments it collected and, when `StatusReorder(ShapeExtend_DONE)`
comes back set, logs "Segments were disordered; fixed" -- i.e. it detects
and algorithmically reorders segments given out of connected sequence
rather than assembling a disjoint wire in list order.

Why Gp176 could not show it: Gp176 hands its COMPOSITE_CURVE to an
EDGE_CURVE as `edge_geometry`, which routes through
StepToTopoDS_TranslateEdge and `StepToGeom::MakeCurve` -- a path that
never constructs a TranslateCompositeCurve at all (live check on Gp176
shows " Make Geom_Curve (3D) failed" / "Could not convert a curve", and
no reorder message, in both segment orders). The per-segment wire
assembly (and therefore FixReorder) is only reached from
StepToTopoDS_Builder::Init(GeometricSet) (:677-698), i.e. when the
COMPOSITE_CURVE is itself an ELEMENT of a GEOMETRIC_CURVE_SET.

Mechanism: this fixture puts the COMPOSITE_CURVE where that call site can
see it -- as the sole element of the shape representation's own
GEOMETRIC_CURVE_SET -- and gives it four genuinely BOUNDED segments (all
degree-1 B_SPLINE_CURVE_WITH_KNOTS with finite [0,1] parameter domains, so
each yields a real finite edge rather than the infinite-parameter segments
that make the assembled wire unusable). The four segments trace the unit
square edge-by-edge, but `composite_curve_scrambled_order` lists them
A, C, B, D -- with C (top edge) sitting between A (bottom) and B (right),
a permutation that is neither the identity nor a cyclic rotation of the
connected sequence, so the disorder cannot be dismissed as a mere choice
of starting point on a closed wire.

Byte assertions:
  - contains(b'composite_curve_scrambled_order')
  - contains(b'seg_a_bottom')
  - contains(b'seg_c_top')
  - count_entity_def(b'COMPOSITE_CURVE_SEGMENT') == 4
  - contains(b'GEOMETRIC_CURVE_SET')

Tier-3 assertions:
  - shape_null == False
  - n_edges_total == 4

live oracle (2026-07-31, this worktree, OCP/OCCT 7.8.1): see the catalog
entry's Expected-validation line. Live-verified: the transfer check list
carries exactly one message, the WARNING "Segments were disordered; fixed"
-- the literal string emitted at :273 when `StatusReorder(ShapeExtend_DONE)`
is set -- and the transfer yields ONE wire of 4 edges (8 raw vertices),
i.e. the segments were assembled into a single wire despite the list order.

Perturbation control (byte-level A/B): re-listing the same four unchanged
segment entities in their connected order A, B, C, D -- a single-token
edit to the COMPOSITE_CURVE's segment list, nothing else -- makes the
"Segments were disordered; fixed" warning disappear entirely while the
resulting shape is byte-for-byte the same topology (1 wire, 4 edges, 8
vertices, zero check messages). The message is therefore caused by the
segment ORDER and nothing else -- which is exactly what Gp176's own
control could not establish, because in Gp176's configuration both orders
produced the identical (empty) signature.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp195",
    defect=(
        "GEOMETRIC_CURVE_SET (the shape representation's own item, a real "
        "translation root) whose sole element is "
        "'composite_curve_scrambled_order', a COMPOSITE_CURVE of FOUR "
        "COMPOSITE_CURVE_SEGMENTs tracing the unit square "
        "(seg_a_bottom, seg_b_right, seg_c_top, seg_d_left, each a "
        "degree-1 B_SPLINE_CURVE_WITH_KNOTS with a finite [0,1] domain so "
        "every segment yields a real bounded edge) but LISTED in the order "
        "A, C, B, D -- successive entries in the list do not follow on from "
        "one another, and the permutation is neither the identity nor a "
        "cyclic rotation. The segment-reordering pass that runs over the "
        "collected segments before the wire is assembled IS the mechanism "
        "under test; the COMPOSITE_CURVE is an element of the root "
        "GEOMETRIC_CURVE_SET, the one call site that reaches that pass, "
        "never orphaned"
    ),
)


def bounded_segment(p0, p1, name):
    """Degree-1 B_SPLINE_CURVE_WITH_KNOTS from p0 to p1: a genuinely
    BOUNDED curve with a finite [0,1] parameter domain, so the segment
    yields a real finite edge (unlike a bare LINE, whose infinite
    parameter range makes the assembled wire unusable)."""
    a = f.cartesian_point(p0)
    b = f.cartesian_point(p1)
    return f._emit_raw(
        f"B_SPLINE_CURVE_WITH_KNOTS('{name}',1,(#{a.eid},#{b.eid}),"
        f".UNSPECIFIED.,.F.,.F.,(2,2),(0.0,1.0),.UNSPECIFIED.)"
    )


# ── The unit square, edge by edge, in CONNECTED sequence A -> B -> C -> D ──
crv_a = bounded_segment((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), "seg_a_bottom")
crv_b = bounded_segment((1.0, 0.0, 0.0), (1.0, 1.0, 0.0), "seg_b_right")
crv_c = bounded_segment((1.0, 1.0, 0.0), (0.0, 1.0, 0.0), "seg_c_top")
crv_d = bounded_segment((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), "seg_d_left")

seg_a = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{crv_a.eid})")
seg_b = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{crv_b.eid})")
seg_c = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{crv_c.eid})")
seg_d = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{crv_d.eid})")

# ── THE DEFECT: segments listed A, C, B, D -- C sits between A and B ───────
composite = f._emit_raw(
    f"COMPOSITE_CURVE('composite_curve_scrambled_order',"
    f"(#{seg_a.eid},#{seg_c.eid},#{seg_b.eid},#{seg_d.eid}),.F.)"
)

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('gp195_composite_set',(#{composite.eid}))"
)
f.add_product_chain(gcs)
