"""Twi299 — Whole-circle edge whose VERTEX_POINT sits at the circle's own
CENTER (on the curve's axis, off the curve, with no unique nearest point):
point-projection-onto-3D-curve failure (stp-makeedge-validity-fallback,
PARTIAL, missing subvariant "point projection onto the 3D curve fails at
all").

Catalog claim: Building a proper OCCT edge from the translated 3D curve
and its vertices (BRepLib_MakeEdge, called from
StepToTopoDS_TranslateEdge::MakeFromCurve3D) requires projecting each
vertex's 3D point onto the curve to determine its parameter, when no
explicit trim parameter is given. For a point exactly ON the curve's axis
of symmetry (a circle's center), EVERY point on the circle is equidistant
-- there is no unique nearest point, so the projection is ambiguous/fails
outright, distinct from Bo030's off-curve-but-with-a-well-defined-nearest-
point case and Twi086's zero-length-line case. OCCT still force-builds a
raw edge directly from curve+vertices+parameters (bypassing the failed
projection) rather than aborting, per DecodeMakeEdgeError's classification
(StepToTopoDS_TranslateEdge.cxx:70-131) and MakeFromCurve3D's fallback
call (:483-489).

Mechanism: a PLANE face (z=0) whose FACE_OUTER_BOUND is a single
whole-circle EDGE_CURVE (radius 1, centered at origin) -- the standard
"one edge, same vertex both ends" convention this corpus already uses for
whole-circle loops (Twi017/Twi035/Gp013's arcs) -- EXCEPT the shared
VERTEX_POINT is placed at (0,0,0), the circle's OWN CENTER (on its axis,
distance 1 from every point of the circle), rather than at any point ON
the circle (e.g. (1,0,0)). BRepLib_MakeEdge's vertex-to-curve-parameter
projection has no unique solution for this input (a genuine, not merely
off-plane, projection failure -- the ambiguity is rotational-symmetric
around the whole curve, not just "far away"). ADVANCED_FACE ->
OPEN_SHELL -> SHELL_BASED_SURFACE_MODEL -> PRODUCT chain; never orphaned.

Byte assertions:
  - contains(b'off_curve_center_vertex')
  - count_entity_def(b'CIRCLE') == 1
  - count_entity_def(b'VERTEX_POINT') == 1

Tier-3 assertions:
  - face[0].surface_type == "plane"

live oracle (2026-07-13, this worktree, OCP/OCCT 7.8.1): occt=shape(1)/shape(1)
(live-verified: reads without crashing, brepcheck.valid=True; edge[0]'s OWN
tolerance stays default 1e-7, but BOTH vertex tolerances are blown out to
1.000001 -- essentially the circle's radius -- confirming BRepLib_MakeEdge's
fallback force-built the edge directly from curve+vertex+params rather than
aborting, and the vertex-tolerance-update pass (BRepLib::UpdateInnerTolerances,
Bo030's own citation) had to widen the VERTEX tolerance to cover the true
1.0-unit gap between the declared off-curve vertex and the curve it
nominally bounds -- the same "force-built anyway, tolerance absorbs the
lie" evidentiary pattern as Bo030, now for the point-projection-fails
subvariant specifically rather than Bo030's projected-point-disagreement
subvariant.)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi299",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with one whole-circle "
        "EDGE_CURVE (radius 1, centered at origin); off_curve_center_vertex "
        "(the SAME VERTEX_POINT at both edge_start and edge_end) sits at "
        "(0,0,0) -- the circle's own center, on its axis of symmetry, "
        "equidistant (radius 1) from every point of the circle, so there "
        "is NO unique nearest point for BRepLib_MakeEdge's vertex-to-curve "
        "projection to find; point-projection-onto-3D-curve failure IS "
        "the mechanism (DecodeMakeEdgeError / MakeFromCurve3D fallback "
        "force-build); EDGE_LOOP IS wired into FACE_OUTER_BOUND, "
        "ADVANCED_FACE, OPEN_SHELL; never orphaned"
    ),
)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

circ_plc = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)), zdir, xdir)
circ = f._emit_raw(f"CIRCLE('',#{circ_plc.eid},1.0)")

# The vertex sits at the circle's CENTER — off the curve, ambiguous nearest point.
v_center = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)), name="off_curve_center_vertex")

edge = f._emit_raw(f"EDGE_CURVE('',#{v_center.eid},#{v_center.eid},#{circ.eid},.T.)")
oe = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{edge.eid},.T.)")
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe.eid}))")

fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
