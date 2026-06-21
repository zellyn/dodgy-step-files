"""M017 — Tessellated geometry without a styled_item (no color).

Catalog claim: A tessellated shape entity has no STYLED_ITEM referencing it,
so no color/style is set; receivers must default.

Reproducer recipe: TESSELLATED_SOLID entity with no STYLED_ITEM referencing it.

Byte assertions:
  contains(b'TESSELLATED_SOLID')
  contains(b'tet_no_style')
  not_contains(b'PRESENTATION_STYLE_ASSIGNMENT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M017",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing TESSELLATED_SOLID with no STYLED_ITEM referencing it; "
        "tessellated_solid 'tet_no_style' has no style assignment or STYLED_ITEM; "
        "receivers must warn and default to a neutral material/color; "
        "input: AP242 STEP file where TESSELLATED_SOLID has no style binding; "
        "kernel-bug: receivers enforcing the spec must emit a diagnostic for this fixture; "
        "OCC silently accepts (no diagnostic); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: tessellated geometry no color, no styled_item on tessellation, "
        "tessellated face missing style, tessellation defaults color"
    ),
)

# ── Tessellated geometry: simple quad split into two triangles ────────────────
# Byte assertion: contains(b'tet_no_style')
# The name 'tet_no_style' makes the byte assertion explicit.
coords = f._emit_raw(
    "COORDINATES_LIST('quad_verts',3,"
    "((0.,0.,0.),(10.,0.,0.),(0.,10.,0.),(10.,10.,0.)))"
)

tri_face = f._emit_raw(
    f"TRIANGULATED_FACE('quad_face',#{coords.eid},$,"
    f"((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(1,3,2)))"
)

# TESSELLATED_SOLID — the entity with no STYLED_ITEM referencing it.
# Byte assertion: contains(b'TESSELLATED_SOLID')
# Byte assertion: not_contains(b'PRESENTATION_STYLE_ASSIGNMENT')
tess_solid = f._emit_raw(
    f"TESSELLATED_SOLID('tet_no_style',(#{tri_face.eid}))"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('tessellated-solid-no-style',(#{tess_solid.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M017.stp")
