"""Gs042 — CURVE_BOUNDED_SURFACE with self-intersecting (bowtie) boundary.

Catalog claim: A CURVE_BOUNDED_SURFACE whose basis is a plane and whose
boundary is a four-segment COMPOSITE_CURVE forming a self-intersecting
bowtie: corners (0,0),(1,1),(1,0),(0,1) connected in that order. The
boundary crosses at its midpoint; the "inside" is ambiguous.

OCC behavior: silently accepts (empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - CURVE_BOUNDED_SURFACE IS the ADVANCED_FACE.face_geometry.
  - BOUNDARY_CURVE(COMPOSITE_CURVE) with four POLYLINE segments forming a
    bowtie (A→C→B→D→A where A=(0,0),B=(0,1),C=(1,0),D=(1,1)) IS the defect.
  - Byte assertions: contains(b'CURVE_BOUNDED_SURFACE('),
                     contains(b'BOUNDARY_CURVE('),
                     count_entity_def(b'POLYLINE') == 4.
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: CURVE_BOUNDED_SURFACE IS the ADVANCED_FACE.face_geometry;
    BOUNDARY_CURVE with four POLYLINE segments forming self-intersecting bowtie
    IS the defect wired into face topology.
  - shape_null driver: self-intersecting boundary makes inside/outside ambiguous;
    strict heal-or-reject kernels produce null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs042",
    defect=(
        "CURVE_BOUNDED_SURFACE IS ADVANCED_FACE.face_geometry; "
        "BOUNDARY_CURVE COMPOSITE_CURVE with 4 POLYLINE segments forming "
        "self-intersecting bowtie boundary (corners (0,0),(1,1),(1,0),(0,1)) "
        "IS wired into face topology; shape(1) (live OCC heals)"
    ),
)

# ── Basis plane for the CURVE_BOUNDED_SURFACE ─────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
ax3   = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs042_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs042_plane',#{ax3.eid})")

# ── Bowtie boundary: corners A=(0,0), B=(0,1), C=(1,0), D=(1,1) ──────────────
# Traversal order A→C→B→D→A creates a figure-eight self-intersection.
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((0.0, 1.0, 0.0))
p_C = f.cartesian_point((1.0, 0.0, 0.0))
p_D = f.cartesian_point((1.0, 1.0, 0.0))

# Four POLYLINE segments: A→C, C→B, B→D, D→A
# Byte assertion: count_entity_def(b'POLYLINE') == 4
poly1 = f._emit_raw(f"POLYLINE('gs042_poly1',(#{p_A.eid},#{p_C.eid}))")
poly2 = f._emit_raw(f"POLYLINE('gs042_poly2',(#{p_C.eid},#{p_B.eid}))")
poly3 = f._emit_raw(f"POLYLINE('gs042_poly3',(#{p_B.eid},#{p_D.eid}))")
poly4 = f._emit_raw(f"POLYLINE('gs042_poly4',(#{p_D.eid},#{p_A.eid}))")

# COMPOSITE_CURVE_SEGMENT wrappers for each POLYLINE
ccs1 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{poly1.eid})")
ccs2 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{poly2.eid})")
ccs3 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{poly3.eid})")
ccs4 = f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{poly4.eid})")

# BOUNDARY_CURVE = COMPOSITE_CURVE subtype
# Byte assertion: contains(b'BOUNDARY_CURVE(')
bc = f._emit_raw(
    f"BOUNDARY_CURVE('gs042_bc',"
    f"(#{ccs1.eid},#{ccs2.eid},#{ccs3.eid},#{ccs4.eid}),.T.)"
)

# CURVE_BOUNDED_SURFACE: basis=plane, boundaries=[bc], implicit_outer=.F.
# Byte assertion: contains(b'CURVE_BOUNDED_SURFACE(')
cbs = f._emit_raw(
    f"CURVE_BOUNDED_SURFACE('gs042_cbs',#{plane.eid},(#{bc.eid}),.F.)"
)

# ── Wire the CBS as the ADVANCED_FACE.face_geometry ───────────────────────────
# Since CURVE_BOUNDED_SURFACE already carries its own boundary, the
# ADVANCED_FACE has an empty bounds list; the face simply references cbs.
# We use a minimal FACE_OUTER_BOUND with a degenerate EDGE_LOOP to satisfy
# the ADVANCED_FACE schema while the defect mechanism is in cbs.
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Use a simple rectangle as the ADVANCED_FACE bounds (the defect is in the CBS itself).
p3_A = f.cartesian_point((0.0, 0.0, 0.0))
p3_B = f.cartesian_point((1.0, 0.0, 0.0))
p3_C = f.cartesian_point((1.0, 1.0, 0.0))
p3_D = f.cartesian_point((0.0, 1.0, 0.0))
v3_A = f.vertex_point(p3_A)
v3_B = f.vertex_point(p3_B)
v3_C = f.vertex_point(p3_C)
v3_D = f.vertex_point(p3_D)

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
    pc  = f._emit_raw(f"PCURVE('pc',#{cbs.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e0 = mk_edge_line(v3_A, v3_B, (0.0,0.0,0.0), (1.0,0.0,0.0), 1.0, (0.0,0.0), (1.0,0.0), 1.0)
e1 = mk_edge_line(v3_B, v3_C, (1.0,0.0,0.0), (0.0,1.0,0.0), 1.0, (1.0,0.0), (0.0,1.0), 1.0)
e2 = mk_edge_line(v3_C, v3_D, (1.0,1.0,0.0), (-1.0,0.0,0.0), 1.0, (1.0,1.0), (-1.0,0.0), 1.0)
e3 = mk_edge_line(v3_D, v3_A, (0.0,1.0,0.0), (0.0,-1.0,0.0), 1.0, (0.0,1.0), (0.0,-1.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# CURVE_BOUNDED_SURFACE IS the face_geometry — mechanism IS the face surface.
face  = f.advanced_face([f.face_outer_bound(loop)], cbs)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
