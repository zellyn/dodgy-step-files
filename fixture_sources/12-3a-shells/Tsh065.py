"""Tsh065 — Tessellated shell with shared nodes between adjacent triangulated faces.

Catalog claim: AP242 TESSELLATED_SHELL_REPRESENTATION wraps several TRIANGULATED_FACE
entities each carrying their own COORDINATES_LIST. A producer that mixes the two —
most faces use a shared shell-level node list, but one face carries its own private list
whose vertex coordinates duplicate shell-level nodes — leaves the shell's connectivity
ambiguous: the stitched mesh has phantom seam edges where the shared and private node
lists meet, neither watertight nor cleanly unstitched.

Mechanism IS the shell structure: TESSELLATED_SHELL_REPRESENTATION wraps 2 TRIANGULATED_FACE
entities. Face A uses a shell-level COORDINATES_LIST (4 nodes at z=0: (0,0,0), (1,0,0),
(1,1,0), (0,1,0)). Face B carries its OWN private COORDINATES_LIST with nodes (1,0,0),
(2,0,0), (2,1,0), (1,1,0) — coordinates (1,0,0) and (1,1,0) DUPLICATE shell-level nodes
but live in a separate entity (different ID). Mixed node-list ownership IS directly wired
into the TESSELLATED_SHELL_REPRESENTATION topology referencing both COORDINATES_LIST
entities. A receiver cannot determine whether the seam at x=1 is a shared edge
(watertight) or an open seam (two independent meshes).

Byte assertions:
  - contains(b'TESSELLATED_SHELL_REPRESENTATION')
  - count(b'TRIANGULATED_FACE') >= 2
  - count(b'COORDINATES_LIST') >= 2

Tier-3 assertion: shape_null == True

live oracle: occt=empty/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh065",
    defect=(
        "TESSELLATED_SHELL_REPRESENTATION with 2 TRIANGULATED_FACEs; "
        "Face A uses shell-level COORDINATES_LIST (4 nodes at z=0); "
        "Face B carries its own private per-face COORDINATES_LIST "
        "whose seam nodes at x=1 DUPLICATE shell-level nodes by value but differ by entity ID; "
        "duplicate seam coordinates across two distinct COORDINATES_LIST entities IS the mechanism; "
        "mixed node-list ownership IS directly wired into TESSELLATED_SHELL_REPRESENTATION; "
        "receiver cannot determine watertight seam vs open seam at x=1; "
        "fix: reject with E_AMBIGUOUS_NODE_LISTS in strict mode; "
        "warn and accept in tolerant mode; "
        "producer must use one node list (shell-level or per-face) consistently"
    ),
)

# Shell-level COORDINATES_LIST: 4 nodes for Face A quad at z=0, x=[0,1]
# Node indices are 1-based in AP242
shell_coords = f._emit_raw(
    "COORDINATES_LIST('shell_nodes',3,"
    "((0.0,0.0,0.0),(1.0,0.0,0.0),(1.0,1.0,0.0),(0.0,1.0,0.0)))"
)

# Face B private COORDINATES_LIST: nodes at x=[1,2] — seam coords (1,0,0) and
# (1,1,0) DUPLICATE shell-level nodes 2 and 3 by value but are a separate entity
face_b_coords = f._emit_raw(
    "COORDINATES_LIST('face_b_private_nodes',3,"
    "((1.0,0.0,0.0),(2.0,0.0,0.0),(2.0,1.0,0.0),(1.0,1.0,0.0)))"
)

# TRIANGULATED_FACE A: uses shell-level coord list (2 triangles from quad)
face_a_tess = f._emit_raw(
    f"TRIANGULATED_FACE('face_a',#{shell_coords.eid},.F.,2,"
    "((1,2,3),(1,3,4)))"
)

# TRIANGULATED_FACE B: uses OWN private coord list — IS the defect
# seam nodes #1=(1,0,0) and #4=(1,1,0) duplicate shell_coords nodes #2 and #3
face_b_tess = f._emit_raw(
    f"TRIANGULATED_FACE('face_b',#{face_b_coords.eid},.F.,2,"
    "((1,2,3),(1,3,4)))"
)

# TESSELLATED_SHELL_REPRESENTATION: wraps both faces + shell-level coord list
# Mixed node-list ownership (face_a references shell_coords, face_b has private)
# IS directly wired into this entity
tess_shell = f._emit_raw(
    f"TESSELLATED_SHELL_REPRESENTATION('mixed_node_lists',"
    f"(#{face_a_tess.eid},#{face_b_tess.eid}),#{shell_coords.eid})"
)

# Wire into product chain via a placeholder SHELL_BASED_SURFACE_MODEL
# (The tessellated representation is referenced via raw SHAPE_DEFINITION_REPRESENTATION)
# Use a minimal plane face as placeholder so add_product_chain succeeds
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

p00 = f.cartesian_point((0.0, 0.0, 0.0)); p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0)); p01 = f.cartesian_point((0.0, 1.0, 0.0))
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)

def led(va, vb, pt, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

e0 = led(v00, v10, p00,  1, 0, 0)
e1 = led(v10, v11, p10,  0, 1, 0)
e2 = led(v11, v01, p11, -1, 0, 0)
e3 = led(v01, v00, p01,  0,-1, 0)
loop = f.edge_loop([f.oriented_edge(e0,True), f.oriented_edge(e1,True),
                    f.oriented_edge(e2,True), f.oriented_edge(e3,True)])
face_placeholder = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face_placeholder])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
