"""Wr054 — Swept spherical face orientation inverted on STEP export round-trip.

Catalog claim: a swept-construction body containing a spherical face has
its face_normal direction inverted (`.T.` ↔ `.F.`) on STEP write+read.
The geometry-side surface is still SPHERICAL_SURFACE with the correct
center+radius, but the topology-level orientation flag at the
ADVANCED_FACE level is wrong, so receivers using the topological normal
compute inside-out lighting / inverted volume sign.

Source: pattern-mined from FreeCAD/FreeCAD#14710 (LGPL-clean — pattern
only, no bytes copied). User-reported reproducer: Part Sweep with a
spherical face produces an inverted face after STEP round-trip.

LGPL-clean: pattern-matched, no bytes copied.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Wr054",
             defect="spherical face .T./.F. orientation inverted on round-trip")

# Sphere center at origin, radius 1.
center = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(center, zdir, xdir)
sphere = f._emit_raw(f"SPHERICAL_SURFACE('inverted_sphere',#{plc.eid},1.0)")

# Boundary: a great circle through the equator. Two vertices on the equator.
v_start_pt = f.cartesian_point((1.0, 0.0, 0.0))
v_end_pt = f.cartesian_point((-1.0, 0.0, 0.0))
v_start = f.vertex_point(v_start_pt)
v_end = f.vertex_point(v_end_pt)

equator_plc = f.axis2_placement_3d(center, zdir, xdir)
equator_circle = f._emit_raw(f"CIRCLE('equator',#{equator_plc.eid},1.0)")
edge = f.edge_curve(v_start, v_end, equator_circle)

loop = f.edge_loop([f.oriented_edge(edge, True)])

# The defect: ADVANCED_FACE marked .F. (face_normal flipped) for the
# sphere upper hemisphere. Receivers using the topological normal will
# light it inside-out / compute negative volume.
# Builder API ord. provides advanced_face with .T. by default; we use
# _emit_raw to explicitly mark .F.
face = f._emit_raw(
    f"ADVANCED_FACE('inverted_sphere_upper',(#{f.face_outer_bound(loop).eid}),"
    f"#{sphere.eid},.F.)"   # ← .F. is the writer-pathology mark
)

shell = f._emit_raw(f"OPEN_SHELL('shell_with_inverted_face',(#{face.eid}))")
sbsm = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('sbsm',(#{shell.eid}))")
f.add_product_chain(sbsm)
