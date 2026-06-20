"""Gs056 — SURFACE_OF_REVOLUTION of an ellipse around its own centre produces a degenerate surface.

Catalog claim: A SURFACE_OF_REVOLUTION references an ELLIPSE as its swept
curve, and the revolution axis passes through the ellipse centre.  The
resulting analytic surface is degenerate at both poles where the generatrix
meets the axis (zero-radius circles).  OCCT cannot recover a usable
parametric surface; the face appears empty or geometry is dropped silently.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SURFACE_OF_REVOLUTION(swept_curve=ELLIPSE) whose AXIS1_PLACEMENT passes
    through the ellipse centre IS the ADVANCED_FACE.face_geometry; axis-
    through-centre construction IS the defect wired into face topology.
  - Byte assertions: contains(b'SURFACE_OF_REVOLUTION'),
                     contains(b'ELLIPSE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_REVOLUTION IS the ADVANCED_FACE.face_geometry;
    ELLIPSE whose centre coincides with the revolution axis IS the swept curve;
    axis-through-centre IS wired into face topology; poles degenerate to zero-
    radius circles.
  - shape_null driver: degenerate poles produce NaN/Inf in surface evaluation;
    strict warn-and-proceed or reject kernels produce empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs056",
    defect=(
        "SURFACE_OF_REVOLUTION(swept_curve=ELLIPSE) IS ADVANCED_FACE.face_geometry; "
        "ELLIPSE centre at origin with revolution axis through that same origin IS the defect; "
        "axis-through-centre degenerate revolution IS wired into face topology; "
        "shape_null (degenerate poles, strict warn-and-proceed)"
    ),
)

# ── ELLIPSE at origin (semi-axes 1.0, 0.5) ────────────────────────────────────
# Byte assertion: contains(b'ELLIPSE')
ell_orig = f.cartesian_point((0.0, 0.0, 0.0))
ell_zdir = f.direction((0.0, 0.0, 1.0))
ell_xdir = f.direction((1.0, 0.0, 0.0))
ell_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs056_ell_ax',#{ell_orig.eid},#{ell_zdir.eid},#{ell_xdir.eid})"
)
ellipse  = f._emit_raw(f"ELLIPSE('gs056_ellipse',#{ell_ax.eid},1.0,0.5)")

# ── Revolution axis: vertical through origin (same centre as ellipse) ─────────
# Byte assertion: contains(b'SURFACE_OF_REVOLUTION')
rev_orig = f.cartesian_point((0.0, 0.0, 0.0))
rev_zdir = f.direction((0.0, 0.0, 1.0))
rev_ax   = f._emit_raw(
    f"AXIS1_PLACEMENT('gs056_rev_ax',#{rev_orig.eid},#{rev_zdir.eid})"
)
sor = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('gs056_sor',#{ellipse.eid},#{rev_ax.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the degenerate SURFACE_OF_REVOLUTION ─────────────
# Use a small rectangular patch in parameter space U∈[0,π/2], V∈[0,π/2].
# 3D approximations use a partial-torus shell corner; the surface is degenerate
# regardless — the face topology is what matters for the defect trigger.
PI = math.pi

p_A = f.cartesian_point(( 1.0,  0.0,  0.0))
p_B = f.cartesian_point(( 0.0,  1.0,  0.0))
p_C = f.cartesian_point(( 0.0,  1.0,  0.5))
p_D = f.cartesian_point(( 1.0,  0.0,  0.5))

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
    pc  = f._emit_raw(f"PCURVE('pc',#{sor.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v_A, v_B, (1.0,0.0,0.0), (-1.0,1.0,0.0), math.sqrt(2),
                  (0.0,0.0), (1.0,0.0), PI/2)
e1 = mk_edge_line(v_B, v_C, (0.0,1.0,0.0), (0.0,0.0,1.0), 0.5,
                  (PI/2,0.0), (0.0,1.0), PI/2)
e2 = mk_edge_line(v_C, v_D, (0.0,1.0,0.5), (1.0,-1.0,0.0), math.sqrt(2),
                  (PI/2,PI/2), (-1.0,0.0), PI/2)
e3 = mk_edge_line(v_D, v_A, (1.0,0.0,0.5), (0.0,0.0,-1.0), 0.5,
                  (0.0,PI/2), (0.0,-1.0), PI/2)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SURFACE_OF_REVOLUTION IS the face_geometry; degenerate revolution IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], sor)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
