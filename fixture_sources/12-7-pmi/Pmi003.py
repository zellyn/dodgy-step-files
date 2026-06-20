"""Pmi003 — Stacked vs composite tolerance frames mis-tagged.

Catalog claim: Two parallelism tolerances drawn one above the other in the
same FCF are merely "stacked" (semantically independent), but the writer
emits a GEOMETRIC_TOLERANCE_RELATIONSHIP with name='composite'. True
composite tolerances must use the 'composite' relationship; stacked
tolerances must not. Receivers that count composite frames will inflate
their count.

Byte assertions:
  count_entity_def(b'PARALLELISM_TOLERANCE') == 2
  contains(b'GEOMETRIC_TOLERANCE_RELATIONSHIP')
  contains(b'composite') or contains(b'stacked')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi003",
    defect=(
        "two stacked PARALLELISM_TOLERANCE instances mis-tagged via "
        "GEOMETRIC_TOLERANCE_RELATIONSHIP(name='composite'); "
        "receivers inflate composite-frame count; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT,
# #9060=GEOMETRIC_REPRESENTATION_CONTEXT

# Two shape aspects to tolerance.
asp1 = f._emit_raw("SHAPE_ASPECT('top_face','',#9055,.T.)")
asp2 = f._emit_raw("SHAPE_ASPECT('side_face','',#9055,.T.)")

# Datum reference for the parallelism tolerances.
datum = f._emit_raw("DATUM('A','primary',#9055,.T.,'A')")
datum_ref_elem = f._emit_raw(f"DATUM_REFERENCE_ELEMENT('',$,#{datum.eid})")
datum_ref_comp = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('',$,#{datum_ref_elem.eid})")
datum_sys = f._emit_raw(
    f"DATUM_SYSTEM('A','',#9055,.T.,(#{datum_ref_comp.eid}))"
)

# Tolerance value (0.05 mm).
tol_val = f._emit_raw(
    "LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.05),#9056)"
)

# Two semantically independent (stacked) PARALLELISM_TOLERANCE instances.
par1 = f._emit_raw(
    f"PARALLELISM_TOLERANCE('par1',$,#{tol_val.eid},#{asp1.eid},#{datum_sys.eid})"
)
par2 = f._emit_raw(
    f"PARALLELISM_TOLERANCE('par2',$,#{tol_val.eid},#{asp2.eid},#{datum_sys.eid})"
)

# Defect: stacked frames mis-tagged as 'composite'.
# A true composite tolerance would require this relationship; stacked must not use it.
f._emit_raw(
    f"GEOMETRIC_TOLERANCE_RELATIONSHIP('composite',"
    f"'stacked frames mis-tagged as composite',#{par1.eid},#{par2.eid})"
)
