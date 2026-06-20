"""Gs045 — SURFACE_OF_REVOLUTION whose revolution axis crosses the basis curve at an interior point.

Catalog claim: basis LINE from x=-2 to x=+2 along y=0,z=0; revolution axis =
Y-axis at origin. The line crosses the axis at (0,0,0) — an interior point of
the parameter range — producing a self-intersecting surface that folds through
itself near the axis.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SURFACE_OF_REVOLUTION (basis=LINE, axis=Y-axis through origin) IS the
    ADVANCED_FACE.face_geometry; the Y-axis crosses the basis line at x=0,
    which is interior to the line's parameter range [-2, +2].
  - Byte assertions: contains(b'SURFACE_OF_REVOLUTION('),
                     contains(b'AXIS1_PLACEMENT('),
                     contains(b'(-2.0,0.0,0.0)').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_REVOLUTION IS the ADVANCED_FACE.face_geometry;
    revolution Y-axis crosses basis LINE at interior point (0,0,0) causing
    self-intersection; defective surface IS wired into face topology.
  - shape_null driver: self-intersecting surface from axis-crossing revolution;
    strict heal-or-reject kernels produce empty result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs045",
    defect=(
        "SURFACE_OF_REVOLUTION IS ADVANCED_FACE.face_geometry; "
        "revolution Y-axis crosses basis LINE at interior point (0,0,0) — "
        "produces self-intersecting surface that folds through itself — "
        "IS wired into face topology; shape(1) (live OCC heals)"
    ),
)

# ── Basis LINE: from (-2,0,0) to (+2,0,0) along X-axis ───────────────────────
# Byte assertion: contains(b'(-2.0,0.0,0.0)')
line_orig = f.cartesian_point((-2.0, 0.0, 0.0))
line_dir  = f.direction((1.0, 0.0, 0.0))
line_vec  = f.vector(line_dir, 4.0)   # magnitude 4 spans -2 to +2
basis_line = f.line(line_orig, line_vec)

# ── AXIS1_PLACEMENT: Y-axis at origin (revolution axis) ───────────────────────
# Byte assertion: contains(b'AXIS1_PLACEMENT(')
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
ax_dir  = f.direction((0.0, 1.0, 0.0))   # Y-axis — crosses basis line at x=0
ax1 = f._emit_raw(f"AXIS1_PLACEMENT('gs045_ax1',#{ax_orig.eid},#{ax_dir.eid})")

# ── SURFACE_OF_REVOLUTION: defect IS that axis crosses basis at interior pt ───
# Byte assertion: contains(b'SURFACE_OF_REVOLUTION(')
sor = f._emit_raw(f"SURFACE_OF_REVOLUTION('gs045_sor',#{basis_line.eid},#{ax1.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary wired onto the self-intersecting SURFACE_OF_REVOLUTION ───────
# Use a rectangular boundary in 3D (the surface folds; topology is still written)
p_A = f.cartesian_point(( 2.0, 0.0, 0.0))
p_B = f.cartesian_point(( 2.0, 0.0, 2.0))
p_C = f.cartesian_point((-2.0, 0.0, 2.0))
p_D = f.cartesian_point((-2.0, 0.0, 0.0))

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

e0 = mk_edge_line(v_A, v_B, (2.0,0.0,0.0), (0.0,0.0,1.0), 2.0, (1.0,0.0), (0.0,1.0), 1.0)
e1 = mk_edge_line(v_B, v_C, (2.0,0.0,2.0), (-1.0,0.0,0.0), 4.0, (1.0,1.0), (-1.0,0.0), 1.0)
e2 = mk_edge_line(v_C, v_D, (-2.0,0.0,2.0), (0.0,0.0,-1.0), 2.0, (0.0,1.0), (0.0,-1.0), 1.0)
e3 = mk_edge_line(v_D, v_A, (-2.0,0.0,0.0), (1.0,0.0,0.0), 4.0, (0.0,0.0), (1.0,0.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# SURFACE_OF_REVOLUTION IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], sor)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
