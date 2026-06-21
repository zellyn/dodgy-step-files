"""M040 — STYLED_ITEM.item is NULL or unresolved.

Catalog claim: STEP file has STYLED_ITEM with NULL item reference, or
PRESENTATION_STYLE_ASSIGNMENT with NULL elements in its styles set; OCCT's
IsKind() call dereferenced NULL.

Reproducer recipe: STYLED_ITEM(name,(..),#null) or PSA with unresolved
style reference.

Byte assertions:
  contains(b'STYLED_ITEM')
  contains(b"STYLED_ITEM('null_item_style',(#606),$)")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M040",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing STYLED_ITEM with NULL item reference; "
        "input: AP242 STEP file where a STYLED_ITEM has its item attribute set to "
        "$ (NULL) — the styled geometry is unresolved; "
        "a second PRESENTATION_STYLE_ASSIGNMENT also references a NULL element in "
        "its styles list; "
        "OCCT OCCT aff1875/b80d766/f0bef12 (Mantis 0028147/0028797/0029633): "
        "IsKind() call on NULL handle caused crash or silent-empty; "
        "kernel must null-check and skip styling for the affected item; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: STYLED_ITEM null item, presentation_style_assignment null element, "
        "OCCT NULL deref on STYLED_ITEM, null reference in style chain"
    ),
)

# ── Colour and style for the styled item ──────────────────────────────────────
colour = f._emit_raw("COLOUR_RGB('red_style',1.,0.,0.)")
fill_area = f._emit_raw(
    f"FILL_AREA_STYLE('red_fill',(#{colour.eid}))"
)
fill_area_style = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fill_area.eid})")
surf_side_style = f._emit_raw(
    f"SURFACE_SIDE_STYLE('red_side',(#{fill_area_style.eid}))"
)

# ── Pad entities so that PSA lands at #606 ────────────────────────────────────
# Currently 4 entities emitted (#1-#4), next is #5.
# Need PSA at #606 => must emit 601 more before it => entities #5..#605.
# We have surf_side_style at #4, so pad = 606 - 4 - 1 = 601 entries (#5..#605).
for _i in range(601):
    f._emit_raw(f"CARTESIAN_POINT('pad_{_i}',(0.,0.,0.))")

# PRESENTATION_STYLE_ASSIGNMENT — forced to entity #606
# Byte assertion: contains(b"STYLED_ITEM('null_item_style',(#606),$)")
psa = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{surf_side_style.eid}))"
)
assert psa.eid == 606, f"Expected PSA at #606, got #{psa.eid}"

# ── STYLED_ITEM with NULL item ($) — the defect ──────────────────────────────
# Byte assertion: contains(b'STYLED_ITEM')
null_styled = f._emit_raw(
    f"STYLED_ITEM('null_item_style',(#{psa.eid}),$)"
)

# ── A valid reference geometry so the file parses ────────────────────────────
ref_pt = f._emit_raw("CARTESIAN_POINT('origin',(1.,1.,1.))")

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('styled-item-null-item',"
    f"(#{null_styled.eid},#{ref_pt.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M040.stp")
