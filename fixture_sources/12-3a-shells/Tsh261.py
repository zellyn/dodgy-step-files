"""Tsh261 — Two hanging vertices project onto the SAME interior stretch of
one longer boundary edge, a hair's breadth apart: the second is bound to the
cut node the first created instead of adding a redundant second cut
(`sew-cutting-hanging-vertex-split`, subvariant "snap-to-existing-cut-vertex
vs create-new-cut-vertex threshold").

Catalog claim (occt-coverage PARTIAL `sew-cutting-hanging-vertex-split`):
Tsh260 already demonstrates the base T-junction split. This fixture supplies
the missing adaptive-threshold subvariant: the rule that a projected point
lying within 10% of its OWN projection distance of an already-created cut
vertex is snapped onto that vertex rather than producing a second cut a
hair's breadth away (`BRepBuilderAPI_Sewing::CreateCuttingNodes`,
`BRepBuilderAPI_Sewing.cxx:4449-4481`: `if (distMin <= Max(disProj*0.1,
MinTolerance()))` -> bind to existing node, `else` -> build a new cutting
vertex).

Geometry (three planar triangles in one OPEN_SHELL):
  * Face LONG (z=0)     : (1,0,0)-(1,2,0)-(-3,1,0). Its edge x=1, y:[0,2] is
                          the reference edge to be cut.
  * Face UP   (z=+0.4)  : (1,0.9,0.4)-(1,2,0.4)-(4,1.5,0.4). Its first edge
                          runs parallel to the reference edge, 0.4 above it,
                          spanning y:[0.9,2.0]; its start vertex hangs on the
                          reference edge's interior at y=0.9 -> CREATES a new
                          cut vertex there (projection distance 0.4).
  * Face DOWN (z=-0.4)  : (1,0.92,-0.4)-(4,0.92,-0.4)-(4,1.5,-0.4). Its first
                          vertex hangs 0.4 BELOW the reference edge and
                          projects onto it at y=0.92 — 0.02 from the cut node
                          UP created, i.e. inside 0.1 x 0.4 = 0.04 -> SNAPS to
                          it, no second cut.

Placing the two hanging vertices on OPPOSITE sides of the reference edge is
what makes the subvariant reachable at all: the two candidate vertices are
0.8 apart (> the 0.6 sewing tolerance) so vertex gluing leaves them distinct,
while both still lie within tolerance of the reference edge and project 0.02
apart on it.

Live verification (this worktree's OCP/OCCT 7.8.1, runtime sewing scaffold
`BRepBuilderAPI_Sewing(0.6, sew=True, analysis=True, cutting=True,
nonmanifold=False)`, fed the shape read from THESE bytes):
  * default STEP read -> shape_null=False, 3 faces, 9 unique edges, reference
    edge [(1,0,0),(1,2,0)] intact (sewing is not on the default read path);
  * after Perform(): the reference edge is replaced by exactly TWO collinear
    sub-edges, [(1,0,0),(1,0.9,*)] and [(1,0.9,*),(1,2,*)] — a single cut, at
    y=0.9 (Face UP's projection). There is NO cut at y=0.92: Face DOWN's
    hanging vertex was snapped onto the existing node. NbContigousEdges()==1
    (the upper section merges with Face UP's parallel edge).
  * threshold sweep on the DOWN vertex's y (projection distance held at 0.4,
    so the predicted threshold is 0.1*0.4 = 0.04): y=0.90/0.92/0.935/0.939/
    0.9400 all give NbContigousEdges==1 (snap, conformalized), y=0.9401/0.941/
    0.945/0.96/1.00 all give NbContigousEdges==0 (a second, redundant cut at
    the hanging vertex's own projection splits the reference edge into three
    sections, none of which matches Face UP's span, so nothing merges and the
    conformalization is lost). The flip is exactly at 0.0400 -> 0.0401.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 3
  - count_entity_def(b'EDGE_CURVE') == 9
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh261",
    schema="AP242",
    defect=(
        "OPEN_SHELL with THREE planar ADVANCED_FACEs. Face LONG (z=0) carries "
        "the reference edge x=1, y:[0,2]. Face UP (z=+0.4) has a vertex "
        "hanging over the reference edge's interior at y=0.9 and an edge "
        "spanning y:[0.9,2.0] parallel to it. Face DOWN (z=-0.4) has a vertex "
        "hanging under the reference edge at y=0.92 -- 0.02 from the first "
        "hanging vertex's projection, inside 10% of its own 0.4 projection "
        "distance. Both hanging vertices project onto the same interior "
        "stretch of one edge a hair's breadth apart; the second must be bound "
        "to the cut node the first created rather than adding a redundant "
        "second cut 0.02 away"
    ),
)


def cp(p):
    return f.cartesian_point(tuple(float(c) for c in p))


def dir3(t):
    return f.direction(tuple(float(c) for c in t))


def seg(va, vb, pa, pb):
    d = [pb[i] - pa[i] for i in range(3)]
    L = sum(c * c for c in d) ** 0.5
    return f.edge_curve(va, vb, f.line(cp(pa), f.vector(dir3([c / L for c in d]), L)))


def tri(pts):
    vs = [f.vertex_point(cp(p)) for p in pts]
    es = [seg(vs[i], vs[(i + 1) % 3], pts[i], pts[(i + 1) % 3]) for i in range(3)]
    loop = f.edge_loop([f.oriented_edge(e, True) for e in es])
    pl = f.plane(f.axis2_placement_3d(cp(pts[0]), dir3([0, 0, 1]), dir3([1, 0, 0])))
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)], pl,
                           same_sense=True)


# Reference edge is the first edge of Face LONG: x=1, y:[0,2], z=0.
face_long = tri([(1.0, 0.0, 0.0), (1.0, 2.0, 0.0), (-3.0, 1.0, 0.0)])

# Face UP: hanging vertex at (1,0.9,+0.4) -> new cut vertex at y=0.9.
face_up = tri([(1.0, 0.9, 0.4), (1.0, 2.0, 0.4), (4.0, 1.5, 0.4)])

# Face DOWN: hanging vertex at (1,0.92,-0.4) -> snaps onto that cut vertex.
face_down = tri([(1.0, 0.92, -0.4), (4.0, 0.92, -0.4), (4.0, 1.5, -0.4)])

shell = f.open_shell([face_long, face_up, face_down],
                     name="tsh261_snap_to_existing_cut_node_shell")
f.add_product_chain(f.shell_based_surface_model([shell]))
