"""Twi027 — ConnectEdgesToWires fails on INTERNAL-only edges / non-determinism.

Catalog claim: A free-edges-to-wires connection pass throws when given a compound
containing only INTERNAL-oriented edges (no wires, no faces). The standalone edges
form a closed ring geometrically, but the algorithm either crashes or returns an
empty result with no diagnostic.

Mechanism IS the GEOMETRIC_CURVE_SET of three standalone EDGE_CURVE entities
with no enclosing wire, face, or shell: each edge is emitted directly into the
GEOMETRIC_CURVE_SET aggregate; none are wired into an EDGE_LOOP. The bare edge
set IS the topological compound that triggers the failure. The GEOMETRIC_CURVE_SET
IS wired into the product chain as the shape representation item.

Byte assertions:
  - contains(b'GEOMETRIC_CURVE_SET(')
  - count_entity_def(b'EDGE_CURVE') == 3
  - count_entity_def(b'EDGE_LOOP') == 0

Tier-3 assertion: shape_null == True

live oracle: occt=empty/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi027",
    defect=(
        "GEOMETRIC_CURVE_SET containing three standalone EDGE_CURVE entities "
        "whose vertices form a closed equilateral triangle in 3D; "
        "no EDGE_LOOP, no FACE_BOUND, no ADVANCED_FACE, no OPEN_SHELL — "
        "bare standalone edges IS the mechanism; "
        "EDGE_CURVEs ARE wired into GEOMETRIC_CURVE_SET which IS the shape item; "
        "ConnectEdgesToWires pass must emit a diagnostic on INTERNAL-only edge compound; "
        "kernel must warn and return empty result, not crash silently"
    ),
)

import math

# ── Three vertices of an equilateral triangle in z=0 ─────────────────────────
R = 1.0
pts = [
    (R * math.cos(math.radians(a)), R * math.sin(math.radians(a)), 0.0)
    for a in (0, 120, 240)
]
verts = [f.vertex_point(f.cartesian_point(p)) for p in pts]

# ── Three line edges forming the triangle ─────────────────────────────────────
edges = []
for i in range(3):
    v_s = verts[i]
    v_e = verts[(i + 1) % 3]
    xs, ys, _ = pts[i]
    xe, ye, _ = pts[(i + 1) % 3]
    dx, dy = xe - xs, ye - ys
    length = math.hypot(dx, dy)
    ln_dir = f.direction((dx / length, dy / length, 0.0))
    ln_vec = f.vector(ln_dir, length)
    ln     = f.line(f.cartesian_point((xs, ys, 0.0)), ln_vec)
    ec     = f.edge_curve(v_s, v_e, ln)
    edges.append(ec)

# ── GEOMETRIC_CURVE_SET: standalone edges, no EDGE_LOOP — IS the mechanism ───
gcs = f._emit_raw(
    "GEOMETRIC_CURVE_SET('',({}))".format(
        ",".join(f"#{ec.eid}" for ec in edges)
    )
)

# Wire the GEOMETRIC_CURVE_SET into the product chain.
f.add_product_chain(gcs)
