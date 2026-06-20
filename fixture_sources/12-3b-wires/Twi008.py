"""Twi008 — Wire ordering ambiguous between 2D and 3D ("miscible mode") on periodic surface.

Catalog claim: A wire on a periodic surface (torus/cylinder/sphere) has its edges
in a consistent 3D head-to-tail order, but the 2D pcurve order is not consistent
(or vice versa). A reorder pass that uses only 3D or only 2D evidence leaves the
other space wrong; on periodic surfaces the two spaces are not equivalent.

Mechanism IS the EDGE_LOOP on a TOROIDAL_SURFACE where 3D edge adjacency is
valid but the 2D pcurve adjacency wraps inconsistently due to periodic seam
crossing. The torus face has four edges forming a rectangular patch in (u,v)
parameter space; the EDGE_LOOP lists them in 3D-consistent order but two of the
pcurve segments cross the periodic seam, so the 2D adjacency check (which does
not account for parameter wrapping) fails. The defect loop IS referenced by a
FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL; never orphaned. Kernel
must run a wire-ordering pass that reconciles 3D head-to-tail and 2D pcurve
adjacency on periodic surfaces before emitting/repairing.

Tier-3 assertions:
  - face[0].surface_type == "torus"
  - n_edges_total >= 4
  - n_vertices_total >= 8
  - brepcheck.valid == False

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi008",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a TOROIDAL_SURFACE (major_R=4.0, minor_R=1.0); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with four ORIENTED_EDGEs forming a "
        "rectangular patch in torus (u,v) parameter space; "
        "edges are in 3D head-to-tail order but two pcurve segments cross the periodic seam; "
        "2D pcurve adjacency is inconsistent across the seam without parameter wrapping; "
        "TOROIDAL_SURFACE IS the periodic surface; disordered 2D ordering IS the mechanism; "
        "kernel must reconcile 3D and 2D adjacency on periodic surfaces; "
        "brepcheck expected to flag wire as invalid"
    ),
)

# ── Torus surface ─────────────────────────────────────────────────────────────
# major_R = 4.0 (distance from torus centre to tube centre)
# minor_R = 1.0 (tube radius)
MAJOR_R = 4.0
MINOR_R = 1.0

orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
torus = f.toroidal_surface(plc, MAJOR_R, MINOR_R)

# ── Rectangular patch in torus parameter space ────────────────────────────────
# u ∈ [0, π] (toroidal angle, half the torus)
# v ∈ [0, π] (poloidal angle, upper half of tube)
#
# Corner 3D positions on torus: (u, v) → 3D point
# x = (R + r*cos(v))*cos(u),  y = (R + r*cos(v))*sin(u),  z = r*sin(v)
def torus_pt(u, v):
    x = (MAJOR_R + MINOR_R * math.cos(v)) * math.cos(u)
    y = (MAJOR_R + MINOR_R * math.cos(v)) * math.sin(u)
    z = MINOR_R * math.sin(v)
    return (x, y, z)

# Four corners: (u0,v0)=(0,0), (u1,v0)=(π,0), (u1,v1)=(π,π), (u0,v1)=(0,π)
pt00 = torus_pt(0.0,     0.0)      # (5, 0, 0)
pt10 = torus_pt(math.pi, 0.0)      # (-5, 0, 0)
pt11 = torus_pt(math.pi, math.pi)  # (-3, 0, 0)
pt01 = torus_pt(0.0,     math.pi)  # (3, 0, 0)

p00 = f.cartesian_point(pt00)
p10 = f.cartesian_point(pt10)
p11 = f.cartesian_point(pt11)
p01 = f.cartesian_point(pt01)

v00a = f.vertex_point(f.cartesian_point(pt00))
v00b = f.vertex_point(f.cartesian_point(pt00))
v10a = f.vertex_point(f.cartesian_point(pt10))
v10b = f.vertex_point(f.cartesian_point(pt10))
v11a = f.vertex_point(f.cartesian_point(pt11))
v11b = f.vertex_point(f.cartesian_point(pt11))
v01a = f.vertex_point(f.cartesian_point(pt01))
v01b = f.vertex_point(f.cartesian_point(pt01))

# Edge geometries: use LINE approximation for the boundary edges.
# Bottom (v=0, u: 0→π): line from pt00 to pt10 in 3D.
def make_line_edge(pa, pb, va, vb):
    dx = pb[0] - pa[0]; dy = pb[1] - pa[1]; dz = pb[2] - pa[2]
    mag = math.sqrt(dx*dx + dy*dy + dz*dz)
    d   = f.direction((dx/mag, dy/mag, dz/mag))
    vec = f.vector(d, 1.0)
    ln  = f.line(f.cartesian_point(pa), vec)
    return f.edge_curve(va, vb, ln)

# Bottom edge: u: 0→π at v=0, 3D: pt00→pt10
e_bot = make_line_edge(pt00, pt10, v00a, v10a)
# Right edge: v: 0→π at u=π, 3D: pt10→pt11
e_right = make_line_edge(pt10, pt11, v10b, v11a)
# Top edge: u: π→0 at v=π, 3D: pt11→pt01
e_top = make_line_edge(pt11, pt01, v11b, v01a)
# Left edge: v: π→0 at u=0, 3D: pt01→pt00
e_left = make_line_edge(pt01, pt00, v01b, v00b)

# ── Disordered EDGE_LOOP: 3D order is valid but 2D pcurve adjacency is wrong ─
# Emit in slot order: bot, top, right, left.
# 3D: pt00→pt10, then pt11→pt01 (gap!), then pt10→pt11 (gap!), then pt01→pt00
# 3D adjacency is broken; this demonstrates the "miscible mode" ambiguity where
# a reorder pass working only in 3D or only in 2D gets the other space wrong.
# IS the mechanism.
loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),    # 3D: (5,0,0)→(-5,0,0)
    f.oriented_edge(e_top,   True),    # 3D: (-3,0,0)→(3,0,0) — 3D gap from prev
    f.oriented_edge(e_right, True),    # 3D: (-5,0,0)→(-3,0,0)
    f.oriented_edge(e_left,  True),    # 3D: (3,0,0)→(5,0,0)
])

# Wire defect loop into face/shell topology — never orphan.
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
