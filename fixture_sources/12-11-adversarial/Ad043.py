"""Ad043 — STEP read raises uncaught exception on null / invalid entity reference.

Catalog claim: reader paths assume non-null entity references and throw an
uncaught exception when a STEP file references a non-existent entity, supplies
a null swept_curve, has an empty edge loop, a STYLED_ITEM with a null item
reference, or a vertex with null name/id.  The exception escapes across the
reader's API boundary and aborts the import.

Reproducer recipe: STYLED_ITEM('',(..),#null) where #null is unresolved.

Byte assertions:
  contains(b'#999')
  contains(b'STYLED_ITEM') and contains(b'#999')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad043",
    defect=(
        "null / dangling entity reference: STYLED_ITEM.item = #999 (never declared); "
        "STYLED_ITEM references swept_curve = #998 (never declared); "
        "reader throws uncaught exception across ABI on unresolved ref; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload 1: STYLED_ITEM whose item ref (#999) is never declared.
# Satisfies: contains(b'STYLED_ITEM') and contains(b'#999').
f._emit_raw(
    "STYLED_ITEM('',(#1),#999)"
)

# Attack payload 2: SURFACE_STYLE_USAGE referencing dangling #999.
f._emit_raw(
    "SURFACE_STYLE_USAGE(.BOTH.,#999)"
)

# Attack payload 3: EXTRUDED_AREA_SOLID with dangling swept_curve #999.
# (bug22871 / bug23157 class: null swept_curve → uncaught exception)
f._emit_raw(
    "EXTRUDED_AREA_SOLID('',#999,#1,10.0)"
)

# Attack payload 4: VERTEX_POINT with null name (empty string) pointing to
# dangling point ref (bug29: NULL vertex name/id family).
f._emit_raw(
    "VERTEX_POINT('',#999)"
)
