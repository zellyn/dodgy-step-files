"""Gs205 — Cone apex written as a VERTEX_LOOP face bound: the zero-length,
curve-less edge OCCT builds from it is a legitimate degenerate edge and must
be passed through sewing untouched, not treated as a small/defective edge
(`sew-degenerate-edge-passthrough`, must-NOT-repair fixture).

Catalog claim (occt-coverage PARTIAL `sew-degenerate-edge-passthrough`): the
class describes two legitimate zero-length archetypes — "the edge running
along a cone's apex, or a seam-collapse point on a sphere". Gs189 supplies
the sphere-pole one, encoded as a radius-0.0 `CIRCLE`. This fixture supplies
the cone-apex one, encoded the way ISO 10303-42 provides for it: a
`VERTEX_LOOP` as the face's inner bound. `StepToTopoDS_TranslateVertexLoop`
(`StepToTopoDS_TranslateVertexLoop.cxx:88-95`) maps that loop to a wire
holding one edge with the same vertex at both ends, no 3D curve at all, and
`B.Degenerated(E, Standard_True)` — so the sewing pass meets a degenerate
edge it cannot even measure, and must take the pass-through branch
(`BRepBuilderAPI_Sewing::FaceAnalysis`: `if (BRep_Tool::Degenerated(edge)) {
B.Add(nwire,edge); myDegenerated.Add(edge); nbSmall++; continue; }` — the
old edge is kept and all small-edge/geometry-update processing is skipped;
`FindFreeBoundaries` `BRepBuilderAPI_Sewing.cxx:2559` likewise skips it as a
boundary candidate).

Geometry: `MANIFOLD_SOLID_BREP` over a `CLOSED_SHELL` of two faces — a
`CONICAL_SURFACE` (ref radius 5 at z=0, 45-degree semi-angle, so the apex is
the point (0,0,-5)) whose outer bound is the z=0 rim circle and whose inner
bound is a `VERTEX_LOOP` at the apex vertex, plus a planar disk closing the
rim.

Live verification (this worktree's OCP/OCCT 7.8.1, fed the shape read from
THESE bytes):
  * default read -> shape_null=False, 2 faces; the apex edge comes back with
    identical start/end vertex at (0,0,-5), `BRep_Tool::Degenerated` True and
    `BRep_Tool::Curve` NULL (nothing to measure a length from);
  * `BRepBuilderAPI_Sewing(1e-2)`.Perform() -> `NbDegeneratedShapes()==1`,
    `NbFreeEdges()==0`, `NbDeletedFaces()==0`, and the apex edge is present in
    the result unchanged: same two coincident vertices, still flagged
    degenerate. Nothing was repaired, removed or collapsed.
  * perturbation (same generator, apex bound replaced by a GENUINE circle of
    radius 0.05 just below the apex, i.e. a small but not formally degenerate
    edge): `NbDegeneratedShapes()` 1 -> 0 and `NbFreeEdges()` 0 -> 1 — the
    edge now IS registered as a free boundary and enters ordinary processing.
    So the degeneracy flag is load-bearing for the observed outcome.

Also recorded (verified, mildly surprising): OCCT normalises BOTH STEP
encodings of a degenerate apex/pole — this fixture's `VERTEX_LOOP` and
Gs189's radius-0.0 `CIRCLE` — to the same in-memory shape, a degenerate edge
whose 3D curve handle is null. The two fixtures therefore differ as INPUT
patterns (which is what a corpus consumer has to survive) while converging on
the same kernel branch.

Byte assertions:
  - count_entity_def(b'VERTEX_LOOP') == 1
  - count_entity_def(b'CONICAL_SURFACE') == 1
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs205",
    schema="AP242",
    defect=(
        "CLOSED_SHELL whose CONICAL_SURFACE face (ref radius 5 at z=0, "
        "45-degree semi-angle, apex at (0,0,-5)) has its apex expressed as a "
        "VERTEX_LOOP inner FACE_BOUND -- the ISO 10303-42 encoding for a "
        "boundary that collapses to a single point. The reader turns it into "
        "a zero-length edge with no 3D curve at all, formally flagged "
        "degenerate: a legitimate, non-defective piece of B-Rep topology that "
        "a healing pass must recognise and leave alone rather than treat as a "
        "small/collapsed edge to remove"
    ),
)

R, SEMI = 5.0, 0.7853981633974483   # 45 degrees -> apex at z = -R
APEX = (0.0, 0.0, -R)


def cp(p):
    return f.cartesian_point(tuple(float(c) for c in p))


def dir3(t):
    n = sum(c * c for c in t) ** 0.5
    return f.direction(tuple(float(c) / n for c in t))


cone = f.conical_surface(
    f.axis2_placement_3d(cp([0, 0, 0]), dir3([0, 0, 1]), dir3([1, 0, 0])),
    R, SEMI, name="gs205_cone")
rim_circle = f.circle(
    f.axis2_placement_3d(cp([0, 0, 0]), dir3([0, 0, 1]), dir3([1, 0, 0])),
    R, name="gs205_rim")
v_rim = f.vertex_point(cp([R, 0, 0]))
e_rim = f.edge_curve(v_rim, v_rim, rim_circle, name="gs205_rim_edge")
outer_bound = f.face_outer_bound(f.edge_loop([f.oriented_edge(e_rim, True)]),
                                 orientation=True)

v_apex = f.vertex_point(cp(APEX))
apex_loop = f._emit("VERTEX_LOOP", v_apex, name="gs205_apex_vertex_loop")
apex_bound = f.face_bound(apex_loop, orientation=True, name="gs205_apex_bound")

face_cone = f.advanced_face([outer_bound, apex_bound], cone, same_sense=True)

disk_plane = f.plane(f.axis2_placement_3d(
    cp([0, 0, 0]), dir3([0, 0, -1]), dir3([1, 0, 0])))
face_disk = f.advanced_face(
    [f.face_outer_bound(f.edge_loop([f.oriented_edge(e_rim, False)]),
                        orientation=True)],
    disk_plane, same_sense=True)

shell = f.closed_shell([face_cone, face_disk], name="gs205_cone_apex_shell")
f.add_product_chain(f.manifold_solid_brep(shell, name="gs205_solid"))
