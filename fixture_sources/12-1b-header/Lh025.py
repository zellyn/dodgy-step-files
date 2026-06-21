"""Lh025 — Mixing #NNN (entity) and @NNN (value) namespaces (Ed.3).

Catalog claim: Edition 3 introduces @NNN value-instance identifiers (e.g.
@1=POSITIVE_LENGTH_MEASURE(..)) alongside #NNN entity-instance identifiers.
The two integer namespaces are disjoint: #1 and @1 are distinct instances.
Files that put a @NNN value-instance reference where a #NNN entity-instance
reference is required (or vice versa), or that use the @-prefix syntax in plain
Edition-2 contexts, break readers that collapse the two namespaces into one map
and silently merge unrelated objects.
Bug-reporter language: "mixing #NNN and @NNN in same STEP", "value-instance
reference where entity expected", "@1 used as #1", "Ed.3 disjoint namespaces
confused", "@NNN at #NNN slot".

Reproducer recipe:
  #1=PRODUCT(..); @1=POSITIVE_LENGTH_MEASURE(2.5);
  #2=ITEM_DEFINED_TRANSFORMATION('',$,@1);

Byte assertions:
  matches(rb'@\\d+\\s*=')
  matches(rb'@1\\s*=')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh025",
    defect=(
        "Mixing #NNN entity and @NNN value namespaces in the same STEP file (Ed.3); "
        "input: DATA section defines both #1=PRODUCT(..) and @1=POSITIVE_LENGTH_MEASURE(2.5); "
        "then #2=ITEM_DEFINED_TRANSFORMATION uses @1 where an entity-instance #NNN is expected; "
        "Edition 3 introduces @NNN value-instance identifiers alongside #NNN entity-instance identifiers; "
        "the two integer namespaces are disjoint: #1 and @1 are distinct instances; "
        "readers that collapse both namespaces into one map silently merge unrelated objects; "
        "using @-prefix syntax in plain Edition-2 contexts further breaks naive parsers; "
        "OCC silently accepts with diagnostic but loads empty result; "
        "expected kernel behavior: maintain two separate dispatch tables; "
        "reject if an attribute slot expects #NNN but the value reference is @NNN (or vice versa); "
        "synonyms: mixing #NNN and @NNN in same STEP, value-instance reference where entity expected, "
        "@1 used as #1, Ed.3 disjoint namespaces confused, @NNN at #NNN slot"
    ),
)


def _render_lh025() -> str:
    """Render a Part-21 with @NNN value-instance used where #NNN entity-instance is expected."""
    return (
        "ISO-10303-21;\n"
        "/* Lh025: mixing #NNN entity and @NNN value namespaces (Edition 3) */\n"
        "/* ISO 10303-21 Ed.3: #NNN and @NNN are disjoint namespaces; #1 != @1 */\n"
        "/* DEFECT: @1 value-instance used in slot expecting #NNN entity-instance */\n"
        "/* Readers collapsing both namespaces into one map silently merge unrelated objects */\n"
        "/* OCC silently accepts (empty result); catalog requires reject */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh025: mixing #NNN entity and @NNN value namespaces'),'2;1');\n"
        "FILE_NAME('Lh025.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: @1 is an Ed.3 value-instance identifier — not valid here */\n"
        "@1=POSITIVE_LENGTH_MEASURE(2.5);\n"
        "/* DEFECT: ITEM_DEFINED_TRANSFORMATION attribute slot expects #NNN entity reference */\n"
        "/* but @1 (a value-instance) is supplied instead — namespace confusion */\n"
        "#5=ITEM_DEFINED_TRANSFORMATION('transform',$,@1);\n"
        "#6=GEOMETRIC_CURVE_SET('namespace-confusion-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh025(path) -> None:
    Path(path).write_text(_render_lh025())


f.render = _render_lh025  # type: ignore[method-assign]
f.write = _write_lh025    # type: ignore[method-assign]
