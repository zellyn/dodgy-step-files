"""Ad138 — GEOMETRIC_CURVE_SET element whose curve construction throws is
caught per-element and skipped; the rest of the set still translates
(stp-transfer-exception-to-fail, PARTIAL — narrow breadth: the class cites
FOUR distinct catch boundaries and only three had a live fixture).

Catalog claim: StepToTopoDS_Builder::Init(GeometricSet)
(StepToTopoDS_Builder.cxx:700-709) wraps EACH GeometricSet element's own
`StepToGeom::MakeCurve` call in its own try/catch; an element whose
underlying geometry throws during construction is reported and skipped
(`res` stays null -> "Entity not mapped to TopoDS" warning at :781) and
the per-element loop simply continues, so the remaining elements of the
same set still land in the output compound.

This is the fourth and last of the class's cited catch boundaries and the
only one that had no live fixture: Ad043 covers the per-ROOT-entity catch
(STEPControl_ActorRead::TransferShape, :1414-1480), Xp008 the per-EDGE
catch inside a wire (StepToTopoDS_TranslateEdgeLoop::Init, :307-326), and
Ad137 the per-SEGMENT catch inside a composite curve
(StepToTopoDS_TranslateCompositeCurve::Init, :188-211,243-249). This one
is the per-ELEMENT catch inside a GeometricSet — a sibling call site in
StepToTopoDS_Builder, not nested inside any of the other three.

Mechanism: a GEOMETRIC_CURVE_SET (the shape-representation's own item —
the translation root, not an orphan) with exactly two elements, both
B_SPLINE_CURVE_WITH_KNOTS of identical structure and identical control
points, differing ONLY in the knot vector:
  - `good_bspline_element`  knots (0.0, 1.0)  — monotonically increasing
  - `throwing_bspline_element` knots (1.0, 0.5) — DECREASING, which
    Geom_BSplineCurve's constructor rejects with Standard_ConstructionError
The bytes are schema-legal Part-21 in both cases; only the numeric content
differs, so the A/B contrast isolates the throw exactly.

Byte assertions:
  - contains(b'good_bspline_element')
  - contains(b'throwing_bspline_element')
  - count_entity_def(b'B_SPLINE_CURVE_WITH_KNOTS') == 2
  - contains(b'GEOMETRIC_CURVE_SET')

Tier-3 assertions:
  - shape_null == False
  - n_edges_total == 1

live oracle (2026-07-31, this worktree, OCP/OCCT 7.8.1): see the catalog
entry's Expected-validation line. Live-verified: the transfer check list
carries exactly one FAIL, " Entity not mapped to TopoDS", attached to the
throwing element's entity number and to NO other entity, while the output
compound carries exactly one edge — the good element's. Perturbation
control: flipping the bad element's knots to (0.0, 1.0) (the good value,
one-token byte change) makes the FAIL disappear and the edge count go
1 -> 2, proving the fixture's observable is caused by the knot bytes and
not by the surrounding scaffold.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad138",
    defect=(
        "GEOMETRIC_CURVE_SET (the shape representation's own item, a real "
        "translation root) with TWO B_SPLINE_CURVE_WITH_KNOTS elements of "
        "identical structure differing only in their knot vector: "
        "'good_bspline_element' with monotonically increasing knots "
        "(0.0,1.0) and 'throwing_bspline_element' with DECREASING knots "
        "(1.0,0.5) which Geom_BSplineCurve's constructor rejects by "
        "raising Standard_ConstructionError; the per-element try/catch "
        "around the geometric-set element's own curve construction IS the "
        "mechanism under test -- the throwing element must be logged and "
        "skipped while the good element still produces its edge in the "
        "output compound; both curves ARE elements of the root "
        "GEOMETRIC_CURVE_SET, never orphaned"
    ),
)

# ── Element 1: good_bspline_element — knots (0.0, 1.0), constructible ───────
g0 = f.cartesian_point((0.0, 0.0, 0.0))
g1 = f.cartesian_point((1.0, 0.0, 0.0))
good_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('good_bspline_element',1,"
    f"(#{g0.eid},#{g1.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(2,2),(0.0,1.0),.UNSPECIFIED.)"
)

# ── Element 2: throwing_bspline_element — knots (1.0, 0.5), DECREASING ──────
# Identical in every other respect to the good element above. A decreasing
# knot sequence is schema-legal Part-21 bytes but numerically invalid:
# Geom_BSplineCurve's constructor raises Standard_ConstructionError.
b0 = f.cartesian_point((0.0, 1.0, 0.0))
b1 = f.cartesian_point((1.0, 1.0, 0.0))
throwing_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('throwing_bspline_element',1,"
    f"(#{b0.eid},#{b1.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(2,2),(1.0,0.5),.UNSPECIFIED.)"
)

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('ad138_element_catch_set',"
    f"(#{good_bspline.eid},#{throwing_bspline.eid}))"
)
f.add_product_chain(gcs)
