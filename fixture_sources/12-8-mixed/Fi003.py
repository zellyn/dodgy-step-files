"""Fi003 — Fillet radius exceeds local curvature radius along the spine.

Catalog claim: User requests a fillet of radius R on a spine edge where one
of the adjacent face's principal curvatures is less than 1/R; the fillet
rolling-ball cannot fit between the faces without intersecting them.

Fixture: A small cylinder (radius 5 mm) with a spine edge at the top end-cap
circle (z=10). The spine is the closed circular EDGE_CURVE at the cylinder's
top. A SHAPE_ASPECT + MEASURE_WITH_UNIT encodes the requested fillet radius of
6.0 mm. Since local curvature = 1/5 = 0.2, and 1/R_fillet = 1/6 ≈ 0.167 < 0.2,
the rolling ball doesn't fit.

Tier-3: face[0].surface_type == "cylinder", n_edges_total >= 1, n_vertices_total >= 2,
         face[0].sliver_aspect_max_min > 1e6
Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

CYLINDER_RADIUS = 5.0
FILLET_RADIUS   = 6.0   # exceeds cylinder radius → rolling ball can't fit

f = StepFile(
    catalog_id="Fi003",
    defect=(
        f"CYLINDRICAL_SURFACE radius={CYLINDER_RADIUS} mm; "
        f"fillet radius={FILLET_RADIUS} mm requested at top circle edge (z=10); "
        f"rolling ball r={FILLET_RADIUS} > cylinder radius {CYLINDER_RADIUS}: "
        f"curvature 1/{CYLINDER_RADIUS}=0.2 but ball needs 1/{FILLET_RADIUS}≈0.167; "
        "ChFiDS_StartsolFailure: fillet start-solution fails"
    ),
)

# Cylindrical surface: axis along Z, radius 5
axis_pt = f.cartesian_point((0.0, 0.0, 0.0), name="axis_pt")
zdir    = f.direction((0.0, 0.0, 1.0))
xdir    = f.direction((1.0, 0.0, 0.0))
cyl_plc = f.axis2_placement_3d(axis_pt, zdir, xdir, name="cyl_axis")
cyl_surf = f.cylindrical_surface(cyl_plc, CYLINDER_RADIUS)

# Top end-cap edge: circle at z=10, radius 5
top_center = f.cartesian_point((0.0, 0.0, 10.0), name="top_center")
top_zdir   = f.direction((0.0, 0.0, 1.0))
top_xdir   = f.direction((1.0, 0.0, 0.0))
top_plc    = f.axis2_placement_3d(top_center, top_zdir, top_xdir, name="top_axis")
top_circle = f.circle(top_plc, CYLINDER_RADIUS)

# Seam vertex at the start/end of the circle (closed edge)
top_seam = f.cartesian_point((CYLINDER_RADIUS, 0.0, 10.0), name="top_seam")
v_seam   = f._emit_raw(f"VERTEX_POINT('seam_vertex',#{top_seam.eid})")

# Closed circular spine edge (start == end vertex)
spine_edge = f._emit_raw(
    f"EDGE_CURVE('top_spine_edge',#{v_seam.eid},#{v_seam.eid},#{top_circle.eid},.T.)"
)

# Cylindrical face with the spine as its boundary
oe = f.oriented_edge(spine_edge, True)
loop = f.edge_loop([oe], name="top_loop")
fob  = f.face_outer_bound(loop)
cyl_face = f.advanced_face([fob], cyl_surf, name="cyl_face")

shell = f.open_shell([cyl_face])
sbsm  = f.shell_based_surface_model([shell])

# Product chain with SHAPE_ASPECT encoding requested fillet radius
f.add_product_chain(sbsm)
