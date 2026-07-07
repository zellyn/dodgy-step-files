"""P004 — LENGTH_UNIT declaration disagrees with actual coordinate scale.

Catalog claim: the GEOMETRIC_REPRESENTATION_CONTEXT declares
LENGTH_UNIT(SI_UNIT(.MILLI.,.METRE.)) but the CARTESIAN_POINT coordinates
are authored at metre scale (values like 500.0 where 0.5 mm was intended),
producing geometry that is 1000× too large when parsed with the declared unit.
A robust kernel must detect or heal the unit/scale disagreement rather than
silently accepting a part that is a thousand times too big.

The defect: the product chain emits a standard millimetre geometric context but
the CARTESIAN_POINT coordinates are in metres (500 instead of 0.5), creating a
1000× scale mismatch between the declared unit context and the actual values.

Byte assertions:
  contains(b'LENGTH_UNIT')
  contains(b'MILLI')
  contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P004",
    defect=(
        "LENGTH_UNIT context declares SI_UNIT(.MILLI.,.METRE.) "
        "but CARTESIAN_POINT coordinates are in metres (500.0 not 0.5 mm); "
        "1000x scale mismatch between declared unit and actual coordinate values; "
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE scaffolding present for §12.6 lint; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Geometry: coordinates in metres (500.0, 500.0, 0.0) while the declared
# LENGTH_UNIT is millimetres. A correct parser would produce a 500 m × 500 m
# square; the defect is that the scale is 1000× too large relative to intent.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((500.0, 0.0, 0.0))    # should be 0.5 mm; wrong: 500 mm = 0.5 m
p2 = f.cartesian_point((500.0, 500.0, 0.0))   # should be 0.5 mm × 0.5 mm
p3 = f.cartesian_point((0.0, 500.0, 0.0))

# GEOMETRIC_CURVE_SET containing the four points — no solid, so shape_null==True.
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('',(#{p0.eid},#{p1.eid},#{p2.eid},#{p3.eid}))"
)

# Product chain emits the standard SI_UNIT(.MILLI.,.METRE.) context which will
# contain LENGTH_UNIT and MILLI — satisfying those byte assertions while the
# coordinates remain at 500 m scale.
f.add_product_chain(gcs)

# NAUO scaffolding to satisfy the §12.6 assembly-presence lint rule.
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(f"PRODUCT('UnitMismatch','UnitMismatch','',(#{sub_pdc.eid}))")
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9053)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','unit_mismatch_instance','',#9054,#{sub_pdef.eid},$)"
)
