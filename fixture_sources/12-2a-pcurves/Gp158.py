"""Gp158 — ShapeAnalysis_Surface.ProjectDegenerated whole-edge-degenerate

Catalog claim: All pcurve points collapse to singularity; even-spacing fallback
not triggered. Inconsistent parametric values remain unmapped. Cone with entire
pcurve at u=0 (apex), varying v in [0, 1].

STEP mechanism (literal):
  - CONICAL_SURFACE (half-angle 30 deg, radius 0 at apex) face with a defect
    edge whose entire pcurve lies on the u=0 singular line.
  - THE CATALOG MECHANISM (whole-edge-degenerate): The entire defect edge pcurve
    traces u=0 from v=0 (the apex itself) to v=1. Every pcurve sample point
    lies on the degenerate line u=0. ProjectDegenerated should detect that ALL
    points collapse to the singularity and trigger an even-spacing fallback to
    redistribute parametric values. Without the fallback, all v values remain
    unmapped against the 3D position (which varies along the edge), leaving
    inconsistent parametric data. OCC heals the shape and produces
    shape(1)/shape(1).
  - 3D curve: a clean LINE from the apex (0,0,0) toward the base rim. Geometry
    is valid and loadable.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: CONICAL_SURFACE apex at u=0, v=0; entire PCurve at u=0,
    v in [0,1]; all pcurve samples collapse to singularity; even-spacing fallback
    not triggered; inconsistent parametric values; whole-edge-degenerate axis;
    OCC heals silently.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp158",
    defect=(
        "CONICAL_SURFACE half_angle=30deg radius=0 (apex at origin); "
        "defect edge: SURFACE_CURVE; "
        "3D LINE from apex (0,0,0) to rim point (0.577,0,1.0) (clean, loadable); "
        "PCurve LINE entirely at u=0: from (0.0,0.0) to (0.0,1.0) — whole edge "
        "on cone apex singularity line; ProjectDegenerated: all sample points "
        "collapse to u=0 singularity; even-spacing fallback not triggered; "
        "inconsistent parametric values remain; whole-edge-degenerate axis; "
        "OCC heals; shape(1)/shape(1)"
    ),
)

HALF_ANGLE = math.pi / 6.0   # 30 degrees
tan_a = math.tan(HALF_ANGLE)  # ~0.5774

# CONICAL_SURFACE with radius=0 at v=0 (apex at origin).
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
cone  = f._emit_raw(
    f"CONICAL_SURFACE('cone_whole_degen',#{plc.eid},0.0,{HALF_ANGLE})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Build a 3-edge triangular patch on the cone:
# Apex A = (0,0,0), B = (u=pi/2, v=1) = (0, tan_a, 1), D = (u=0, v=1) = (tan_a, 0, 1).
# The defect edge is A→D: entirely along u=0, from v=0 (apex) to v=1.
# Supporting edges: A→B (along u=pi/2 from apex to rim), B→D (arc at v=1).

apex_3d = (0.0, 0.0, 0.0)

def cone_pt(u_rad, v_h):
    return (math.cos(u_rad)*v_h*tan_a, math.sin(u_rad)*v_h*tan_a, v_h)

# Use v=1 for the rim.
B3 = cone_pt(math.pi / 2.0, 1.0)   # (0, tan_a, 1)
D3 = cone_pt(0.0,           1.0)   # (tan_a, 0, 1)

p_apex = f.cartesian_point(apex_3d); v_apex = f.vertex_point(p_apex)
p_B    = f.cartesian_point(B3);      v_B    = f.vertex_point(p_B)
p_D    = f.cartesian_point(D3);      v_D    = f.vertex_point(p_D)

def mk_line_edge_with_pc(vs, ve, p3, d3, len3, p2, d2, len2):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2)
    d2e = f.direction(d2); v2e = f.vector(d2e, len2); l2 = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{cone.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Edge apex→B: along u=pi/2 from v=0 to v=1; 3D chord from (0,0,0) to B3.
chord_AB = B3  # since apex is (0,0,0)
len_AB   = math.sqrt(sum(x*x for x in chord_AB))
d_AB     = tuple(x/len_AB for x in chord_AB)
e_AB = mk_line_edge_with_pc(
    v_apex, v_B,
    apex_3d, d_AB, len_AB,
    (math.pi/2.0, 0.0), (0.0, 1.0), 1.0
)

# Edge B→D: rim chord at v=1, u=pi/2→0.
chord_BD = tuple(D3[i]-B3[i] for i in range(3))
len_BD   = math.sqrt(sum(x*x for x in chord_BD))
d_BD     = tuple(x/len_BD for x in chord_BD)
e_BD = mk_line_edge_with_pc(
    v_B, v_D,
    B3, d_BD, len_BD,
    (math.pi/2.0, 1.0), (-1.0, 0.0), math.pi/2.0
)

# ── DEFECT EDGE D→apex — entirely on u=0 singularity line ─────────────────────
#
# THE CATALOG MECHANISM: PCurve LINE at u=0, v from 1 down to 0 (toward apex).
# ALL pcurve points lie on the u=0 singular line of the cone.
# ProjectDegenerated samples this pcurve; every sample collapses to the
# singularity; even-spacing fallback should redistribute v values but is not
# triggered. 3D counterpart: LINE from D3=(tan_a,0,1) to apex (0,0,0).
# OCC heals the inconsistency → shape(1)/shape(1).
# NO C-1 break: Archetype B.
chord_DA = tuple(apex_3d[i]-D3[i] for i in range(3))
len_DA   = math.sqrt(sum(x*x for x in chord_DA))
d_DA     = tuple(x/len_DA for x in chord_DA)

line_3d_orig_DA = f.cartesian_point(D3)
line_3d_dir_DA  = f.direction(d_DA)
line_3d_vec_DA  = f.vector(line_3d_dir_DA, len_DA)
line_3d_DA      = f.line(line_3d_orig_DA, line_3d_vec_DA)

# PCurve: LINE at u=0, from (0.0, 1.0) to (0.0, 0.0) — entire edge on u=0.
pc_start_DA = f.cartesian_point((0.0, 1.0))
pc_dir_DA   = f.direction((0.0, -1.0))   # decreasing v (toward apex)
pc_vec_DA   = f.vector(pc_dir_DA, 1.0)
pc_line_DA  = f.line(pc_start_DA, pc_vec_DA)

defrep_DA = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('whole_degen_pc_def',(#{pc_line_DA.eid}),#{prc.eid})"
)
pcurve_DA = f._emit_raw(f"PCURVE('whole_degen_pc',#{cone.eid},#{defrep_DA.eid})")
sc_DA = f._emit_raw(
    f"SURFACE_CURVE('whole_degen_sc',#{line_3d_DA.eid},(#{pcurve_DA.eid}),.PCURVE_S1.)"
)
e_DA = f._emit_raw(
    f"EDGE_CURVE('whole_degen_edge',#{v_D.eid},#{v_apex.eid},#{sc_DA.eid},.T.)"
)

# Triangle: apex→B, B→D, D→apex
loop = f.edge_loop([
    f.oriented_edge(e_AB, True),
    f.oriented_edge(e_BD, True),
    f.oriented_edge(e_DA, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
