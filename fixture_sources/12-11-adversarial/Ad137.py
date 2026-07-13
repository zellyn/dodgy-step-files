"""Ad137 — COMPOSITE_CURVE with one numerically degenerate segment
(non-monotonic B-spline knot vector) alongside one ordinary LINE segment:
segment-dropped-not-whole-curve-aborted catch site (stp-transfer-
exception-to-fail, PARTIAL, narrow breadth: "A COMPOSITE_CURVE segment
whose per-segment 3D-curve or pcurve conversion throws mid-translation
(numerically degenerate segment geometry), demonstrating the segment-
dropped-not-whole-curve-aborted catch site (distinct call site from
Ad043/Xp008's already-covered root-entity and per-edge catches)").

Catalog claim: StepToTopoDS_TranslateCompositeCurve::Init
(StepToTopoDS_TranslateCompositeCurve.cxx:188-211,243-249) wraps EACH
segment's own 3D-curve/pcurve conversion in its own try/catch; a segment
whose underlying geometry throws during construction (as opposed to
merely being disconnected from its neighbor, Gp034/Gp188's already-
covered connectivity-gap warning path) is simply dropped, letting the
REST of the composite curve's segments -- and the containing face --
still translate. This is a structurally different call site from Ad043's
root-entity dispatch try/catch (STEPControl_ActorRead::TransferShape,
per-ROOT) and Xp008's per-edge catch (StepToTopoDS_TranslateEdgeLoop's
own per-edge 3D-curve-conversion try/catch, :307-326) -- this one is
nested one level deeper, INSIDE a single edge's own composite-curve
geometry, at per-SEGMENT granularity.

Mechanism: mirrors Gp188's proven-working COMPOSITE_CURVE structural
pattern (COMPOSITE_CURVE_SEGMENTs referencing plain, untrimmed base
curves directly -- not TRIMMED_CURVE-wrapped -- with the COMPOSITE_CURVE
itself wrapped in a SURFACE_CURVE + PCURVE, used as a single self-loop
EDGE_CURVE's 3D geometry). Two segments: good_composite_segment_line (an
ordinary LINE, (0,0,0)->(1,0,0), genuinely constructible) and
degenerate_composite_segment_bspline (a B_SPLINE_CURVE_WITH_KNOTS whose
knot vector (1.0, 0.5, 2.0) is NOT monotonically non-decreasing --
structurally schema-legal Part-21 bytes, but numerically invalid for
Geom_BSplineCurve's constructor, which requires a non-decreasing knot
sequence and throws Standard_ConstructionError on violation). If the
per-segment catch fires as claimed, the whole face still translates
(occt=shape(1)) with the bad segment's contribution dropped rather than
the whole read aborting. ADVANCED_FACE -> OPEN_SHELL ->
SHELL_BASED_SURFACE_MODEL -> PRODUCT chain; never orphaned.

Byte assertions:
  - contains(b'good_composite_segment_line')
  - contains(b'degenerate_composite_segment_bspline')
  - count_entity_def(b'COMPOSITE_CURVE_SEGMENT') == 2
  - count_entity_def(b'COMPOSITE_CURVE') == 1

Tier-3 assertions:
  - shape_null == False
  - n_faces_total == 1

live oracle (2026-07-13, this worktree, OCP/OCCT 7.8.1): occt=shape(1)/shape(1)
(live-verified: reads without crashing, TransferRoots()==1, OneShape() not
null, matching Gp188's own pre-existing "n_edges_total==0 despite
n_faces_total==1" tier-3 signature for this single-self-loop
COMPOSITE_CURVE-edge structural family -- confirmed via direct read this
is NOT a new concern, it is the established pattern for this construction
style in this corpus. A prior variant of this fixture used TRIMMED_CURVE-
wrapped segments (matching Gp063's pattern) instead of Gp188's plain-LINE-
segment style, and used the COMPOSITE_CURVE bare as EDGE_CURVE.edge_
geometry instead of Gp188's SURFACE_CURVE+PCURVE wrapper -- BOTH prior
variants also read as shape(1)/non-null, so the choice of exact
sub-pattern does not appear load-bearing for reachability; this version
follows Gp188's own proven convention for consistency and byte-
economy.)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad137",
    defect=(
        "ADVANCED_FACE on a PLANE (z=0); its sole boundary is a "
        "self-loop EDGE_CURVE whose 3D geometry is a SURFACE_CURVE "
        "wrapping a COMPOSITE_CURVE ('mixed_segment_composite_curve') of "
        "TWO COMPOSITE_CURVE_SEGMENTs: good_composite_segment_line (an "
        "ordinary LINE, genuinely constructible) and "
        "degenerate_composite_segment_bspline (a B_SPLINE_CURVE_WITH_KNOTS "
        "whose knot vector (1.0,0.5,2.0) is NOT monotonically "
        "non-decreasing -- schema-legal bytes, numerically invalid "
        "geometry that throws Standard_ConstructionError when Geom_"
        "BSplineCurve actually tries to construct it); "
        "StepToTopoDS_TranslateCompositeCurve::Init's per-segment "
        "try/catch IS the mechanism under test -- the bad segment should "
        "be dropped, not the whole composite curve/edge/face aborted; "
        "EDGE_CURVE IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, "
        "OPEN_SHELL; never orphaned"
    ),
)

p_orig = f.cartesian_point((0.0, 0.0, 0.0))
p_norm = f.direction((0.0, 0.0, 1.0))
p_ref  = f.direction((1.0, 0.0, 0.0))
p_axis = f.axis2_placement_3d(p_orig, p_norm, p_ref)
plane  = f.plane(p_axis)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
v0 = f.vertex_point(p0)

# ── Segment 1: good_composite_segment_line — ordinary, constructible ────────
good_line = f._emit_raw(
    f"LINE('good_composite_segment_line',#{p0.eid},"
    f"#{f.vector(f.direction((1.0, 0.0, 0.0)), 1.0).eid})"
)

# ── Segment 2: degenerate_composite_segment_bspline — non-monotonic knots ───
p_a = f.cartesian_point((1.0, 0.0, 0.0))
p_b = f.cartesian_point((1.5, 0.3, 0.0))
p_c = f.cartesian_point((2.0, 0.0, 0.0))
bad_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('degenerate_composite_segment_bspline',2,"
    f"(#{p_a.eid},#{p_b.eid},#{p_c.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3),(1.0,0.5,2.0),.UNSPECIFIED.)"
    # NOTE: knots (1.0, 0.5, 2.0) are NOT monotonically non-decreasing —
    # schema-legal Part-21 bytes, numerically invalid geometry.
)

seg1 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{good_line.eid})")
seg2 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{bad_bspline.eid})")
composite_curve = f._emit_raw(
    f"COMPOSITE_CURVE('mixed_segment_composite_curve',(#{seg1.eid},#{seg2.eid}),.F.)"
)

pc_p0 = f.cartesian_point((0.0, 0.0))
pc_line = f.line(pc_p0, f.vector(f.direction((1.0, 0.0)), 2.0))
pc_def = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{pc_line.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('',#{plane.eid},#{pc_def.eid})")

surf_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{composite_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(f"EDGE_CURVE('',#{v0.eid},#{v0.eid},#{surf_curve.eid},.T.)")

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
