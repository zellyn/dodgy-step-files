"""Lh050 — STEP header DATE_AND_TIME malformed — FreeBSD timezone bug.

Catalog claim: a STEP AP203 file with FILE_DESCRIPTION / FILE_NAME header where
the DATE_AND_TIME field contains a deliberately malformed value produced by
buggy FreeBSD-specific code: the `timezone` global variable was declared as
`long timezone` in a local header conflicting with POSIX `extern long timezone`,
producing a garbage UTC offset value in the time-zone field of the timestamp.
The synthesized fixture has an explicitly malformed DATE_AND_TIME field in the
STEP header (negative year, out-of-range timezone offset) to test that consumers
tolerate malformed header dates without crash.

Expected: geometry-reading proceeds despite invalid header date; strict parsers
may emit a warning; no crash. The STEP header is non-critical for geometry.

Source: OCCT V8.0.0 (FreeBSD timezone `extern long timezone` declaration fix)
B4 wave-5 DEF-R. Confidence: MEDIUM — STEP header malformed-date class is new
fixture class; file is otherwise well-formed geometry-wise.

Byte assertions:
  contains(b'FILE_NAME')
  contains(b'-9999')   (malformed negative year in timestamp)
  matches(rb'FILE_NAME\\([^,]*,-9999')   (malformed date in FILE_NAME field)
Tier-3: load == "ok" (geometry should load despite bad header date)
Expected: verify with live oracle
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh050",
    defect=(
        "STEP header FILE_NAME timestamp contains malformed DATE_AND_TIME value "
        "produced by FreeBSD timezone-declaration bug: 'extern long timezone' vs "
        "'long timezone' conflict yields garbage UTC offset; fixture uses "
        "date '-9999-99-99T99:99:99+9999:99' — explicitly out-of-range year, "
        "month, day, hour, minute, and timezone offset; geometry (simple cube) "
        "is well-formed; consumers must tolerate malformed header dates without crash; "
        "strict parsers emit W_MALFORMED_DATE; OCCT V8.0.0 fixes the FreeBSD "
        "declaration clash that generated these values"
    ),
)


def _render_lh050() -> str:
    """Render a Part-21 with malformed DATE_AND_TIME in the FILE_NAME header record.

    The malformed timestamp '-9999-99-99T99:99:99+9999:99' simulates what the
    FreeBSD timezone bug produced: garbage values in the UTC-offset field that,
    when printed as ISO 8601, yield an entirely invalid date string. The year
    -9999, month 99, day 99, etc. are all out of range.

    The DATA section contains a valid minimal planar face geometry so geometry-
    loading tests can confirm the reader proceeds despite the bad header.
    """
    return (
        "ISO-10303-21;\n"
        "/* Lh050: malformed DATE_AND_TIME in FILE_NAME header — FreeBSD timezone bug */\n"
        "/* DEFECT: 'long timezone' vs 'extern long timezone' declaration mismatch on FreeBSD */\n"
        "/* produces garbage UTC offset; synthesized as explicit out-of-range date string */\n"
        "/* OCCT V8.0.0 fixes: https://github.com/Open-Cascade-SAS/OCCT/releases */\n"
        "/* Expected: geometry loads; strict parsers emit W_MALFORMED_DATE; no crash */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh050: malformed header DATE_AND_TIME (FreeBSD timezone bug)'),'2;1');\n"
        "/* DEFECT: next line has malformed timestamp with garbage timezone offset */\n"
        "FILE_NAME('Lh050.stp','-9999-99-99T99:99:99+9999:99',(''),(''),"
        "'cad-research-suite','FreeBSD/OCCT-7.x-timezone-bug','');\n"
        "FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('',(10.,0.,0.));\n"
        "#3=CARTESIAN_POINT('',(10.,10.,0.));\n"
        "#4=CARTESIAN_POINT('',(0.,10.,0.));\n"
        "#5=DIRECTION('',(1.,0.,0.));\n"
        "#6=DIRECTION('',(0.,1.,0.));\n"
        "#7=DIRECTION('',(0.,0.,1.));\n"
        "#8=VECTOR('',#5,10.);\n"
        "#9=VECTOR('',#6,10.);\n"
        "#10=LINE('',#1,#8);\n"
        "#11=LINE('',#2,#9);\n"
        "#12=VECTOR('',#5,10.);\n"
        "#13=LINE('',#4,#12);\n"
        "#14=VECTOR('',#6,10.);\n"
        "#15=LINE('',#1,#14);\n"
        "#16=VERTEX_POINT('',#1);\n"
        "#17=VERTEX_POINT('',#2);\n"
        "#18=VERTEX_POINT('',#3);\n"
        "#19=VERTEX_POINT('',#4);\n"
        "#20=EDGE_CURVE('',#16,#17,#10,.T.);\n"
        "#21=EDGE_CURVE('',#17,#18,#11,.T.);\n"
        "#22=EDGE_CURVE('',#19,#18,#13,.T.);\n"
        "#23=EDGE_CURVE('',#16,#19,#15,.T.);\n"
        "#24=ORIENTED_EDGE('',*,*,#20,.T.);\n"
        "#25=ORIENTED_EDGE('',*,*,#21,.T.);\n"
        "#26=ORIENTED_EDGE('',*,*,#22,.F.);\n"
        "#27=ORIENTED_EDGE('',*,*,#23,.F.);\n"
        "#28=EDGE_LOOP('',(#24,#25,#26,#27));\n"
        "#29=AXIS2_PLACEMENT_3D('',#1,#7,#5);\n"
        "#30=PLANE('',#29);\n"
        "#31=FACE_OUTER_BOUND('',#28,.T.);\n"
        "#32=ADVANCED_FACE('',(#31),#30,.T.);\n"
        "#33=OPEN_SHELL('',(#32));\n"
        "#34=SHELL_BASED_SURFACE_MODEL('',(#33));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh050(path) -> None:
    Path(path).write_bytes(_render_lh050().encode("utf-8"))


f.render = _render_lh050   # type: ignore[method-assign]
f.write = _write_lh050     # type: ignore[method-assign]
