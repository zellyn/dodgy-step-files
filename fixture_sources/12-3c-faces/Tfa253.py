"""Tfa253 — Outer/inner wire share a >50% collinear overlap segment.

Catalog claim (occt-coverage GAP `tkshh-face-intersecting-wires`, missing
subvariant): a hole (inner FACE_BOUND) wire and the outer wire of the same
face run collinear along a shared segment whose overlap exceeds 50% of the
overlapping edge's length -- ShapeFix_IntersectionTool::FixIntersectingWires'
segment-overlap branch (large-overlap path, ShapeFix_IntersectionTool.cxx
~1740-1913: CutEdge + 3-edge reconstruction), distinct from the small-overlap
2-edge-split path and distinct from Tfa039's plain transverse point-crossing.

Mechanism IS the wire/face topology: a 10x10 PLANE face's FACE_OUTER_BOUND is
the unit square (0,0)-(10,0)-(10,10)-(0,10). Its inner FACE_BOUND (hole) is a
7x3 rectangle (2,0)-(9,0)-(9,3)-(2,3) whose bottom edge lies exactly on the
line y=0 -- the same line as the outer wire's bottom edge -- for x in [2,9]:
a 7-unit overlap against the outer edge's 10-unit length (70%) and the
inner edge's own full 7-unit length (100%), both comfortably over the 50%
threshold that selects the large-overlap reconstruction path over the
small-overlap 2-edge split.

Live oracle (this worktree's OCP/OCCT 7.8.1, default STEPControl_Reader):
authored topology is 8 edges (4 outer + 4 inner); post-heal the live shape
carries 10 edges (n_edges_total==10, +2 over the 8 authored) -- direct
evidence that the overlap-handling repair fired and restructured the
colinear-overlap boundary rather than leaving it untouched. BRepCheck valid
after heal (brepcheck.valid==True): the reconstruction produces a
well-formed face. face[0].area == 79.0 == 100 - (7*3), confirming the hole
geometry survives the repair intact.

Byte assertions:
  - contains(b'FACE_OUTER_BOUND')
  - contains(b'FACE_BOUND(')
Tier-3 assertions:
  - load == "ok"
  - n_edges_total == 10
  - face[0].surface_type == "plane"
  - brepcheck.valid == True
Expected: occt=shape(1)/shape(1) gmsh=... (see catalog entry) ifc=schema_n/a
"""
import math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tfa253",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on 10x10 PLANE; FACE_OUTER_BOUND is "
        "the 10x10 square; inner FACE_BOUND is a 7x3 rectangle whose bottom "
        "edge (2,0)-(9,0) is collinear with and 70%/100% overlapping the "
        "outer bound's bottom edge (0,0)-(10,0); "
        "ShapeFix_IntersectionTool::FixIntersectingWires large-overlap "
        "(>50%) branch fires: live edge count rises from 8 authored to 10 "
        "post-heal; defect IS on live OPEN_SHELL traversal path"
    ),
)

pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
plane0 = f.plane(f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir))


def mk_poly_loop(coords_xy):
    n = len(coords_xy)
    cps = [f.cartesian_point((float(x), float(y), 0.0)) for x, y in coords_xy]
    vs = [f.vertex_point(cp) for cp in cps]
    ecs = []
    for i in range(n):
        x0, y0 = coords_xy[i]
        x1, y1 = coords_xy[(i + 1) % n]
        dx = x1 - x0
        dy = y1 - y0
        mag = math.sqrt(dx * dx + dy * dy)
        d = f.direction((dx / mag, dy / mag, 0.0))
        vec = f.vector(d, mag)
        ec = f.edge_curve(vs[i], vs[(i + 1) % n], f.line(cps[i], vec))
        ecs.append(ec)
    return f.edge_loop([f.oriented_edge(ec, True) for ec in ecs])


outer_loop = mk_poly_loop([(0, 0), (10, 0), (10, 10), (0, 10)])
# Inner hole: bottom edge (2,0)-(9,0) collinear/overlapping with the outer
# bound's bottom edge (0,0)-(10,0) for x in [2,9] -- 70% of the outer edge,
# 100% of the inner edge (both well over the 50% large-overlap threshold).
inner_loop = mk_poly_loop([(2, 0), (9, 0), (9, 3), (2, 3)])

face0 = f.advanced_face([
    f.face_outer_bound(outer_loop),
    f.face_bound(inner_loop, orientation=False),
], plane0)
shell = f.open_shell([face0])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa253.stp")
