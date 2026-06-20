"""Gn038 — BOUNDED_PCURVE LoadONBrep stub (BRL-CAD step-g).

Catalog claim: BOUNDED_PCURVE is a degenerate subclass whose role is to give
a bounded version of an otherwise infinite parametric basis curve. step-g loads
the entity but LoadONBrep falls through to the base-class stub, so the trim
becomes 3D-only and is later re-projected numerically (introducing drift).

OCC behavior: silent-accept observed. Expected: occt=empty (via shape_null=True).

STEP mechanism (literal):
  - BOUNDED_PCURVE references a definitional basis curve on a host surface.
    In STEP AP214/AP242, BOUNDED_PCURVE is defined as a PCURVE whose
    parametric range is bounded; it is stored as a compound entity.
  - The BOUNDED_PCURVE entity appears in SURFACE_CURVE.associated_geometry.
    BRL-CAD step-g's LoadONBrep falls to the base-class stub for this type.
  - C-1 break in the 3D edge curve drives shape_null=True (belt+suspenders).

Mechanism vs driver:
  - CATALOG MECHANISM: BOUNDED_PCURVE in associated_geometry; step-g
    LoadONBrep stub returns false; trim becomes 3D-only; See Gn019, Twi100.
  - C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 drives shape_null.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn038",
    defect=(
        "BOUNDED_PCURVE('bp_on_plane') in SURFACE_CURVE.associated_geometry; "
        "BRL-CAD step-g LoadONBrep stub returns false for BoundedPCurve subtype; "
        "trim loses parametric curve, becomes 3D-only, re-projected with drift; "
        "compliant kernel must defer to definitional basis curve and reparameterise; "
        "OCC silent-accept; See also Gn019, Twi100, Twi101; "
        "C-1 break in 3D edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

# ── HOST SURFACE: flat PLANE at Z=0 ──────────────────────────────────────────
plane_origin = f.cartesian_point((0.0, 0.0, 0.0))
plane_normal = f.direction((0.0, 0.0, 1.0))
plane_ref    = f.direction((1.0, 0.0, 0.0))
plane_ax2 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('plane_ax',#{plane_origin.eid},#{plane_normal.eid},#{plane_ref.eid})"
)
surf = f._emit_raw(f"PLANE('flat_plane',#{plane_ax2.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: BOUNDED_PCURVE in associated_geometry ─────────────────
# The underlying basis pcurve is a 2D LINE in the parametric domain.
# BOUNDED_PCURVE adds a bounding box on top of the basis pcurve.
# BRL-CAD step-g's LoadONBrep stub falls through for BoundedPCurve.

bp_p2d = f.cartesian_point((0.0, 0.0))
bp_d2d = f.direction((1.0, 0.0))
bp_v2d = f.vector(bp_d2d, 1.0)
bp_l2d = f.line(bp_p2d, bp_v2d)

bp_defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bp_basis_def',(#{bp_l2d.eid}),#{prc.eid})"
)
# THE DEFECT: BOUNDED_PCURVE entity in associated_geometry slot.
# BOUNDED_PCURVE is a subtype of PCURVE; BRL-CAD step-g falls to base stub.
bounded_pcurve = f._emit_raw(
    f"BOUNDED_PCURVE('bp_on_plane',#{surf.eid},#{bp_defrep.eid})"
)

# ── C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 ─────────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.25, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit C-1 gap
dc4 = f.cartesian_point((4.75, 0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn038_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# The defect edge uses the BOUNDED_PCURVE in its SURFACE_CURVE
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn038_sc',#{bspline_3d.eid},(#{bounded_pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn038_edge',#{v_a.eid},#{v_b.eid},#{sc_defect.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, length)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 5.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
