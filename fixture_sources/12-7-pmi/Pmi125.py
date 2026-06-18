"""Pmi125 — LOCATING_FEATURE referencing a non-existent shape aspect (dangling target)

Catalog claim: "AP242 locating_feature (datum-target / inspection locator) is
a SHAPE_ASPECT whose DIMENSIONAL_LOCATION carries a pointer to a second
SHAPE_ASPECT that names what the locator is measured against. A producer that
emits a locator whose target is a forward-declared entity reference that is
never actually instantiated (e.g. #9999) leaves a feature definition with a
dangling pointer."

Demonstration: A SHAPE_ASPECT('locating_feature',..) linked via
DIMENSIONAL_LOCATION whose related_shape_aspect is #9999 (an entity reference
that is never declared). Expected kernel behavior: reject at cross-reference
pass; never silently drop the locator.
"""
from step_corpus.step_builder import StepFile, DanglingRef

f = StepFile(catalog_id="Pmi125",
             defect="LOCATING_FEATURE with dangling shape aspect reference")

# Create minimal base geometry
origin = f.cartesian_point((0.0, 0.0, 0.0))
z_axis = f.direction((0.0, 0.0, 1.0))
x_axis = f.direction((1.0, 0.0, 0.0))
placement = f.axis2_placement_3d(origin, z_axis, x_axis)
plane = f.plane(placement)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="base_face")
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")

# Create the locating feature SHAPE_ASPECT
locating_aspect = f._emit("SHAPE_ASPECT", "locating_feature", "datum target locator", 0)

# Create a DIMENSIONAL_LOCATION that links the locator to a dangling target #9999
# DIMENSIONAL_LOCATION(name, relating_shape_aspect, related_shape_aspect, description)
dangling = DanglingRef(9999)
dim_location = f._emit("DIMENSIONAL_LOCATION", "", locating_aspect, dangling, "")

# The locating_aspect now references a non-existent host
