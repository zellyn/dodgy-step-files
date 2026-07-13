"""Twi293 — Full-period closed edge nested inside a TRIMMED_CURVE wrapper:
the closed-curve split must fall back to the nearest knot on the true basis
curve underneath the wrapper (missing subvariant of
tkshh-closed-edge-full-period-unsplit, distinct from Twi019's bare-CIRCLE
case).

Catalog claim (occt-coverage/tkshhealing/problems.json,
tkshh-closed-edge-full-period-unsplit, subvariant "Parameter correction
nested inside Offset/Trimmed curve wrappers falls back to nearest
true-basis-curve knot" — evidence: static CorrectParameter() in
ShapeAnalysis_TransferParametersProj.cxx). Twi019 demonstrates the
full-period-edge-needs-splitting defect directly on a bare CIRCLE
EDGE_CURVE. Real STEP exporters sometimes wrap the periodic basis curve in
an intermediate TRIMMED_CURVE entity (e.g. re-exporting a curve that was
itself already a trimmed sub-segment of a longer periodic definition) —
when the closed-curve split logic needs to snap a duplicated/ambiguous
transferred knot toward the true closure point, it cannot read knot
structure off the TRIMMED_CURVE wrapper itself (a TRIMMED_CURVE has no
independent knot vector) and must fall back to the BASIS_CURVE underneath
it. This fixture's defect edge references a TRIMMED_CURVE(trim 0..2*pi)
whose basis_curve is the full-period CIRCLE, rather than referencing the
CIRCLE directly.

Mechanism IS the single-edge closed EDGE_LOOP on a PLANE face (Twi019/
Twi017's "closed curve is the entire wire" pattern): one EDGE_CURVE whose
`edge_geometry` is a TRIMMED_CURVE (trim_1=PARAMETER_VALUE(0.0),
trim_2=PARAMETER_VALUE(2*pi), sense_agreement=.T.) wrapping a full-period
CIRCLE basis_curve, start vertex == end vertex — the wrapper-nested
full-period edge IS the mechanism. The edge IS referenced by the wire's
EDGE_LOOP, which IS referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE
in an OPEN_SHELL; never orphaned.

Byte assertions:
  - count_entity_def(b'TRIMMED_CURVE') == 1
  - count_entity_def(b'CIRCLE') == 1
  - contains(b'wrapped_closed_edge')

Tier-3 assertions:
  - face[0].surface_type == "plane"
  - n_edges_total == 0
  - n_vertices_total == 0
  - brepcheck.valid == True

Live finding (stronger than the docstring's original hypothesis): OCCT
7.8.1 does NOT fall back to the basis CIRCLE's knot structure at all for
this wrapper shape — it fails to translate the TRIMMED_CURVE-wrapped
full-period EDGE_CURVE outright (tested both with a PARAMETER_VALUE(0,
2*pi) trim and a CARTESIAN_POINT same-point-both-ends trim; both fail
identically), silently drops the entire EDGE_LOOP/FACE_OUTER_BOUND, and
falls through to STEP's "closed surface with no outer bound" rule
(Twi091's pattern): the ADVANCED_FACE is read as an UNBOUNDED natural
plane (n_edges_total==0, n_vertices_total==0, face area ~8e100,
brepcheck.valid==True regardless). This is a harsher failure mode than
Twi019's bare-CIRCLE case (which loads the single closed edge as-is,
unsplit, with brepcheck.valid==False) — confirming the wrapper genuinely
defeats the closed-curve-split path rather than merely leaving it
unsplit, i.e. there is no true-basis-curve fallback for this shape at
all in this OCCT build.

live oracle: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi293",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE; FACE_OUTER_BOUND "
        "references an EDGE_LOOP whose sole EDGE_CURVE 'wrapped_closed_edge' has "
        "start vertex == end vertex (full-period, Twi019's core pattern) but its "
        "curve slot references a TRIMMED_CURVE(trim_1=PARAMETER_VALUE(0.0), "
        "trim_2=PARAMETER_VALUE(2*pi), .T., .PARAMETER.) wrapping a plain "
        "full-period CIRCLE basis_curve — NOT the CIRCLE directly (Twi019's "
        "pattern); the closed-curve split/periodic-knot-correction logic must "
        "look past the TRIMMED_CURVE wrapper (which carries no independent knot "
        "structure of its own) to the true basis CIRCLE underneath to compute "
        "the seam split point; "
        "defect edge IS wired into EDGE_LOOP, FACE_OUTER_BOUND, ADVANCED_FACE, "
        "OPEN_SHELL; never orphaned"
    ),
)

RADIUS = 2.5
TWO_PI = 2.0 * math.pi

v_seam = f.vertex_point(f.cartesian_point((RADIUS, 0.0, 0.0)))

circ_orig = f.cartesian_point((0.0, 0.0, 0.0))
circ_zdir = f.direction((0.0, 0.0, 1.0))
circ_xdir = f.direction((1.0, 0.0, 0.0))
circ_plc = f.axis2_placement_3d(circ_orig, circ_zdir, circ_xdir)
circle = f._emit_raw(f"CIRCLE('',#{circ_plc.eid},{RADIUS:.10f})")

# TRIMMED_CURVE wrapper: full [0, 2*pi] trim of the closed CIRCLE basis curve.
trimmed = f._emit_raw(
    f"TRIMMED_CURVE('',#{circle.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({TWO_PI:.10f})),.T.,.PARAMETER.)"
)

# Full-period edge: start==end vertex, curve is the TRIMMED_CURVE wrapper.
wrapped_edge = f._emit_raw(
    f"EDGE_CURVE('wrapped_closed_edge',#{v_seam.eid},#{v_seam.eid},#{trimmed.eid},.T.)"
)
oe = f.oriented_edge(wrapped_edge, True)

loop = f.edge_loop([oe])
fob = f.face_outer_bound(loop)

plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_zdir = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_plc = f.axis2_placement_3d(plane_orig, plane_zdir, plane_xdir)
plane = f.plane(plane_plc)

face = f.advanced_face([fob], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
