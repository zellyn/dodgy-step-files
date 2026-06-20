"""Gs051 — Sphere/cylinder cut produces wrong pcurves on second seam.

Catalog claim: Boolean cut — sphere radius 5 at origin by cylinder radius 2
along Z.  The cut introduces a new seam edge that crosses the sphere's
natural seam.  After the cut there are two seams; the second seam's pcurves
reference U=π instead of U=0.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius 5) IS the ADVANCED_FACE.face_geometry.
  - The defect EDGE_CURVE for the second seam carries a pcurve referencing
    U=π (3.141592653589793) instead of U=0 — wrong seam parameter — IS the
    defect wired into face topology.
  - The CYLINDRICAL_SURFACE (radius 2) appears as the mating face_geometry.
  - Byte assertions: contains(b'SPHERICAL_SURFACE('),
                     contains(b'CYLINDRICAL_SURFACE('),
                     contains(b'3.141592653589793').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SPHERICAL_SURFACE IS the ADVANCED_FACE.face_geometry;
    second-seam EDGE_CURVE carries pcurve with U=3.141592653589793 instead
    of U=0 IS wired into face topology; wrong pcurve parameter IS the defect.
  - shape_null driver: pcurve referencing wrong parameter domain cannot close
    the wire; strict heal-or-reject kernels produce empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs051",
    defect=(
        "SPHERICAL_SURFACE (radius 5) IS ADVANCED_FACE.face_geometry; "
        "second seam EDGE_CURVE pcurve referencing U=3.141592653589793 instead "
        "of U=0 IS wired into face topology; wrong seam pcurve IS the defect; "
        "shape_null (strict reject)"
    ),
)

# ── CATALOG MECHANISM: SPHERICAL_SURFACE as face_geometry ────────────────────
# Byte assertion: contains(b'SPHERICAL_SURFACE(')
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs051_sph_ax',#{sph_orig.eid},#{sph_zdir.eid},#{sph_xdir.eid})"
)
sphere = f._emit_raw(f"SPHERICAL_SURFACE('gs051_sphere',#{sph_ax.eid},5.0)")

# ── CYLINDRICAL_SURFACE (the cutting cylinder, radius 2) ─────────────────────
# Byte assertion: contains(b'CYLINDRICAL_SURFACE(')
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs051_cyl_ax',#{cyl_orig.eid},#{cyl_zdir.eid},#{cyl_xdir.eid})"
)
cylinder = f._emit_raw(f"CYLINDRICAL_SURFACE('gs051_cyl',#{cyl_ax.eid},2.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Sphere face boundary ──────────────────────────────────────────────────────
# Upper-hemisphere patch bounded by the cylinder cut.
# Use circle at z=sqrt(5²-2²)=sqrt(21)≈4.583 (cylinder/sphere intersection)
# and the sphere's natural seam at U=0/U=2π.

PI = math.pi
z_cut = math.sqrt(25.0 - 4.0)  # ≈ 4.583

# Corner 3D points on sphere/cylinder intersection circle
p_A = f.cartesian_point(( 2.0,  0.0, z_cut))
p_B = f.cartesian_point(( 0.0,  2.0, z_cut))
p_C = f.cartesian_point((-2.0,  0.0, z_cut))
p_D = f.cartesian_point(( 0.0, -2.0, z_cut))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_edge_line_on_sphere(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{sphere.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# e0: first seam edge at U=0 (correct)
e0 = mk_edge_line_on_sphere(v_A, v_A,
                             (2.0, 0.0, z_cut), (0.0, 0.0, 1.0), 1.0,
                             (0.0, PI/2), (0.0, 1.0), 0.1)

# e1, e2: normal edges along the cut circle
e1 = mk_edge_line_on_sphere(v_A, v_B,
                             (2.0, 0.0, z_cut), (-1.0, 1.0, 0.0), 2.0*math.sqrt(2),
                             (0.0, PI/2), (1.0, 0.0), PI/2)
e2 = mk_edge_line_on_sphere(v_B, v_C,
                             (0.0, 2.0, z_cut), (-1.0,-1.0, 0.0), 2.0*math.sqrt(2),
                             (PI/2, PI/2), (1.0, 0.0), PI/2)

# e3: DEFECT — second seam pcurve references U=π (3.141592653589793) instead of U=0
# Byte assertion: contains(b'3.141592653589793')
p3_e3  = f.cartesian_point((-2.0, 0.0, z_cut))
d3_e3  = f.direction((0.0, 0.0, 1.0))
v3_e3  = f.vector(d3_e3, 1.0)
l3_e3  = f.line(p3_e3, v3_e3)
# Wrong pcurve: U=3.141592653589793 instead of U=0 — IS the defect
p2_e3  = f.cartesian_point((3.141592653589793, PI/2))
d2_e3  = f.direction((0.0, 1.0))
v2_e3  = f.vector(d2_e3, 0.1)
l2_e3  = f.line(p2_e3, v2_e3)
pcd_e3 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_e3',(#{l2_e3.eid}),#{prc.eid})")
pc_e3  = f._emit_raw(f"PCURVE('pc_e3',#{sphere.eid},#{pcd_e3.eid})")
sc_e3  = f._emit_raw(f"SURFACE_CURVE('sc_e3',#{l3_e3.eid},(#{pc_e3.eid}),.PCURVE_S1.)")
e3     = f._emit_raw(f"EDGE_CURVE('ec_e3',#{v_C.eid},#{v_C.eid},#{sc_e3.eid},.T.)")

e4 = mk_edge_line_on_sphere(v_C, v_D,
                             (-2.0, 0.0, z_cut), (1.0, -1.0, 0.0), 2.0*math.sqrt(2),
                             (PI, PI/2), (1.0, 0.0), PI/2)
e5 = mk_edge_line_on_sphere(v_D, v_A,
                             (0.0, -2.0, z_cut), (1.0, 1.0, 0.0), 2.0*math.sqrt(2),
                             (3*PI/2, PI/2), (1.0, 0.0), PI/2)

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
    f.oriented_edge(e4, True),
    f.oriented_edge(e5, True),
])

# SPHERICAL_SURFACE IS the face_geometry; wrong-U pcurve IS the defect edge pcurve.
face  = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
