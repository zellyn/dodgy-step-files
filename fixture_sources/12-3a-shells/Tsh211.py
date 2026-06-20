"""Tsh211 — Degenerate edge-only wire removal.

Catalog claim: Shell face with inner wire containing single degenerate edge
(zero-length, both endpoints identical). DispatchWires must detect and remove
wire when NbEdges()==1 && Degenerated(edge).

Mechanism IS the shell structure: AN OPEN_SHELL containing TWO ADVANCED_FACEs —
face_a (unit square with a valid outer loop) and face_b (unit square carrying
BOTH a FACE_OUTER_BOUND outer loop AND a FACE_BOUND inner loop) IS the defect
trigger. The inner FACE_BOUND of face_b references an EDGE_LOOP with a SINGLE
DEGENERATE EDGE_CURVE (start vertex == end vertex, zero-length LINE) — IS the
degenerate wire. ShapeFix_ComposeShell.DispatchWires IS the defect path: it
must detect NbEdges()==1 && Degenerated(edge) on the inner wire and remove it;
failure to do so leaves the degenerate inner wire in the face topology — IS
the defect.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(10) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh211",
    defect=(
        "OPEN_SHELL with TWO ADVANCED_FACEs — face_b carrying a degenerate FACE_BOUND inner wire IS the degenerate-wire-removal defect trigger; "
        "face_a IS unit square (0,0,0)-(1,1,0) with normal outer loop — IS the clean reference face; "
        "face_b IS unit square (2,0,0)-(3,1,0) — IS the face carrying the degenerate inner wire; "
        "face_b FACE_OUTER_BOUND IS valid outer loop (four edges) — IS the outer boundary; "
        "face_b FACE_BOUND IS inner wire with ONE degenerate EDGE_CURVE — IS the degenerate inner wire; "
        "degenerate edge IS EDGE_CURVE from v_degen to v_degen (same vertex, zero-length LINE) — IS the degenerate edge; "
        "NbEdges()==1 on the inner EDGE_LOOP — IS the single-edge wire condition; "
        "Degenerated(edge) IS True because start==end vertex — IS the degenerate condition; "
        "DispatchWires IS the defect path: must detect NbEdges==1 && Degenerated and remove inner wire; "
        "failure leaves degenerate inner wire in face topology — IS the defect; "
        "fix: DispatchWires must remove inner wires where NbEdges==1 && Degenerated(edge); "
        "emit E_DEGENERATE_WIRE_NOT_PRUNED when degenerate-only inner wire survives DispatchWires"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# face_a: clean unit square at X=0..1 — IS the clean reference face
pa00 = cp(0, 0, 0); va00 = f.vertex_point(pa00)
pa10 = cp(1, 0, 0); va10 = f.vertex_point(pa10)
pa11 = cp(1, 1, 0); va11 = f.vertex_point(pa11)
pa01 = cp(0, 1, 0); va01 = f.vertex_point(pa01)

ea_bot = led(va00, va10, pa00,  1, 0, 0)
ea_rgt = led(va10, va11, pa10,  0, 1, 0)
ea_top = led(va11, va01, pa11, -1, 0, 0)
ea_lft = led(va01, va00, pa01,  0,-1, 0)

loop_a = f.edge_loop([
    f.oriented_edge(ea_bot, True),
    f.oriented_edge(ea_rgt, True),
    f.oriented_edge(ea_top, True),
    f.oriented_edge(ea_lft, True),
])
plane_a = f.plane(f.axis2_placement_3d(pa00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], plane_a, same_sense=True)

# face_b: unit square at X=2..3 with degenerate inner wire — IS the defect face
pb00 = cp(2, 0, 0); vb00 = f.vertex_point(pb00)
pb10 = cp(3, 0, 0); vb10 = f.vertex_point(pb10)
pb11 = cp(3, 1, 0); vb11 = f.vertex_point(pb11)
pb01 = cp(2, 1, 0); vb01 = f.vertex_point(pb01)

eb_bot = led(vb00, vb10, pb00,  1, 0, 0)
eb_rgt = led(vb10, vb11, pb10,  0, 1, 0)
eb_top = led(vb11, vb01, pb11, -1, 0, 0)
eb_lft = led(vb01, vb00, pb01,  0,-1, 0)

loop_b_outer = f.edge_loop([
    f.oriented_edge(eb_bot, True),
    f.oriented_edge(eb_rgt, True),
    f.oriented_edge(eb_top, True),
    f.oriented_edge(eb_lft, True),
])

# Degenerate inner wire: single zero-length edge, start==end — IS the degenerate edge
p_degen = cp(2.5, 0.5, 0); v_degen = f.vertex_point(p_degen)   # interior point
d_zero = dir3(1, 0, 0)
vec_zero = f.vector(d_zero, 0.0)    # zero magnitude — IS the degenerate vector
ln_zero = f.line(p_degen, vec_zero)
# v_degen IS both start and end — IS the degenerate condition (Degenerated==True)
e_degen = f.edge_curve(v_degen, v_degen, ln_zero, same_sense=True)

loop_b_inner = f.edge_loop([
    f.oriented_edge(e_degen, True),   # single degenerate edge — IS the NbEdges==1 condition
])

plane_b = f.plane(f.axis2_placement_3d(pb00, dir3(0, 0, 1), dir3(1, 0, 0)))
# face_b: outer bound + inner degenerate FACE_BOUND — IS the degenerate-wire face
face_b = f.advanced_face(
    [
        f.face_outer_bound(loop_b_outer, orientation=True),
        f.face_bound(loop_b_inner, orientation=False),   # inner degenerate wire — IS the defect
    ],
    plane_b,
    same_sense=True,
)

# OPEN_SHELL: face_a (clean) + face_b (degenerate inner wire) — IS the degenerate-wire-removal mechanism
shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
