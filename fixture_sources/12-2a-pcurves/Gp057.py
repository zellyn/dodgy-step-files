"""Gp057 — ShapeFix_Edge.FixAddCurve3d trim-aware extension.

Catalog claim: Edge has only 2D pcurve on trimmed face; FixAddCurve3d
builds 3D curve from pcurve but ignores face trim bounds, extending past
boundary.

Mechanism: The defect IS in the pcurve — a linear pcurve on a
RECTANGULAR_TRIMMED_SURFACE that extends beyond the trim window (u extends
to 1.3 while u_max=1.0). FixAddCurve3d is supposed to clip the generated
3D curve to the face's trim extent before assigning it, but it uses the
full pcurve domain instead. The face loads cleanly (shape(1)) because OCC
heals silently; the bug is that the resulting 3D curve extends past the
face trim boundary.

NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp057",
    defect=(
        "RECTANGULAR_TRIMMED_SURFACE (u ∈ [0,1], v ∈ [0,1]) on PLANE; "
        "pcurve LINE extends from (0,0) to (1.3, 0.8) in UV — u=1.3 exceeds "
        "u_max=1.0 trim boundary; FixAddCurve3d generates 3D curve from full "
        "pcurve domain without clipping to trim window; 3D curve extends past "
        "face boundary; trim-unaware extension IS the defect mechanism"
    ),
)

# Underlying plane Z=0
plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
plc_zdir = f.direction((0.0, 0.0, 1.0))
plc_xdir = f.direction((1.0, 0.0, 0.0))
plc_ax   = f.axis2_placement_3d(plc_orig, plc_zdir, plc_xdir)
base_plane = f._emit_raw(f"PLANE('gp057_base_plane',#{plc_ax.eid})")

# RECTANGULAR_TRIMMED_SURFACE: u ∈ [0,1], v ∈ [0,1]
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gp057_trimmed',#{base_plane.eid},"
    f"0.0,1.0,0.0,1.0,.T.,.T.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices within the trim window (3D coordinates match surface map for plane at Z=0)
p_s = f.cartesian_point((0.0, 0.0, 0.0))
p_e = f.cartesian_point((1.0, 0.8, 0.0))   # at the face boundary
v_s = f.vertex_point(p_s)
v_e = f.vertex_point(p_e)

import math
dx, dy = 1.0, 0.8
ln_len = math.sqrt(dx*dx + dy*dy)
d_3d  = f.direction((dx/ln_len, dy/ln_len, 0.0))
vec_3d = f.vector(d_3d, ln_len)
line_3d = f.line(p_s, vec_3d)

# CATALOG MECHANISM: pcurve extends to (u=1.3, v=0.8) — BEYOND u_max=1.0
# FixAddCurve3d uses full pcurve domain without clipping to [0,1]x[0,1]
uv_s  = f.cartesian_point((0.0, 0.0))
# Pcurve endpoint at (1.3, 0.8) — u=1.3 exceeds trim window u_max=1.0
uv_e_x, uv_e_y = 1.3, 0.8
uv_len = math.sqrt(uv_e_x**2 + uv_e_y**2)
uv_d  = f.direction((uv_e_x/uv_len, uv_e_y/uv_len))
uv_v  = f.vector(uv_d, uv_len)
uv_ln = f.line(uv_s, uv_v)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp057_pcdef',(#{uv_ln.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp057_uv',#{rts.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp057_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('gp057_edge',#{v_s.eid},#{v_e.eid},#{surface_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], rts)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
