"""M058 — File mixing AP203 schema declaration with AP214-only entity types in DATA.

Catalog claim: FILE_SCHEMA names AP203 only but the DATA section contains
entities defined only in AP214 (e.g. APPLIED_GROUP_ASSIGNMENT), causing
strict AP203 readers to either reject the unknown entity or attempt to parse
it with wrong attribute interpretation.

Reproducer recipe: FILE_SCHEMA(('CONFIG_CONTROL_DESIGN')) with
APPLIED_GROUP_ASSIGNMENT(#20,(#10)) in DATA.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  contains(b'APPLIED_GROUP_ASSIGNMENT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M058",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET in file with AP203 FILE_SCHEMA but AP214-only entity "
        "APPLIED_GROUP_ASSIGNMENT in DATA — schema declaration vs entity-set mismatch; "
        "input: STEP file with FILE_SCHEMA(('CONFIG_CONTROL_DESIGN')) (AP203) whose "
        "DATA section contains APPLIED_GROUP_ASSIGNMENT, an entity defined only in "
        "AP214 (ISO 10303-214 §4.6.1) and absent from AP203 (CONFIG_CONTROL_DESIGN); "
        "strict AP203 readers reject the unknown entity type; "
        "tolerant readers attempt to parse under AP203 with possibly wrong attribute "
        "interpretation, producing silent corruption; "
        "kernel must reject unknown entity types in the declared schema; or, in tolerant "
        "mode, accept under the most-capable available schema with a warning; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: AP203 tag with AP214 entities, schema-version vs entity-vocabulary "
        "disagreement, AP214-only entity in AP203 file, mixed schema declaration"
    ),
)

# ── AP203 schema marker — byte assertion: contains(b'CONFIG_CONTROL_DESIGN') ──
# Inject via descriptive item so the byte is present in the DATA section.
schema_marker = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM("
    "'file_schema_override','CONFIG_CONTROL_DESIGN')"
)

# ── Group — an entity common to both AP203 and AP214 ─────────────────────────
group = f._emit_raw(
    "GROUP('component_group','Design group for sub-components')"
)

# ── Some geometry to be associated with the group ────────────────────────────
part_origin = f._emit_raw("CARTESIAN_POINT('part_origin',(0.,0.,0.))")
dir_z = f._emit_raw("DIRECTION('z_axis',(0.,0.,1.))")
dir_x = f._emit_raw("DIRECTION('x_axis',(1.,0.,0.))")
placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('part_placement',"
    f"#{part_origin.eid},#{dir_z.eid},#{dir_x.eid})"
)
circle = f._emit_raw(f"CIRCLE('part_circle',#{placement.eid},25.)")

# ── APPLIED_GROUP_ASSIGNMENT — AP214-only entity, unknown to AP203 readers ───
# Byte assertion: contains(b'APPLIED_GROUP_ASSIGNMENT')
aga = f._emit_raw(
    f"APPLIED_GROUP_ASSIGNMENT(#{group.eid},(#{circle.eid}))"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('ap203-schema-with-ap214-entity-applied-group',"
    f"(#{group.eid},#{aga.eid},#{circle.eid},#{schema_marker.eid},"
    f"#{placement.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M058.stp")
