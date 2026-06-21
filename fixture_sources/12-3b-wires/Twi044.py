"""Twi044 — Internal FACE_BOUND hole-wire with sub-tolerance enclosed area.

Catalog claim: a face carries one or more inner FACE_BOUND ("hole") wires whose
enclosed area is below a configurable threshold — a tiny wire that almost-encloses-
nothing, typically left behind by imprecise reverse-engineering or Boolean fallout.
Common shape: a triangle inner wire with vertices like (5,5,0), (5.001,5,0),
(5.0,5.001,0) — enclosed area ~5e-7 mm² well below typical working tolerance —
sitting inside a 100 mm² planar face.

OCC crashes (signal 11) on this fixture — catalog disallows crash.

Byte assertions: contains(b'(5.001,5.0,0.0)'), contains(b'(5.0,5.001,0.0)'),
                 contains(b'FACE_BOUND(')
Expected: occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi044",
    defect=(
        "ADVANCED_FACE on a PLANE (10x10 outer square, area=100); "
        "inner FACE_BOUND hole-wire is a triangle at (5,5,0)→(5.001,5,0)→(5,5.001,0) "
        "enclosing area ~5e-7 mm² — well below ShapeUpgrade_RemoveInternalWires threshold; "
        "tiny hole-wire IS the FACE_BOUND mechanism wired into the ADVANCED_FACE; "
        "OCC crashes (signal 11) via NaN propagation through BRepLib::SameParameter "
        "on degenerate geometry; compliant kernels must reject, never crash"
    ),
)

# Plane at origin, normal +Z
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Outer 10x10 square wire ───────────────────────────────────────────────────
p_o0 = f.cartesian_point((0.0,  0.0, 0.0))
p_o1 = f.cartesian_point((10.0, 0.0, 0.0))
p_o2 = f.cartesian_point((10.0, 10.0, 0.0))
p_o3 = f.cartesian_point((0.0,  10.0, 0.0))
v_o0 = f.vertex_point(p_o0)
v_o1 = f.vertex_point(p_o1)
v_o2 = f.vertex_point(p_o2)
v_o3 = f.vertex_point(p_o3)

def line_edge(p_start, dx, dy, length, va, vb):
    d  = f.direction((dx, dy, 0.0))
    v  = f.vector(d, length)
    ln = f.line(p_start, v)
    return f.edge_curve(va, vb, ln)

e_o0 = line_edge(p_o0,  1, 0, 10.0, v_o0, v_o1)
e_o1 = line_edge(p_o1,  0, 1, 10.0, v_o1, v_o2)
e_o2 = line_edge(p_o2, -1, 0, 10.0, v_o2, v_o3)
e_o3 = line_edge(p_o3,  0,-1, 10.0, v_o3, v_o0)

outer_loop = f.edge_loop([
    f.oriented_edge(e_o0, True),
    f.oriented_edge(e_o1, True),
    f.oriented_edge(e_o2, True),
    f.oriented_edge(e_o3, True),
])
outer_fob = f.face_outer_bound(outer_loop)

# ── Inner tiny triangle wire — THE MECHANISM ──────────────────────────────────
# Vertices: (5,5,0), (5.001,5,0), (5.0,5.001,0)
# Enclosed area = 0.5 * |cross((5.001-5,0,0), (5.0-5,5.001-5,0))|
#               = 0.5 * |(0.001,0,0) × (0.0,0.001,0)|
#               = 0.5 * (0.001 * 0.001) = 5e-7 mm²
p_i0 = f.cartesian_point((5.0,   5.0,   0.0))
p_i1 = f.cartesian_point((5.001, 5.0,   0.0))
p_i2 = f.cartesian_point((5.0,   5.001, 0.0))
v_i0 = f.vertex_point(p_i0)
v_i1 = f.vertex_point(p_i1)
v_i2 = f.vertex_point(p_i2)

import math
e_i0 = line_edge(p_i0,  1, 0, 0.001,   v_i0, v_i1)
d_i1_diag = math.sqrt(0.001**2 + 0.001**2)
e_i1 = f.edge_curve(v_i1, v_i2,
                    f.line(p_i1, f.vector(f.direction((-1.0/math.sqrt(2), 1.0/math.sqrt(2), 0.0)),
                                          d_i1_diag)))
e_i2 = line_edge(p_i2,  0,-1, 0.001,   v_i2, v_i0)

inner_loop = f.edge_loop([
    f.oriented_edge(e_i0, True),
    f.oriented_edge(e_i1, True),
    f.oriented_edge(e_i2, True),
])
# Inner wire IS a FACE_BOUND (not FACE_OUTER_BOUND) — this is the hole
inner_fb = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.T.)")

# ADVANCED_FACE with both outer and inner bound
face = f._emit_raw(
    f"ADVANCED_FACE('',(#{outer_fob.eid},#{inner_fb.eid}),#{plane.eid},.T.)"
)

shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
