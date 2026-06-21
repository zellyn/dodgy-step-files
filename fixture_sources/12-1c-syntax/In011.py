"""In011 — Reader exception swallowed (entity bound to null) when B_SPLINE control
points use extreme-magnitude or subnormal coordinates (1.0E+308 / 5.0E-324).

Catalog claim: A C++ exception is thrown during the transfer of a single
entity; the transfer record is "bound" but the bound result is null.
Downstream consumers see "Done" status with no shape attached.

Reproducer recipe:
  A B_SPLINE_CURVE_WITH_KNOTS whose CARTESIAN_POINT control points use
  extreme-magnitude IEEE-754 values (1.0E+308 near the ceiling, subnormal
  5.0E-324) that overflow during arithmetic at transfer time.

Byte assertions:
  contains(b'DATA;')
  contains(b'HEADER;')
  count(b'ENDSEC;') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="In011",
    defect=(
        "Reader exception swallowed: entity bound to null when B_SPLINE control points "
        "use extreme-magnitude or subnormal coordinates (1.0E+308 / 5.0E-324); "
        "OCCT Transfer_TransferOutput.cxx:67 (Transfer_TransferFailure raise; binding null); "
        "a C++ exception is thrown during the transfer of a single entity; "
        "the transfer record is bound but the bound result is null; "
        "downstream consumers see Done status with no shape attached; "
        "defect: B_SPLINE_CURVE_WITH_KNOTS with CARTESIAN_POINT control points using "
        "1.0E+308 (near IEEE-754 double ceiling) coordinates — any pairwise multiplication "
        "during length/norm evaluation overflows to +Inf, triggering the exception; "
        "also includes a subnormal control point (5.0E-324) for the underflow path; "
        "receiver must reject and emit the underlying exception text: "
        "mark transfer as Error, not Done; must not silently swallow exceptions; "
        "bug-reporter synonyms: kernel says done but produced nothing, "
        "transfer succeeded with empty result, extreme-magnitude coordinates overflow, "
        "STEP transfer Done but shape null, exception swallowed during STEP transfer; "
        "GEOMETRIC_CURVE_SET IS NOT used — B-spline entity is the defect carrier"
    ),
)

# No product chain — the defect is the exception-triggering B-spline.
# Override render() to emit extreme-magnitude and subnormal control points.

_original_render = f.render


def _render_exception_swallowed() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Control points with extreme-magnitude coordinates near the IEEE-754 double\n"
        f"   ceiling. Any pairwise multiplication during length/norm evaluation\n"
        f"   overflows to +Inf and triggers the transfer exception. */\n"
        f"#10=CARTESIAN_POINT('cp_extreme_a',(1.0E+308,0.0,0.0));\n"
        f"#11=CARTESIAN_POINT('cp_extreme_b',(1.0E+308,1.0E+308,0.0));\n"
        f"#12=CARTESIAN_POINT('cp_extreme_c',(1.0E+308,1.0E+308,1.0E+308));\n"
        f"/* Subnormal value (smallest positive double ~5e-324) for underflow path. */\n"
        f"#13=CARTESIAN_POINT('cp_subnormal',(5.0E-324,0.0,0.0));\n"
        f"#20=B_SPLINE_CURVE_WITH_KNOTS('exception_trigger',2,(#10,#11,#12),"
        f".UNSPECIFIED.,.F.,.F.,(3,3),(0.0,1.0),.UNSPECIFIED.);\n"
        f"/* Dependent VECTOR/LINE that, when normalised, multiplies extreme-magnitude\n"
        f"   coordinates and drives the result to +Inf. */\n"
        f"#30=DIRECTION('overflow_dir',(1.0E+308,1.0E+308,0.0));\n"
        f"#31=VECTOR('overflow_vec',#30,1.0E+154);\n"
        f"#32=LINE('overflow_line',#10,#31);\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_exception_swallowed  # type: ignore[method-assign]
