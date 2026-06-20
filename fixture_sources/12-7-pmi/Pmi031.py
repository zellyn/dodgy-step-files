"""Pmi031 — Projected zone projection_end is not a plane.

Catalog claim: projected_zone_definition.projection_end references a
non-plane geometry (cylindrical_surface instead of a plane).

Reproducer recipe: projected_zone_definition whose projection_end is a
cylindrical_surface.

Byte assertions:
  contains(b'PROJECTED_ZONE_DEFINITION')
  contains(b'CYLINDRICAL_SURFACE')
  contains(b'POSITION_TOLERANCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi031",
    defect=(
        "PROJECTED_ZONE_DEFINITION.projection_end references a CYLINDRICAL_SURFACE "
        "instead of a plane; spec requires the end face to be planar; receivers must "
        "warn and accept, or reject with E_MISSING_PLANE diagnostic; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Feature to attach the tolerance to.
asp_tol = f._emit_raw("SHAPE_ASPECT('tol_feature','',#9055,.T.)")

# Tolerance value.
tol_val = f._emit_raw("MEASURE_REPRESENTATION_ITEM('tol',LENGTH_MEASURE(0.05),#9056)")

# Axis for the cylindrical surface: placed at origin, Z axis.
axis_origin = f.cartesian_point((0.0, 0.0, 0.0))
axis_dir = f._emit_raw("DIRECTION('',(0.0,0.0,1.0))")
ref_dir = f._emit_raw("DIRECTION('',(1.0,0.0,0.0))")
placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('',#{axis_origin.eid},#{axis_dir.eid},#{ref_dir.eid})"
)

# Defect: projection_end is a CYLINDRICAL_SURFACE, not a plane.
# Radius 10.0 mm — any valid cylinder; the point is the wrong entity type.
cyl_surf = f._emit_raw(
    f"CYLINDRICAL_SURFACE('',#{placement.eid},10.0)"
)

# TOLERANCE_ZONE_FORM to satisfy byte assertion.
zone_form = f._emit_raw("TOLERANCE_ZONE_FORM('cylindrical')")

# PROJECTED_ZONE_DEFINITION: projection_end = cylindrical_surface (wrong type).
proj_zone = f._emit_raw(
    f"PROJECTED_ZONE_DEFINITION(LENGTH_MEASURE(5.0),#{zone_form.eid},#{cyl_surf.eid})"
)

# POSITION_TOLERANCE referencing the projected zone definition.
f._emit_raw(
    f"POSITION_TOLERANCE(#{asp_tol.eid},#{tol_val.eid},#{proj_zone.eid},$)"
)
