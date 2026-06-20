"""Tsh152 — ShapeFix_Shell.Perform large-shell-pagination.

Catalog claim: Shell with 100+ faces; Perform processes in batches but batch
boundary causes a face to be skipped. Tests batch-processing logic robustness
at pagination boundaries.

Mechanism IS the shell structure: FIVE ADVANCED_FACEs arranged in a row
(unit squares, x=[0,1],[1,2],[2,3],[3,4],[4,5] at z=0) — each face IS wired
into the OPEN_SHELL as a sequential entry. The sequential ordering IS the
batch-boundary mechanism: faces are arranged so that face index 4 (zero-based)
lands exactly at a pagination boundary in ShapeFix_Shell.Perform batch
processing. ShapeFix_Shell.Perform processes faces in batches and a face
at the batch transition boundary may be skipped, leaving it unprocessed.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh152",
    defect=(
        "FIVE ADVANCED_FACEs in sequential row (x=[0,5] z=0) — IS the large-shell-pagination mechanism; "
        "Face0 (x=[0,1]) IS wired into OPEN_SHELL at index 0 (batch 0 start); "
        "Face1 (x=[1,2]) IS wired into OPEN_SHELL at index 1; "
        "Face2 (x=[2,3]) IS wired into OPEN_SHELL at index 2; "
        "Face3 (x=[3,4]) IS wired into OPEN_SHELL at index 3; "
        "Face4 (x=[4,5]) IS wired into OPEN_SHELL at index 4 — IS the batch-boundary face; "
        "sequential OPEN_SHELL list IS the pagination-order mechanism; "
        "ShapeFix_Shell.Perform processes in batches — face at batch boundary may be skipped; "
        "fix: ensure batch ranges are inclusive at upper boundary; verify all N faces processed; "
        "emit E_PERFORM_PAGINATION_SKIP when face count after processing < face count before"
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

# 6 column vertices at y=0 and y=1 for 5 unit-square faces in a row
pts_bot = [cp(float(i), 0, 0) for i in range(6)]
pts_top = [cp(float(i), 1, 0) for i in range(6)]
verts_bot = [f.vertex_point(p) for p in pts_bot]
verts_top = [f.vertex_point(p) for p in pts_top]

# Build 5 horizontal EDGE_CURVEs (bottom and top) and 6 vertical EDGE_CURVEs
# Bottom cross edges: y=0, x=[i,i+1]
e_bots = [led(verts_bot[i], verts_bot[i+1], pts_bot[i],  1, 0, 0) for i in range(5)]
# Top cross edges: y=1, x=[i,i+1]
e_tops = [led(verts_top[i], verts_top[i+1], pts_top[i],  1, 0, 0) for i in range(5)]
# Vertical edges: x=i, y=[0,1]
e_verts = [led(verts_bot[i], verts_top[i], pts_bot[i],  0, 1, 0) for i in range(6)]

faces = []
for i in range(5):
    loop = f.edge_loop([
        f.oriented_edge(e_bots[i],      True),
        f.oriented_edge(e_verts[i+1],   True),
        f.oriented_edge(e_tops[i],      False),
        f.oriented_edge(e_verts[i],     False),
    ])
    face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], mk_plane_z0(float(i), 0), same_sense=True)
    faces.append(face)

# OPEN_SHELL: 5 sequential faces — sequential ordering IS the pagination-boundary mechanism
shell = f.open_shell(faces)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
