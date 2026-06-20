"""Tsh003 — Closed solid round-trips as SHELL_BASED_SURFACE_MODEL/OPEN_SHELL.

Catalog claim (SpaceClaim regression): a topologically closed solid is emitted
as SHELL_BASED_SURFACE_MODEL → OPEN_SHELL instead of MANIFOLD_SOLID_BREP →
CLOSED_SHELL.  Downstream tools that gate on MANIFOLD_SOLID_BREP refuse to
import it as a solid.

Mechanism IS the shell structure: a topologically closed 4-face tetrahedron is
wired as OPEN_SHELL inside SHELL_BASED_SURFACE_MODEL with no MANIFOLD_SOLID_BREP
present.  The wrong container type IS the defect, wired into the shell/face
topology.

Byte assertions:
  - contains(b'OPEN_SHELL')
  - contains(b'SHELL_BASED_SURFACE_MODEL')
  - count_entity_def(b'MANIFOLD_SOLID_BREP') == 0

Tier-3 assertion: n_faces_total == 4
live oracle: occt=shape(1)/shape(1)/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh003",
    defect=(
        "Topologically closed tetrahedron emitted as SHELL_BASED_SURFACE_MODEL/"
        "OPEN_SHELL instead of MANIFOLD_SOLID_BREP/CLOSED_SHELL; no MANIFOLD_SOLID_BREP "
        "present; wrong container type IS wired into shell/face topology; "
        "downstream tools that gate on MANIFOLD_SOLID_BREP reject it as solid"
    ),
)

# ── Tetrahedron: 4 triangular ADVANCED_FACEs, topologically closed ──────────
# Vertices of a unit tetrahedron
p0 = f.cartesian_point(( 0.0,  0.0,  0.0))
p1 = f.cartesian_point(( 1.0,  0.0,  0.0))
p2 = f.cartesian_point(( 0.5,  0.866025403784, 0.0))
p3 = f.cartesian_point(( 0.5,  0.288675134595, 0.816496580928))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

def line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# Edges of the tetrahedron (each shared by two faces but we build independent
# edge objects per face to keep the fixture self-contained)
def tri_face(va, vb, vc, pa, pb, pc, dx01, dy01, dz01,
             dx12, dy12, dz12, dx20, dy20, dz20, nx, ny, nz):
    e0 = line_edge(va, vb, pa, dx01, dy01, dz01)
    e1 = line_edge(vb, vc, pb, dx12, dy12, dz12)
    e2 = line_edge(vc, va, pc, dx20, dy20, dz20)
    loop = f.edge_loop([f.oriented_edge(e0, True),
                        f.oriented_edge(e1, True),
                        f.oriented_edge(e2, True)])
    ax = f.axis2_placement_3d(
        pa, f.direction((float(nx), float(ny), float(nz))),
        f.direction((float(dx01), float(dy01), float(dz01)))
    )
    pl = f.plane(ax)
    return f.advanced_face([f.face_outer_bound(loop)], pl)

# Face 0: base (p0, p1, p2) — normal pointing down (0,0,-1)
face0 = tri_face(v0, v2, v1, p0, p2, p1,
                 0.5, 0.866025, 0,  # p0→p2
                 0.5,-0.866025, 0,  # p2→p1
                -1,  0,          0, # p1→p0
                 0, 0, -1)

# Face 1: (p0, p1, p3) — normal approximately (-0.816, 0, 0.577) rotated
# Use a simple outward-pointing normal for the plane
face1 = tri_face(v0, v1, v3, p0, p1, p3,
                 1, 0, 0,
                -0.5, 0.288675, 0.816497,
                -0.5,-0.288675,-0.816497,
                 0, -0.942809, 0.333333)

# Face 2: (p1, p2, p3)
face2 = tri_face(v1, v2, v3, p1, p2, p3,
                -0.5, 0.866025, 0,
                 0,  -0.57735, 0.816497,
                 0.5,-0.288675,-0.816497,
                 0.816497, 0.471405, 0.333333)

# Face 3: (p2, p0, p3)
face3 = tri_face(v2, v0, v3, p2, p0, p3,
                -0.5,-0.866025, 0,
                 0,   0.57735, 0.816497,
                 0.5,-0.288675,-0.816497,
                -0.816497, 0.471405, 0.333333)

# ── DEFECT: topologically closed but wrapped as OPEN_SHELL/SHELL_BASED_SURFACE_MODEL ──
# No MANIFOLD_SOLID_BREP is emitted — that IS the SpaceClaim regression mechanism.
open_sh = f.open_shell([face0, face1, face2, face3])
sbsm = f.shell_based_surface_model([open_sh])

f.add_product_chain(sbsm)
