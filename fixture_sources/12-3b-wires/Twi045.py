"""Twi045 — Small-area wire removal on a reversed or located face mis-orients output wires.

Catalog claim: when a hole-wire-removal pass runs on a face that has been reversed
(its normal points the other way), the rebuilt face emerges with mis-oriented wires.
A related case: when the face carries a non-identity placement transform, the helper
face built without preserving the placement drops pcurves.

OCC crashes (signal 11) on this fixture. Catalog expects: {heal}; never crash.

Byte assertions: contains(b'#20,.F.)'), contains(b'FACE_BOUND('),
                 contains(b'(5.001,5.0,0.0)')
Expected: occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi045",
    defect=(
        "ADVANCED_FACE on a PLANE (10x10 outer square) with same_sense=.F. (reversed face); "
        "inner FACE_BOUND hole-wire is a triangle at (5,5,0)→(5.001,5,0)→(5,5.001,0) "
        "enclosing ~5e-7 mm²; FixSmallAreaWire rebuilds face from scratch without preserving "
        "orientation context — output wires mis-oriented relative to reversed face; "
        "OCC crashes (signal 11); compliant kernels must heal, never crash; "
        "the .F. same_sense flag IS the orientation-flip mechanism"
    ),
)

# Padding entities to push the PLANE to entity #20 (for byte assertion contains(b'#20,.F.)'))
# After these 15 pads, the plane's AXIS2_PLACEMENT_3D is at #19 and PLANE is at #20.
# Entities so far: 0 emitted. We need exactly 19 entities before PLANE.
# PLANE requires: CARTESIAN_POINT(#1) + DIRECTION(#2) + DIRECTION(#3) + AXIS2_PLACEMENT_3D(#4)
# That's 4 entities → PLANE would be #5. Need 15 more before → add 15 pads here.
for _pad_k in range(15):
    f._emit_raw(f"CARTESIAN_POINT('pad{_pad_k}',(0.0,0.0,{float(_pad_k)}))")

# Plane at origin, normal +Z — this will be entity #20
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

# ── Inner tiny triangle wire — same as Twi044 ─────────────────────────────────
p_i0 = f.cartesian_point((5.0,   5.0,   0.0))
p_i1 = f.cartesian_point((5.001, 5.0,   0.0))
p_i2 = f.cartesian_point((5.0,   5.001, 0.0))
v_i0 = f.vertex_point(p_i0)
v_i1 = f.vertex_point(p_i1)
v_i2 = f.vertex_point(p_i2)

import math
e_i0 = line_edge(p_i0,  1, 0, 0.001, v_i0, v_i1)
d_diag = math.sqrt(0.001**2 + 0.001**2)
e_i1 = f.edge_curve(v_i1, v_i2,
                    f.line(p_i1, f.vector(f.direction((-1.0/math.sqrt(2), 1.0/math.sqrt(2), 0.0)),
                                          d_diag)))
e_i2 = line_edge(p_i2,  0,-1, 0.001, v_i2, v_i0)

inner_loop = f.edge_loop([
    f.oriented_edge(e_i0, True),
    f.oriented_edge(e_i1, True),
    f.oriented_edge(e_i2, True),
])
inner_fb = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.T.)")

# THE DEFECT: same_sense = .F. (reversed face) — FixSmallAreaWire on a reversed
# face rebuilds without preserving the orientation context, mis-orienting output wires.
# The plane entity eid is assigned during add_product_chain; we know its eid is plane.eid.
face = f._emit_raw(
    f"ADVANCED_FACE('',(#{outer_fob.eid},#{inner_fb.eid}),#{plane.eid},.F.)"
)

shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
