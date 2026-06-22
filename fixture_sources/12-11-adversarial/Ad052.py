"""Ad052 — STEP file referencing itself as external file (infinite loop).

Catalog claim: external-file-assignment whose target path resolves to the main
file under translation; reader loops forever.

Reproducer recipe: APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT to same .step
file path.

Byte assertions:
  contains(b'APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT')
  contains(b'EXTERNAL') or contains(b'IDENTIFICATION_ASSIGNMENT')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad052",
    defect=(
        "self-referential external file assignment: "
        "APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT whose target path resolves "
        "to the main file under translation; reader loops forever on self-ref; "
        "Mantis 0031711; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload: APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT referencing
# the same file path as the current file.  The path "Ad052.step" is a
# canonical-path match to the file containing this DATA section.
#
# The entity tree for an AEXA is:
#   EXTERNAL_SOURCE → supplies the file path
#   EXTERNAL_IDENTIFICATION_ASSIGNMENT → holds the ID and source
#   APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT → attaches it to items

ext_src = f._emit_raw(
    "EXTERNAL_SOURCE(('Ad052.step'))"
)

ext_id = f._emit_raw(
    f"EXTERNAL_IDENTIFICATION_ASSIGNMENT('self','self-referential file',"
    f"#{ext_src.eid})"
)

# Satisfies: contains(b'APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT')
# and: contains(b'EXTERNAL') and contains(b'IDENTIFICATION_ASSIGNMENT')
f._emit_raw(
    f"APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT(#{ext_id.eid},"
    f"(#{origin.eid}))"
)

# Second variant using a relative-path alias to the same file
# (canonical path loop attack on systems that normalise './' prefix).
ext_src2 = f._emit_raw(
    "EXTERNAL_SOURCE(('./Ad052.step'))"
)
ext_id2 = f._emit_raw(
    f"EXTERNAL_IDENTIFICATION_ASSIGNMENT('self2','relative self-ref',"
    f"#{ext_src2.eid})"
)
f._emit_raw(
    f"APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT(#{ext_id2.eid},"
    f"(#{origin.eid}))"
)
