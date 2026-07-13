"""Tfa252 — EDGE_CURVE with null edge_geometry ($) wired into a live face.

Catalog claim (occt-coverage GAP `stp-missing-geometry-definition`): a
topological entity references its underlying geometric definition, but that
reference is null ($). OCCT detects this missing-geometry condition per
entity and fails cleanly for just that one entity (logged, not crashed),
leaving the caller free to treat it as a single partial-transfer failure
rather than aborting the whole read. Prior candidates (Xp008's null-geometry
face, Tfa003's null-geometry edges) were downgraded GAP because the defect
entity was either a dead trailing entity never referenced by the live shell,
or hosted inside a GEOMETRIC_CURVE_SET (a builder-dispatch path that never
reaches StepToTopoDS_TranslateEdge::Init at all). This fixture places the
null-geometry EDGE_CURVE directly inside a wire of a live ADVANCED_FACE that
IS referenced by a real OPEN_SHELL on the default import path.

Mechanism IS the wire/face topology: a 10x10 PLANE face's outer wire has 4
edges; edge[2] is `EDGE_CURVE('null_geom_edge',#V2,#V3,$,.T.)` -- its
edge_geometry slot is null. The other 3 edges are ordinary LINE-based
EDGE_CURVEs. StepToTopoDS_TranslateEdge::Init hits the null EdgeGeometry
curve and fails cleanly for that one edge; the wire translator (unable to
build a valid closed wire with a missing edge) drops the whole bound, and the
face survives translation as a genuinely UNBOUNDED plane (empty bounds list)
rather than crashing or silently fabricating geometry -- the reader's
clean-fail path, live and reachable.

Live oracle (this worktree's OCP/OCCT 7.8.1, default STEPControl_Reader):
  occt_heal_on / occt_heal_off: status=accept, n_roots=1, shape_null=False,
  shape_counts: face=1, shell=1, edge=0, vertex=0, wire=0 -- i.e. the ONE
  ADVANCED_FACE survives with its bound wire fully dropped (0 edges/vertices
  under it), not a crash and not a silently-fabricated shape.
tier3_geometric: n_faces_total=1, face[0].surface_type="plane",
  face[0].edge_count=0, face[0].area ~ 8e100 (unbounded natural-surface
  fallback -- OCCT's signature for "face_geometry present, bound list
  effectively empty").

Byte assertions:
  - contains(b"EDGE_CURVE('null_geom_edge',")
  - contains(b'ADVANCED_FACE')
Tier-3 assertions:
  - load == "ok"
  - n_faces_total == 1
  - face[0].surface_type == "plane"
  - face[0].edge_count == 0
Expected: occt=shape(1)/shape(1) gmsh=... (see catalog entry) ifc=schema_n/a
"""
import math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tfa252",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on a 10x10 PLANE; outer wire has 4 "
        "edges, edge[2] is EDGE_CURVE('null_geom_edge',#V2,#V3,$,.T.) -- "
        "edge_geometry is null ($), not a GEOMETRIC_CURVE_SET orphan and not "
        "a dead trailing entity; StepToTopoDS_TranslateEdge::Init hits the "
        "null curve and fails cleanly for that one edge; wire translation "
        "drops the whole bound and the face survives as an unbounded "
        "natural-surface fallback (edge_count==0), not a crash; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
plane0 = f.plane(f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir))

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point((0.0, 10.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)


def line_edge(pa, va, pb, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    mag = math.sqrt(dx * dx + dy * dy)
    d = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, mag)
    return f.edge_curve(va, vb, f.line(pa, vec))


e0 = line_edge(p0, v0, p1, v1)
e1 = line_edge(p1, v1, p2, v2)
# e2: THE DEFECT -- edge_geometry = $ (null), live/reachable via OPEN_SHELL.
e2 = f._emit_raw(f"EDGE_CURVE('null_geom_edge',#{v2.eid},#{v3.eid},$,.T.)")
e3 = line_edge(p3, v3, p0, v0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
face0 = f.advanced_face([f.face_outer_bound(loop)], plane0)
shell = f.open_shell([face0])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa252.stp")
