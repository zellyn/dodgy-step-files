"""Tsh066 — Same CLOSED_SHELL referenced from two MANIFOLD_SOLID_BREP entities.

Catalog claim: An EXPRESS-level CLOSED_SHELL entity is referenced as the outer attribute
of two distinct MANIFOLD_SOLID_BREP entities. Cross-referencing the same shell from two
solids creates aliasing: modifications to one solid (orientation flip, healing) affect
the other, or receivers that copy-on-read produce two independent solids that lose the
producer's intent.

Mechanism IS the shell structure: one CLOSED_SHELL entity (6 ADVANCED_FACEs forming a
unit cube) IS directly referenced by two MANIFOLD_SOLID_BREP entities via the same
entity ID. The dual-reference IS wired into the STEP entity graph. A receiver that builds
in-memory topology by walking from each solid into its shell produces two solids both
pointing at the same shell object, and mutating one corrupts the other.

Byte assertions:
  - count_entity_def(b'MANIFOLD_SOLID_BREP') == 2
  - count_entity_def(b'CLOSED_SHELL') == 1
  - count_entity_def(b'ADVANCED_FACE') == 6

Tier-3 assertion: shape_null == True

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh066",
    defect=(
        "One CLOSED_SHELL entity (6-face unit cube) IS referenced by two "
        "MANIFOLD_SOLID_BREP entities via the same CLOSED_SHELL entity ID; "
        "dual MANIFOLD_SOLID_BREP reference to single CLOSED_SHELL IS the mechanism; "
        "receiver walking each solid into the same shell object produces aliased solids; "
        "mutation or orientation-flip of one solid's shell corrupts the other; "
        "fix: detect shared-shell aliasing; reject as malformed or copy-on-read with "
        "documented policy; never allow two MANIFOLD_SOLID_BREPs to alias one shell"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))

def make_plane(ox, oy, oz, nx, ny, nz, rx, ry, rz):
    plc = f.axis2_placement_3d(cp(ox,oy,oz), dir3(nx,ny,nz), dir3(rx,ry,rz))
    return f.plane(plc)

def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def rect_face(corner_pts_dirs, plane):
    """Build an ADVANCED_FACE from list of (cartesian_point, (dx,dy,dz)) pairs.
    Each entry gives a corner point and the direction to the next corner.
    """
    verts = [f.vertex_point(p) for p, _ in corner_pts_dirs]
    edges = []
    n = len(corner_pts_dirs)
    for i in range(n):
        va = verts[i]; vb = verts[(i+1) % n]
        pt, dxyz = corner_pts_dirs[i]
        edges.append(led(va, vb, pt, *dxyz))
    lp = f.edge_loop([f.oriented_edge(e, True) for e in edges])
    return f.advanced_face([f.face_outer_bound(lp)], plane)

# Unit cube: 6 faces on planes at z=0, z=1, x=0, x=1, y=0, y=1
pl_z0 = make_plane(0,0,0,  0,0,-1,  1,0,0)
pl_z1 = make_plane(0,0,1,  0,0, 1,  1,0,0)
pl_x0 = make_plane(0,0,0, -1,0, 0,  0,1,0)
pl_x1 = make_plane(1,0,0,  1,0, 0,  0,1,0)
pl_y0 = make_plane(0,0,0,  0,-1,0,  1,0,0)
pl_y1 = make_plane(0,1,0,  0, 1,0,  1,0,0)

face_bot = rect_face([
    (cp(0,0,0), ( 1,0,0)), (cp(1,0,0), (0, 1,0)),
    (cp(1,1,0), (-1,0,0)), (cp(0,1,0), (0,-1,0)),
], pl_z0)
face_top = rect_face([
    (cp(0,0,1), (0, 1,0)), (cp(0,1,1), ( 1,0,0)),
    (cp(1,1,1), (0,-1,0)), (cp(1,0,1), (-1,0,0)),
], pl_z1)
face_frt = rect_face([
    (cp(0,0,0), (0,0, 1)), (cp(0,0,1), ( 1,0,0)),
    (cp(1,0,1), (0,0,-1)), (cp(1,0,0), (-1,0,0)),
], pl_y0)
face_bck = rect_face([
    (cp(0,1,0), ( 1,0,0)), (cp(1,1,0), (0,0, 1)),
    (cp(1,1,1), (-1,0,0)), (cp(0,1,1), (0,0,-1)),
], pl_y1)
face_lft = rect_face([
    (cp(0,0,0), (0, 1,0)), (cp(0,1,0), (0,0, 1)),
    (cp(0,1,1), (0,-1,0)), (cp(0,0,1), (0,0,-1)),
], pl_x0)
face_rgt = rect_face([
    (cp(1,0,0), (0,0, 1)), (cp(1,0,1), (0, 1,0)),
    (cp(1,1,1), (0,0,-1)), (cp(1,1,0), (0,-1,0)),
], pl_x1)

# ONE CLOSED_SHELL referenced by TWO MANIFOLD_SOLID_BREPs — IS the mechanism
closed = f.closed_shell([face_bot, face_top, face_frt, face_bck, face_lft, face_rgt])

# Both solids reference the same closed shell entity ID
f._emit_raw(f"MANIFOLD_SOLID_BREP('brep_a',#{closed.eid})")
f._emit_raw(f"MANIFOLD_SOLID_BREP('brep_b',#{closed.eid})")

# Product chain via surface shape (closed shell acts as the shell model)
sbsm = f.shell_based_surface_model([closed])
f.add_product_chain(sbsm)
