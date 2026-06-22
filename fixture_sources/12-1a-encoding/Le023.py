"""Le023 — Locale-dependent decimal separator inside numeric attribute.

Catalog claim: The REAL grammar in ISO 10303-21 uses '.' only as the decimal
separator. A producer using locale-aware printf on a European locale (e.g.
LC_NUMERIC=de_DE) emits '1,5' for one-and-a-half. A parser using strtod
without setlocale("C") on such a host reads '1,5' as integer '1', then a
comma token, then integer '5', or fails entirely. Geometry then has wildly
wrong coordinates; downstream tessellation can crash on degenerate triangles.

Reproducer recipe:
  #1=CARTESIAN_POINT('',(1,5,0.,0.));

Byte assertions:
  matches(rb"CARTESIAN_POINT\\('[^']*',\\([0-9]+,[0-9]+,")
  matches(rb'\\(0,\\s*0,\\s*0,\\s*0,\\s*0\\)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le023",
    defect=(
        "Locale-dependent decimal separator inside numeric attribute; "
        "ISO 10303-21 §6.4.4: REAL grammar uses '.' only as decimal separator; "
        "European locale (LC_NUMERIC=de_DE) printf emits '1,5' for one-and-a-half; "
        "parser using strtod without setlocale(\"C\") reads comma-separated as separate tokens; "
        "CARTESIAN_POINT with commas instead of decimal points in coordinate list; "
        "wildly wrong coordinates — degenerate geometry downstream, possible tessellation crash; "
        "receiver must use strtod_l with C locale; reject anything strtod does not consume; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject CARTESIAN_POINT entities whose coordinate lists
# use commas as decimal separators instead of decimal points.
#
# CARTESIAN_POINT #8997: (1,5,0.,0.)  — "1,5" means 1.5 in de_DE locale;
#   a naive parser sees this as the integer 1, comma, integer 5, comma,
#   the valid REAL 0., comma, the valid REAL 0. — four values where three
#   were intended. OCCT typically accepts 1 as x, 5 as y, 0 as z (wildly
#   wrong), or raises a parse error.
#
# CARTESIAN_POINT #8998: (0,0,0,0,0) — five zeros with commas only;
#   satisfies the second byte assertion: matches(rb'\(0,\s*0,\s*0,\s*0,\s*0\)')
#   and clearly demonstrates the "no decimal point at all" defect class.
#
# Satisfies:
#   matches(rb"CARTESIAN_POINT\('[^']*',\([0-9]+,[0-9]+,")  — #8997
#   matches(rb'\(0,\s*0,\s*0,\s*0,\s*0\)')                  — #8998

_original_render = f.render


def _render_with_locale_comma() -> str:
    text = _original_render()
    # Locale-comma CARTESIAN_POINT: coordinate list uses integer comma integer
    # as a producer with LC_NUMERIC=de_DE would emit for '1.5,0.0,0.0'
    defect_lines = (
        "#8997=CARTESIAN_POINT('',(1,5,0.,0.));\n"
        "#8998=CARTESIAN_POINT('',(0,0,0,0,0));\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + defect_lines + text[idx:]


f.render = _render_with_locale_comma  # type: ignore[method-assign]
