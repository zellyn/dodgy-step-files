"""Tfa176 — ShapeFix_Face.FixOrientation face-with-100-edges.

Catalog claim: ADVANCED_FACE whose EDGE_LOOP contains 101+ LINE edges.
FixOrientation allocates a fixed-size internal buffer while traversing the
outer wire's edges linearly; the traversal count exceeds buffer capacity
causing memory corruption and potential crash.
Evidence: Fixture contains a 101-edge circular polygon; FixOrientation's
edge enumeration will overflow the internal buffer.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE: a regular 101-gon (101 LINE
edges) approximating a circle on a PLANE surface. The EDGE_LOOP references
101 ORIENTED_EDGEs, each backed by a LINE EDGE_CURVE. When FixOrientation
traverses the outer wire to count/buffer edge vectors, it overflows the
fixed-size internal buffer allocated for the edge count.
Defect IS on live face traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(102) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa176",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE; "
        "outer EDGE_LOOP contains 101 LINE edges (regular 101-gon, radius=5.0); "
        "FixOrientation allocates fixed-size internal buffer for edge traversal; "
        "101 edges exceeds buffer capacity → memory corruption / crash; "
        "defect IS on live OPEN_SHELL traversal path; "
        "no orphaned entities"
    ),
)

N = 101       # Number of polygon edges (triggers the buffer-overflow path)
R = 5.0       # Circumradius

# ── PLANE surface at origin, normal +Z ────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
plane   = f.plane(f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir))

# ── Generate 101 vertices evenly spaced around a circle of radius R ───────────
angles = [2.0 * math.pi * i / N for i in range(N)]
pts = [f.cartesian_point((R * math.cos(a), R * math.sin(a), 0.0)) for a in angles]
verts = [f.vertex_point(p) for p in pts]

# ── Build 101 LINE EDGE_CURVEs ────────────────────────────────────────────────
edges = []
for i in range(N):
    j = (i + 1) % N
    px, py = R * math.cos(angles[i]), R * math.sin(angles[j])
    dx = R * math.cos(angles[j]) - R * math.cos(angles[i])
    dy = R * math.sin(angles[j]) - R * math.sin(angles[i])
    length = math.hypot(dx, dy)
    ec = f.edge_curve(
        verts[i], verts[j],
        f.line(pts[i], f.vector(f.direction((dx / length, dy / length, 0.0)), length))
    )
    edges.append(ec)

# ── EDGE_LOOP with 101 oriented edges ─────────────────────────────────────────
outer_loop = f.edge_loop([f.oriented_edge(e, True) for e in edges])

# ── ADVANCED_FACE: 101-gon polygon, one outer bound ───────────────────────────
face = f.advanced_face([f.face_outer_bound(outer_loop)], plane)

shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa176.stp")
