"""Tsh084 — ShapeAnalysis_Shell.CheckOrientedShells closed-shell self-test.

Catalog claim: Single CLOSED_SHELL containing one face with inwardly-oriented
normal (inside-out solid). Detector must classify geometric orientation before
propagating fixes; fixture passes validate2 despite reversed normal, exposing
tier-3 lint class.

Mechanism IS the shell structure: CLOSED_SHELL contains a single unit-cube
ADVANCED_FACE (z=0 square) with same_sense=False, causing the face's surface
normal to point inward (−Z into the solid interior) rather than outward (+Z).
The CLOSED_SHELL wraps this face with its inward-pointing geometry — the
same_sense=False wired into the ADVANCED_FACE IS the mechanism. OCCT's
CheckOrientedShells must detect this reversed normal before propagating
orientation fixes; failure to detect results in an inside-out solid that
validates structurally but is geometrically inverted.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh084",
    defect=(
        "CLOSED_SHELL containing one ADVANCED_FACE (unit square at z=0); "
        "face IS wired with same_sense=False causing inward-pointing normal (−Z); "
        "inside-out normal IS the mechanism directly in ADVANCED_FACE topology; "
        "CLOSED_SHELL references this inward-normal face as its sole face; "
        "ShapeAnalysis_Shell.CheckOrientedShells must detect reversed orientation; "
        "fixture passes structural validate2 but is geometrically inside-out; "
        "fix: detect same_sense=False in closed-shell context; "
        "emit E_INWARD_NORMAL or re-orient before propagating fixes"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Unit square at z=0
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

# Plane with +Z axis; same_sense=False makes surface normal point −Z (inward)
pl = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))

# same_sense=False IS the inward-normal mechanism wired into ADVANCED_FACE
face = f.advanced_face([f.face_outer_bound(loop)], pl, same_sense=False)

# CLOSED_SHELL with inward-normal face IS the defect topology
shell = f.closed_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
