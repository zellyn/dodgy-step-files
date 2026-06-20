"""Tfa004 — Missing natural bound on sphere / torus face.

Catalog claim: A face on a closed surface (sphere, torus) is given with only
inner wires — or with a single VERTEX_LOOP — and no outer bound. STEP semantics
permit this ("the entire surface with cutouts"), but kernels that pre-orient
inner wires before adding the natural bound flip the region.

Mechanism: SHELL_BASED_SURFACE_MODEL with TWO ADVANCED_FACEs:
  face[0] on TOROIDAL_SURFACE — only FACE_BOUND (inner wire), no FACE_OUTER_BOUND
  face[1] on SPHERICAL_SURFACE — only FACE_BOUND (inner wire), no FACE_OUTER_BOUND
Each face's inner wire is a closed polygon around the surface seam. OCC heals
by inserting natural bounds, but may pre-orient inner wires before insertion,
flipping the hole region.

Tier-3 assertions:
  face[0].surface_type == "torus"
  face[1].surface_type == "sphere"
  n_edges_total >= 5
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa004",
    defect=(
        "TWO ADVANCED_FACEs on closed surfaces with no FACE_OUTER_BOUND: "
        "face[0] on TOROIDAL_SURFACE with only inner FACE_BOUND (3-edge loop); "
        "face[1] on SPHERICAL_SURFACE with only inner FACE_BOUND (4-edge loop); "
        "STEP semantics allow entire-surface-with-cutout representation; "
        "OCC must insert natural bound before orienting inner wire, not after; "
        "both faces wired into OPEN_SHELL — defect is live on face traversal path"
    ),
)

# ── TORUS face (face[0]): major_r=10, minor_r=3, center at origin ─────────────
# Toroidal surface: major radius 10, minor radius 3
t_orig = f.cartesian_point((0.0, 0.0, 0.0))
t_zdir = f.direction((0.0, 0.0, 1.0))
t_xdir = f.direction((1.0, 0.0, 0.0))
t_plc  = f.axis2_placement_3d(t_orig, t_zdir, t_xdir)
torus  = f.toroidal_surface(t_plc, 10.0, 3.0)

# Inner wire on torus: 3-edge triangle on the torus body
# Place vertices on the outer equator of the torus
tr = 10.0  # major radius
mn = 3.0   # minor radius
# Three equatorial points on the torus (at v=0, i.e., on the outer equator circle)
t_pts = [
    f.cartesian_point(((tr + mn) * _math.cos(a), (tr + mn) * _math.sin(a), 0.0))
    for a in [0.0, 2.0 * _math.pi / 3, 4.0 * _math.pi / 3]
]
t_verts = [f.vertex_point(p) for p in t_pts]

# 3 edges forming the triangle
t_edges = []
for i in range(3):
    pa = t_pts[i]
    pb = t_pts[(i + 1) % 3]
    va = t_verts[i]
    vb = t_verts[(i + 1) % 3]
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx*dx + dy*dy + dz*dz) ** 0.5
    d   = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln  = f.line(pa, vec)
    t_edges.append(f.edge_curve(va, vb, ln))

t_inner_loop = f.edge_loop([f.oriented_edge(e, True) for e in t_edges])
# FACE_BOUND (inner), no FACE_OUTER_BOUND — this is the defect
t_inner_bound = f.face_bound(t_inner_loop, True)
torus_face = f.advanced_face([t_inner_bound], torus)

# ── SPHERE face (face[1]): radius=5, center at (30, 0, 0) ────────────────────
sp_orig = f.cartesian_point((30.0, 0.0, 0.0))
sp_zdir = f.direction((0.0, 0.0, 1.0))
sp_xdir = f.direction((1.0, 0.0, 0.0))
sp_plc  = f.axis2_placement_3d(sp_orig, sp_zdir, sp_xdir)
sphere  = f.spherical_surface(sp_plc, 5.0)

# Inner wire on sphere: 4-edge loop around the equator
# Four equatorial points at 90° intervals
sp_r = 5.0
sp_pts = [
    f.cartesian_point((30.0 + sp_r * _math.cos(a), sp_r * _math.sin(a), 0.0))
    for a in [0.0, _math.pi / 2, _math.pi, 3 * _math.pi / 2]
]
sp_verts = [f.vertex_point(p) for p in sp_pts]

sp_edges = []
for i in range(4):
    pa = sp_pts[i]
    pb = sp_pts[(i + 1) % 4]
    va = sp_verts[i]
    vb = sp_verts[(i + 1) % 4]
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx*dx + dy*dy + dz*dz) ** 0.5
    d   = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln  = f.line(pa, vec)
    sp_edges.append(f.edge_curve(va, vb, ln))

sp_inner_loop  = f.edge_loop([f.oriented_edge(e, True) for e in sp_edges])
# FACE_BOUND (inner), no FACE_OUTER_BOUND — this is the defect
sp_inner_bound = f.face_bound(sp_inner_loop, True)
sphere_face    = f.advanced_face([sp_inner_bound], sphere)

# ── Wire both faces into OPEN_SHELL → SBSM → product chain ───────────────────
# face[0] = torus, face[1] = sphere (matching tier-3 assertions)
shell = f.open_shell([torus_face, sphere_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa004.stp")
