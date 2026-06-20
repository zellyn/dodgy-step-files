"""Tsh194 — ShapeAnalysis_Shell.BadEdges uninitialized extent.

Catalog claim: BadEdges() returns myBad compound without validating that
Perform() has completed. If called before analysis finishes, the compound is
uninitialized, causing undefined Extent() behavior. Manifests as lost or
spurious bad-edge reports when shell contains degenerate edges.

Mechanism IS the shell structure: AN OPEN_SHELL containing ONE ADVANCED_FACE
with a DEGENERATE ZERO-AREA EDGE LOOP IS the defect trigger. The loop IS a
degenerate triangle where all three vertices are distinct but the face normal IS
the zero vector — degenerate geometry causes ShapeAnalysis_Shell.Perform() to
encounter an edge it flags as bad in myBad, then halt early. BadEdges() IS the
defect path: it returns myBad before Perform() marks it as complete, yielding
undefined Extent() — IS the defect.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh194",
    defect=(
        "OPEN_SHELL with DEGENERATE COLLINEAR TRIANGLE IS the BadEdges uninitialized-extent defect trigger; "
        "p0=(0,0,0), p1=(1,0,0), p2=(2,0,0) are collinear — IS the degenerate triangle (zero-area face); "
        "e_01 IS EDGE_CURVE from v0 to v1 along X — IS first degenerate edge; "
        "e_12 IS EDGE_CURVE from v1 to v2 along X — IS second degenerate edge; "
        "e_20 IS EDGE_CURVE from v2 back to v0 along -X — IS closing degenerate edge; "
        "collinear vertices produce zero face normal — IS the geometry-degenerate trigger for Perform(); "
        "Perform() flags edges as bad in myBad then halts early — IS the premature-halt path; "
        "BadEdges() returns myBad before Perform() sets completion flag — IS the defect path; "
        "Extent() on uninitialized myBad yields undefined result — IS the defect; "
        "fix: BadEdges() must check Perform() completion flag before returning myBad; "
        "emit E_BAD_EDGES_UNINITIALIZED_EXTENT when BadEdges() called before analysis completion"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Degenerate collinear triangle: all three points on X-axis — IS the zero-area face
p0 = cp(0, 0, 0); v0 = f.vertex_point(p0)
p1 = cp(1, 0, 0); v1 = f.vertex_point(p1)
p2 = cp(2, 0, 0); v2 = f.vertex_point(p2)

# Three collinear edges — produce zero face normal — IS the bad-edge geometry
e_01 = led(v0, v1, p0,  1, 0, 0)   # forward — IS first degenerate edge
e_12 = led(v1, v2, p1,  1, 0, 0)   # forward — IS second degenerate edge
e_20 = led(v2, v0, p2, -1, 0, 0)   # reverse — IS closing degenerate edge

loop = f.edge_loop([
    f.oriented_edge(e_01, True),
    f.oriented_edge(e_12, True),
    f.oriented_edge(e_20, True),
])
# Plane normal points in Z but face is collinear in X — IS the degenerate face geometry
plane = f.plane(f.axis2_placement_3d(p0, dir3(0, 0, 1), dir3(1, 0, 0)))
face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# OPEN_SHELL with degenerate collinear face — IS the BadEdges uninitialized-extent mechanism
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
