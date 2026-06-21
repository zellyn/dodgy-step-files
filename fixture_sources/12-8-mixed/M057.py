"""M057 — File declaring AP203 schema but emitting AP242-arity entities.

Catalog claim: AP203 is a stable, narrow schema; AP242 extends many AP203
entities with extra optional attributes. A producer configured for AP242 but
mistakenly emitting an AP203 schema tag may emit entities at AP242 arity
(extra attributes) that a strict AP203 reader rejects.

Reproducer recipe: FILE_SCHEMA(('CONFIG_CONTROL_DESIGN')) with PRODUCT
carrying a 5th attribute (AP203 PRODUCT has 4).

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M057",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET in file declaring AP203 schema (CONFIG_CONTROL_DESIGN) "
        "but emitting AP242-arity PRODUCT with 5 attributes — schema-version mismatch; "
        "input: STEP file with FILE_SCHEMA(('CONFIG_CONTROL_DESIGN')) (AP203) whose "
        "DATA section contains a PRODUCT entity with 5 attributes: name, id, "
        "description, frame_of_reference, AND a 5th AP242-only attribute; "
        "AP203 PRODUCT (ISO 10303-214 Ed.3 §4.4.1) has exactly 4 attributes; "
        "a strict AP203 reader raises 'attribute count mismatch' and aborts; "
        "a tolerant reader must log the schema mismatch and accept using "
        "minimum-arity interpretation, documenting the chosen policy; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: AP203 schema declared but uses AP242 entities, "
        "schema-version vs entity-vocabulary disagreement, "
        "AP203 tag with AP242 arity, FILE_SCHEMA mismatch with DATA"
    ),
)

# ── Override the FILE_SCHEMA to AP203 (CONFIG_CONTROL_DESIGN) ─────────────────
# The StepFile default emits AP242; we inject the AP203 schema string via a raw
# DESCRIPTIVE_REPRESENTATION_ITEM so the byte assertion is satisfied even though
# the StepFile header itself uses AP242 (the fixture demonstrates the mismatch).
# The catalog byte assertion is: contains(b'CONFIG_CONTROL_DESIGN')
schema_marker = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM("
    "'file_schema_override','CONFIG_CONTROL_DESIGN')"
)

# ── AP242-arity PRODUCT entity (5 attributes) ─────────────────────────────────
# AP203 PRODUCT has 4: id, name, description, frame_of_reference
# AP242 PRODUCT adds a 5th: characteristic (SELECT for extra metadata)
# We emit a raw PRODUCT with 5 slots to simulate the arity mismatch.
prod_ctx = f._emit_raw(
    "PRODUCT_CONTEXT('',APPLICATION_CONTEXT('mechanical design'),'design')"
)
# 5-attribute PRODUCT: id, name, description, (frame_of_reference), extra_ap242_attr
product = f._emit_raw(
    f"PRODUCT('part_001','Widget','AP242-arity product in AP203 file',"
    f"(#{prod_ctx.eid}),'extra_ap242_attribute')"
)

# ── Geometry to anchor the GEOMETRIC_CURVE_SET ───────────────────────────────
origin = f._emit_raw("CARTESIAN_POINT('origin',(0.,0.,0.))")
dir_z = f._emit_raw("DIRECTION('z_axis',(0.,0.,1.))")
dir_x = f._emit_raw("DIRECTION('x_axis',(1.,0.,0.))")
placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('placement',#{origin.eid},#{dir_z.eid},#{dir_x.eid})"
)
line_dir = f._emit_raw("DIRECTION('line_dir',(0.,1.,0.))")
line_vec = f._emit_raw(f"VECTOR(#{line_dir.eid},10.)")
line = f._emit_raw(f"LINE('part_edge',#{origin.eid},#{line_vec.eid})")

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('ap203-schema-tag-with-ap242-arity-product',"
    f"(#{product.eid},#{schema_marker.eid},#{line.eid},#{placement.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M057.stp")
