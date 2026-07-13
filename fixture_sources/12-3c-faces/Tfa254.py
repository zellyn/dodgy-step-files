"""Tfa254 — Outer/inner wire touch at a clean endpoint-endpoint contact.

Catalog claim (occt-coverage GAP `tkshh-face-intersecting-wires`, missing
subvariant): the outer wire and an inner (hole) wire of the same face touch
at exactly one point that is a genuine ENDPOINT of an edge on both wires
(not a transverse interior crossing) -- ShapeFix_IntersectionTool::
FixIntersectingWires' both-endpoints branch (UnionVertexes,
ShapeFix_IntersectionTool.cxx ~1598-1604), distinct from Tfa039's transverse
point-crossing and from Twi250's crossing-near-one-edge's-endpoint case.

Mechanism IS the wire/face topology: a 10x10 PLANE face's FACE_OUTER_BOUND is
the unit square (0,0)-(10,0)-(10,10)-(0,10). Its inner FACE_BOUND (hole) is a
small right triangle (0,0)-(3,0)-(0,3): its own corner at (0,0) sits at the
EXACT same coordinate as the outer wire's own corner (0,0) -- but is encoded
as an INDEPENDENT VERTEX_POINT entity, not the same STEP id reused. Both
occurrences of (0,0) are genuine edge ENDPOINTS on their respective wires
(never a mid-edge point), so the contact is a clean endpoint-endpoint touch,
not a crossing.

Live oracle (this worktree's OCP/OCCT 7.8.1, default STEPControl_Reader):
authored topology has 7 independent VERTEX_POINT entities (4 outer + 3
inner); post-heal the live shape carries only 6 UNIQUE TopoDS vertices --
direct evidence that UnionVertexes merged the two independently-authored
(0,0) vertices into one shared TopoDS_Vertex. The resulting face is
BRepCheck-invalid (brepcheck.valid==False, status
BRepCheck_InvalidImbricationOfWires): once the hole's corner is unified with
the outer boundary's corner, the wire-containment classifier
(BRepTopAdaptor_FClass2d-based) cannot cleanly decide the hole is "inside"
the outer wire, and reports imbrication failure -- a genuine, live side
effect of the touching-at-a-shared-corner configuration, reported honestly
rather than mirrored. BRepCheck_Face::IntersectWires() itself returns
BRepCheck_NoError (the touch point is excused as a shared vertex, not
flagged as a crossing) -- consistent with a clean endpoint-endpoint contact,
not a transverse intersection.

Byte assertions:
  - contains(b'FACE_OUTER_BOUND')
  - contains(b'FACE_BOUND(')
Tier-3 assertions:
  - load == "ok"
  - n_edges_total == 9
  - face[0].surface_type == "plane"
  - brepcheck.valid == False
Expected: occt=shape(1)/shape(1) gmsh=... (see catalog entry) ifc=schema_n/a
"""
import math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tfa254",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on 10x10 PLANE; FACE_OUTER_BOUND is "
        "the 10x10 square; inner FACE_BOUND is a small right triangle "
        "(0,0)-(3,0)-(0,3) whose (0,0) corner is an INDEPENDENT VERTEX_POINT "
        "entity coincident with the outer bound's own (0,0) corner -- a "
        "genuine endpoint-endpoint touch, not a transverse crossing; "
        "ShapeFix_IntersectionTool::FixIntersectingWires' UnionVertexes "
        "both-endpoints branch fires: live unique vertex count drops from 7 "
        "authored to 6 post-heal; defect IS on live OPEN_SHELL traversal path"
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
# Inner triangle: (0,0) is a NEW, independent VERTEX_POINT coincident with
# the outer wire's own (0,0) corner -- both are edge ENDPOINTS (never
# mid-edge), so the touch is a clean endpoint-endpoint contact.
inner_loop = mk_poly_loop([(0, 0), (3, 0), (0, 3)])

face0 = f.advanced_face([
    f.face_outer_bound(outer_loop),
    f.face_bound(inner_loop, orientation=False),
], plane0)
shell = f.open_shell([face0])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa254.stp")
