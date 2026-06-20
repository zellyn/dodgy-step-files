"""Gp137 — ShapeFix_Face.FixMissingSeam pcurve-translation-period-sync.

Catalog claim: When non-boundary wires require period shift on a closed
surface, 3D geometry is corrected but PCurve UV is not translated. Without
PCurve translation: 3D geometry fixed but UV wraps incorrectly. With translation:
3D-UV consistent.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE (periodic in U, period = 2*pi) with a wire that
    requires a period shift to close correctly.
  - 3D edge: correct 3D geometry after period-shift healing.
  - PCurve: UV position that has NOT been translated by one period in U —
    it sits at u=0 when it should be at u=2*pi after period shift.
    This represents the defect: 3D is fixed but PCurve UV is not updated.
  - THE CATALOG MECHANISM: FixMissingSeam applies period shift to 3D wire
    vertices/edges but does not translate the associated PCurve by the same
    period in U. The PCurve ends up at the wrong U position on the cylinder,
    causing UV wrapping inconsistency even though 3D geometry looks correct.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE (periodic U); PCurve LINE at u=0
    instead of u=2*pi — missing period translation after FixMissingSeam;
    3D edge correct but UV wraps to wrong position.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp137",
    defect=(
        "CYLINDRICAL_SURFACE radius=1.0 periodic U (period=2*pi); defect edge: "
        "SURFACE_CURVE; 3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "PCurve LINE at u=0 (UV origin) instead of u=2*pi=6.2832 — "
        "missing period-translation after FixMissingSeam period shift; "
        "3D wire vertices corrected by period shift but PCurve UV not translated "
        "by one period; UV wraps to wrong U position on cylinder; shape_null=True"
    ),
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Host surface: CYLINDRICAL_SURFACE radius=1.0, axis along Z.
# Periodic in U: period = 2*pi ≈ 6.2832.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
# THE CATALOG MECHANISM: periodic cylindrical surface — period shift required
surf = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl_periodic_surf',#{plc.eid},1.0)")

# Face corners on the cylinder (u in [0, pi/2], v in [0, 2])
# u=0 → (1,0,z), u=pi/2 → (0,1,z)
p_a = f.cartesian_point((1.0, 0.0, 0.0))   # u=0, v=0
p_b = f.cartesian_point((0.0, 1.0, 0.0))   # u=pi/2, v=0
p_c = f.cartesian_point((0.0, 1.0, 2.0))   # u=pi/2, v=2
p_d = f.cartesian_point((1.0, 0.0, 2.0))   # u=0, v=2
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges with proper pcurves
def mk_line_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, len2=None):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    if len2 is None:
        len2 = len3
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len2); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Right edge: v_b → v_c (vertical at u=pi/2)
e_right = mk_line_edge_with_pc(
    v_b, v_c,
    (0.0, 1.0, 0.0), (0., 0., 1.), 2.0,
    (1.5707963, 0.0), (0., 1.), 2.0
)
# Top edge: v_c → v_d (arc at v=2, u=pi/2→0)
e_top = mk_line_edge_with_pc(
    v_c, v_d,
    (0.0, 1.0, 2.0), (-1., 0., 0.), 1.0,
    (1.5707963, 2.0), (-1., 0.), 1.5707963
)
# Left edge: v_d → v_a (vertical at u=0)
e_left = mk_line_edge_with_pc(
    v_d, v_a,
    (1.0, 0.0, 2.0), (0., 0., -1.), 2.0,
    (0.0, 2.0), (0., -1.), 2.0
)

# ── DEFECT EDGE — bottom arc (v_a -> v_b, u=0→pi/2, v=0) ──────────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((1.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.25, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))   # end of first Bezier — C-1 break start
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap from dc2 = C-1 break
dc4 = f.cartesian_point((0.5,  0.75, 0.0))
dc5 = f.cartesian_point((0.0,  1.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('fixmissingseam_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve at u=0 (UV origin) instead of u=2*pi.
# On a periodic cylindrical surface (period=2*pi in U), FixMissingSeam
# shifts wire vertices by one period in 3D but does not translate the
# PCurve UV coordinates. The PCurve should be at u=2*pi=6.2832 to match
# the post-shift 3D geometry, but it remains at u=0.
# This missing UV translation causes the PCurve to wrap to the wrong U position.
pp_start = f.cartesian_point((0.0, 0.0))   # u=0 instead of u=2*pi — the defect
pp_dir   = f.direction((1.0, 0.0))
pp_vec   = f.vector(pp_dir, 1.5707963)     # pi/2 arc length in U
pp_line  = f.line(pp_start, pp_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('fixmissingseam_pc_def',(#{pp_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('fixmissingseam_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('fixmissingseam_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('fixmissingseam_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
