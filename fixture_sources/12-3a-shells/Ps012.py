"""Ps012 — Sweep silently truncated to a CONICAL_SURFACE.

Catalog claim: a producer modelled a "vase" (solid of revolution with B-spline
generatrix that bulges outward). The export pipeline simplified the generatrix
to a straight line, yielding a CONICAL_SURFACE frustum. The file is clean and
topologically sound.

Tier-3: face[0].surface_type == "cone", face[1].surface_type == "plane",
        face[2].surface_type == "plane", n_edges_total >= 4
Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Ps012",
    defect=(
        "Sweep silently truncated to CONICAL_SURFACE: producer intended curved vase "
        "(B-spline generatrix bulging outward at mid-height); export simplified to straight "
        "line, yielding a valid CONICAL_SURFACE frustum (radius 5 at z=0, radius 2 at z=10); "
        "file is clean and topologically sound; defect is producer intent vs export result; "
        "MANIFOLD_SOLID_BREP IS model entity — OCC yields shape(1)"
    ),
)

# Frustum: cone with radius 5 at z=0, radius 2 at z=10
# semi_angle = atan((5-2)/10) = atan(0.3) ≈ 0.2915926 rad
semi_angle = math.atan((5.0 - 2.0) / 10.0)

# Cone surface: apex at z = 10 + 2/tan(semi_angle) = 10 + 2/0.3 = 16.667
apex_z = 10.0 + 2.0 / math.tan(semi_angle)

# AXIS2_PLACEMENT_3D at apex, axis pointing -Z so cone opens downward
cone_orig = f.cartesian_point((0.0, 0.0, apex_z))
cone_zdir = f.direction((0.0, 0.0, -1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
cone_surf = f.conical_surface(cone_plc, radius=0.0, semi_angle=semi_angle)

# Bottom disk (z=0, radius 5)
bot_orig  = f.cartesian_point((0.0, 0.0, 0.0))
bot_zdir  = f.direction((0.0, 0.0, -1.0))
bot_xdir  = f.direction((1.0, 0.0, 0.0))
bot_plc   = f.axis2_placement_3d(bot_orig, bot_zdir, bot_xdir)
bot_plane = f.plane(bot_plc)

# Top disk (z=10, radius 2)
top_orig  = f.cartesian_point((0.0, 0.0, 10.0))
top_zdir  = f.direction((0.0, 0.0, 1.0))
top_xdir  = f.direction((1.0, 0.0, 0.0))
top_plc   = f.axis2_placement_3d(top_orig, top_zdir, top_xdir)
top_plane = f.plane(top_plc)

# Bottom circle (radius 5) and top circle (radius 2) as CIRCLE edges
bot_circle_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
bot_circle = f._emit_raw(f"CIRCLE('',#{bot_circle_plc.eid},5.0)")

top_circle_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 10.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
top_circle = f._emit_raw(f"CIRCLE('',#{top_circle_plc.eid},2.0)")

# Vertices: one on bottom rim, one on top rim (STEP circles need vertex on circle)
v_bot = f.vertex_point(f.cartesian_point((5.0, 0.0, 0.0)))
v_top = f.vertex_point(f.cartesian_point((2.0, 0.0, 10.0)))

# Edge curves for the two circles
e_bot = f._emit_raw(
    f"EDGE_CURVE('bot_circle',#{v_bot.eid},#{v_bot.eid},#{bot_circle.eid},.T.)"
)
e_top = f._emit_raw(
    f"EDGE_CURVE('top_circle',#{v_top.eid},#{v_top.eid},#{top_circle.eid},.T.)"
)

# Bottom face (disk)
bot_loop = f.edge_loop([f.oriented_edge(e_bot, True)])
bot_fob  = f.face_outer_bound(bot_loop)
bot_face = f.advanced_face([bot_fob], bot_plane)

# Top face (disk)
top_loop = f.edge_loop([f.oriented_edge(e_top, True)])
top_fob  = f.face_outer_bound(top_loop)
top_face = f.advanced_face([top_fob], top_plane)

# Cone side face
cone_bot_loop = f.edge_loop([f.oriented_edge(e_bot, False)])
cone_top_loop = f.edge_loop([f.oriented_edge(e_top, True)])
cone_fob  = f.face_outer_bound(cone_bot_loop)
cone_fb   = f._emit_raw(f"FACE_BOUND('',#{cone_top_loop.eid},.T.)")
cone_face = f._emit_raw(
    f"ADVANCED_FACE('',(#{cone_fob.eid},#{cone_fb.eid}),#{cone_surf.eid},.T.)"
)

all_faces = [cone_face, bot_face, top_face]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('ps012_frustum_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('ps012_frustum_solid',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")
