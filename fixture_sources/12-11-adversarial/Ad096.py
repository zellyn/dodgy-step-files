"""Ad096 — Crash on AP242 file: access violation reading entity.

Catalog claim: AP242 introduces entities (e.g., TESSELLATED_SHELL,
KINEMATIC_LINK_REPRESENTATION) that older readers do not recognise. Reader
attempts to construct an in-memory entity object and access-violates when
the entity factory returns null.

Reproducer recipe: AP242 STEP file with TESSELLATED_SHELL referencing
triangles. Reader is AP203/AP214-only.

Byte assertions:
  contains(b'TESSELLATED_SHELL')
  contains(b'TESSELLATED')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad096",
    defect=(
        "AP242 TESSELLATED_SHELL entity not recognised by AP203/AP214-only reader; "
        "entity factory returns null for unknown type; "
        "reader access-violates dereferencing the null factory result; "
        "unrecognised entity types must be skipped with diagnostic; "
        "OCCT MANTIS#0027645, #0027404, #0030380; See also A030; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload 1: COORDINATES_LIST (AP242 tessellation support entity).
# Three triangle vertices as a flat coordinate list.
coords = f._emit_raw(
    "COORDINATES_LIST('tess_coords',3,"
    "((0.0,0.0,0.0),(1.0,0.0,0.0),(0.5,1.0,0.0)))"
)

# Attack payload 2: TRIANGULATED_FACE — AP242 tessellated face entity.
# Satisfies: contains(b'TESSELLATED') (via TESSELLATED_SHELL below)
tface = f._emit_raw(
    f"TRIANGULATED_FACE('tess_face',#{coords.eid},$,((.FALSE.,.FALSE.,.FALSE.)),((1,2,3)))"
)

# Attack payload 3: TESSELLATED_SHELL referencing the triangulated face.
# This is the entity type that crashes AP203/AP214 readers (factory returns null).
# Satisfies:
#   contains(b'TESSELLATED_SHELL')
#   contains(b'TESSELLATED')
f._emit_raw(
    f"TESSELLATED_SHELL('ap242_shell',(#{tface.eid}))"
)

# Attack payload 4: KINEMATIC_LINK_REPRESENTATION — another AP242-only entity.
# A second unknown-entity trigger to exercise the same factory-null path.
f._emit_raw(
    "KINEMATIC_LINK_REPRESENTATION('ap242_kinematic',(),#9003)"
)
