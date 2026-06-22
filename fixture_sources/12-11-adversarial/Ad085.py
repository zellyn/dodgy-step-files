"""Ad085 — Composite-curve-segment self-cyclic reference.

Catalog claim: a composite curve whose segment list contains a reference back
to the curve itself. The receiver must detect the cycle during composite-curve
assembly and reject with E_CURVE_CYCLE; instead it recurses infinitely or
silently accepts with no model.

Reproducer recipe:
  #1=COMPOSITE_CURVE('',(#2),.T.);
  #2=COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#1);

Byte assertions:
  contains(b'COMPOSITE_CURVE') and contains(b'COMPOSITE_CURVE_SEGMENT')
  count_entity_def(b'COMPOSITE_CURVE_SEGMENT') >= 1

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad085",
    defect=(
        "COMPOSITE_CURVE whose segment list references COMPOSITE_CURVE_SEGMENT "
        "that references back the parent curve (self-cycle); "
        "cycle-detect must reject with E_CURVE_CYCLE; "
        "OCC silently accepts with empty result; "
        "Q023; See also Ad004, Gs035, Pf010; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload: composite curve self-cycle.
# We need to know the two entity IDs before emitting:
#   cc_id   = COMPOSITE_CURVE
#   seg_id  = COMPOSITE_CURVE_SEGMENT (references cc_id back)
cc_id = f._next_id
seg_id = cc_id + 1

# #cc_id = COMPOSITE_CURVE with segment list pointing at #seg_id
# Satisfies: contains(b'COMPOSITE_CURVE')
f._emit_raw(f"COMPOSITE_CURVE('',( #{seg_id}),.T.)")

# #seg_id = COMPOSITE_CURVE_SEGMENT whose parent_curve is #cc_id (the cycle)
# Satisfies: contains(b'COMPOSITE_CURVE_SEGMENT')
#            count_entity_def(b'COMPOSITE_CURVE_SEGMENT') >= 1
f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{cc_id})")

# Second variant: two-node cycle between distinct COMPOSITE_CURVEs.
# This exercises multi-hop cycle detection.
cc_a_id = f._next_id
cc_b_id = cc_a_id + 1
seg_a_id = cc_b_id + 1
seg_b_id = seg_a_id + 1

f._emit_raw(f"COMPOSITE_CURVE('a',(#{seg_a_id}),.T.)")   # cc_a → seg_a → cc_b
f._emit_raw(f"COMPOSITE_CURVE('b',(#{seg_b_id}),.T.)")   # cc_b → seg_b → cc_a
f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{cc_b_id})")  # seg_a
f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{cc_a_id})")  # seg_b
