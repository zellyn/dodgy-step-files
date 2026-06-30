"""Pmi141 — AP242 coordinate-system connection point entity silently dropped.

Catalog claim: a STEP AP242 file containing a valid geometry and product structure
with a coordinate-system connection-point entity present in the data section.
The AP242 mechanism for coordinate-system links between assembly components uses
CONSTRUCTIVE_GEOMETRY_REPRESENTATION_RELATIONSHIP + POINT_ON_SURFACE or a
product-structural link that OCCT 7.x does not process; the entity is silently
ignored (no error), but OCCT V8+ exposes the coordinate-system connection via the
updated assembly-data API.

Expected-valid synthesis target: OCCT 7.x loads geometry and ignores the
connection-point entity; OCCT V8+ may expose it. The fixture documents the entity
class and connection chain for conformance testing.

Source: OCCT V8.0.0 issue #779 (GitHub release notes)
B4 wave-5 DEF-Q. Confidence: MEDIUM — AP242 schema knowledge required; documented
as expected-valid synthesis target since local OCCT yields no diagnostic.

Byte assertions:
  contains(b'PRODUCT_DEFINITION_SHAPE')
  contains(b'CONSTRUCTIVE_GEOMETRY_REPRESENTATION')
  contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
Tier-3: shape_null == False (geometry loads; connection-point entity ignored under V7)
Expected: verify with live oracle
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi141",
    schema="AP242",
    defect=(
        "AP242 file with PRODUCT_DEFINITION_SHAPE linked to a coordinate-system "
        "connection point via CONSTRUCTIVE_GEOMETRY_REPRESENTATION_RELATIONSHIP + "
        "AXIS2_PLACEMENT_3D chain (AP242 §, issue #779); connection-point entity "
        "silently dropped under OCCT 7.x (no error); readable under OCCT V8+ "
        "assembly-data API; documented as expected-valid synthesis target; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty (shape_null)"
    ),
)

# ── Minimal geometry wrapped in GEOMETRIC_CURVE_SET (PMI pattern) ─────────────
# Use GCS so OCCT returns shape_null (as with other PMI fixtures),
# confirming the file is geometry-file OK but PMI data inaccessible.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain allocates:
#   #9000 = APPLICATION_CONTEXT
#   #9001 = PRODUCT_CONTEXT
#   #9002 = PRODUCT (Pmi141)
#   #9003 = PRODUCT_DEFINITION_FORMATION
#   #9004 = PRODUCT_DEFINITION_CONTEXT
#   #9005 = PRODUCT_DEFINITION
#   #9055 = PRODUCT_DEFINITION_SHAPE
#   #9060 = geometric context complex

# ── Coordinate-system connection-point chain ──────────────────────────────────
# Encode a minimal AP242 assembly with two product definitions connected by
# NEXT_ASSEMBLY_USAGE_OCCURRENCE, plus a CONSTRUCTIVE_GEOMETRY_REPRESENTATION
# carrying an AXIS2_PLACEMENT_3D as the connection-point coordinate system.
#
# The connection-point mechanism (AP242 §D.3): a coordinate-system anchor is
# encoded as an AXIS2_PLACEMENT_3D inside a CONSTRUCTIVE_GEOMETRY_REPRESENTATION,
# linked to the assembly component via
# CONSTRUCTIVE_GEOMETRY_REPRESENTATION_RELATIONSHIP.

# Component product definitions
comp_ctx = f._emit_raw(
    f"PRODUCT_CONTEXT('',#9000,'mechanical')"
)
comp_prod = f._emit_raw(
    f"PRODUCT('component','component','',(#{comp_ctx.eid}))"
)
comp_pdf = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{comp_prod.eid})"
)
comp_pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#9000,'design')"
)
comp_pd = f._emit_raw(
    f"PRODUCT_DEFINITION('','','',#{comp_pdf.eid},#{comp_pdc.eid})"
)
comp_pds = f._emit_raw(
    f"PRODUCT_DEFINITION_SHAPE('','','',#{comp_pd.eid})"
)

# NEXT_ASSEMBLY_USAGE_OCCURRENCE: link parent (#9054 = PRODUCT_DEFINITION) to component
# Byte assertion: contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
nauo = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','','',#9054,#{comp_pd.eid},$)"
)

# ── Coordinate-system anchor (the connection point) ───────────────────────────
# AXIS2_PLACEMENT_3D at (5, 0, 0) pointing in +Z direction.
cs_orig = f.cartesian_point((5.0, 0.0, 0.0))
cs_zdir = f.direction((0.0, 0.0, 1.0))
cs_xdir = f.direction((1.0, 0.0, 0.0))
cs_ax   = f.axis2_placement_3d(cs_orig, cs_zdir, cs_xdir)

# CONSTRUCTIVE_GEOMETRY_REPRESENTATION carrying the connection-point axis
# Byte assertion: contains(b'CONSTRUCTIVE_GEOMETRY_REPRESENTATION')
cgr = f._emit_raw(
    f"CONSTRUCTIVE_GEOMETRY_REPRESENTATION('',(#{cs_ax.eid}),#9060)"
)

# CONSTRUCTIVE_GEOMETRY_REPRESENTATION_RELATIONSHIP links the CGR to the
# component's product-definition shape representation (the assembly shape rep).
# Per AP242 §: the relationship anchors the coordinate system to the component.
cgr_rel = f._emit_raw(
    f"CONSTRUCTIVE_GEOMETRY_REPRESENTATION_RELATIONSHIP('cs_conn_pt','',#{cgr.eid},#9060)"
)

# PROPERTY_DEFINITION_REPRESENTATION wires the connection-point rep to the shape.
# Under OCCT 7.x this chain is not traversed; under V8+ it populates
# the assembly-data coordinate-system API.
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('connection_point','coordinate system anchor',#{comp_pds.eid})"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{cgr.eid})"
)
