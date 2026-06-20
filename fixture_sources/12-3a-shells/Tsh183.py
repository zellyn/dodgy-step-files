"""Tsh183 — ShapeAnalysis_Shell.LoadShells with-shell-marker-but-no-faces.

Catalog claim: Shape labeled as CLOSED_SHELL but containing zero faces;
LoadShells produces empty entry in result; CheckOrientedShells() on empty
shell causes null dereference or assertion on normal computation.

Mechanism IS the shell structure: A SHELL_BASED_SURFACE_MODEL containing ONE
CLOSED_SHELL with an EMPTY face list IS the defect trigger. The CLOSED_SHELL
entity IS validly formed in STEP syntax (CLOSED_SHELL('empty',()) ) but
contains no ADVANCED_FACE references. LoadShells IS the defect path: it
creates a shell entry for the marker, passes it to downstream processing, and
CheckOrientedShells receives an empty shell — then null-dereferences when
attempting to compute face normals on an empty iterator.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh183",
    defect=(
        "CLOSED_SHELL with EMPTY face list IS the LoadShells defect trigger; "
        "SHELL_BASED_SURFACE_MODEL containing single CLOSED_SHELL('empty',()) — IS the input; "
        "CLOSED_SHELL IS syntactically valid STEP but contains zero ADVANCED_FACE references; "
        "LoadShells creates shell entry for empty marker — IS the defect path entry; "
        "CheckOrientedShells receives empty shell — IS the null-dereference trigger; "
        "normal computation on empty face iterator yields null dereference or assertion — IS the defect; "
        "fix: LoadShells must skip or flag shells with zero faces before downstream processing; "
        "emit E_LOAD_SHELLS_EMPTY_SHELL when CLOSED_SHELL with no faces IS encountered"
    ),
)

# An empty CLOSED_SHELL: no faces wired in at all
# This IS the minimal structure that triggers LoadShells empty-shell defect
shell = f.closed_shell([])   # zero faces — IS the mechanism
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
