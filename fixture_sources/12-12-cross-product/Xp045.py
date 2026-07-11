"""Xp045 — Far-from-origin model collapses in a float32 (single-precision)
viewer output buffer while double-precision CAD renders it correctly.

Catalog claim (cross-oracle double-vs-single-precision differential): a
fully VALID solid whose own extent is ~10 mm but which is authored a very
large distance from the origin — here a 10×10 planar square whose corners
sit at absolute coordinates ~1.2e8 mm (GIS / absolute-coordinate style).

Double-precision readers (OCCT, CAD Assistant) load and render it fine —
the 10 mm relief is ~1e-7 of the absolute magnitude, still far above the
1e-6 mm model tolerance. A reader that down-converts vertex positions into
a **float32** buffer (three.js / glTF / WASM viewer pipeline) cannot
represent 10-unit relief at magnitude 1.2e8: the float32 ULP there is ~16
units, so all four corners quantize to the SAME grid point and the face
collapses to a degenerate zero-area primitive — the viewer shows an empty
model ("doesn't contain any meshes … all positions are 0").

This is ORACLE-INVISIBLE to our single (double-precision) OCCT oracle: the
file loads as a normal shape; only the float32 output stage exhibits the
collapse. Provenance tier runtime-only.

Distinct from Tb013 (far-from-origin DOUBLE-precision ULP-vs-tolerance) and
Tb010 (float32 round-trip that MASKS a real self-intersection). Here the
file is clean and self-consistent; the defect is purely the output-buffer
precision down-conversion in a WASM/glTF/three.js viewer.

Byte assertions:
  contains(b'CARTESIAN_POINT')
  contains(b'120000000.0')     # base X ~1.2e8 — far-from-origin placement
  count_entity_def(b'CARTESIAN_POINT') >= 4

Tier-3 assertion:
  load == "ok"                  # valid file: double-precision oracle loads it

Expected (double-precision oracle; the float32 collapse is viewer-only):
  occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a  (gmsh count PROVISIONAL)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Xp045",
    defect=(
        "valid 10x10 planar square whose four CARTESIAN_POINTs sit at absolute "
        "coordinates ~1.2e8 mm from the origin (own extent ~10 mm); double-"
        "precision readers load it, but a float32 viewer output buffer cannot "
        "resolve 10-unit relief at magnitude 1.2e8 (ULP ~16) so all corners "
        "quantize to one point and the mesh collapses to zero — reader must "
        "recentre to a local frame before down-converting, or warn"
    ),
)

# Large absolute base offset (~1.2e8, GIS/absolute-coordinate style); the
# square's own extent is only 10 units, ~1e-7 of the magnitude.
BX, BY, BZ = 120000000.0, 85000000.0, 33000000.0
S = 10.0  # side length (mm)

# ── Carrier plane at the far-away location, normal +Z ─────────────────────────
orig  = f.cartesian_point((BX, BY, BZ))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Square corners (all far from origin) ──────────────────────────────────────
p0 = f.cartesian_point((BX,     BY,     BZ))
p1 = f.cartesian_point((BX + S, BY,     BZ))
p2 = f.cartesian_point((BX + S, BY + S, BZ))
p3 = f.cartesian_point((BX,     BY + S, BZ))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)


def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx * dx + dy * dy + dz * dz) ** 0.5
    d = f.direction((dx / length, dy / length, dz / length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)


e0 = line_edge(p0, p1, v0, v1)
e1 = line_edge(p1, p2, v1, v2)
e2 = line_edge(p2, p3, v2, v3)
e3 = line_edge(p3, p0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
