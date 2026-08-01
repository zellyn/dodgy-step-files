"""Tsh262 — A hanging vertex projects onto the interior of a cylinder's SEAM
edge: the seam is split, and each resulting sub-edge keeps BOTH of the seam's
2D curve representations (`sew-cutting-hanging-vertex-split`, subvariant
"seam-edge dual-pcurve propagation across the cut").

Catalog claim (occt-coverage PARTIAL `sew-cutting-hanging-vertex-split`):
Tsh260 demonstrates the base T-junction split and Tsh261 the snap-vs-new-node
threshold; both cut ordinary single-pcurve boundary edges. This fixture
supplies the remaining seam subvariant: when the edge being cut is a seam on
a closed surface, both the forward and the reversed 2D curve representations
must be retrieved and re-attached to every sub-edge, or the split silently
destroys the face's periodicity information
(`BRepBuilderAPI_Sewing::CreateSections`, `BRepBuilderAPI_Sewing.cxx:
4610-4653` retrieve-both and `:4693-4704` orientation-aware re-attach).

Geometry (one OPEN_SHELL, two ADVANCED_FACEs):
  * Face CYL : full 360-degree CYLINDRICAL_SURFACE (r=1, axis +Z), U-closed.
               Its FACE_OUTER_BOUND is the standard 4-element seam loop —
               bottom CIRCLE forward, the vertical seam EDGE_CURVE (1,0,0)->
               (1,0,2) FORWARD, top CIRCLE reversed, THE SAME seam EDGE_CURVE
               again REVERSED — which is what makes that edge a true seam
               carrying two pcurves (u=0 and u=2pi) on one face.
  * Face TAB : planar triangle (1.3,0,1)-(1.3,0,2)-(4,1.2,1.5). Its first
               vertex hangs 0.3 off the seam and projects onto the seam's
               INTERIOR at z=1; its first edge runs parallel to the seam's
               upper half so the upper cut section has a merge partner and the
               split survives into the sewn result.

Live verification (this worktree's OCP/OCCT 7.8.1, runtime sewing scaffold,
fed the shape read from THESE bytes):
  * default STEP read -> shape_null=False, 2 faces, 6 unique edges; the seam
    edge [(1,0,0),(1,0,2)] is a genuine seam on Face CYL —
    `BRep_Tool::IsClosed(edge, face)` is True and the forward/reversed
    pcurves evaluate to u=6.28319 / u=0.0 at the first parameter.
  * after `BRepBuilderAPI_Sewing(0.5, sew=True, analysis=True, cutting=True,
    nonmanifold=True).Perform()`: the seam edge is GONE and is replaced by two
    collinear sub-edges cut at the hanging vertex's projection z=1 —
    [(1,0,0),(1.15,0,1)] and [(1.15,0,1),(1.15,0,2)] (the upper one merged
    with Face TAB's parallel edge, hence the averaged x=1.15;
    NbContigousEdges()==1). BOTH sub-edges satisfy
    `BRep_Tool::IsClosed(sub, face)` and carry two DISTINCT pcurves on the
    cylinder — forward/reversed evaluating to (6.28319, 0.0) on the lower
    section and (0.0, 6.28319) on the upper one (the orientation-dependent
    argument order of the re-attach). The seam's dual representation survived
    the split intact.
  * nonmanifold=False on the same bytes -> no cut at all (a seam edge is
    listed against its one face twice, so it is only registered as a
    cuttable bound in non-manifold mode); dx widened 0.3 -> 0.8, i.e. past
    the 0.5 tolerance -> no cut either, seam edge intact. Both perturbations
    change the observed outcome, so the split really is driven by the hanging
    vertex.

Byte assertions:
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_CURVE') == 6
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh262",
    schema="AP242",
    defect=(
        "OPEN_SHELL with a full-period CYLINDRICAL_SURFACE face whose "
        "FACE_OUTER_BOUND uses one vertical EDGE_CURVE TWICE (forward and "
        "reversed) as a true seam, plus a planar triangular face whose "
        "vertex hangs 0.3 off that seam and projects onto its interior at "
        "z=1 without sharing a vertex with it -- a non-conformal T-junction "
        "landing on a seam edge, so the conformalizing split has to carry "
        "both of the seam's 2D curve representations onto each sub-edge"
    ),
)

H, R, DX, ZH = 2.0, 1.0, 0.3, 1.0


def cp(p):
    return f.cartesian_point(tuple(float(c) for c in p))


def dir3(t):
    n = sum(c * c for c in t) ** 0.5
    return f.direction(tuple(float(c) / n for c in t))


def sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]


def seg(va, vb, pa, pb):
    d = sub(pb, pa)
    L = sum(c * c for c in d) ** 0.5
    return f.edge_curve(va, vb, f.line(cp(pa), f.vector(dir3(d), L)))


# --- Face CYL: full cylinder patch with a genuine seam edge -----------------
cyl = f.cylindrical_surface(
    f.axis2_placement_3d(cp([0, 0, 0]), dir3([0, 0, 1]), dir3([1, 0, 0])), R)
v_bot = f.vertex_point(cp([R, 0, 0]))
v_top = f.vertex_point(cp([R, 0, H]))
e_bot = f.edge_curve(v_bot, v_bot, f.circle(
    f.axis2_placement_3d(cp([0, 0, 0]), dir3([0, 0, 1]), dir3([1, 0, 0])), R))
e_top = f.edge_curve(v_top, v_top, f.circle(
    f.axis2_placement_3d(cp([0, 0, H]), dir3([0, 0, 1]), dir3([1, 0, 0])), R))
e_seam = seg(v_bot, v_top, [R, 0, 0], [R, 0, H])
loop_cyl = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_seam, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_seam, False),
])
face_cyl = f.advanced_face([f.face_outer_bound(loop_cyl, orientation=True)],
                           cyl, same_sense=True)

# --- Face TAB: hanging vertex on the seam's interior at z=ZH ---------------
A = (R + DX, 0.0, ZH)
B = (R + DX, 0.0, H)
C = (R + 3.0, 1.2, (ZH + H) / 2.0)
PT = [A, B, C]
vt = [f.vertex_point(cp(p)) for p in PT]
et = [seg(vt[i], vt[(i + 1) % 3], PT[i], PT[(i + 1) % 3]) for i in range(3)]
loop_tab = f.edge_loop([f.oriented_edge(e, True) for e in et])
plane_tab = f.plane(f.axis2_placement_3d(
    cp(A), dir3(cross(sub(B, A), sub(C, A))), dir3(sub(B, A))))
face_tab = f.advanced_face([f.face_outer_bound(loop_tab, orientation=True)],
                           plane_tab, same_sense=True)

shell = f.open_shell([face_cyl, face_tab],
                     name="tsh262_seam_edge_cut_dual_pcurve_shell")
f.add_product_chain(f.shell_based_surface_model([shell]))
