"""Tfa062 — Face crash during fix on invalid face — null inner wire.

Catalog claim: "An ADVANCED_FACE lists a FACE_BOUND with a null /
unresolvable wire reference. The face-fix routine, when iterating bounds,
dereferences the null wire and segfaults instead of skipping or rejecting."

Demonstration: A valid 10×10 outer face loop plus a second FACE_BOUND whose
EDGE_LOOP slot is a DanglingRef (entity #777, never defined). This matches
the reproducer recipe from OCCT MANTIS#0026524 / #0033179:
    ADVANCED_FACE('',(#outer_bound,#bad_bound),#surface,.T.);
where #bad_bound is a FACE_BOUND pointing to an undefined entity.
A strict parser rejects with E_UNRESOLVED_REFS; OCCT crashes or silently
drops the inner bound.
"""
from step_corpus.step_builder import StepFile, DanglingRef

f = StepFile(catalog_id="Tfa062",
             defect="ADVANCED_FACE with inner FACE_BOUND referencing undefined EDGE_LOOP entity #777")

# -----------------------------------------------------------------------
# Outer boundary: a valid 10×10 rectangle
# -----------------------------------------------------------------------
p0 = f.cartesian_point(( 0.0,  0.0, 0.0))
p1 = f.cartesian_point((10.0,  0.0, 0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point(( 0.0, 10.0, 0.0))
outer_loop = f.closed_polyline_loop([p0, p1, p2, p3])
outer_bound = f.face_outer_bound(outer_loop)

# -----------------------------------------------------------------------
# Inner (hole) FACE_BOUND: the EDGE_LOOP reference is a dangling ref (#777)
# This is the defect: FACE_BOUND points to a non-existent entity.
# -----------------------------------------------------------------------
dangling_loop = DanglingRef(777)
bad_inner_bound = f._emit("FACE_BOUND", dangling_loop, True, name="bad_inner_bound")

# -----------------------------------------------------------------------
# Surface and face
# -----------------------------------------------------------------------
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

# Both the valid outer bound AND the broken inner bound are in the bounds list
face = f.advanced_face([outer_bound, bad_inner_bound], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
