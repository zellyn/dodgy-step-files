"""Pmi106 — SLOT/GROOVE/BOSS reference non-existent host face (dangling GISU target)

Catalog claim: "AP242 feature definitions (SLOT, GROOVE, BOSS, etc.) link to
host geometry via GEOMETRIC_ITEM_SPECIFIC_USAGE whose definition references
the host face's ADVANCED_FACE entity id. A producer that emits SHAPE_ASPECT/
GISU records for SLOT, GROOVE, and BOSS — all pointing at entity id #9999
which is never declared in the file — leaves three orphaned feature definitions."

Demonstration: Three SHAPE_ASPECT records (SLOT, GROOVE, BOSS) each linked
through GEOMETRIC_ITEM_SPECIFIC_USAGE with dangling reference to #9999.
Expected kernel behavior: reject at cross-reference pass and name dangling
targets; never silently drop feature linkages.
"""
from step_corpus.step_builder import StepFile, DanglingRef

f = StepFile(catalog_id="Pmi106",
             defect="SLOT/GROOVE/BOSS features with dangling GISU host face references")

# Create a minimal base geometry (single face)
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
face = f.advanced_face([fob], plane, name="host_face")
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")

# Now emit AP242 feature definitions with dangling GISU references
# SHAPE_ASPECT for SLOT, dangling target #9999
slot_aspect = f._emit("SHAPE_ASPECT", "SLOT", "SLOT feature", 0)

# SHAPE_ASPECT for GROOVE, dangling target #9999
groove_aspect = f._emit("SHAPE_ASPECT", "GROOVE", "GROOVE feature", 0)

# SHAPE_ASPECT for BOSS, dangling target #9999
boss_aspect = f._emit("SHAPE_ASPECT", "BOSS", "BOSS feature", 0)

# GEOMETRIC_ITEM_SPECIFIC_USAGE linking each feature to dangling #9999
dangling = DanglingRef(9999)
f._emit("GEOMETRIC_ITEM_SPECIFIC_USAGE", "gisu_slot", slot_aspect, dangling)
f._emit("GEOMETRIC_ITEM_SPECIFIC_USAGE", "gisu_groove", groove_aspect, dangling)
f._emit("GEOMETRIC_ITEM_SPECIFIC_USAGE", "gisu_boss", boss_aspect, dangling)
