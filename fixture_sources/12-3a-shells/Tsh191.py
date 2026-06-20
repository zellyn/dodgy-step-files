"""Tsh191 — ShapeFix_Shell.FixFaceOrientation multi-connected edge unbounded.

Catalog claim: Multi-connected edges (3+ faces sharing one edge) only handled
when isAccountMultiConex=true; the loop processing lacks an iteration bound.
Three faces share a single edge; aMapMultiConnectEdges is exhaustively populated
without a complexity limit, producing O(n^2) or worse behavior.

Mechanism IS the shell structure: AN OPEN_SHELL containing THREE ADVANCED_FACEs
all sharing ONE common EDGE_CURVE IS the defect trigger. The shared edge IS the
multi-connected edge — the same EDGE_CURVE entity appears in the oriented-edge
lists of all three faces. FixFaceOrientation IS the defect path: when it
encounters an edge with face-count > 2 it enters the isAccountMultiConex branch
and populates aMapMultiConnectEdges with all three faces. Without a bound on the
traversal the map grows unboundedly with pathological inputs — IS the defect.

Tier-3 assertion: n_faces_total == 3

live oracle: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh191",
    defect=(
        "OPEN_SHELL with THREE ADVANCED_FACEs sharing ONE EDGE_CURVE IS the multi-connected edge defect trigger; "
        "e_shared IS EDGE_CURVE from v_origin to v_end — IS the multi-connected edge; "
        "face_a, face_b, face_c each reference e_shared via oriented_edge — IS the three-face share; "
        "face_a IS triangle (origin, end, apex_a) — IS first multi-connected face; "
        "face_b IS triangle (origin, end, apex_b) — IS second multi-connected face; "
        "face_c IS triangle (origin, end, apex_c) — IS third multi-connected face; "
        "FixFaceOrientation detects e_shared has count > 2 — IS the multi-connected trigger; "
        "isAccountMultiConex branch populates aMapMultiConnectEdges with all three faces — IS the defect path; "
        "traversal lacks iteration bound — IS the unbounded loop defect; "
        "fix: limit aMapMultiConnectEdges traversal to O(n) with early-exit guard; "
        "emit E_MULTICONNECT_UNBOUNDED when edge face-count exceeds threshold without bound"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Shared edge vertices — v_origin to v_end IS the multi-connected edge endpoints
p_origin = cp(0, 0, 0); v_origin = f.vertex_point(p_origin)
p_end    = cp(1, 0, 0); v_end    = f.vertex_point(p_end)

# e_shared: THE multi-connected EDGE_CURVE referenced by all three faces
e_shared = led(v_origin, v_end, p_origin, 1, 0, 0)

# fan apex vertices in distinct planes
p_a = cp(0.5,  1, 0); v_a = f.vertex_point(p_a)  # apex_a — IS above Z=0
p_b = cp(0.5, -1, 0); v_b = f.vertex_point(p_b)  # apex_b — IS below Z=0
p_c = cp(0.5,  0, 1); v_c = f.vertex_point(p_c)  # apex_c — IS above in Z

# face_a: triangle (origin, end, apex_a) — shares e_shared
ea_2 = led(v_end,    v_a, p_end,   -0.5,  1, 0)
ea_3 = led(v_a, v_origin, p_a,     -0.5, -1, 0)
loop_a = f.edge_loop([
    f.oriented_edge(e_shared, True),
    f.oriented_edge(ea_2, True),
    f.oriented_edge(ea_3, True),
])
pl_a = f.plane(f.axis2_placement_3d(p_origin, dir3(0, 0, 1), dir3(1, 0, 0)))
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], pl_a, same_sense=True)

# face_b: triangle (origin, end, apex_b) — shares e_shared — IS second multi-connected face
eb_2 = led(v_end,    v_b, p_end,   -0.5, -1, 0)
eb_3 = led(v_b, v_origin, p_b,     -0.5,  1, 0)
loop_b = f.edge_loop([
    f.oriented_edge(e_shared, True),
    f.oriented_edge(eb_2, True),
    f.oriented_edge(eb_3, True),
])
pl_b = f.plane(f.axis2_placement_3d(p_origin, dir3(0, 0, -1), dir3(1, 0, 0)))
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], pl_b, same_sense=True)

# face_c: triangle (origin, end, apex_c) — shares e_shared — IS third multi-connected face
ec_2 = led(v_end,    v_c, p_end,   -0.5, 0,  1)
ec_3 = led(v_c, v_origin, p_c,     -0.5, 0, -1)
loop_c = f.edge_loop([
    f.oriented_edge(e_shared, True),
    f.oriented_edge(ec_2, True),
    f.oriented_edge(ec_3, True),
])
pl_c = f.plane(f.axis2_placement_3d(p_origin, dir3(0, -1, 0), dir3(1, 0, 0)))
face_c = f.advanced_face([f.face_outer_bound(loop_c, orientation=True)], pl_c, same_sense=True)

# OPEN_SHELL: three faces sharing one edge — IS the multi-connected edge unbounded mechanism
shell = f.open_shell([face_a, face_b, face_c])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
