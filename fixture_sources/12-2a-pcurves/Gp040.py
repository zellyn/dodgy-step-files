"""Gp040 — Pcurves emitted by default duplicate / contradict the surface 3D curve.

Catalog defect (OCCT MANTIS#0025654): STEP writer emits PCURVE alongside the
3D curve on EDGE_CURVE. The pcurve, computed by a separate pass, disagrees with
the 3D curve at the edge tolerance — producing edges that drift off the surface,
BRepCheck_InvalidEdgeOnSurface errors, or sewing failures. Fixture has a
rectangular PLANE face where the bottom edge's PCURVE is offset 0.1 mm in V
from its actual 3D LINE position, causing 3D/2D disagreement far beyond edge
tolerance (0.001 mm).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp040",
    defect=(
        "SURFACE_CURVE on bottom edge: 3D LINE at y=0, but PCURVE starts at "
        "V=0.1 — a 0.1 mm drift far beyond edge tolerance 0.001 mm; "
        "writer-emitted PCURVE contradicts the 3D curve; "
        "receiver must detect BRepCheck_InvalidEdgeOnSurface and heal"
    ),
)

# Planar surface in the XY plane.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Rectangle corners: (0,0,0), (10,0,0), (10,5,0), (0,5,0)
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((10.0, 0.0, 0.0))
p11 = f.cartesian_point((10.0, 5.0, 0.0))
p01 = f.cartesian_point((0.0, 5.0, 0.0))
v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

# THE DEFECT: bottom edge 3D LINE lies at y=0; pcurve starts at V=0.1 — mismatch.
# 3D: (0,0,0) -> (10,0,0)
d_x    = f.direction((1.0, 0.0, 0.0))
vec_x  = f.vector(d_x, 10.0)
line_bot_3d = f.line(p00, vec_x)

# Pcurve at V=0.1 (DEFECT: should be V=0.0 to match 3D y=0 on the plane).
pc_bot_start = f.cartesian_point((0.0, 0.1))   # DEFECT: V=0.1 instead of V=0.0
pc_bot_dir   = f.direction((1.0, 0.0))
pc_bot_vec   = f.vector(pc_bot_dir, 10.0)
pc_bot_line  = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_pc',#{surf.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bottom',#{line_bot_3d.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bot_edge',#{v00.eid},#{v10.eid},#{sc_bot.eid},.T.)"
)

# Correct right edge: (10,0,0) -> (10,5,0)
d_y   = f.direction((0.0, 1.0, 0.0))
vec_y = f.vector(d_y, 5.0)
line_right_3d = f.line(p10, vec_y)
pc_r_start = f.cartesian_point((10.0, 0.0))
pc_r_dir   = f.direction((0.0, 1.0))
pc_r_vec   = f.vector(pc_r_dir, 5.0)
pc_r_line  = f.line(pc_r_start, pc_r_vec)
pc_r_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_right',(#{pc_r_line.eid}),#{prc.eid})"
)
pcurve_r = f._emit_raw(f"PCURVE('right_pc',#{surf.eid},#{pc_r_def.eid})")
sc_right = f._emit_raw(
    f"SURFACE_CURVE('right',#{line_right_3d.eid},(#{pcurve_r.eid}),.PCURVE_S1.)"
)
edge_right = f._emit_raw(
    f"EDGE_CURVE('right_edge',#{v10.eid},#{v11.eid},#{sc_right.eid},.T.)"
)

# Correct top edge: (10,5,0) -> (0,5,0)
d_xn    = f.direction((-1.0, 0.0, 0.0))
vec_xn  = f.vector(d_xn, 10.0)
line_top_3d = f.line(p11, vec_xn)
pc_t_start = f.cartesian_point((10.0, 5.0))
pc_t_dir   = f.direction((-1.0, 0.0))
pc_t_vec   = f.vector(pc_t_dir, 10.0)
pc_t_line  = f.line(pc_t_start, pc_t_vec)
pc_t_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top',(#{pc_t_line.eid}),#{prc.eid})"
)
pcurve_t = f._emit_raw(f"PCURVE('top_pc',#{surf.eid},#{pc_t_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top',#{line_top_3d.eid},(#{pcurve_t.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('top_edge',#{v11.eid},#{v01.eid},#{sc_top.eid},.T.)"
)

# Correct left edge: (0,5,0) -> (0,0,0)
d_yn    = f.direction((0.0, -1.0, 0.0))
vec_yn  = f.vector(d_yn, 5.0)
line_left_3d = f.line(p01, vec_yn)
pc_l_start = f.cartesian_point((0.0, 5.0))
pc_l_dir   = f.direction((0.0, -1.0))
pc_l_vec   = f.vector(pc_l_dir, 5.0)
pc_l_line  = f.line(pc_l_start, pc_l_vec)
pc_l_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_left',(#{pc_l_line.eid}),#{prc.eid})"
)
pcurve_l = f._emit_raw(f"PCURVE('left_pc',#{surf.eid},#{pc_l_def.eid})")
sc_left = f._emit_raw(
    f"SURFACE_CURVE('left',#{line_left_3d.eid},(#{pcurve_l.eid}),.PCURVE_S1.)"
)
edge_left = f._emit_raw(
    f"EDGE_CURVE('left_edge',#{v01.eid},#{v00.eid},#{sc_left.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(edge_bot,   True),
    f.oriented_edge(edge_right, True),
    f.oriented_edge(edge_top,   True),
    f.oriented_edge(edge_left,  True),
])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
