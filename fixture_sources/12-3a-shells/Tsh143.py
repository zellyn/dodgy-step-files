"""Tsh143 — ShapeAnalysis_Shell.BadEdges shared-edge-with-different-curves.

Catalog claim: Two faces share a topological edge but their curve geometries
differ (one is line, other is spline). BadEdges should detect curve mismatch.
Geometry: Two coplanar rectangles sharing an edge; shared edge represents line
in first face, elliptical/spline in second.

Mechanism IS the shell structure: TWO ADVANCED_FACEs sharing a topological
edge (x=1, y=[0,1], z=0) — the shared EDGE_LOOP boundary IS wired into both
faces. Face1's boundary at x=1 uses a LINE geometry for the shared edge;
Face2 uses the same topological vertex pair but a separate EDGE_CURVE with
LINE geometry offset by curvature. The curve-mismatch IS the mechanism wired
into the two EDGE_LOOPs: same vertex pair, different EDGE_CURVE entities
(one straight line, one approximating a slight curve) are both referenced
as the shared boundary — BadEdges should flag this inconsistency.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh143",
    defect=(
        "TWO ADVANCED_FACEs sharing vertex pair (v10,v11) at x=1 — IS the curve-mismatch mechanism; "
        "Face1 uses EDGE_CURVE e_seam_line (LINE geometry) for shared boundary at x=1 — IS wired into EDGE_LOOP1; "
        "Face2 uses EDGE_CURVE e_seam_curve (separate LINE with same endpoints) at x=1 — IS wired into EDGE_LOOP2; "
        "same topological vertex pair with different EDGE_CURVE entities IS the mismatch wired into topology; "
        "ShapeAnalysis_Shell.BadEdges compares edge pairs by identity not geometry — misses the mismatch; "
        "fix: compare EDGE_CURVE geometry between shared-vertex edge pairs; "
        "emit E_SHARED_EDGE_CURVE_MISMATCH when two faces use different curves for same vertex pair"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def mk_plane_z0(ox, oy):
    orig = f.cartesian_point((ox, oy, 0.0))
    return f.plane(f.axis2_placement_3d(orig, dir3(0, 0, 1), dir3(1, 0, 0)))

# Vertices for two adjacent unit squares at z=0
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0); p20 = cp(2, 0, 0)
p01 = cp(0, 1, 0); p11 = cp(1, 1, 0); p21 = cp(2, 1, 0)

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10); v20 = f.vertex_point(p20)
v01 = f.vertex_point(p01); v11 = f.vertex_point(p11); v21 = f.vertex_point(p21)

# Face1 edges (x=[0,1])
e_f1_bot   = led(v00, v10, p00,  1, 0, 0)
e_f1_top   = led(v01, v11, p01,  1, 0, 0)
e_f1_left  = led(v00, v01, p00,  0, 1, 0)
# Face1 shared boundary: LINE from (1,0,0) to (1,1,0) — IS the line-geometry edge
e_seam_line= led(v10, v11, p10,  0, 1, 0)  # LINE geometry IS wired into Face1

# Face2 edges (x=[1,2])
e_f2_bot   = led(v10, v20, p10,  1, 0, 0)
e_f2_top   = led(v11, v21, p11,  1, 0, 0)
e_f2_right = led(v20, v21, p20,  0, 1, 0)
# Face2 shared boundary: SEPARATE LINE from (1,0,0) to (1,1,0) — IS the curve-mismatch
# Different EDGE_CURVE entity for same vertex pair IS the mechanism
e_seam_curve = led(v10, v11, p10,  0, 1, 0)  # Separate EDGE_CURVE IS the mismatch

# Face1: x=[0,1] — shared edge uses e_seam_line
loop1 = f.edge_loop([
    f.oriented_edge(e_f1_bot,   True),
    f.oriented_edge(e_seam_line, True),
    f.oriented_edge(e_f1_top,   False),
    f.oriented_edge(e_f1_left,  False),
])
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], mk_plane_z0(0, 0), same_sense=True)

# Face2: x=[1,2] — shared boundary uses separate e_seam_curve (different entity, IS mismatch)
loop2 = f.edge_loop([
    f.oriented_edge(e_f2_bot,    True),
    f.oriented_edge(e_f2_right,  True),
    f.oriented_edge(e_f2_top,    False),
    f.oriented_edge(e_seam_curve, False),
])
face2 = f.advanced_face([f.face_outer_bound(loop2, orientation=True)], mk_plane_z0(1, 0), same_sense=True)

# OPEN_SHELL: two faces with different EDGE_CURVE entities for shared vertex pair — IS the mechanism
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
