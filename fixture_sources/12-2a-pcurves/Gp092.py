"""Gp092 — ShapeAnalysis_Edge.CheckCurve3dWithPCurve degenerate-pcurve.

Catalog claim: Edge whose pcurve degenerates to a single point.
CheckCurve3dWithPCurve treats degenerate as trivially agreeing with 3D curve.
Fixture has LINE edge with a PCURVE whose DEFINITIONAL_REPRESENTATION contains
a LINE with very small (near-zero) but nonzero magnitude vector (~1e-7).

STEP mechanism (literal):
  - PLANE face. The defect edge is an EDGE_CURVE via SURFACE_CURVE.
  - 3D curve: a clean LINE from (0,0,0) to (4,0,0).
  - PCurve: PCURVE wrapping a DEFINITIONAL_REPRESENTATION containing a LINE
    whose direction vector has magnitude ~1e-7 (nearly zero). This makes the
    pcurve degenerate: it maps the entire edge to a single UV point.
  - THE DEFECT: CheckCurve3dWithPCurve evaluates the degenerate pcurve and
    treats it as trivially agreeing (no span → no mismatch detected).
  - Geometry is valid and loadable: shape(1)/shape(1).

NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp092",
    defect=(
        "PLANE Z=0; defect edge: EDGE_CURVE via SURFACE_CURVE; 3D LINE (0,0,0)"
        "→(4,0,0); PCurve has DEFINITIONAL_REPRESENTATION with LINE whose VECTOR "
        "magnitude=1e-7 (nearly degenerate point at UV origin); "
        "CheckCurve3dWithPCurve treats degenerate as trivially agreeing; "
        "OCC heals cleanly; shape(1)/shape(1)"
    ),
)

# Host surface: planar Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners: rectangle [0,4] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) — with proper SURFACE_CURVE + pcurves
def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


e_right = mk_edge_with_pc(v_b, v_c, (4.0, 0.0, 0.0), (0., 1., 0.), 2.0, (4.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (4.0, 2.0, 0.0), (-1., 0., 0.), 4.0, (4.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────

# 3D curve: clean LINE (0,0,0)→(4,0,0)
line_p = f.cartesian_point((0.0, 0.0, 0.0))
line_d = f.direction((1.0, 0.0, 0.0))
line_v = f.vector(line_d, 4.0)
line_3d = f.line(line_p, line_v)

# THE CATALOG MECHANISM: PCURVE with degenerate DEFINITIONAL_REPRESENTATION.
# The UV LINE has origin at (0,0) and direction (1,0), but the VECTOR magnitude
# is 1e-7 — effectively zero — so the pcurve maps the entire edge to UV≈(0,0).
# CheckCurve3dWithPCurve: no span in pcurve → trivially "agrees" with 3D curve.
pc_pt  = f.cartesian_point((0.0, 0.0))          # UV origin
pc_dir = f.direction((1.0, 0.0))
# Very small magnitude: the pcurve degenerates to a single point
pc_vec = f._emit_raw(f"VECTOR('degen_vec',#{pc_dir.eid},1.0E-7)")
pc_line = f._emit_raw(f"LINE('degen_line',#{pc_pt.eid},#{pc_vec.eid})")

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('degen_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('degen_pcurve',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('degen_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('degen_pcurve_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
