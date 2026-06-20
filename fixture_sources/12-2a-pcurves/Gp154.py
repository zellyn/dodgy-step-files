"""Gp154 — ShapeAnalysis_Edge.CheckVerticesWithPCurve selective_vertex_checking

Catalog claim: First vertex offset from 3D curve start; distance check omitted
when vtx==2 parameter set. Analyzer masks V1 discrepancy while checking V2.
Reproduces line 533 defect.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge wrapped in SURFACE_CURVE.
  - THE CATALOG MECHANISM (selective_vertex_checking): CheckVerticesWithPCurve
    at line 533 accepts an optional vtx parameter that restricts vertex checking.
    When vtx==2 is set (check only V2), the V1 distance check is silently skipped.
    The defect edge has V1 placed 0.5 units off the PCurve start projection —
    a genuine discrepancy that would normally flag a V1 mismatch. But with vtx==2
    in effect, only V2 is examined; V1 goes unchecked. OCC heals and produces
    shape(1)/shape(1) because V2 is consistent.
  - 3D curve: a clean LINE. Geometry is valid and loadable.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: vtx==2 selective_vertex_checking at line 533 skips V1
    distance check; V1 at (0.5,0,0) offset from PCurve start projection (0,0,0)
    by 0.5 units; discrepancy masked; selective_vertex_checking axis.
  - NO C-1 DRIVER: Archetype B — geometry is clean and loadable.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp154",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D LINE from (0.5,0,0) to (4.0,0,0) (clean, loadable); "
        "PCurve LINE in UV from (0.0,0.0) direction (1,0): PCurve start projects "
        "to 3D (0,0,0) but V1 vertex is at (0.5,0,0) — 0.5-unit V1 offset; "
        "CheckVerticesWithPCurve (line 533) with vtx==2: V1 distance check skipped; "
        "only V2 checked (V2 at (4,0,0) matches PCurve end at UV=(4,0) → (4,0,0)); "
        "V1 discrepancy silently masked; selective_vertex_checking axis; "
        "OCC heals; shape(1)/shape(1)"
    ),
)

# Host surface: PLANE Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners. V1 of the defect edge is deliberately at (0.5,0,0), not (0,0,0).
# This creates the V1-vs-PCurve-start offset. The other corners close normally.
p_a = f.cartesian_point((0.5, 0.0, 0.0))   # V1 of defect edge — 0.5-unit X offset
p_b = f.cartesian_point((4.0, 0.0, 0.0))   # V2 of defect edge — clean
p_c = f.cartesian_point((4.0, 2.0, 0.0))
p_d = f.cartesian_point((0.5, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge_with_pc(v_b, v_c, (4.0, 0.0, 0.0), (0., 1., 0.), 2.0, (4.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (4.0, 2.0, 0.0), (-1., 0., 0.), 3.5, (4.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.5, 2.0, 0.0), (0., -1., 0.), 2.0, (0.5, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
#
# NO C-1 DRIVER: Archetype B — OCC heals, expected shape(1)/shape(1).
# 3D curve: clean LINE from (0.5,0,0) to (4.0,0,0).
line_3d_orig = f.cartesian_point((0.5, 0.0, 0.0))
line_3d_dir  = f.direction((1.0, 0.0, 0.0))
line_3d_vec  = f.vector(line_3d_dir, 3.5)
line_3d      = f.line(line_3d_orig, line_3d_vec)

# THE CATALOG MECHANISM: PCurve LINE starts at UV=(0,0) — projects to 3D (0,0,0).
# V1 vertex is at (0.5,0,0) in 3D. That is a 0.5-unit discrepancy at V1.
# CheckVerticesWithPCurve with vtx==2: only V2 is checked.
# V2 = (4,0,0); PCurve at t=1 → UV=(3.5,0) → 3D=(3.5,0,0)... but we set PC
# to span from UV=(0,0) to UV=(4,0) so V2 at UV=4 matches 3D (4,0,0) exactly.
# PCurve: LINE from (0,0) direction (1,0), length 4 → endpoint UV=(4,0).
# PCurve start UV=(0,0) → 3D (0,0,0), but V1 is at (0.5,0,0). Gap = 0.5 units.
# vtx==2 path: V1 skip masks the gap; V2 check passes cleanly.
pc_start = f.cartesian_point((0.0, 0.0))
pc_dir   = f.direction((1.0, 0.0))
pc_vec   = f.vector(pc_dir, 4.0)
pc_line  = f.line(pc_start, pc_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('selective_vtx_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('selective_vtx_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('selective_vtx_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('selective_vtx_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
