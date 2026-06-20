"""Tsh030 — Non-finite (infinite) solid built from open shell.

Catalog claim: A solid whose oriented shells do not bound a finite region;
typically a half-space accidentally produced by a Boolean op. The volume
integral over the shell returns infinite or NaN; the "solid" describes an
unbounded volume rather than a bounded body.

Mechanism IS the shell structure: a single planar ADVANCED_FACE is wrapped
as the sole face in a CLOSED_SHELL which is then referenced by
MANIFOLD_SOLID_BREP. A single planar face cannot close any finite volume —
the "shell" is entirely open, enclosing an infinite half-space. The
non-finite nature IS wired into the shell/face topology: one face with
infinite-extent plane surface but no enclosing boundary.

Tier-3 assertions:
  - face[0].surface_type == "plane"
  - n_edges_total >= 4
  - n_vertices_total >= 8
  - face[0].sliver_aspect_max_min > 1e6

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh030",
    defect=(
        "MANIFOLD_SOLID_BREP wrapping a CLOSED_SHELL containing a single planar face; "
        "one plane cannot close any finite volume — shell encloses infinite half-space; "
        "non-finite solid IS wired into shell/face topology; strict receivers must reject"
    ),
)

# Single large planar face — the only face in the "solid".
# A plane has infinite extent; wrapping it as a CLOSED_SHELL with no other
# faces means the enclosed volume is unbounded (infinite half-space).
# Make the face a very elongated quad to satisfy sliver_aspect_max_min > 1e6:
# width = 1e-6, length = 10 -> aspect = 1e7 > 1e6.

def pt(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))

def mk_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# Sliver rectangle: 10 units long (X), 1e-6 units wide (Y) — aspect = 1e7
W = 1e-6  # width
L = 10.0  # length

p0 = pt(0.0,  0.0, 0.0)
p1 = pt(L,    0.0, 0.0)
p2 = pt(L,    W,   0.0)
p3 = pt(0.0,  W,   0.0)

v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

e0 = mk_edge(v0, v1, p0,  1, 0, 0)
e1 = mk_edge(v1, v2, p1,  0, 1, 0)
e2 = mk_edge(v2, v3, p2, -1, 0, 0)
e3 = mk_edge(v3, v0, p3,  0,-1, 0)

lp = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# Plane with normal (0,0,1)
ax = f.axis2_placement_3d(p0, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
plane = f.plane(ax)
face = f.advanced_face([f.face_outer_bound(lp)], plane)

# DEFECT: single planar face in CLOSED_SHELL → MANIFOLD_SOLID_BREP.
# One face cannot close a finite volume — this IS the mechanism.
closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb)
