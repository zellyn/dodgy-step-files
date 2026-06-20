"""Tsh189 — ShapeAnalysis_Shell.BadEdges uninitialized compound.

Catalog claim: BadEdges() returns compound from uninitialized myBad without
validation. Calling before Perform() completes exposes lazy-init violation.
Shell contains degenerate zero-length edge to trigger analysis path.

Mechanism IS the shell structure: A CLOSED_SHELL containing ONE ADVANCED_FACE
with a DEGENERATE ZERO-LENGTH EDGE IS the defect trigger. The zero-length edge
IS created by having two adjacent vertices at the same point — va and vb coincide
at (0,0,0). BadEdges() IS the defect path: it returns myBad compound before
Perform() has populated it. The shell IS syntactically valid STEP (a triangle
with one collapsed edge) but the zero-length edge causes analysis to halt early.
BadEdges() called on the incomplete analysis state returns an uninitialized or
empty compound instead of the degenerate edge — IS the defect.

Tier-3 assertion: shape_null == True

live oracle: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh189",
    defect=(
        "CLOSED_SHELL with ONE ADVANCED_FACE containing ZERO-LENGTH EDGE IS the BadEdges defect trigger; "
        "va and vb are COINCIDENT VERTICES at (0,0,0) — IS the zero-length edge source; "
        "e_zero IS EDGE_CURVE from va to vb at same point — IS the degenerate edge; "
        "e_bc IS edge from vb=(0,0,0) to vc=(1,0,0) — IS the second edge; "
        "e_ca IS edge from vc=(1,0,0) back to va=(0,0,0) — IS the third edge; "
        "triangle collapses: zero-length e_zero causes Perform() to halt early — IS the trigger path; "
        "BadEdges() returns myBad before population — IS the uninitialized compound defect; "
        "returned compound IS empty or uninitialized instead of containing e_zero — IS the defect; "
        "fix: BadEdges() must guard against pre-Perform call; Perform() must mark myBad before halt; "
        "emit E_BAD_EDGES_UNINITIALIZED when BadEdges() called before analysis completion"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))

# ZERO-LENGTH EDGE: va and vb are coincident at origin — IS the degenerate edge
pa = cp(0, 0, 0); va = f.vertex_point(pa)  # coincident point 1
pb = cp(0, 0, 0); vb = f.vertex_point(pb)  # coincident point 2 (same coords — IS zero-length)
pc = cp(1, 0, 0); vc = f.vertex_point(pc)

# e_zero: EDGE_CURVE from va to vb with zero length — IS the degenerate bad edge
d_zero = dir3(1, 0, 0)  # direction required but length collapses to zero
vec_zero = f.vector(d_zero, 0.0)  # zero-length vector — IS the degenerate magnitude
ln_zero = f.line(pa, vec_zero)
e_zero = f.edge_curve(va, vb, ln_zero)  # zero-length — IS the defect trigger edge

# e_bc: from vb (=origin) to vc=(1,0,0)
d_bc = dir3(1, 0, 0)
vec_bc = f.vector(d_bc, 1.0)
ln_bc = f.line(pb, vec_bc)
e_bc = f.edge_curve(vb, vc, ln_bc)

# e_ca: from vc=(1,0,0) back to va=(0,0,0)
d_ca = dir3(-1, 0, 0)
vec_ca = f.vector(d_ca, 1.0)
ln_ca = f.line(pc, vec_ca)
e_ca = f.edge_curve(vc, va, ln_ca)

# Degenerate triangle loop with zero-length first edge
loop = f.edge_loop([
    f.oriented_edge(e_zero, True),   # IS the zero-length degenerate edge
    f.oriented_edge(e_bc,   True),
    f.oriented_edge(e_ca,   True),
])
plane = f.plane(f.axis2_placement_3d(pa, dir3(0, 0, 1), dir3(1, 0, 0)))
face_degen = f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# CLOSED_SHELL with degenerate zero-length edge — IS the BadEdges uninitialized-compound mechanism
shell = f.closed_shell([face_degen])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
