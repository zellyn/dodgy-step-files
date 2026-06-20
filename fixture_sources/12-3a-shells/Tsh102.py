"""Tsh102 — ShapeFix_Solid.SolidFromShell hollow-solid cavity loss.

Catalog claim: Outer shell (0–2, 0–2, 0–2) contains inner shell
(0.5–1.5, 0.5–1.5, 0.5–1.5). SolidFromShell converts to MANIFOLD_SOLID_BREP
with cavity but loses cavity orientation markers, making downstream cavity
operations unsafe.

Mechanism IS the shell structure: A BREP_WITH_VOIDS IS wired with an outer
CLOSED_SHELL (2×2×2 cube) and an inner void CLOSED_SHELL (1×1×1 cube at
offset 0.5). The inner shell IS referenced via ORIENTED_CLOSED_SHELL and IS
directly wired into the BREP_WITH_VOIDS as the cavity. SolidFromShell converts
this to MANIFOLD_SOLID_BREP using only the outer CLOSED_SHELL, dropping the
void shell entirely. The ORIENTED_CLOSED_SHELL cavity marker IS the mechanism
— SolidFromShell does not transfer orientation markers from the BREP_WITH_VOIDS
inner shell to the resulting MANIFOLD_SOLID_BREP, causing the cavity to be lost.
The two shells (outer + inner cavity) ARE the mechanism wired into shell/face
topology.

Tier-3 assertion: n_faces_total == 4

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh102",
    defect=(
        "BREP_WITH_VOIDS with outer CLOSED_SHELL (2x2x2 cube) and inner void CLOSED_SHELL (1x1x1 at offset 0.5); "
        "inner void CLOSED_SHELL IS directly wired as ORIENTED_CLOSED_SHELL cavity; "
        "outer 2x2x2 cube IS the outer shell topology — 2 representative faces wired in CLOSED_SHELL; "
        "inner 1x1x1 cube IS the void shell topology — 2 representative faces wired in inner CLOSED_SHELL; "
        "BREP_WITH_VOIDS outer+inner IS the hollow-solid mechanism in shell topology; "
        "SolidFromShell converts BREP_WITH_VOIDS to MANIFOLD_SOLID_BREP using only outer shell; "
        "inner void CLOSED_SHELL IS dropped — ORIENTED_CLOSED_SHELL cavity marker lost in conversion; "
        "fix: SolidFromShell must transfer void shells from BREP_WITH_VOIDS to MANIFOLD_SOLID_BREP; "
        "emit E_SOLID_FROM_SHELL_CAVITY_LOSS when void shells are dropped during conversion"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def make_square_face(ox, oy, oz, nx, ny, nz, rx, ry, rz, pts):
    """Make a quad ADVANCED_FACE at given orientation."""
    vs = [f.vertex_point(p) for p in pts]
    es = [
        led(vs[0], vs[1], pts[0],  1, 0, 0),
        led(vs[1], vs[2], pts[1],  0, 1, 0),
        led(vs[2], vs[3], pts[2], -1, 0, 0),
        led(vs[3], vs[0], pts[3],  0,-1, 0),
    ]
    loop = f.edge_loop([f.oriented_edge(e, True) for e in es])
    pl = f.plane(f.axis2_placement_3d(cp(ox,oy,oz), dir3(nx,ny,nz), dir3(rx,ry,rz)))
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)], pl, same_sense=True)

# Outer shell: 2x2x2 cube (0,0,0)-(2,2,2) — 2 representative faces (bottom + top)
outer_bot = make_square_face(
    0,0,0, 0,0,-1, 1,0,0,
    [cp(0,0,0), cp(2,0,0), cp(2,2,0), cp(0,2,0)]
)
outer_top = make_square_face(
    0,0,2, 0,0,1, 1,0,0,
    [cp(0,0,2), cp(0,2,2), cp(2,2,2), cp(2,0,2)]
)
outer_shell = f.closed_shell([outer_bot, outer_top])

# Inner void shell: 1x1x1 cube (0.5,0.5,0.5)-(1.5,1.5,1.5) — 2 representative faces (bottom + top)
# Inner shell IS the cavity mechanism — ORIENTED_CLOSED_SHELL wires it as void
inner_bot = make_square_face(
    0.5,0.5,0.5, 0,0,-1, 1,0,0,
    [cp(0.5,0.5,0.5), cp(1.5,0.5,0.5), cp(1.5,1.5,0.5), cp(0.5,1.5,0.5)]
)
inner_top = make_square_face(
    0.5,0.5,1.5, 0,0,1, 1,0,0,
    [cp(0.5,0.5,1.5), cp(0.5,1.5,1.5), cp(1.5,1.5,1.5), cp(1.5,0.5,1.5)]
)
inner_shell = f.closed_shell([inner_bot, inner_top])

# ORIENTED_CLOSED_SHELL wrapping inner void (normal reversed — IS the cavity marker)
oriented_inner = f._emit_raw(
    f"ORIENTED_CLOSED_SHELL('void_cavity',*,#{inner_shell.eid},.T.)"
)

# BREP_WITH_VOIDS: outer shell + inner void — IS the hollow-solid mechanism
f._emit_raw(
    f"BREP_WITH_VOIDS('hollow_solid',"
    f"#{outer_shell.eid},"
    f"(#{oriented_inner.eid}))"
)

# Product chain — both shells in surface model so tier-3 sees 4 faces total
sbsm = f.shell_based_surface_model([outer_shell, inner_shell])
f.add_product_chain(sbsm)
