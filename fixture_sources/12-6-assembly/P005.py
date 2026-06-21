"""P005 — Inverted spherical face on certain sweep orientations.

Catalog claim: a face on a sphere produced by sweeping with a particular
profile orientation has its FACE_OUTER_BOUND.orientation reversed in the
output STEP; visually inside-out.  Mirror-sweep variant is correct.

The defect: a MANIFOLD_SOLID_BREP whose single ADVANCED_FACE over a
SPHERICAL_SURFACE has its FACE_OUTER_BOUND with orientation .F. (reversed),
so the face normal points inward.  OCCT heals and loads the shape.

Byte assertions:
  contains(b'SPHERICAL_SURFACE')
  contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(6) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P005",
    defect=(
        "MANIFOLD_SOLID_BREP with a single ADVANCED_FACE over SPHERICAL_SURFACE "
        "whose FACE_OUTER_BOUND has orientation .F. (inverted); "
        "face normal points inward — inside-out sphere face; "
        "sweep-orientation bug from FreeCAD Part workbench; "
        "OCCT heals the orientation and loads shape(1)"
    ),
)

# Build a valid spherical face geometry.
# Sphere radius = 5 mm, centred at origin.
origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir   = f.direction((0.0, 0.0, 1.0))
xdir   = f.direction((1.0, 0.0, 0.0))
plc    = f.axis2_placement_3d(origin, zdir, xdir)

# SPHERICAL_SURFACE: the key byte-assertion entity.
sphere_plc_o = f.cartesian_point((0.0, 0.0, 0.0))
sphere_plc_z = f.direction((0.0, 0.0, 1.0))
sphere_plc_x = f.direction((1.0, 0.0, 0.0))
sphere_plc   = f.axis2_placement_3d(sphere_plc_o, sphere_plc_z, sphere_plc_x)
sphere       = f._emit_raw(f"SPHERICAL_SURFACE('sphere_surf',#{sphere_plc.eid},5.0)")

# Build a degenerate-free single bounding loop for the sphere face.
# Use a point on the equator as a seam vertex; the edge is a full circle seam.
seam_pt    = f.cartesian_point((5.0, 0.0, 0.0))
seam_vx    = f.vertex_point(seam_pt)

# Seam circle on the equatorial plane.
circ_plc_o = f.cartesian_point((0.0, 0.0, 0.0))
circ_plc_z = f.direction((0.0, 0.0, 1.0))
circ_plc_x = f.direction((1.0, 0.0, 0.0))
circ_plc   = f.axis2_placement_3d(circ_plc_o, circ_plc_z, circ_plc_x)
seam_circle = f._emit_raw(f"CIRCLE('seam_circle',#{circ_plc.eid},5.0)")

# A single degenerate seam edge (start==end, full circle — common in sphere STEP).
seam_edge = f._emit_raw(
    f"EDGE_CURVE('seam_edge',#{seam_vx.eid},#{seam_vx.eid},#{seam_circle.eid},.T.)"
)
oe_seam = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{seam_edge.eid},.T.)")
loop    = f._emit_raw(f"EDGE_LOOP('',(#{oe_seam.eid}))")

# FACE_OUTER_BOUND with orientation .F. — the defect (inverted normal).
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.F.)")

# ADVANCED_FACE over the sphere with .T. same-sense, but bound orientation is .F.
face = f._emit_raw(f"ADVANCED_FACE('sphere_face',(#{fob.eid}),#{sphere.eid},.T.)")

# Wrap in CLOSED_SHELL + MANIFOLD_SOLID_BREP and connect product chain.
shell = f._emit_raw(f"CLOSED_SHELL('sphere_shell',(#{face.eid}))")
brep  = f._emit_raw(f"MANIFOLD_SOLID_BREP('inverted_sphere',#{shell.eid})")
f.add_product_chain(brep, mode="brep_shape")

# Assembly-presence scaffolding (COLOUR_RGB satisfies §12.6 lint).
colour = f._emit_raw("COLOUR_RGB('sphere_color',0.4,0.6,0.8)")
fasc   = f._emit_raw(f"FILL_AREA_STYLE_COLOUR('',#{colour.eid})")
fas    = f._emit_raw(f"FILL_AREA_STYLE('',(#{fasc.eid}))")
ssfa   = f._emit_raw(f"SURFACE_STYLE_FILL_AREA(#{fas.eid})")
sss    = f._emit_raw(f"SURFACE_SIDE_STYLE('',(#{ssfa.eid}))")
ssu    = f._emit_raw(f"SURFACE_STYLE_USAGE(.BOTH.,#{sss.eid})")
psa    = f._emit_raw(f"PRESENTATION_STYLE_ASSIGNMENT((#{ssu.eid}))")
f._emit_raw(f"STYLED_ITEM('sphere_style',(#{psa.eid}),#{face.eid})")
