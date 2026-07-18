"""M020 — Tessellated face style binding lost (no TransferBRep_ShapeBinder).

Catalog claim: When a face is encoded as TESSELLATED_FACE/COMPLEX_TRIANGULATED_SURFACE_SET,
the style attached to it was not bound (no shape binder created).

Reproducer recipe: TESSELLATED_FACE with associated STYLED_ITEM.

Byte assertions:
  contains(b'STYLED_ITEM')
  contains(b'TRIANGULATED_FACE')
  contains(b'COLOUR_RGB')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M020",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing TESSELLATED_FACE with STYLED_ITEM and COLOUR_RGB "
        "referencing it; "
        "input: AP242 STEP file where TESSELLATED_FACE (TRIANGULATED_FACE) has an associated "
        "STYLED_ITEM with COLOUR_RGB but the style binding is not propagated to a shape binder; "
        "OCCT 9d93d9b (Mantis 0033638): no TransferBRep_ShapeBinder created for tessellated face "
        "style; color silently lost on import; "
        "kernel must heal: bind STYLED_ITEM color to tessellated shape; preserve color; "
        "must not silently lose color; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: tessellated face style binding lost, TransferBRep_ShapeBinder not created, "
        "complex triangulated face has no style, tessellated face color not bound"
    ),
)

# ── Tessellated face: a simple quad split into two triangles ──────────────────
# Byte assertion: contains(b'TRIANGULATED_FACE')
coords = f._emit_raw(
    "COORDINATES_LIST('tface_verts',3,"
    "((0.,0.,0.),(8.,0.,0.),(8.,8.,0.),(0.,8.,0.)))"
)

tri_face = f._emit_raw(
    f"TRIANGULATED_FACE('tface_quad',#{coords.eid},$,"
    f"((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(0,2,3)))"
)

# ── Style binding: STYLED_ITEM + COLOUR_RGB ───────────────────────────────────
# Byte assertion: contains(b'COLOUR_RGB')
colour = f._emit_raw(
    "COLOUR_RGB('face_colour',0.2,0.6,0.9)"
)

fill_style = f._emit_raw(
    f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})"
)
fill_area = f._emit_raw(
    f"FILL_AREA_STYLE('face_fill',(#{fill_style.eid}))"
)
surf_style_fill = f._emit_raw(
    f"SURFACE_STYLE_FILL_AREA(#{fill_area.eid})"
)
surf_side_style = f._emit_raw(
    f"SURFACE_SIDE_STYLE('face_side_style',(#{surf_style_fill.eid}))"
)
surf_style_usage = f._emit_raw(
    f"SURFACE_STYLE_USAGE(.BOTH.,#{surf_side_style.eid})"
)
pres_style = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{surf_style_usage.eid}))"
)

# STYLED_ITEM referencing the TESSELLATED_FACE — the binding that must not be lost.
# Byte assertion: contains(b'STYLED_ITEM')
styled = f._emit_raw(
    f"STYLED_ITEM('tface_styled',(#{pres_style.eid}),#{tri_face.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('tessellated-face-style-binding-lost',"
    f"(#{tri_face.eid},#{styled.eid}))"
)
f.add_product_chain(gcs, uncertainty_literal="LENGTH_MEASURE(1.0E-7)")  # bare typed real, not enum-wrapped (scaffolding-artifact fix)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M020.stp")
