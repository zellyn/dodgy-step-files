"""Twi278 — AP242 Ed.3 length-constrained curve/topology triad (E07 + E09 + E10) dropped by Ed.2/AP214 readers.

Catalog claim: STEP AP242 Edition 3 file with a single planar face and a
straight B-spline edge whose length-invariant is layered via three
Ed.3 length-constraint entities all pointed at the same curve/edge:
  (a) `BOUNDED_CURVE_WITH_LENGTH('bcwl',#bspline_curve,POSITIVE_LENGTH_MEASURE(1.0))`
      — length-invariant on the underlying `B_SPLINE_CURVE_WITH_KNOTS`;
  (b) `EDGE_BOUNDED_CURVE_WITH_LENGTH('ebcwl',#edge_curve,POSITIVE_LENGTH_MEASURE(1.0))`
      — length-invariant on the corresponding `EDGE_CURVE`;
  (c) `EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT('ebtrwlc',(#edge_curve),POSITIVE_LENGTH_MEASURE(1.0))`
      — topological-representation-level constraint bundling the edges.

The file header declares the AP242 Ed.3 OID (`{1 0 10303 442 4 1 4}`)
with schema name `AUTOMOTIVE_DESIGN`.

Expected:
- Geometry loads under any reader (single planar face with a
  polyline-derived quad boundary and a co-present B-spline edge).
- Under AP242 Ed.3 readers, all three constraint entities resolve and
  expose the length invariant at curve, edge, and topology-representation
  levels.
- Under AP242 Ed.2 / AP214 readers, all three entities produce a `Void`
  transfer status: curve geometry still loads but the length-invariant
  is silently absent — a wire-harness routing / gasket-length application
  would fail to enforce the constraint.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html
(AP242 Ed.3 21-new-entities list, §4.4 — `BOUNDED_CURVE_WITH_LENGTH`
E07, `EDGE_BOUNDED_CURVE_WITH_LENGTH` E10,
`EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT` E09).
B4 wave-8 DEF-VV. Confidence: MEDIUM — three distinct Ed.3 entities
layered on the same edge to demonstrate that all three drop together.

Byte assertions:
  contains(b'BOUNDED_CURVE_WITH_LENGTH')
  contains(b'EDGE_BOUNDED_CURVE_WITH_LENGTH')
  contains(b'EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT')
  contains(b'POSITIVE_LENGTH_MEASURE')
  contains(b'10303 442 4 1 4')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi278",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: single planar 1x1 mm face plus a co-present straight "
        "B_SPLINE_CURVE_WITH_KNOTS edge (from (0,0,0) to (1,0,0), degree 1); "
        "three Ed.3 length-constraint entities point at that curve/edge — "
        "(a) BOUNDED_CURVE_WITH_LENGTH on the B-spline curve, "
        "(b) EDGE_BOUNDED_CURVE_WITH_LENGTH on the EDGE_CURVE, "
        "(c) EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT bundling "
        "the edges at the topological-representation level (AP242 Ed.3 §4.4, three "
        "of 21 new Ed.3 entities); header OID = {1 0 10303 442 4 1 4}; Ed.3 readers "
        "resolve the length-invariant at curve, edge, and topology-representation "
        "levels; Ed.2 / AP214 readers produce Void transfer status on all three — "
        "the curve/edge still load but the length-invariant is silently absent, "
        "so a wire-harness / gasket-length application cannot enforce the "
        "constraint; edition-boundary drop; steptools notes_ap242e3.html; "
        "MANIFOLD_SURFACE_SHAPE_REPRESENTATION with one face — OCC yields shape(1)"
    ),
)

# ── Override header to AP242 Ed.3 OID with AUTOMOTIVE_DESIGN schema name ─────
_HDR = (
    "HEADER;\n"
    f"FILE_DESCRIPTION(('{f.catalog_id}'),'2;1');\n"
    f"FILE_NAME('{f.catalog_id}.stp','{f.timestamp}',(''),(''),"
    f"'cad-research-suite','','');\n"
    "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 442 4 1 4 }'));\n"
    "ENDSEC;"
)
f._render_header = lambda: _HDR

# ── Planar carrier face (1x1 mm patch in the XY plane, z=0) ───────────────────
S = 1.0
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc, name="twi278_plane")

# Four corner points and a closed polyline loop → face boundary
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((S,   0.0, 0.0))
p11 = f.cartesian_point((S,   S,   0.0))
p01 = f.cartesian_point((0.0, S,   0.0))
loop = f.closed_polyline_loop([p00, p10, p11, p01])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="twi278_face")
shell = f.open_shell([face], name="twi278_shell")
sbsm  = f.shell_based_surface_model([shell], name="twi278_sbsm")
f.add_product_chain(sbsm)

# ── Co-present degree-1 B-spline edge (straight line from (0,0,0) to (1,0,0)) ─
# Two control points, knot mults [2, 2], knots [0.0, 1.0].
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((S,   0.0, 0.0))
bspline = f.b_spline_curve_with_knots(
    1, [cp0, cp1], [2, 2], [0.0, 1.0],
    curve_form="POLYLINE_FORM",
    name="twi278_bspline",
)
v_start = f.vertex_point(cp0)
v_end   = f.vertex_point(cp1)
edge_curve = f._emit_raw(
    f"EDGE_CURVE('twi278_edge',#{v_start.eid},#{v_end.eid},"
    f"#{bspline.eid},.T.)"
)

# ── AP242 Ed.3 BOUNDED_CURVE_WITH_LENGTH (E07) ───────────────────────────────
# Per AP242 Ed.3 §4.4: this entity attaches a POSITIVE_LENGTH_MEASURE
# length-invariant to a BOUNDED_CURVE (here the B_SPLINE_CURVE_WITH_KNOTS).
# Attributes per Ed.3: (name, curve, length).
# Byte assertion: contains(b'BOUNDED_CURVE_WITH_LENGTH')
# Ed.2 / AP214 readers produce Void transfer status on this entity.
bcwl = f._emit_raw(
    f"BOUNDED_CURVE_WITH_LENGTH('twi278_bcwl',#{bspline.eid},"
    f"POSITIVE_LENGTH_MEASURE(1.0))"
)

# ── AP242 Ed.3 EDGE_BOUNDED_CURVE_WITH_LENGTH (E10) ──────────────────────────
# Per AP242 Ed.3 §4.4: this entity attaches a POSITIVE_LENGTH_MEASURE
# length-invariant to an EDGE_CURVE (the topological-edge form of E07).
# Attributes per Ed.3: (name, edge, length).
# Byte assertion: contains(b'EDGE_BOUNDED_CURVE_WITH_LENGTH')
ebcwl = f._emit_raw(
    f"EDGE_BOUNDED_CURVE_WITH_LENGTH('twi278_ebcwl',#{edge_curve.eid},"
    f"POSITIVE_LENGTH_MEASURE(1.0))"
)

# ── AP242 Ed.3 EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT (E9)
# Per AP242 Ed.3 §4.4: this entity bundles edges at the topological
# representation level and attaches a POSITIVE_LENGTH_MEASURE constraint
# to the aggregate. Attributes per Ed.3: (name, edges, length).
# Byte assertion:
#   contains(b'EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT')
ebtrwlc = f._emit_raw(
    f"EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT("
    f"'twi278_ebtrwlc',(#{edge_curve.eid}),"
    f"POSITIVE_LENGTH_MEASURE(1.0))"
)

# ── Tie the length-constraint triad into a property representation ───────────
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('twi278_length_constraints',"
    f"'AP242 Ed.3 length-constraint triad',#9055)"
)
constraint_rep = f._emit_raw(
    f"REPRESENTATION('twi278_constraint_rep',(#{bcwl.eid},#{ebcwl.eid},"
    f"#{ebtrwlc.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{constraint_rep.eid})"
)
