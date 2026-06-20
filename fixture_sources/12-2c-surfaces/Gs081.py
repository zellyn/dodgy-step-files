"""Gs081 — ShapeAnalysis_Surface.IsUClosed extrusion-base form.

Catalog claim: SURFACE_OF_LINEAR_EXTRUSION with open parabolic base curve.
IsUClosed correctly returns false but loses extrusion-axis closure metadata
needed by downstream processors.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SURFACE_OF_LINEAR_EXTRUSION (open parabolic base curve B_SPLINE_CURVE_WITH_KNOTS)
    IS the ADVANCED_FACE.face_geometry; open (non-closed) extruded base curve IS
    the mechanism wired into face topology; IsUClosed returns false but downstream
    loses extrusion-axis closure metadata IS the defect.
  - Byte assertions: contains(b'SURFACE_OF_LINEAR_EXTRUSION'),
                     contains(b'gs081').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_LINEAR_EXTRUSION (open parabolic B-spline base)
    IS the ADVANCED_FACE.face_geometry; open base curve (not closed in U) IS the
    mechanism wired into face topology; IsUClosed metadata loss for extrusion axis
    IS the defect.
  - shape_null driver: lost closure metadata; strict kernels reject inconsistent
    extrusion topology; empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs081",
    defect=(
        "SURFACE_OF_LINEAR_EXTRUSION (open parabolic B-spline base curve) IS "
        "ADVANCED_FACE.face_geometry; open base curve (non-closed in U) IS the "
        "mechanism wired into face topology; IsUClosed loses extrusion-axis "
        "closure metadata IS the defect; shape_null"
    ),
)

# ── Open parabolic base curve: degree-2 B-spline, 3 control points ────────────
# Parabola: (0,0,0) → (0.5,1,0) → (1,0,0) — open, not closed in U.
# Knots: (0,0,0,1,1,1) with mults (3,3) for a single Bezier segment.
base_pts = [
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((0.5, 1.0, 0.0)),
    f.cartesian_point((1.0, 0.0, 0.0)),
]
bp_str = "(" + ",".join(f"#{p.eid}" for p in base_pts) + ")"

# Byte assertion: contains(b'gs081')
base_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gs081_parabola',2,"
    f"{bp_str},"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

# ── Extrusion direction: Z-axis ────────────────────────────────────────────────
ext_dir = f.direction((0.0, 0.0, 1.0))
ext_vec = f.vector(ext_dir, 1.0)

# ── SURFACE_OF_LINEAR_EXTRUSION (open parabola extruded in Z) ─────────────────
# Byte assertion: contains(b'SURFACE_OF_LINEAR_EXTRUSION'), contains(b'gs081')
sole = f._emit_raw(
    f"SURFACE_OF_LINEAR_EXTRUSION('gs081_sole',#{base_curve.eid},#{ext_vec.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: parabolic patch u∈[0,1], v∈[0,1] ─────────────────────────
# 3D corners of the extruded parabola patch:
#   v=0: base curve at u=0 → (0,0,0), u=1 → (1,0,0)
#   v=1: extruded at u=0 → (0,0,1), u=1 → (1,0,1)
p_A = f.cartesian_point((0.0, 0.0, 0.0))   # u=0, v=0
p_B = f.cartesian_point((1.0, 0.0, 0.0))   # u=1, v=0
p_C = f.cartesian_point((1.0, 0.0, 1.0))   # u=1, v=1
p_D = f.cartesian_point((0.0, 0.0, 1.0))   # u=0, v=1

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
    pc  = f._emit_raw(f"PCURVE('pc',#{sole.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# e0: bottom u: 0→1 at v=0
e0 = mk_edge_line(v_A, v_B,
                  (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0,
                  (0.0, 0.0), (1.0, 0.0), 1.0)
# e1: right v: 0→1 at u=1
e1 = mk_edge_line(v_B, v_C,
                  (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 1.0,
                  (1.0, 0.0), (0.0, 1.0), 1.0)
# e2: top u: 1→0 at v=1
e2 = mk_edge_line(v_C, v_D,
                  (1.0, 0.0, 1.0), (-1.0, 0.0, 0.0), 1.0,
                  (1.0, 1.0), (-1.0, 0.0), 1.0)
# e3: left v: 1→0 at u=0
e3 = mk_edge_line(v_D, v_A,
                  (0.0, 0.0, 1.0), (0.0, 0.0, -1.0), 1.0,
                  (0.0, 1.0), (0.0, -1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SURFACE_OF_LINEAR_EXTRUSION IS the face_geometry; open base curve IS the mechanism on face.
face  = f.advanced_face([f.face_outer_bound(loop)], sole)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
