"""Gp036 — Pcurve shifting on non-periodic surface produces wrong result.

Catalog defect (OCCT MANTIS#0028595): A pcurve-shift routine designed for
periodic surfaces is invoked on a planar (non-periodic) surface. The shift
is by the surface's "period" which is undefined on a plane — returning 0 or
NaN — so the shifted pcurve is invalid. Kernel must reject: pcurve-shifting
is a precondition error on non-periodic surfaces.

Fixture: A rectangular PLANE face whose outer wire pcurves were emitted with
U values outside the face's natural parametric range — simulating what a
sender that mis-fired the shift pass produces. The SURFACE_CURVE carries a
PCURVE whose U start coordinate is shifted by a large amount (10000.0) that
would represent a "period" value, leaving the pcurve outside the face bounds.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp036",
    defect=(
        "PLANE face: pcurve-shift routine applied to non-periodic surface; "
        "outer-wire PCURVE U values shifted by 10000.0 (a pseudo-period) — "
        "invalid on a non-periodic plane; kernel must reject as precondition error"
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

# The planar face in 3D: rectangle (0,0,0)-(1,0,0)-(1,1,0)-(0,1,0).
# 4 corner vertices:
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

# THE DEFECT: all pcurves are shifted by SHIFT=10000.0 in U — simulating what
# a misfired period-shift pass produces on a non-periodic plane.
# The 3D LINE geometry is correct; only the UV coordinates are wrong.
SHIFT = 10000.0

def make_edge_3d_then_pcurve_shifted(p_start_3d, p_end_3d, vert_s, vert_e,
                                     uv_s, uv_e, name):
    """Build a line-edge with correct 3D LINE but U-shifted pcurve."""
    dx = p_end_3d[0] - p_start_3d[0]
    dy = p_end_3d[1] - p_start_3d[1]
    length = (dx*dx + dy*dy) ** 0.5
    # 3D line
    pt3  = f.cartesian_point(p_start_3d)
    d3   = f.direction((dx/length, dy/length, 0.0))
    vec3 = f.vector(d3, length)
    line3d = f.line(pt3, vec3)
    # Shifted pcurve: U offset by SHIFT
    du = uv_e[0] - uv_s[0]
    dv = uv_e[1] - uv_s[1]
    uvlen = (du*du + dv*dv) ** 0.5
    pc_start = f.cartesian_point((uv_s[0] + SHIFT, uv_s[1]))  # DEFECT: shifted
    pc_dir   = f.direction((du/uvlen, dv/uvlen))
    pc_vec   = f.vector(pc_dir, uvlen)
    pc_line  = f.line(pc_start, pc_vec)
    pc_def   = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('pc_{name}',(#{pc_line.eid}),#{prc.eid})"
    )
    pcurve = f._emit_raw(f"PCURVE('pcv_{name}',#{surf.eid},#{pc_def.eid})")
    sc = f._emit_raw(
        f"SURFACE_CURVE('{name}',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
    )
    edge = f._emit_raw(
        f"EDGE_CURVE('{name}',#{vert_s.eid},#{vert_e.eid},#{sc.eid},.T.)"
    )
    return edge

# 4 edges of the rectangle, all with U-shifted pcurves.
e_bot   = make_edge_3d_then_pcurve_shifted(
    (0.0,0.0,0.0),(1.0,0.0,0.0), v00,v10, (0.0,0.0),(1.0,0.0), 'bot')
e_right = make_edge_3d_then_pcurve_shifted(
    (1.0,0.0,0.0),(1.0,1.0,0.0), v10,v11, (1.0,0.0),(1.0,1.0), 'right')
e_top   = make_edge_3d_then_pcurve_shifted(
    (1.0,1.0,0.0),(0.0,1.0,0.0), v11,v01, (1.0,1.0),(0.0,1.0), 'top')
e_left  = make_edge_3d_then_pcurve_shifted(
    (0.0,1.0,0.0),(0.0,0.0,0.0), v01,v00, (0.0,1.0),(0.0,0.0), 'left')

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
