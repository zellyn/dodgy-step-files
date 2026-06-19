"""Gs151 — FixWireTool seam edge consolidation on TOROIDAL_SURFACE.

Catalog claim: ShapeFix_Face::FixWireTool must consolidate seam edges on
closed (periodic) surfaces; asymmetric handling duplicates or malforms the
seam representation, breaking wire closure.

Previous fixture had only a single vertical LINE edge — that's not a seam
edge on a torus, just an unrelated 3D line in space. Regen: an EDGE_LOOP
that actually contains a seam edge crossing the u=0 / u=2π identification
on a TOROIDAL_SURFACE.
"""
from math import pi
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs151",
             defect="seam-edge consolidation on torus u=0 ≡ u=2π")

# TOROIDAL_SURFACE: major radius 5, minor radius 2, periodic in U and V.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
torus = f._emit_raw(f"TOROIDAL_SURFACE('torus',#{plc.eid},5.0,2.0)")

# Seam edge along u=0: a small minor-circle arc at the X-axis cross-section.
# 3D: arc at (5+2cos(v), 0, 2sin(v)) for v in [0, 2π].
v_start_pt = f.cartesian_point((7.0, 0.0, 0.0))    # u=0, v=0
v_end_pt = v_start_pt                                # full periodic loop
v_start = f.vertex_point(v_start_pt)

# 3D: a circle in the XZ plane centered at (5, 0, 0).
seam_center = f.cartesian_point((5.0, 0.0, 0.0))
y_axis = f.direction((0.0, 1.0, 0.0))
seam_plc = f.axis2_placement_3d(seam_center, y_axis, xdir)
seam_circle = f._emit_raw(f"CIRCLE('seam_3d',#{seam_plc.eid},2.0)")

# This edge is the seam: it lies on the u=0 identification line of the torus.
# Both endpoints are the same vertex (full periodic loop).
seam_edge = f.edge_curve(v_start, v_start, seam_circle)

# Use the same edge twice (.T. and .F.) in the loop — the canonical seam
# pattern that FixWireTool must consolidate.
loop = f.edge_loop([
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(seam_edge, False),
])
face = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
