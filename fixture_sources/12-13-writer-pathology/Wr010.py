"""Wr010 — Re-emitted `*` (overridden) where schema does not allow it.

Catalog claim: The `*` token denotes an attribute inherited from a supertype
and overridden in a subtype context; valid only inside complex (subtype-stack)
records.  The producer emits `*` in a simple-entity instance where no supertype
exists, producing `CARTESIAN_POINT('p',(*,0.0,0.0))` or similar.  Receivers
diverge: some treat `*` as an error, some treat it as zero, some treat it as
`$`.  ISO 10303-21 §10 defines `*` semantics narrowly.

Reproducer recipe: `CARTESIAN_POINT('p',(*,0.0,0.0))` in a non-subtype context.

Byte assertions:
  matches(rb'CARTESIAN_POINT\\([^;]*,\\(\\*\\s*,')
  matches(rb'\\(\\*,')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr010",
    defect=(
        "Re-emitted asterisk (overridden) where schema does not allow it; "
        "the asterisk token denotes an attribute inherited from a supertype "
        "and overridden in a subtype context, valid only inside complex "
        "(subtype-stack) records; "
        "the producer emits asterisk in a simple-entity instance where no "
        "supertype exists, producing CARTESIAN_POINT('p',(*,0.0,0.0)) or similar; "
        "buggy writers that mis-handle the inheritance-override mechanism for "
        "complex (subtype) entities and apply it to non-inherited attributes; "
        "receivers diverge: some treat asterisk as an error, some treat it as zero, "
        "some treat it as dollar-sign; "
        "ISO 10303-21 section 10 defines asterisk semantics narrowly; "
        "expected kernel behavior: reject as malformed; "
        "asterisk is meaningful only in complex-instance subtype-override position; "
        "synonyms: asterisk where number expected, STEP file has stars in coordinates, "
        "writer used override-marker incorrectly"
    ),
)


def _render_asterisk_in_simple_entity() -> str:
    """Return a Part-21 string with `*` used in a simple (non-subtype) CARTESIAN_POINT."""
    return (
        "ISO-10303-21;\n"
        "/* Wr010: asterisk used as override-marker in non-subtype CARTESIAN_POINT */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr010 - asterisk in simple entity coordinates'),'2;1');\n"
        "FILE_NAME('Wr010.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: * used as a coord value in a plain CARTESIAN_POINT (not a subtype stack) */\n"
        "/* Valid context for * is inside complex entity records only, e.g.: */\n"
        "/* #N=(POINT()CARTESIAN_POINT((*,0.,0.))...) */\n"
        "/* Here it appears in a simple entity: schema violation */\n"
        "#1=CARTESIAN_POINT('defect-point',(*,0.,0.));\n"
        "#2=CARTESIAN_POINT('ok-point',(1.,0.,0.));\n"
        "#3=CARTESIAN_POINT('ok-point2',(1.,1.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=DIRECTION('xdir',(1.,0.,0.));\n"
        "#6=GEOMETRIC_CURVE_SET('asterisk-defect',(#2,#3));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_asterisk_in_simple_entity(path) -> None:
    Path(path).write_bytes(_render_asterisk_in_simple_entity().encode("utf-8"))


f.render = _render_asterisk_in_simple_entity  # type: ignore[method-assign]
f.write = _write_asterisk_in_simple_entity  # type: ignore[method-assign]
