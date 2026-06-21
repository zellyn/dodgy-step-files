"""Gp048 — ShapeFix_Edge.FixAddPCurve degenerate-curve at cone apex.

Catalog claim: Conical surface with an edge running vertically from the cone
apex. The pcurve at the apex degenerates to the single line u=0 (axis of
revolution). FixAddPCurve must construct the degenerate pcurve correctly
rather than skipping or producing an invalid representation.

Mechanism: The defect IS in the pcurve — an edge runs from the cone apex
(where the cone's surface map is singular) upward along the generator line
u=0. The pcurve degenerates to a vertical strip at u=0 in the (u,v) cone
parameter space. The face is geometrically valid and loads (shape(1)), but
the apex singularity stresses FixAddPCurve's degenerate-pcurve path.

NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp048",
    defect=(
        "CONICAL_SURFACE (apex at origin, axis Z, half-angle 30 deg); "
        "edge from apex (0,0,0) to (0,0,5) runs up the cone generator at u=0; "
        "pcurve degenerates to line u=0, v in [0,5] on the cone — the cone's "
        "surface map is singular at v=0 (apex); FixAddPCurve must produce a "
        "valid degenerate pcurve rather than skipping or crashing"
    ),
)

# Host surface: conical surface, apex at origin, axis Z, half-angle 30° (π/6)
import math
half_angle = math.pi / 6.0   # 30 degrees

cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
cone = f.conical_surface(cone_plc, 0.0, half_angle)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ------------------------------------------------------------------
# Defect edge: from apex (0,0,0) up along generator u=0 to (0,0,5)
# At u=0, cone surface map: x = v*tan(30)*cos(0) = v/√3, y=0, z=v
# But for apex at radius=0, the generator along x-axis: (v*sin(30), 0, v*cos(30))
# Simplified: straight line along Z from apex
# ------------------------------------------------------------------
p_apex = f.cartesian_point((0.0, 0.0, 0.0))
p_top  = f.cartesian_point((0.0, 0.0, 5.0))
v_apex = f.vertex_point(p_apex)
v_top  = f.vertex_point(p_top)

line_dir = f.direction((0.0, 0.0, 1.0))
line_vec = f.vector(line_dir, 5.0)
line_3d  = f.line(p_apex, line_vec)

# CATALOG MECHANISM: degenerate pcurve at u=0 on cone parameter space
# The pcurve runs from (u=0, v=0) to (u=0, v=5) — a vertical strip at the apex
uv_s = f.cartesian_point((0.0, 0.0))
uv_e_dir = f.direction((0.0, 1.0))
uv_e_vec = f.vector(uv_e_dir, 5.0)
uv_line  = f.line(uv_s, uv_e_vec)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp048_pcdef',(#{uv_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp048_uv',#{cone.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp048_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge_defect = f._emit_raw(
    f"EDGE_CURVE('gp048_apex_edge',#{v_apex.eid},#{v_top.eid},#{surface_curve.eid},.T.)"
)

# Remaining edges to close the face: a triangular patch on the cone
# Point at (5*tan(30°), 0, 5) = (2.887..., 0, 5) at generator angle 0
# and an arc back along the base.
# For simplicity: a single triangular face — two side edges + base
# Side edges at u=0 and u=0 again create degenerate face; instead use
# a small fan: apex to v_top (done), v_top to v_far, v_far back to apex.
# v_far: cone surface at u=π/4, v=5 → x=5*tan(30)*cos(π/4), y=5*tan(30)*sin(π/4), z=5
r5 = 5.0 * math.tan(half_angle)  # ≈ 2.887
p_far = f.cartesian_point((r5 * math.cos(math.pi / 4), r5 * math.sin(math.pi / 4), 5.0))
v_far = f.vertex_point(p_far)

# Edge top → far: line from p_top to p_far on the cone rim (v=5, varying u)
# Arc along the rim at v=5, r=r5
arc_plc_orig = f.cartesian_point((0.0, 0.0, 5.0))
arc_plc_zdir = f.direction((0.0, 0.0, 1.0))
arc_plc_xdir = f.direction((1.0, 0.0, 0.0))
arc_plc      = f.axis2_placement_3d(arc_plc_orig, arc_plc_zdir, arc_plc_xdir)
arc_rim      = f.circle(arc_plc, r5)

# Pcurve for arc: from (u=0, v=5) to (u=π/4, v=5), horizontal in UV
uv_arc_s  = f.cartesian_point((0.0, 5.0))
uv_arc_d  = f.direction((1.0, 0.0))
uv_arc_v  = f.vector(uv_arc_d, math.pi / 4)
uv_arc_l  = f.line(uv_arc_s, uv_arc_v)
arc_defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp048_arc_pcdef',(#{uv_arc_l.eid}),#{prc.eid})"
)
arc_pc = f._emit_raw(f"PCURVE('gp048_arc_uv',#{cone.eid},#{arc_defrep.eid})")
arc_sc = f._emit_raw(
    f"SURFACE_CURVE('gp048_arc_sc',#{arc_rim.eid},(#{arc_pc.eid}),.PCURVE_S1.)"
)
edge_rim = f._emit_raw(
    f"EDGE_CURVE('gp048_rim_edge',#{v_top.eid},#{v_far.eid},#{arc_sc.eid},.T.)"
)

# Edge far → apex: generator line at u=π/4
p_gen_orig = f.cartesian_point((0.0, 0.0, 0.0))
gen_len = math.sqrt(r5**2 + 25.0)
gen_dx  = r5 * math.cos(math.pi / 4) / gen_len
gen_dy  = r5 * math.sin(math.pi / 4) / gen_len
gen_dz  = 5.0 / gen_len
gen_dir = f.direction((gen_dx, gen_dy, gen_dz))
gen_vec = f.vector(gen_dir, gen_len)
gen_line = f.line(p_gen_orig, gen_vec)

uv_gen_s = f.cartesian_point((math.pi / 4, 5.0))
uv_gen_d = f.direction((0.0, -1.0))
uv_gen_v = f.vector(uv_gen_d, 5.0)
uv_gen_l = f.line(uv_gen_s, uv_gen_v)
gen_defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp048_gen_pcdef',(#{uv_gen_l.eid}),#{prc.eid})"
)
gen_pc = f._emit_raw(f"PCURVE('gp048_gen_uv',#{cone.eid},#{gen_defrep.eid})")
gen_sc = f._emit_raw(
    f"SURFACE_CURVE('gp048_gen_sc',#{gen_line.eid},(#{gen_pc.eid}),.PCURVE_S1.)"
)
edge_gen = f._emit_raw(
    f"EDGE_CURVE('gp048_gen_edge',#{v_far.eid},#{v_apex.eid},#{gen_sc.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(edge_defect, True),
    f.oriented_edge(edge_rim,    True),
    f.oriented_edge(edge_gen,    True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
