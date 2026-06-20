"""Tsh068 — MANIFOLD_SOLID_BREP whose outer shell is open (not closed) silently accepted.

Catalog claim: The schema mandates that the outer shell of a MANIFOLD_SOLID_BREP be a
watertight CLOSED_SHELL. Some producers route an OPEN_SHELL through the same slot or emit
a CLOSED_SHELL whose face/edge graph has free edges. The reader accepts both forms; the
resulting "solid" has open boundary, downstream Boolean operations fail with cryptic errors.

Mechanism IS the shell structure: an OPEN_SHELL containing 2 ADVANCED_FACEs (a bottom and
top quad that share no edges — an open patch pair, not a closed solid boundary) IS directly
referenced by a MANIFOLD_SOLID_BREP entity. MANIFOLD_SOLID_BREP's `outer` attribute is
supposed to require a CLOSED_SHELL; the OPEN_SHELL IS the violation wired directly into
the MANIFOLD_SOLID_BREP reference. The shell has free edges on all four sides of each face;
no edge is shared between the two faces. Downstream operations on this "solid" fail or
produce invalid results.

Byte assertions:
  - contains(b'MANIFOLD_SOLID_BREP')
  - contains(b'OPEN_SHELL')

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh068",
    defect=(
        "OPEN_SHELL with 2 ADVANCED_FACEs (separate unit quads sharing no edges) "
        "IS directly referenced by MANIFOLD_SOLID_BREP as its outer shell; "
        "OPEN_SHELL-as-outer-of-MANIFOLD_SOLID_BREP IS the mechanism; "
        "OPEN_SHELL has free edges on all sides of both faces; "
        "schema requires outer shell of MANIFOLD_SOLID_BREP to be a CLOSED_SHELL; "
        "reader silently accepts; resulting solid has open boundary; "
        "fix: verify shell closedness (every edge in exactly 2 faces) before promoting "
        "to solid; emit E_OPEN_OUTER_SHELL when invariant fails"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def make_plane(ox, oy, oz, nx, ny, nz, rx, ry, rz):
    plc = f.axis2_placement_3d(cp(ox,oy,oz), dir3(nx,ny,nz), dir3(rx,ry,rz))
    return f.plane(plc)

# Face 1: unit quad at z=0, normal -Z (bottom cap)
pl_bot = make_plane(0,0,0, 0,0,-1, 1,0,0)
p00 = cp(0,0,0); p10 = cp(1,0,0); p11 = cp(1,1,0); p01 = cp(0,1,0)
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)
e0 = led(v00, v10, p00,  1, 0, 0)
e1 = led(v10, v11, p10,  0, 1, 0)
e2 = led(v11, v01, p11, -1, 0, 0)
e3 = led(v01, v00, p01,  0,-1, 0)
loop0 = f.edge_loop([f.oriented_edge(e0,True), f.oriented_edge(e1,True),
                     f.oriented_edge(e2,True), f.oriented_edge(e3,True)])
face_bot = f.advanced_face([f.face_outer_bound(loop0)], pl_bot)

# Face 2: unit quad at z=1, normal +Z (top cap)
# Independent edges — shares NO edges with face_bot (IS the open-shell defect)
pl_top = make_plane(0,0,1, 0,0,1, 1,0,0)
q00 = cp(0,0,1); q10 = cp(1,0,1); q11 = cp(1,1,1); q01 = cp(0,1,1)
w00 = f.vertex_point(q00); w10 = f.vertex_point(q10)
w11 = f.vertex_point(q11); w01 = f.vertex_point(q01)
f0 = led(w00, w10, q00,  1, 0, 0)
f1 = led(w10, w11, q10,  0, 1, 0)
f2 = led(w11, w01, q11, -1, 0, 0)
f3 = led(w01, w00, q01,  0,-1, 0)
loop1 = f.edge_loop([f.oriented_edge(f0,True), f.oriented_edge(f1,True),
                     f.oriented_edge(f2,True), f.oriented_edge(f3,True)])
face_top = f.advanced_face([f.face_outer_bound(loop1)], pl_top)

# OPEN_SHELL — IS directly used as MANIFOLD_SOLID_BREP's outer (the violation)
open_shell = f.open_shell([face_bot, face_top])

# MANIFOLD_SOLID_BREP with OPEN_SHELL as outer IS the mechanism
msb = f._emit_raw(f"MANIFOLD_SOLID_BREP('open_outer_solid',#{open_shell.eid})")

# Product chain via surface shape (so file is loadable)
sbsm = f.shell_based_surface_model([open_shell])
f.add_product_chain(sbsm)
