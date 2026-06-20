"""Gp037 — Pcurve projection produces infinite line instead of bounded.

Catalog defect (OCCT MANTIS#0026198): A 3D curve segment with parameter range
[0,1] is projected onto a plane to compute a pcurve. The resulting PCURVE
entity stores a LINE with an astronomically large magnitude (simulating an
effectively unbounded/infinite parameter range) instead of being bounded to
[0,1]. Downstream face-bound check and mesher read the unbounded curve and
either crash or produce infinite tessellation.

Fixture: A rectangular PLANE face with one edge (the bottom) whose PCURVE
carries a LINE with magnitude 1e30 (infinite) instead of 1.0, while the 3D
LINE correctly spans [0,1] over a 1-unit segment. The other three edges are
correct. This embodies the "projection emits infinite parameter range" defect.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp037",
    defect=(
        "Bottom edge PCURVE on PLANE has LINE magnitude 1e30 (effectively infinite) "
        "while the 3D LINE spans [0,1] over 1 unit; projection range does not match "
        "input curve range — unbounded pcurve crashes mesher"
    ),
)

# Planar surface: XY plane.
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

# Rectangle vertices (0,0,0)-(1,0,0)-(1,1,0)-(0,1,0).
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

# ---- THE DEFECT: bottom edge pcurve with magnitude 1e30 ----
# 3D LINE: from (0,0,0) in +X direction, magnitude=1.0 (correct)
bot_pt3  = f.cartesian_point((0.0, 0.0, 0.0))
bot_d3   = f.direction((1.0, 0.0, 0.0))
bot_vec3 = f.vector(bot_d3, 1.0)
bot_line3d = f.line(bot_pt3, bot_vec3)
# PCURVE: LINE at UV (0,0) in +U direction — DEFECT: magnitude is 1e30
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir   = f.direction((1.0, 0.0))
pc_bot_vec   = f.vector(pc_bot_dir, 1.0e30)   # DEFECT: should be 1.0
pc_bot_line  = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot_infinite',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_infinite',#{surf.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot_edge',#{bot_line3d.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bot_edge',#{v00.eid},#{v10.eid},#{sc_bot.eid},.T.)"
)

# ---- Remaining 3 edges: correct geometry ----
def make_correct_edge(p_s, p_e, vs, ve, uv_s, uv_e, name):
    dx = p_e[0] - p_s[0]
    dy = p_e[1] - p_s[1]
    length = (dx*dx + dy*dy) ** 0.5
    pt3  = f.cartesian_point(p_s)
    d3   = f.direction((dx/length, dy/length, 0.0))
    v3   = f.vector(d3, length)
    l3d  = f.line(pt3, v3)
    du = uv_e[0] - uv_s[0]
    dv = uv_e[1] - uv_s[1]
    uvlen = (du*du + dv*dv) ** 0.5
    pc_s = f.cartesian_point(uv_s)
    pc_d = f.direction((du/uvlen, dv/uvlen))
    pc_v = f.vector(pc_d, uvlen)
    pc_l = f.line(pc_s, pc_v)
    pc_def = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('pc_{name}',(#{pc_l.eid}),#{prc.eid})"
    )
    pcv = f._emit_raw(f"PCURVE('pcv_{name}',#{surf.eid},#{pc_def.eid})")
    sc  = f._emit_raw(
        f"SURFACE_CURVE('{name}',#{l3d.eid},(#{pcv.eid}),.PCURVE_S1.)"
    )
    return f._emit_raw(
        f"EDGE_CURVE('{name}',#{vs.eid},#{ve.eid},#{sc.eid},.T.)"
    )

e_right = make_correct_edge(
    (1.0,0.0,0.0),(1.0,1.0,0.0), v10,v11, (1.0,0.0),(1.0,1.0), 'right')
e_top   = make_correct_edge(
    (1.0,1.0,0.0),(0.0,1.0,0.0), v11,v01, (1.0,1.0),(0.0,1.0), 'top')
e_left  = make_correct_edge(
    (0.0,1.0,0.0),(0.0,0.0,0.0), v01,v00, (0.0,1.0),(0.0,0.0), 'left')

loop = f.edge_loop([
    f.oriented_edge(edge_bot, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
