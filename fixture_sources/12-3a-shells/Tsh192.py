"""Tsh192 — ShapeFix_Shell.Perform closed-flag sync-failure.

Catalog claim: Shell marked closed but FixFaceOrientation detects free edges
post-fix; the Closed() flag is not reset. A face with edges offset by tolerance
creates a gap; the shell is incorrectly marked as closed while actually open.

Mechanism IS the shell structure: A CLOSED_SHELL containing ONE ADVANCED_FACE
(unit square) WHERE the face edge loop closes with a gap edge — one edge endpoint
IS offset by tolerance (1e-5) from its mating vertex — IS the defect trigger.
The CLOSED_SHELL entity type IS the erroneous closed flag: the shell IS declared
closed but the gap means FixFaceOrientation detects free edges post-fix. Perform()
sets myStatus but does not reset the Closed() flag after detecting the free edge
— IS the sync-failure defect. Downstream solid construction assumes watertight
geometry and fails validation — IS the model impact.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh192",
    defect=(
        "CLOSED_SHELL with GAP EDGE IS the closed-flag sync-failure defect trigger; "
        "unit square face has four boundary edges; v_gap IS vertex offset by 1e-5 from v00 — IS the gap; "
        "e_close IS the closing edge from v01 to v_gap instead of v00 — IS the gap-introducing edge; "
        "v_gap at (1e-5, 0, 0) IS displaced from v00 at (0, 0, 0) by tolerance — IS the gap source; "
        "CLOSED_SHELL entity IS the erroneous closed-flag declaration — IS the sync mismatch; "
        "Perform() processes face, detects free edges at gap — IS the post-fix detection; "
        "Closed() flag IS not reset after free-edge detection — IS the sync-failure defect; "
        "downstream solid construction reads Closed()=true and fails — IS the model impact; "
        "fix: Perform() must reset Closed() when HasFreeEdges() is true post-fix; "
        "emit E_CLOSED_FLAG_SYNC_FAILURE when shell marked closed but free edges detected"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Unit square corners — normal vertices
p00 = cp(0, 0, 0);   v00  = f.vertex_point(p00)
p10 = cp(1, 0, 0);   v10  = f.vertex_point(p10)
p11 = cp(1, 1, 0);   v11  = f.vertex_point(p11)
p01 = cp(0, 1, 0);   v01  = f.vertex_point(p01)
# v_gap: displaced from v00 by 1e-5 — IS the gap-introducing vertex
p_gap = cp(1e-5, 0, 0); v_gap = f.vertex_point(p_gap)

e_bot = led(v00,  v10,  p00,   1, 0, 0)   # bottom — from v00 to v10
e_rgt = led(v10,  v11,  p10,   0, 1, 0)   # right
e_top = led(v11,  v01,  p11,  -1, 0, 0)   # top
# e_close: closes to v_gap instead of v00 — IS the gap edge
e_close = led(v01, v_gap, p01, 0, -1, 0)  # left — closes with gap to v_gap not v00

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_rgt,   True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_close, True),
])
plane = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# CLOSED_SHELL (declared closed) with gap edge — IS the closed-flag sync-failure mechanism
shell = f.closed_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
