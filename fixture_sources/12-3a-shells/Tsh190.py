"""Tsh190 — ShapeAnalysis_Shell.FreeEdges uninitialized compound.

Catalog claim: FreeEdges() returns compound from uninitialized myFree without
a completion guard. Open shell with incomplete edge loop creates free edges;
FreeEdges() called before analysis state initialized yields undefined Extent().

Mechanism IS the shell structure: AN OPEN_SHELL containing ONE ADVANCED_FACE
(a unit square with only THREE of four boundary edges wired into the face loop)
IS the defect trigger. The missing fourth edge IS the free edge — an unpaired
boundary segment that ShapeAnalysis_Shell IS expected to detect in myFree. The
open shell IS syntactically valid STEP but the loop closure is intentionally
incomplete: one boundary segment has no oriented_edge in the loop. FreeEdges()
IS the defect path: it returns myFree compound before Perform() populates it,
yielding uninitialized or empty Extent() instead of the free edge count — IS
the defect.

Tier-3 assertion: shape_null == True

live oracle: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh190",
    defect=(
        "OPEN_SHELL with INCOMPLETE EDGE LOOP IS the FreeEdges uninitialized-compound defect trigger; "
        "unit square face has only THREE oriented edges in loop — IS the incomplete loop; "
        "v00, v10, v11 form the wired boundary; edge e_top from v11 to v01 IS omitted — IS the free edge; "
        "the open left edge from v01 back to v00 IS also implicitly free — IS the second free boundary; "
        "FreeEdges() IS the defect path: returns myFree before Perform() populates it; "
        "Extent() on uninitialized myFree compound yields undefined result — IS the defect; "
        "fix: FreeEdges() must guard against pre-Perform call with completion flag; "
        "emit E_FREE_EDGES_UNINITIALIZED when FreeEdges() called before analysis completion"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Unit square corners: (0,0,0) -> (1,0,0) -> (1,1,0) -> (0,1,0)
p00 = cp(0, 0, 0); v00 = f.vertex_point(p00)
p10 = cp(1, 0, 0); v10 = f.vertex_point(p10)
p11 = cp(1, 1, 0); v11 = f.vertex_point(p11)
p01 = cp(0, 1, 0); v01 = f.vertex_point(p01)

# Three edges wired — IS the partial (incomplete) boundary
e_bot = led(v00, v10, p00,  1, 0, 0)   # bottom edge — wired
e_rgt = led(v10, v11, p10,  0, 1, 0)   # right edge — wired
e_top = led(v11, v01, p11, -1, 0, 0)   # top edge — wired
# e_lft from v01 to v00 IS intentionally ABSENT from loop — IS the free edge

# Edge loop with only three edges — IS the incomplete loop (missing left edge)
loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    # left edge omitted — IS the free-edge gap that triggers FreeEdges() path
])
plane = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# OPEN_SHELL with incomplete loop — IS the FreeEdges uninitialized-compound mechanism
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
