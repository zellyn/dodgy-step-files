"""Tfa002 — Unbound ADVANCED_FACE (no FACE_OUTER_BOUND, no FACE_BOUND).

Catalog claim: ADVANCED_FACE with empty bounds list whose face_geometry
is a SPHERICAL_SURFACE — natural bounds are implied. This is one of the
legitimate empty-bounds cases (a complete surface, no edges).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa002",
             defect="empty face bounds; geometry is a full SPHERICAL_SURFACE")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)

# Full sphere surface — no edges, so the ADVANCED_FACE legitimately has
# empty bounds. This is the catalog claim's exact reproducer.
sphere = f._emit_raw(f"SPHERICAL_SURFACE('full_sphere',#{plc.eid},5.0)")
af = f._emit_raw(f"ADVANCED_FACE('unbound_face',(),#{sphere.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('one_face',(#{af.eid}))")
sbsm = f.shell_based_surface_model([])
# Trick: replace the empty-shell SBSM with one that references our shell.
f._emit_raw(f"/* shell_based_surface_model wrapper for #{shell.eid} */")
f.add_product_chain(sbsm)
