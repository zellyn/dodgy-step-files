"""Gp038 — Vertex 3D point and pcurve do not match within tolerance.

Catalog defect (OCCT MANTIS#0025634): An edge's vertex V at (1.0, 0.0, 0.0)
is matched by the 3D curve at parameter 0 (correct), but the PCURVE evaluated
at parameter 0 maps to UV (0.5, 0.0), whose 3D image on the surface is
(1.05, 0.0, 0.0) — 0.05 > vertex tolerance. The edge passes the 3D-curve-vs-
vertex check but fails the 2D-pcurve-vs-vertex check. Both must pass
independently; kernel must reject.

Fixture: A rectangular PLANE face (surface is x=U, y=V, z=0). The right
edge has vertex V_right at (1.0, 0.0, 0.0); its 3D LINE starts at
(1.0, 0.0, 0.0) (correct), but its PCURVE LINE starts at UV (1.05, 0.0) —
so surface(1.05, 0.0) = (1.05, 0.0, 0.0) which is 0.05 away from V_right.
Vertex-3D-curve check passes; vertex-pcurve check fails by 0.05.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp038",
    defect=(
        "Right-seam EDGE_CURVE on PLANE: 3D LINE starts at (1.0,0,0) matching "
        "vertex V_right, but PCURVE LINE starts at UV (1.05,0.0) whose 3D image "
        "is (1.05,0,0) — 0.05 beyond vertex tolerance; vertex-pcurve consistency "
        "check fails independently of vertex-3D-curve check"
    ),
)

# Planar surface: XY plane (surface(U,V) -> (U,V,0)).
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

# Rectangle vertices: (0,0,0), (1,0,0), (1,1,0), (0,1,0).
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))  # V_right_bot
p11 = f.cartesian_point((1.0, 1.0, 0.0))  # V_right_top
p01 = f.cartesian_point((0.0, 1.0, 0.0))
v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

# Helper: correct edge with matching 3D LINE and pcurve LINE.
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

e_bot  = make_correct_edge(
    (0.0,0.0,0.0),(1.0,0.0,0.0), v00,v10, (0.0,0.0),(1.0,0.0), 'bot')
e_top  = make_correct_edge(
    (1.0,1.0,0.0),(0.0,1.0,0.0), v11,v01, (1.0,1.0),(0.0,1.0), 'top')
e_left = make_correct_edge(
    (0.0,1.0,0.0),(0.0,0.0,0.0), v01,v00, (0.0,1.0),(0.0,0.0), 'left')

# ---- THE DEFECT: right edge — 3D LINE correct, PCURVE LINE U-offset by +0.05 ----
# 3D LINE: from (1.0, 0.0, 0.0) in +Y direction, magnitude=1.0 (correct).
# Vertex v10 is at (1.0, 0.0, 0.0) — 3D check passes.
right_pt3  = f.cartesian_point((1.0, 0.0, 0.0))
right_d3   = f.direction((0.0, 1.0, 0.0))
right_vec3 = f.vector(right_d3, 1.0)
right_line3d = f.line(right_pt3, right_vec3)
# PCURVE: LINE starts at UV (1.05, 0.0) — DEFECT: should be (1.0, 0.0).
# On the XY plane, surface(1.05, 0.0) = (1.05, 0.0, 0.0), which is 0.05
# from vertex V_right at (1.0, 0.0, 0.0) — beyond vertex tolerance.
pc_right_start = f.cartesian_point((1.05, 0.0))    # DEFECT: should be (1.0, 0.0)
pc_right_dir   = f.direction((0.0, 1.0))
pc_right_vec   = f.vector(pc_right_dir, 1.0)
pc_right_line  = f.line(pc_right_start, pc_right_vec)
pc_right_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_right_offset',(#{pc_right_line.eid}),#{prc.eid})"
)
pcurve_right = f._emit_raw(f"PCURVE('right_uoffset',#{surf.eid},#{pc_right_def.eid})")
sc_right = f._emit_raw(
    f"SURFACE_CURVE('right_edge',#{right_line3d.eid},(#{pcurve_right.eid}),.PCURVE_S1.)"
)
e_right = f._emit_raw(
    f"EDGE_CURVE('right_edge',#{v10.eid},#{v11.eid},#{sc_right.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
