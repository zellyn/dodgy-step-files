"""Ad056 — General-transform constructor throws on extreme non-uniform face stretch.

Catalog claim: applying an extreme non-uniform (general) transform to a face
raises a construction-error exception across the API boundary rather than
returning a failure status. Trigger: CARTESIAN_TRANSFORMATION_OPERATOR_3D
with scale factors at 1.0E+18.

Reproducer recipe: CARTESIAN_TRANSFORMATION_OPERATOR_3D with 1.0E+18 scaling;
instantiate transform → unhandled exception escapes API boundary.

Byte assertions:
  contains(b'CARTESIAN_TRANSFORMATION_OPERATOR_3D') and contains(b'1.0E+18')
  contains(b'1.0E+18')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad056",
    defect=(
        "general-transform constructor throws on extreme non-uniform scale: "
        "CARTESIAN_TRANSFORMATION_OPERATOR_3D with 1.0E+18 factor raises "
        "construction-error exception across API boundary; "
        "must return failure status, not crash; OCCT #872; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: CARTESIAN_TRANSFORMATION_OPERATOR_3D with extreme scale.
# The entity form is:
#   CARTESIAN_TRANSFORMATION_OPERATOR_3D(
#     name, axis1, axis2, local_origin, scale, axis3)
# axis1/axis2/axis3 are DIRECTION; local_origin is CARTESIAN_POINT.
# scale is the uniform scale factor — we set to 1.0E+18 to trigger the throw.
#
# We also emit a second form with individual per-axis scale factors (the
# CARTESIAN_TRANSFORMATION_OPERATOR_3D non-uniform variant) to stress the
# general-transform constructor path.

ax1 = f._emit_raw("DIRECTION('x_axis',(1.0E+18,0.,0.))")
ax2 = f._emit_raw("DIRECTION('y_axis',(0.,1.0E+18,0.))")
ax3 = f._emit_raw("DIRECTION('z_axis',(0.,0.,1.0E+18))")
loc = f._emit_raw("CARTESIAN_POINT('origin',(0.,0.,0.))")

# Satisfies: contains(b'CARTESIAN_TRANSFORMATION_OPERATOR_3D') and contains(b'1.0E+18')
f._emit_raw(
    f"CARTESIAN_TRANSFORMATION_OPERATOR_3D('extreme_scale',"
    f"#{ax1.eid},#{ax2.eid},#{loc.eid},1.0E+18,#{ax3.eid})"
)

# Second variant: axis ratios already encode the extreme stretch — any
# downstream code that reads direction ratios directly also hits 1.0E+18.
ax4 = f._emit_raw("DIRECTION('nonuniform_x',(1.0E+18,1.0,1.0))")
loc2 = f._emit_raw("CARTESIAN_POINT('origin2',(1.,2.,3.))")
f._emit_raw(
    f"CARTESIAN_TRANSFORMATION_OPERATOR_3D('nonuniform_scale',"
    f"#{ax4.eid},#{ax2.eid},#{loc2.eid},1.0E+18,#{ax3.eid})"
)
