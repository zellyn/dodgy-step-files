"""Gs052 — Surface of revolution with offset basis curve breaks on export.

Catalog claim: SURFACE_OF_REVOLUTION whose basis curve is an OFFSET_CURVE_3D
referencing a B_SPLINE_CURVE.  On round-trip the offset relationship is lost;
the receiver sees a freshly-evaluated B-spline approximation; edits to the
original curve no longer propagate.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SURFACE_OF_REVOLUTION(basis=OFFSET_CURVE_3D(B_SPLINE_CURVE,...)) IS the
    ADVANCED_FACE.face_geometry; the offset-is-baked defect IS wired into face
    topology.
  - Byte assertions: contains(b'OFFSET_CURVE_3D('),
                     contains(b'SURFACE_OF_REVOLUTION(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_REVOLUTION with basis=OFFSET_CURVE_3D IS
    the ADVANCED_FACE.face_geometry; OFFSET_CURVE_3D referencing B_SPLINE_CURVE
    IS the basis curve; offset IS wired into face topology via surface-of-
    revolution; baked-offset defect IS the face surface.
  - shape_null driver: offset relationship silently dropped → approximated
    B-spline has wrong parameterization; strict heal-or-reject kernels produce
    empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs052",
    defect=(
        "SURFACE_OF_REVOLUTION(basis=OFFSET_CURVE_3D(...)) IS ADVANCED_FACE.face_geometry; "
        "OFFSET_CURVE_3D referencing B_SPLINE_CURVE with offset distance 0.1 IS the basis; "
        "offset relationship baked/lost on export IS the defect wired into face topology; "
        "shape_null (strict reject)"
    ),
)

# ── B_SPLINE_CURVE: the original basis (before offset) ───────────────────────
# Simple degree-1 B-spline: a vertical line segment from (1,0,0) to (1,0,2)
bsc_p0 = f.cartesian_point((1.0, 0.0, 0.0))
bsc_p1 = f.cartesian_point((1.0, 0.0, 2.0))

bsc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gs052_bsc',1,"
    f"(#{bsc_p0.eid},#{bsc_p1.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,2),(0.0,1.0),.UNSPECIFIED.)"
)

# ── OFFSET_CURVE_3D: offset 0.1 from B_SPLINE_CURVE in direction (0,1,0) ─────
# Byte assertion: contains(b'OFFSET_CURVE_3D(')
# OFFSET_CURVE_3D(name, basis_curve, distance, self_intersect, ref_direction)
ref_dir = f.direction((0.0, 1.0, 0.0))
offset_curve = f._emit_raw(
    f"OFFSET_CURVE_3D('gs052_oc',#{bsc.eid},0.1,.F.,#{ref_dir.eid})"
)

# ── SURFACE_OF_REVOLUTION: revolve offset curve around Z-axis ─────────────────
# Byte assertion: contains(b'SURFACE_OF_REVOLUTION(')
# SURFACE_OF_REVOLUTION(name, swept_curve, axis_position)
rev_orig = f.cartesian_point((0.0, 0.0, 0.0))
rev_zdir = f.direction((0.0, 0.0, 1.0))
rev_xdir = f.direction((1.0, 0.0, 0.0))
rev_ax   = f._emit_raw(
    f"AXIS1_PLACEMENT('gs052_rev_ax',#{rev_orig.eid},#{rev_zdir.eid})"
)
surface_of_rev = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('gs052_sor',#{offset_curve.eid},#{rev_ax.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the SURFACE_OF_REVOLUTION ───────────────────────
# The surface is a thin cylinder-like shell (offset 0.1 from r=1 → r=1.1),
# revolved full circle.  Use a simple rectangular patch: U ∈ [0,1], V ∈ [0,1]
# mapping to angle ∈ [0,π/2], height ∈ [0,2].
import math
p_A = f.cartesian_point((1.1,  0.0, 0.0))
p_B = f.cartesian_point(( 0.0, 1.1, 0.0))
p_C = f.cartesian_point(( 0.0, 1.1, 2.0))
p_D = f.cartesian_point((1.1,  0.0, 2.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surface_of_rev.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v_A, v_B, (1.1, 0.0, 0.0), (-1.1, 1.1, 0.0), 1.1*math.sqrt(2),
                  (0.0, 0.0), (1.0, 0.0), math.pi/2)
e1 = mk_edge_line(v_B, v_C, (0.0, 1.1, 0.0), (0.0, 0.0, 1.0), 2.0,
                  (math.pi/2, 0.0), (0.0, 1.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (0.0, 1.1, 2.0), (1.1,-1.1, 0.0), 1.1*math.sqrt(2),
                  (math.pi/2, 1.0), (-1.0, 0.0), math.pi/2)
e3 = mk_edge_line(v_D, v_A, (1.1, 0.0, 2.0), (0.0, 0.0,-1.0), 2.0,
                  (0.0, 1.0), (0.0,-1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SURFACE_OF_REVOLUTION (basis=OFFSET_CURVE_3D) IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], surface_of_rev)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
