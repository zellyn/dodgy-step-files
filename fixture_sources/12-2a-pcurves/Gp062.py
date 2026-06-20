"""Gp062 — ShapeFix_Edge.FixAddPCurve trimmed-surface boundary.

Catalog claim: Edge on RECTANGULAR_TRIMMED_SURFACE (u,v ∈ [0,1]) with 3D
endpoint at (1.0, 1.1, 0.0), extending beyond v_max trim boundary.
FixAddPCurve constructs pcurve without validating trim window constraints.

Mechanism: The edge IS wired into a RECTANGULAR_TRIMMED_SURFACE face, and the
3D endpoint explicitly extends BEYOND the v_max=1.0 trim boundary (to v=1.1).
The pcurve's V endpoint at 1.1 is outside the trim window, which FixAddPCurve
fails to catch.

Tier-3 assertion: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp062",
    defect=(
        "RECTANGULAR_TRIMMED_SURFACE (u ∈ [0,1], v ∈ [0,1]) on underlying PLANE; "
        "edge 3D endpoint at (1.0, 1.1, 0.0) extends BEYOND v_max=1.0 trim boundary; "
        "pcurve V endpoint at 1.1 > v_max; FixAddPCurve constructs pcurve without "
        "trim-window validation → boundary violation IS in edge wired into trimmed face"
    ),
)

# Underlying plane z=0
plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
plc_zdir = f.direction((0.0, 0.0, 1.0))
plc_xdir = f.direction((1.0, 0.0, 0.0))
plc_ax   = f.axis2_placement_3d(plc_orig, plc_zdir, plc_xdir)
base_plane = f._emit_raw(f"PLANE('gp062_base_plane',#{plc_ax.eid})")

# RECTANGULAR_TRIMMED_SURFACE: u ∈ [0,1], v ∈ [0,1]
# This is the trim window — v_max=1.0
rts = f._emit_raw(
    f"RECTANGULAR_TRIMMED_SURFACE('gp062_trimmed',#{base_plane.eid},"
    f"0.0,1.0,0.0,1.0,.T.,.T.)"
)

# 3D edge: from (0,0,0) to (1.0, 1.1, 0.0)
# The endpoint at V=1.1 is BEYOND v_max=1.0 — the defect
p_s = f.cartesian_point((0.0, 0.0, 0.0))
p_e = f.cartesian_point((1.0, 1.1, 0.0))   # v=1.1 > v_max=1.0 ← DEFECT
v_s = f.vertex_point(p_s)
v_e = f.vertex_point(p_e)

dx, dy = 1.0, 1.1
import math
ln_len = math.sqrt(dx*dx + dy*dy)
d_xy  = f.direction((dx/ln_len, dy/ln_len, 0.0))
vec_xy = f.vector(d_xy, ln_len)
line3d = f.line(p_s, vec_xy)

# Pcurve: linear from (u=0, v=0) to (u=1, v=1.1) on the trimmed surface
# The pcurve V endpoint 1.1 exceeds the trim window v_max=1.0.
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
uv_s  = f.cartesian_point((0.0, 0.0))
uv_e  = f.cartesian_point((1.0, 1.1))   # V=1.1 BEYOND v_max=1.0
uv_d  = f.direction((dx/ln_len, dy/ln_len))
uv_v  = f.vector(uv_d, ln_len)
uv_ln = f.line(uv_s, uv_v)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp062_pcdef',(#{uv_ln.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp062_uv',#{rts.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp062_sc',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('gp062_edge',#{v_s.eid},#{v_e.eid},#{surface_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], rts)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
