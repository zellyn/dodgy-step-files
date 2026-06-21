"""In001 — Model marked Loaded without entities; load skipped silently.

Catalog claim: A reader's data state is "Unloaded"; the file was opened
but the entity table was never populated (e.g., parser bailed silently
after the header). Downstream consumers see an empty model and may not
realize the load was incomplete.

Reproducer recipe:
  A Part-21 file with a valid HEADER but a DATA section that contains
  only a comment, no entities; ENDSEC ends the section.

Byte assertions:
  contains(b'DATA;')
  contains(b'HEADER;')
  count(b'ENDSEC;') >= 2

Tier-3: load == "ok"  (shape_null is secondary; primary is load state)
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="In001",
    defect=(
        "Model marked Loaded without entities; load skipped silently; "
        "OCCT Interface_InterfaceModel.cxx:276 (Interface_StateUnloaded); "
        "a reader data state is Unloaded when the file was opened but the entity "
        "table was never populated — e.g. parser bailed silently after the header; "
        "defect: a Part-21 file with a valid HEADER but a DATA section containing "
        "only a comment and no entities; ENDSEC closes the section; "
        "downstream consumers see an empty model without a diagnostic; "
        "receiver must distinguish empty-data from load-failed with separate diagnostic codes; "
        "never let the consumer see an empty model from a load failure; "
        "must not silently accept failed load; "
        "bug-reporter synonyms: STEP loaded but empty, no entities in file, "
        "kernel imports nothing silently; "
        "GEOMETRIC_CURVE_SET IS NOT used — DATA section intentionally empty of entities"
    ),
)

# No geometry is emitted — the defect is that the DATA section is empty.
# Override render() to produce a file whose DATA section contains only a comment.

_original_render = f.render


def _render_empty_data() -> str:
    # Build the header using the builder's header renderer.
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* This DATA section is intentionally empty of entities. */\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_empty_data  # type: ignore[method-assign]
