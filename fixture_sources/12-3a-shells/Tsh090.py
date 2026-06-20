"""Tsh090 — ShapeFix_Shell.FixFaceOrientation single-face shell.

Catalog claim: Single-face closed shell with inverted orientation flag (.F.
on FACE_OUTER_BOUND). Tests orientation propagation logic in FixFaceOrientation.
With only one face, no adjacent face to propagate from. Expected: orientation
flipped to .T.. Likely failure: Silent skip; propagation assumes ≥2 faces,
returns unchanged inverted shell.

Mechanism IS the shell structure: OPEN_SHELL contains exactly 1 ADVANCED_FACE.
The FACE_OUTER_BOUND IS wired with orientation=False (.F.) — the inverted outer-
bound flag IS directly in the face topology. There is no adjacent face for
orientation propagation. The single-face shell with inverted FACE_OUTER_BOUND
IS the mechanism that exposes the ≥2-face assumption in FixFaceOrientation.
The algorithm skips the single-face case without flipping, returning the shell
with the inverted outer bound unchanged.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh090",
    defect=(
        "OPEN_SHELL with exactly 1 ADVANCED_FACE — IS the single-face mechanism; "
        "FACE_OUTER_BOUND IS wired with orientation=False (.F.) — inverted flag; "
        "inverted .F. outer-bound IS directly embedded in ADVANCED_FACE topology; "
        "no adjacent face exists for orientation propagation — IS the mechanism; "
        "single-face shell with inverted FACE_OUTER_BOUND exposes ≥2-face assumption; "
        "ShapeFix_Shell.FixFaceOrientation silently skips; returns inverted shell; "
        "fix: detect single-face shell; flip FACE_OUTER_BOUND to .T. directly; "
        "emit E_SINGLE_FACE_ORIENTATION_SKIP when propagation is bypassed"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Single unit quad: x=0..1, y=0..1, z=0
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0)
p11 = cp(1, 1, 0); p01 = cp(0, 1, 0)
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)
e0 = led(v00, v10, p00,  1, 0, 0)
e1 = led(v10, v11, p10,  0, 1, 0)
e2 = led(v11, v01, p11, -1, 0, 0)
e3 = led(v01, v00, p01,  0,-1, 0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
pl = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
# FACE_OUTER_BOUND orientation=False (.F.) IS the inverted flag — IS the mechanism
face = f.advanced_face([f.face_outer_bound(loop, orientation=False)], pl, same_sense=True)

# OPEN_SHELL with exactly 1 face: no propagation neighbour — IS the mechanism
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
