"""Gp010 — Surface_curve.associated_geometry contains a 3D curve in lieu of pcurve.

Catalog claim: A SURFACE_CURVE's associated_geometry slot uses a 3D curve
(e.g. LINE) lying in a PLANE rather than a PCURVE with 2D parameters.
Mathematically valid for flat surfaces, but importers that hardcode the 2D
form fail; consumers cannot evaluate PointAtStart/PointAtEnd because the
path through pcurve→surface is unimplemented.

Fixture: Planar surface (z=0) with an edge whose SURFACE_CURVE.associated_geometry
contains a 3D LINE (not a PCURVE). The line lies in the plane, so it's
geometrically correct, but the defect is that the associated_geometry is
the raw 3D curve instead of a parametric curve in UV space.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp010",
             defect="associated_geometry contains 3D curve in lieu of pcurve")

# Planar surface (z=0)
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f._emit_raw(f"PLANE('',#{plc.eid})")

# 3D curve: line on the plane from (0,0,0) to (1,0,0)
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end = f.cartesian_point((1.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)

line_dir = f.direction((1.0, 0.0, 0.0))
line_vec = f.vector(line_dir, 1.0)
line3d = f.line(p_start, line_vec)

# DEFECT: associated_geometry uses a 3D LINE instead of a PCURVE
# Create a second 3D LINE (in the same location) to put in associated_geometry
# This is syntactically valid for flat surfaces but breaks importers expecting PCURVE
assoc_geom_line = f._emit_raw(
    f"LINE('',#{p_start.eid},#{line_vec.eid})"
)

# SURFACE_CURVE with 3D curve in associated_geometry (not PCURVE)
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{line3d.eid},(#{assoc_geom_line.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
)

# Build the face and shell for the PRODUCT chain
loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
