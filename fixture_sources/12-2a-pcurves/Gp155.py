"""Gp155 — ShapeAnalysis_Edge.CheckCurve3dWithPCurve pcurve_extraction_failure

Catalog claim: Empty P-curve representation with null curve data; extraction
fails silently at FAIL1 status. Analyzer masks missing parametric curve without
reporting diagnostic. Reproduces line 391 defect.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge wrapped in SURFACE_CURVE.
  - THE CATALOG MECHANISM (pcurve_extraction_failure): CheckCurve3dWithPCurve
    at line 391 calls BRep_Tool::PCurve to extract the parametric curve from the
    edge. When the SURFACE_CURVE references a PCURVE whose DEFINITIONAL_REPRESENTATION
    contains an empty curve list '()' (no actual curve entity), the extraction
    returns a null handle. The function sets FAIL1 status internally but returns
    without emitting a user-visible diagnostic — the caller never receives a
    pcurve_extraction_failure report. OCC chokes on the null pcurve handle when
    attempting shape construction → shape_null=True.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: PCURVE DEFINITIONAL_REPRESENTATION with empty curve list
    '()'; BRep_Tool::PCurve returns null handle; FAIL1 status set at line 391;
    no diagnostic emitted to caller; pcurve_extraction_failure axis.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp155",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "PCURVE references DEFINITIONAL_REPRESENTATION with empty curve list '()'; "
        "BRep_Tool::PCurve extraction returns null handle; "
        "CheckCurve3dWithPCurve sets FAIL1 at line 391 silently; "
        "no pcurve_extraction_failure diagnostic emitted; "
        "shape_null=True"
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

# Face corners: rectangle [0,5] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
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

e_right = mk_edge_with_pc(v_b, v_c, (5.0, 0.0, 0.0), (0., 1., 0.), 2.0, (5.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (5.0, 2.0, 0.0), (-1., 0., 0.), 5.0, (5.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('pcurve_extraction_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: DEFINITIONAL_REPRESENTATION with an EMPTY curve list.
# The '()' item list means there is no curve entity inside the representation.
# BRep_Tool::PCurve dereferences the representation and finds no geometry entity;
# it returns a null handle. CheckCurve3dWithPCurve sets FAIL1 at line 391 but
# does not propagate a user-visible pcurve_extraction_failure diagnostic.
empty_defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcurve_null_def',(),#{prc.eid})"
)
null_pcurve = f._emit_raw(
    f"PCURVE('pcurve_null',#{surf.eid},#{empty_defrep.eid})"
)
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('pcurve_extraction_sc',#{bspline_3d.eid},(#{null_pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('pcurve_extraction_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
