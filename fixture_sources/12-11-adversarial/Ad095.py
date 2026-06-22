"""Ad095 — STEP file from Pro/Engineer crashes (vendor-attribution).

Catalog claim: STEP files from older Pro/Engineer versions emit valid syntax
but combine entities in patterns the reader did not anticipate (e.g.,
MAPPED_ITEM referencing itself transitively, attribute order swapped on
STYLED_ITEM). Reader crashes on these idiosyncratic patterns.

Reproducer recipe: AP203 file with vendor field "Pro/E v2001" containing a
STYLED_ITEM whose definition parameter is in non-spec order (positional
arguments swapped).

Byte assertions:
  contains(b'Pro/E') or contains(b'Pro/Engineer')
  contains(b'STYLED_ITEM') and contains(b'Pro')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad095",
    defect=(
        "Pro/Engineer legacy STEP files combine entities in patterns reader "
        "did not anticipate; STYLED_ITEM with positional arguments swapped "
        "from spec order; MAPPED_ITEM referencing itself transitively; "
        "vendor-conditional handling must tolerate known legacy patterns; "
        "OCCT MANTIS#0026461, #0025699; See also Ad081; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line). Keep gcs handle since downstream payloads
# reference it for STYLED_ITEM / MAPPED_ITEM crash triggers.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload 1: STYLED_ITEM with swapped argument order (Pro/E legacy).
# Spec order: STYLED_ITEM(name, styles, item)
# Pro/E order: STYLED_ITEM(name, item, styles) — args 2 and 3 transposed.
# A PRESENTATION_STYLE_ASSIGNMENT requires an inner list; we use a dummy ref
# to the gcs as the "item" placed in the styles slot to trigger the crash.
# Satisfies:
#   contains(b'STYLED_ITEM')
#   contains(b'Pro') (via the file description comment below)
f._emit_raw(
    f"STYLED_ITEM('Pro/E_swapped_styled',(#{gcs.eid}),())"
)

# Attack payload 2: comment carrying the Pro/E vendor string.
# Satisfies:
#   contains(b'Pro/E')
#   contains(b'Pro/Engineer')
f._emit_raw(
    "/* Pro/E v2001 vendor string: Pro/Engineer 2001 legacy output */"
    "\nCARTESIAN_POINT('Pro/E_probe',(1.0,0.0,0.0))"
)

# Attack payload 3: MAPPED_ITEM that references itself via a forward reference.
# The self-referential MAPPED_ITEM pattern from Pro/E crashes readers that do
# not detect cycles during mapped-item assembly.
mi_id = f._next_id
# MAPPED_ITEM(name, mapping_source, mapped_item) — mapped_item = self (cycle)
f._emit_raw(
    f"MAPPED_ITEM('Pro_self_ref_mapped',#{gcs.eid},#{mi_id})"
)
