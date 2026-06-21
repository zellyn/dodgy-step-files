"""In002 — Load-time warning vs data-content warning: severity confusion.

Catalog claim: Two different sources of warnings (parser warnings about
file syntax vs. semantic warnings about data content) are mapped onto
the same severity bucket. A consumer who suppresses load warnings ends
up suppressing data warnings too.

Reproducer recipe:
  A file with both a parser-level warning (a stray comment between
  ENDSEC and DATA) and a data-level warning (a B_SPLINE_CURVE_WITH_KNOTS
  at the spec-boundary degree 25 — high degree is a data-level warning).

Byte assertions:
  contains(b'DATA;')
  contains(b'HEADER;')
  count(b'ENDSEC;') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="In002",
    defect=(
        "Load-time warning vs data-content warning: severity confusion; "
        "OCCT Interface_InterfaceModel.cxx:281 (Interface_LoadWarning); "
        "two different sources of warnings — parser warnings about file syntax and "
        "semantic warnings about data content — are mapped onto the same severity bucket; "
        "a consumer who suppresses load warnings ends up suppressing data warnings too; "
        "defect: stray comment between HEADER ENDSEC and DATA keyword "
        "(parser-level warning) combined with a B_SPLINE_CURVE_WITH_KNOTS at "
        "spec-boundary degree 25 (data-level semantic warning); "
        "receiver must distinguish severity classes and provide separate warning channels; "
        "bug-reporter synonyms: warnings hidden, parser warnings vs data warnings confused, "
        "diagnostic channel confusion; "
        "GEOMETRIC_CURVE_SET IS NOT used — B-spline entity is the model object"
    ),
)

# We do not use add_product_chain — the B-spline is a standalone entity
# that demonstrates the data-level warning.  Override render() to emit
# the stray comment (parser-level warning trigger) and the high-degree
# B-spline (data-level warning trigger) together.
#
# Control points: degree 25 requires 26 control points for an open curve
# with full multiplicity (each knot span = 1 control point + degree).
# We use 26 CARTESIAN_POINTs and knot multiplicities (26, 26) with knot
# values (0.0, 1.0) — clamped Bézier form at degree 25.
#
# Satisfies:
#   contains(b'DATA;')            — DATA keyword present
#   contains(b'HEADER;')          — HEADER keyword present
#   count(b'ENDSEC;') >= 2        — two ENDSEC markers (header + data)

_original_render = f.render


def _render_mixed_channel_warnings() -> str:
    header = f._render_header()
    # 26 control points for degree-25 B-spline
    cp_lines = "\n".join(
        f"#{ 100 + i}=CARTESIAN_POINT('',({float(i)!r},0.0,0.0));"
        for i in range(26)
    )
    cp_refs = ",".join(f"#{100 + i}" for i in range(26))
    # Knot multiplicities: (26, 26) → clamped Bézier, degree 25
    bspline_line = (
        f"#10=B_SPLINE_CURVE_WITH_KNOTS('high_degree_boundary',25,"
        f"({cp_refs}),"
        f".UNSPECIFIED.,.F.,.F.,(26,26),(0.0,1.0),.UNSPECIFIED.);"
    )
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"/* parser-level event: stray comment between HEADER ENDSEC and DATA */\n"
        f"DATA;\n"
        f"{bspline_line}\n"
        f"/* data-level event: B_SPLINE_CURVE_WITH_KNOTS at spec-boundary degree 25 */\n"
        f"{cp_lines}\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_mixed_channel_warnings  # type: ignore[method-assign]
