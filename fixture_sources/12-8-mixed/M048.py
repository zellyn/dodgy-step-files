"""M048 — Material / appearance / physical attributes silently dropped on STEP export.

Catalog claim: Visual appearances and physical attributes (density, material name)
absent from STEP output; material with missing name crashes reader; material with
zero density emits invalid density entities.

Reproducer recipe: XCAF document with material density=0 or material with empty
name field; export to STEP.

Byte assertions:
  contains(b'MATERIAL_DESIGNATION')
  contains(b'MASS_DENSITY_MEASURE(0.0)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M048",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing MATERIAL_DESIGNATION with empty name and "
        "MASS_DENSITY_MEASURE(0.0) — physical attributes silently dropped on export; "
        "input: AP242 STEP file where MATERIAL_DESIGNATION has an empty name string "
        "and a density property uses MASS_DENSITY_MEASURE(0.0); "
        "OCCT Mantis (G057, G059): reader crashed on empty material name; "
        "writer emitted invalid density entity when density==0; "
        "Autodesk Fusion (V025) / SolidWorks→Inventor (V048) / HOOPS Exchange (W024): "
        "visual appearances and density stripped on STEP round-trip; "
        "kernel must default empty datum/material description, skip density emission "
        "for zero-density, and never silently drop appearance attributes; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: material attributes silently dropped, STEP export loses appearance, "
        "physical attributes missing on export, material/density lost on STEP write, "
        "appearance stripped on STEP output"
    ),
)

# ── MATERIAL_DESIGNATION with empty name — triggers reader crash in OCCT G057 ─
# Byte assertion: contains(b'MATERIAL_DESIGNATION')
material = f._emit_raw(
    "MATERIAL_DESIGNATION('','',$)"
)

# ── Property definition for the material ─────────────────────────────────────
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('material_property','physical attributes',#{material.eid})"
)

# ── MASS_DENSITY_MEASURE(0.0) — triggers invalid entity in OCCT G059 ──────────
# Byte assertion: contains(b'MASS_DENSITY_MEASURE(0.0)')
density_measure = f._emit_raw(
    "MEASURE_WITH_UNIT(MASS_DENSITY_MEASURE(0.0),$)"
)

# ── Appearance: COLOUR_RGB and STYLED_ITEM — the dropped appearance chain ──────
colour = f._emit_raw("COLOUR_RGB('material_colour',0.5,0.5,0.5)")
fill_area = f._emit_raw(f"FILL_AREA_STYLE('material_fill',(#{colour.eid}))")
fill_area_style = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fill_area.eid})")
surf_side = f._emit_raw(
    f"SURFACE_SIDE_STYLE('material_side',(#{fill_area_style.eid}))"
)
surf_usage = f._emit_raw(
    f"SURFACE_STYLE_USAGE(.BOTH.,#{surf_side.eid})"
)
psa = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{surf_usage.eid}))"
)
styled = f._emit_raw(
    f"STYLED_ITEM('material_appearance',(#{psa.eid}),$)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('material-appearance-dropped-on-export',"
    f"(#{material.eid},#{prop_def.eid},#{density_measure.eid},"
    f"#{styled.eid},#{colour.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M048.stp")
