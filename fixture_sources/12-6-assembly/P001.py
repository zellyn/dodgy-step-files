"""P001 — Schema variant: CONFIG_CONTROL_DESIGN with no PRODUCT entity.

Catalog claim: a re-exported file uses the older `CONFIG_CONTROL_DESIGN` schema
(rather than `AUTOMOTIVE_DESIGN`) and lacks a PRODUCT/PRODUCT_DEFINITION chain at
the protocol layer. OCCT's reader silently returns success with zero objects and
no console message. Other readers (e.g., Rhino) accept it.

The defect: FILE_SCHEMA declares CONFIG_CONTROL_DESIGN, there is no PRODUCT
entity anywhere in the file (only PRODUCT_DEFINITION / PRODUCT_DEFINITION_FORMATION
are present as minimal scaffolding), yet a MANIFOLD_SOLID_BREP payload exists.
A kernel must reject with an explicit diagnostic or accept successfully — silent
empty result is the bug.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  declared_schema == b'CONFIG_CONTROL_DESIGN'
  count_entity_def(b'PRODUCT') == 0

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P001",
    defect=(
        "FILE_SCHEMA=CONFIG_CONTROL_DESIGN; no PRODUCT entity present; "
        "only PRODUCT_DEFINITION/PRODUCT_DEFINITION_FORMATION as minimal scaffolding; "
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE + SHAPE_DEFINITION_REPRESENTATION for §12.6 lint; "
        "OCCT silently accepts with empty result — must reject or diagnose; "
        "GEOMETRIC_CURVE_SET IS model entity"
    ),
    schema="AP242",
)

# Minimal geometry: a single point inside a GEOMETRIC_CURVE_SET so that
# a reader that somehow accepts the schema still yields no solid.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Manually emit the product chain WITHOUT a PRODUCT entity.
# count_entity_def(b'PRODUCT') == 0 is the key byte assertion.
# We still need SHAPE_DEFINITION_REPRESENTATION for assembly-presence lint.
app_ctx = f._emit_raw("APPLICATION_CONTEXT('mechanical design')")
prod_def_form = f._emit_raw("PRODUCT_DEFINITION_FORMATION('','',#9999)")  # dangling ref — no PRODUCT
prod_def_ctx = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT(#{app_ctx.eid},'design')"
)
prod_def = f._emit_raw(
    f"PRODUCT_DEFINITION('','',#{prod_def_form.eid},#{prod_def_ctx.eid})"
)
prod_def_shape = f._emit_raw(
    f"PRODUCT_DEFINITION_SHAPE('','',#{prod_def.eid})"
)

# Minimal geometric context for the shape representation.
length_unit = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pa_unit = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sa_unit = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),"
    f"#{length_unit.eid},'distance_accuracy_value','')"
)
geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{length_unit.eid},#{pa_unit.eid},#{sa_unit.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)
shape_rep = f._emit_raw(
    f"MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{geom_ctx.eid})"
)
# SHAPE_DEFINITION_REPRESENTATION satisfies §12.6 assembly-presence lint.
f._emit_raw(
    f"SHAPE_DEFINITION_REPRESENTATION(#{prod_def_shape.eid},#{shape_rep.eid})"
)

# NAUO scaffolding (assembly presence, doubles as defect context).
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1','CCD_instance','',#{prod_def.eid},$,$)"
)

# Override the FILE_SCHEMA line so the emitted header reads
#   FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));
# instead of the AP242 literal. This is the sole defect mechanism.
_original_render = f.render


def _render_with_ccd_schema():
    text = _original_render()
    text = text.replace(
        "AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }",
        "CONFIG_CONTROL_DESIGN",
    )
    return text


f.render = _render_with_ccd_schema  # type: ignore[method-assign]
