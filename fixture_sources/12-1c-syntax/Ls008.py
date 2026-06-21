"""Ls008 — Float literal with extreme exponent / non-finite real.

Catalog claim: `1.0E+999999` parsed via `strtod` yields `inf`; `NaN`
results from malformed inputs. Geometry pipelines that compare via
`<`/`>` then violate sort invariants in STL containers.

Reproducer recipe: #1=CARTESIAN_POINT('',(1.0E+999999,0.,0.));

Byte assertions:
  contains(b'1.0E+999999') or contains(b'1.0E-999999')
  count(b'E+999999') + count(b'E-999999') >= 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls008",
    defect=(
        "Float literal with extreme exponent overflowing to non-finite real; "
        "1.0E+999999 parsed via strtod yields IEEE 754 infinity; "
        "NaN results from malformed or indeterminate inputs; "
        "geometry pipelines that compare via less-than or greater-than "
        "then violate strict-weak-ordering invariants in STL containers; "
        "defect: CARTESIAN_POINT with 1.0E+999999 in the X coordinate — "
        "extreme positive exponent overflows to positive infinity; "
        "also DIRECTION uses 1.0E-999999 (underflow to zero) in the Y coordinate; "
        "conformant kernel must clamp magnitude or reject non-finite "
        "where geometry expects finite values; "
        "OCC silently accepts with no diagnostic and loads an empty result — "
        "receivers enforcing the spec must reject this fixture; "
        "synonyms: 1.0E+999999 overflows to infinity, STEP REAL becomes inf, "
        "NaN from STEP, infinity in geometry pipeline, non-finite REAL breaks sort; "
        "GEOMETRIC_CURVE_SET IS NOT used — CARTESIAN_POINT entity is the defect carrier"
    ),
)

_original_render = f.render


def _render_extreme_exponent() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Defect: extreme exponent causes overflow to IEEE 754 infinity. */\n"
        f"/* 1.0E+999999 -> +inf via strtod; violates geometry sort invariants. */\n"
        f"/* 1.0E-999999 -> 0.0 (underflow); second defect variant. */\n"
        f"#1=CARTESIAN_POINT('',(1.0E+999999,0.,0.));\n"
        f"#2=DIRECTION('',(0.,1.0E-999999,0.));\n"
        f"#3=VECTOR('v',#2,1.0E+999999);\n"
        f"#4=LINE('l',#1,#3);\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_extreme_exponent  # type: ignore[method-assign]
