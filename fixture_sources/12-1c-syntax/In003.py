"""In003 — A "Mend" demotes a Fail to a Warning, hiding the original failure.

Catalog claim: A reader's `Mend()` step takes a Fail-class diagnostic
and downgrades it to a Warning if the kernel "fixed" the underlying
problem. A consumer relying on the original Fail to gate further
processing now misses it.

Reproducer recipe:
  A B_SPLINE_CURVE_WITH_KNOTS whose knot multiplicities don't match the
  required count (degree 2, 3 control points: expected sum-of-multiplicities
  = n+degree+1 = 3+2+1 = 6, but multiplicities (3,1,3) sum to 7).
  A Fail-class condition that gets auto-mended and silently demoted.

Byte assertions:
  contains(b'DATA;')
  contains(b'HEADER;')
  count(b'ENDSEC;') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="In003",
    defect=(
        "A Mend demotes a Fail to a Warning, hiding the original failure; "
        "OCCT Interface_Check.hxx:97 (Mend method); "
        "a reader Mend() step takes a Fail-class diagnostic and downgrades it "
        "to a Warning if the kernel auto-fixed the underlying problem; "
        "a consumer relying on the original Fail to gate further processing misses it; "
        "defect: B_SPLINE_CURVE_WITH_KNOTS degree 2 with 3 control points: "
        "required knot sum = n+degree+1 = 3+2+1 = 6, "
        "but knot_multiplicities (3,1,3) sum to 7 (off-by-one extra knot); "
        "a Fail-class condition that gets auto-mended and silently demoted to Warning; "
        "receiver must always preserve the original severity; "
        "record the Mend as a separate auto-corrected event; "
        "must not silently downgrade Fail to Warning; "
        "bug-reporter synonyms: kernel hid an error, fail downgraded to warning silently, "
        "wrong knot count not reported, B_SPLINE knot defect silently fixed; "
        "GEOMETRIC_CURVE_SET IS NOT used — B-spline entity is the defect carrier"
    ),
)

# No product chain — the defect is the malformed B-spline entity.
# Override render() to emit the off-by-one knot-multiplicity fixture.

_original_render = f.render


def _render_mend_demotes_fail() -> str:
    header = f._render_header()
    # degree 2, 3 control points => expected knot count = 3+2+1 = 6
    # multiplicities (3,1,3) sum to 7: off-by-one (extra knot in the middle span)
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"#10=CARTESIAN_POINT('',( 0.0,0.0,0.0));\n"
        f"#11=CARTESIAN_POINT('',( 1.0,1.0,0.0));\n"
        f"#12=CARTESIAN_POINT('',( 2.0,0.0,0.0));\n"
        f"/* Defect: degree 2, 3 ctrl-pts => expected knot sum 6; "
        f"multiplicities (3,1,3) sum to 7 (off-by-one). */\n"
        f"#20=B_SPLINE_CURVE_WITH_KNOTS('extra_knot',2,(#10,#11,#12),"
        f".UNSPECIFIED.,.F.,.F.,(3,1,3),(0.0,0.5,1.0),.UNSPECIFIED.);\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_mend_demotes_fail  # type: ignore[method-assign]
