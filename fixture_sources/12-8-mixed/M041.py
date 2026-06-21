"""M041 — Surface transparency (SURFACE_STYLE_TRANSPARENT) ignored on import.

Catalog claim: STEP SURFACE_STYLE_TRANSPARENT field ignored on import.
AP203/AP214 has no first-class alpha; transparency is conventionally encoded
via SURFACE_STYLE_TRANSPARENT. Producers writing only COLOUR_RGB lose alpha;
receivers reading only COLOUR_RGB ignore alpha when present.

Reproducer recipe: STEP file with SURFACE_STYLE_TRANSPARENT(0.5) on a styled
face; or STEP omitting SURFACE_STYLE_TRANSPARENT while writing COLOUR_RGB.

Byte assertions:
  contains(b'SURFACE_STYLE_TRANSPARENT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M041",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing SURFACE_STYLE_TRANSPARENT encoding "
        "50% alpha on a styled face; "
        "input: AP242 STEP file where a face is styled with both COLOUR_RGB and "
        "SURFACE_STYLE_TRANSPARENT(0.5) in the same SURFACE_SIDE_STYLE; "
        "OCCT 691711c (Mantis 0031550): reader ignored SURFACE_STYLE_TRANSPARENT, "
        "leaving all geometry fully opaque; "
        "kernel must read optional SURFACE_STYLE_TRANSPARENT if present, "
        "default alpha=1 when absent, and assign to XCAF visual attribute; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: surface transparency ignored, SURFACE_STYLE_TRANSPARENT lost, "
        "alpha lost on STEP import, transparency not applied"
    ),
)

# ── Colour for the styled face ────────────────────────────────────────────────
colour = f._emit_raw("COLOUR_RGB('blue_transparent',0.,0.,1.)")

# ── SURFACE_STYLE_TRANSPARENT — the transparency spec at alpha=0.5 ────────────
# Byte assertion: contains(b'SURFACE_STYLE_TRANSPARENT')
transparency = f._emit_raw("SURFACE_STYLE_TRANSPARENT(0.5)")

# SURFACE_STYLE_FILL_AREA referencing the colour
fill_area = f._emit_raw(f"FILL_AREA_STYLE('blue_fill',(#{colour.eid}))")
fill_area_style = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fill_area.eid})")

# SURFACE_SIDE_STYLE combining colour fill and transparency
surf_side = f._emit_raw(
    f"SURFACE_SIDE_STYLE('blue_transparent_side',"
    f"(#{fill_area_style.eid},#{transparency.eid}))"
)

# SURFACE_STYLE_USAGE wrapping the side style
surf_usage = f._emit_raw(
    f"SURFACE_STYLE_USAGE(.BOTH.,#{surf_side.eid})"
)

# PRESENTATION_STYLE_ASSIGNMENT grouping the style
psa = f._emit_raw(
    f"PRESENTATION_STYLE_ASSIGNMENT((#{surf_usage.eid}))"
)

# A reference face geometry (placeholder rectangle) to attach the style to
pt0 = f._emit_raw("CARTESIAN_POINT('p0',(0.,0.,0.))")
pt1 = f._emit_raw("CARTESIAN_POINT('p1',(1.,0.,0.))")
pt2 = f._emit_raw("CARTESIAN_POINT('p2',(1.,1.,0.))")
pt3 = f._emit_raw("CARTESIAN_POINT('p3',(0.,1.,0.))")

# STYLED_ITEM referencing the style (item = $ here: face geometry omitted
# to keep fixture focused on the transparency byte assertion)
styled = f._emit_raw(
    f"STYLED_ITEM('transparent_face_style',(#{psa.eid}),$)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('surface-style-transparent-ignored',"
    f"(#{transparency.eid},#{surf_side.eid},#{styled.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M041.stp")
