"""Twi003 — EDGE_LOOP edges not head-to-tail — adjacent edges' shared
vertices don't coincide.

Catalog claim: Edge n's end vertex is not edge n+1's start vertex; they are
positioned at distinct VERTEX_POINTs separated by more than the kernel's
vertex-equality tolerance. The edges are listed in traversal order but the
wire is broken: there is a 3D gap between consecutive edges. Affects ~5% of
"imperfect" Onshape STEP exports per ABC paper.

Mechanism IS the broken head-to-tail chain in the EDGE_LOOP: four edges
form an almost-square where the end vertex of each edge is a distinct
VERTEX_POINT from the start vertex of the next edge, with each gap = 0.01
(well above any reasonable kernel tolerance). The defect loop IS referenced
by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL; never orphaned.
Kernel must merge near-coincident vertices within tolerance or reject as
malformed if the gap exceeds the working tolerance budget.

Tier-3 assertions:
  - n_edges_total >= 4
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi003",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with four ORIENTED_EDGEs; "
        "each edge's end VERTEX_POINT differs from the next edge's start VERTEX_POINT "
        "by 0.01 units (well above kernel tolerance); "
        "wire is topologically broken at all four junctions; "
        "kernel must merge near-coincident vertices or reject as malformed"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Square corners with 0.01-unit gap at each junction ───────────────────────
# Nominal corners: A(0,0), B(1,0), C(1,1), D(0,1).
# Each edge ends 0.01 short of the next edge's nominal start.
# Gap = 0.01 — well above typical kernel tolerances (1e-7 .. 1e-4).
G = 0.01  # gap magnitude

# Edge 0: A0(0,0) → A1(1-G, 0)   (→ B-side start is B0=(1,0))
pA0 = f.cartesian_point((0.0,     0.0, 0.0))
pA1 = f.cartesian_point((1.0 - G, 0.0, 0.0))
# Edge 1: B0(1,0) → B1(1, 1-G)   (→ C-side start is C0=(1,1))
pB0 = f.cartesian_point((1.0,     0.0,       0.0))
pB1 = f.cartesian_point((1.0,     1.0 - G,   0.0))
# Edge 2: C0(1,1) → C1(G, 1)     (→ D-side start is D0=(0,1))
pC0 = f.cartesian_point((1.0,     1.0, 0.0))
pC1 = f.cartesian_point((G,       1.0, 0.0))
# Edge 3: D0(0,1) → D1(0, G)     (→ A-side start is A0=(0,0))
pD0 = f.cartesian_point((0.0,     1.0, 0.0))
pD1 = f.cartesian_point((0.0,     G,   0.0))

vA0 = f.vertex_point(pA0); vA1 = f.vertex_point(pA1)
vB0 = f.vertex_point(pB0); vB1 = f.vertex_point(pB1)
vC0 = f.vertex_point(pC0); vC1 = f.vertex_point(pC1)
vD0 = f.vertex_point(pD0); vD1 = f.vertex_point(pD1)

def line_edge(p, dx, dy, va, vb):
    import math
    mag = math.hypot(dx, dy)
    d   = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, 1.0)
    ln  = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(pA0,  1.0,  0.0, vA0, vA1)   # A0 → A1 (short of B)
e1 = line_edge(pB0,  0.0,  1.0, vB0, vB1)   # B0 → B1 (short of C); gap after A1
e2 = line_edge(pC0, -1.0,  0.0, vC0, vC1)   # C0 → C1 (short of D); gap after B1
e3 = line_edge(pD0,  0.0, -1.0, vD0, vD1)   # D0 → D1 (short of A); gap after C1

# ── EDGE_LOOP IS the mechanism: four broken junctions ────────────────────────
loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# Wire defect loop into face/shell topology — never orphan.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
