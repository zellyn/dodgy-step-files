"""Gp136 — ShapeFix_Edge.FixRemovePCurve orphan_pcurves.

Catalog claim: RemoveCurve3d may leave orphaned PCurves on faces without
cleanup. Multi-face edge with inconsistent PCurves on two faces; removing 3D
curve without updating face-edge relationships leaves stale PCurves that cause
downstream validation failures.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge having two associated PCurves in the
    SURFACE_CURVE associated_geometry list (two PCURVE entries for the same
    SURFACE_CURVE, representing the "multi-face" scenario with stale orphan).
  - The second PCurve is a stale orphan: it references a different UV position
    than the actual edge geometry (mismatched UV origin), simulating what remains
    after FixRemovePCurve fails to clean up face-edge relationships.
  - THE CATALOG MECHANISM: SURFACE_CURVE with two PCURVE entries in
    associated_geometry; second PCurve has mismatched UV position (orphan stale
    reference); FixRemovePCurve does not remove the stale entry.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_CURVE with two PCURVEs — first valid, second
    orphan with mismatched UV origin; stale PCurve not removed by FixRemovePCurve.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp136",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE with two PCURVE entries in "
        "associated_geometry: (1) valid PCurve LINE (0,0)→(5,0), "
        "(2) orphan stale PCurve LINE (10,5)→(15,5) mismatched UV position; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "FixRemovePCurve does not remove stale orphan PCurve — "
        "downstream validation fails on stale face-edge reference; shape_null=True"
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

# Face corners: rectangle [0,5] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) with proper pcurves
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

e_right = mk_edge_with_pc(v_b, v_c, (5.0, 0.0, 0.0), (0., 1., 0.), 2.0, (5.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (5.0, 2.0, 0.0), (-1., 0., 0.), 5.0, (5.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # start of second — 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('orphan_pcurve_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: Two PCURVEs in SURFACE_CURVE associated_geometry.
# PCurve 1: valid — LINE (0,0)→(5,0) matching the 3D geometry.
pp_start1 = f.cartesian_point((0.0, 0.0))
pp_dir1   = f.direction((1.0, 0.0))
pp_vec1   = f.vector(pp_dir1, 5.0)
pp_line1  = f.line(pp_start1, pp_vec1)
defrep1 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('orphan_pc_def1',(#{pp_line1.eid}),#{prc.eid})"
)
pcurve1 = f._emit_raw(f"PCURVE('orphan_valid_pc',#{surf.eid},#{defrep1.eid})")

# PCurve 2: stale orphan — LINE (10,5)→(15,5), completely mismatched UV position.
# Simulates the stale PCurve that FixRemovePCurve fails to clean up after
# removing the 3D curve; face-edge relationship left inconsistent.
pp_start2 = f.cartesian_point((10.0, 5.0))
pp_dir2   = f.direction((1.0, 0.0))
pp_vec2   = f.vector(pp_dir2, 5.0)
pp_line2  = f.line(pp_start2, pp_vec2)
defrep2 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('orphan_pc_def2',(#{pp_line2.eid}),#{prc.eid})"
)
pcurve2 = f._emit_raw(f"PCURVE('orphan_stale_pc',#{surf.eid},#{defrep2.eid})")

# SURFACE_CURVE with both PCURVEs: valid + orphan stale
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('orphan_pcurve_sc',#{bspline_3d.eid},"
    f"(#{pcurve1.eid},#{pcurve2.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('orphan_pcurve_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
