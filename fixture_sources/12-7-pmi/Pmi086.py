"""Pmi086 — Empty IGES/STEP write loses general attributes.

Catalog claim: a document with GENERAL_PROPERTY entries (AP242 free-form
attributes) writes to STEP successfully. But the writer routes attributes
through the styled-item pipeline only for shapes with non-trivial geometry;
empty shape representations lose their general attributes even when they
have valuable metadata.

Reproducer recipe: Document with one part marked as a "configuration
placeholder" (no geometry, only metadata: revision, status, owner).
Writer drops the metadata.

Byte assertions:
  count_entity_def(b'GENERAL_PROPERTY') == 3
  contains(b'ANNOTATION_PLANE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi086",
    schema="AP242",
    defect=(
        "Three GENERAL_PROPERTY entries carry free-form attributes "
        "('revision', 'status', 'owner') on a configuration-placeholder part "
        "with no geometry; the writer routes attribute emission through the "
        "styled-item pipeline which is skipped for parts with empty shape "
        "representations; on round-trip all three GENERAL_PROPERTY entities "
        "are silently dropped; receivers must emit GENERAL_PROPERTY entries "
        "for every labelled part regardless of whether the label has geometry; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE

# ── Three GENERAL_PROPERTY entities (byte assertion: count == 3) ──────────────
# DEFECT: writer skips these on empty-geometry labels; they vanish on export.
gp_rev = f._emit_raw(
    "GENERAL_PROPERTY('revision','configuration placeholder revision','A')"
)
gp_status = f._emit_raw(
    "GENERAL_PROPERTY('status','configuration placeholder status','released')"
)
gp_owner = f._emit_raw(
    "GENERAL_PROPERTY('owner','configuration placeholder owner','design-eng')"
)

# Property relationships binding the attributes to the part definition.
f._emit_raw(
    f"PROPERTY_DEFINITION('revision_prop','part revision attr',#9055)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION('status_prop','part status attr',#9055)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION('owner_prop','part owner attr',#9055)"
)

# ── ANNOTATION_PLANE (byte assertion: contains(b'ANNOTATION_PLANE')) ──────────
# A placeholder annotation plane is present in the document (e.g. for a title
# block); confirms the file is a real AP242 document with PMI infrastructure.
ann_origin = f._emit_raw("CARTESIAN_POINT('ann_origin',(0.0,0.0,0.0))")
ann_normal = f._emit_raw("DIRECTION('ann_normal',(0.0,0.0,1.0))")
ann_xdir = f._emit_raw("DIRECTION('ann_xdir',(1.0,0.0,0.0))")
ann_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('ann_plc',#{ann_origin.eid},"
    f"#{ann_normal.eid},#{ann_xdir.eid})"
)
f._emit_raw(
    f"ANNOTATION_PLANE('title_block_plane',(),#{ann_plc.eid},())"
)
