"""Tfa249 — genuine splitting-vertex trigger for
ShapeAnalysis_CheckSmallFace::CheckSplittingVertices (closes TKShHealing GAP
`tkshh-splitting-vertex-face`).

Background: ~17 existing catalog fixtures are named after
CheckSplittingVertices/FixSplitFace (Tfa010, Tfa079, Tfa085, Tfa094, Tfa098,
Tfa104, Tfa117, Tfa118, Tfa129, Tfa136, Tfa145, Tfa149, Tfa163, Tfa169,
Tfa173, Tfa183, Tfa210, Tfa239), but every one of them encodes the
"splitting" vertex as a genuine SHARED TOPOLOGICAL ENDPOINT of the edges it
touches (e.g. Tfa010's bottom edge is pre-split into two EDGE_CURVEs at the
vertex) -- exactly the case OCCT's own guard skips:
`if (V.IsSame(V1) || V.IsSame(V2)) continue;`
(ShapeAnalysis_CheckSmallFace.cxx:533 @ bd2a789f15235755ce4d1a3b07379a2e062fdc2e).

This fixture is different: face[0]'s outer wire has edge AB as ONE
uninterrupted EDGE_CURVE from A(0,0,0) to B(10,0,0) -- never split. A
separate inner wire (triangle V1-V2-V3) has V1 at (5.0, 0.0, 5.0e-8): a NEW,
independent VERTEX_POINT that is NOT a topological endpoint of edge AB,
offset 5e-8 off AB's line (inside the vertex's default 1e-7 tolerance, but
not exactly 0 -- ShapeAnalysis_Curve::Project's caller in
CheckSplittingVertices explicitly skips an exact `dist == 0.0` hit, so an
exact on-curve coincidence would NOT trigger the mechanism; see line 539
`if (dist == 0.0) continue; //smh`).

Live-verified (2026-07-12, OCP 7.8.1):
  - Reconstructing this exact geometry directly via BRepBuilderAPI
    (bypassing STEP reading) and calling
    `ShapeAnalysis_CheckSmallFace().CheckSplittingVertices(face, mapEdges,
    mapParam, allVertCompound)` with an explicit `SetTolerance(1e-4)` (the
    checker's own `myPrecision` member is never initialized by its
    constructor and is left at whatever indeterminate value the allocator
    happens to produce if `SetTolerance` is never called -- silently
    yielding 0 hits regardless of geometry) returns **2** (V1 is visited
    twice by the face's un-deduplicated vertex walk, once per adjacent
    inner-wire edge, and both times correctly identified as splitting edge
    AB's interior). `mapEdges` binds V1 to edge AB. This is the genuine
    trigger the 17 misnamed fixtures fail to encode.
  - IMPORTANT caveat, itself a real finding: loading this file through the
    STANDARD `STEPControl_Reader().TransferRoots()` pipeline does NOT
    preserve the untouched topology needed to reproduce the above call.
    Every STEP face translation is unconditionally passed through
    `XSAlgo_AlgoContainer::ProcessShape` (STEPControl_ActorRead.cxx
    ~line 1660), which -- even with no explicit resource sequence
    configured, and with no Interface_Static switch able to disable it
    (XSAlgo_AlgoContainer::ProcessShape falls back to running
    `ShapeFix_Shape::Perform()` unconditionally when the named resource
    sequence isn't found) -- resolves the SAME T-junction via a DIFFERENT,
    already-covered mechanism inside `ShapeFix_Face`/`ShapeFix_Wire`
    (observed: edge AB gets split into two EDGE_CURVEs at (5,0,0) during
    ordinary reading, i.e. by the time a caller inspects the loaded face,
    V1 IS already a genuine shared endpoint -- exactly the fate of the 17
    misnamed fixtures). So: this file's RAW ENTITIES are a verified-genuine
    CheckSplittingVertices trigger; reproducing that SPECIFIC mechanism
    (as opposed to the STEP reader's own default healing, which also
    "fixes" this defect but via a different code path) requires either
    reconstructing the face via BRepBuilderAPI from this file's raw
    vertex/edge coordinates, or otherwise bypassing STEPControl_Reader's
    mandatory per-face ShapeFix_Shape pass.
  - `validate2` (live, standard STEPControl_Reader pipeline, 2026-07-12):
    occt_heal_on/off both shape(1); shape_counts vertex=24 edge=12 wire=3
    face=2 shell=2 solid=0 compound=1 (edge count is 12, not the 11 raw
    EDGE_CURVE entities in this file, confirming the reader's own default
    healing DID split edge AB into two, as described above).
    gmsh_autofix_on/off=shape(25); ifcopenshell=schema_n/a (AUTOMOTIVE_DESIGN
    unsupported).
  - tier3_geometric.geometric_report: shape_null=False, n_faces_total=2,
    n_edges_total=12, n_vertices_total=24.

Fixture kind: scaffold (kernel-test-pair: this file's raw Part-21 entities
provide the untouched, verified-genuine splitting-vertex setup;
ShapeAnalysis_CheckSmallFace::CheckSplittingVertices must be invoked on a
BRepBuilderAPI-reconstructed face -- or any load path that bypasses
STEPControl_Reader's own unconditional per-face ShapeFix_Shape pass -- to
reproduce the SPECIFIC mechanism; a plain STEPControl_Reader load instead
demonstrates a related, already-covered wire/edge auto-repair).

Do NOT rename or modify the 17 existing misleadingly-named fixtures listed
above -- they demonstrate other real OCCT behaviors; this fixture closes
the coverage gap without touching them.
"""
from pathlib import Path as _Path

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tfa249",
    defect=(
        "genuine CheckSplittingVertices trigger: face[0] outer wire has edge AB "
        "as ONE uninterrupted EDGE_CURVE A(0,0,0)-B(10,0,0) (never pre-split); a "
        "separate inner triangle wire (V1-V2-V3) has V1=(5,0,5e-8), a NEW "
        "independent VERTEX_POINT that is NOT a topological endpoint of edge AB, "
        "offset 5e-8 off AB's interior (within default 1e-7 tolerance, not exactly "
        "on it) -- V.IsSame(V1)||V.IsSame(V2) is FALSE for edge AB, unlike the ~17 "
        "existing misnamed CheckSplittingVertices/FixSplitFace fixtures which all "
        "encode the vertex as a genuine shared topological endpoint; "
        "companion 1x1 face ensures shape(1)"
    ),
)

# ── SPLIT-VERTEX FACE (face[0]): 10x10 square, edge AB uninterrupted ─────────
sp_p0 = f.cartesian_point((0.0, 0.0, 0.0))    # A
sp_p1 = f.cartesian_point((10.0, 0.0, 0.0))   # B
sp_p2 = f.cartesian_point((10.0, 10.0, 0.0))  # C
sp_p3 = f.cartesian_point((0.0, 10.0, 0.0))   # D

sp_v0 = f.vertex_point(sp_p0)
sp_v1 = f.vertex_point(sp_p1)
sp_v2 = f.vertex_point(sp_p2)
sp_v3 = f.vertex_point(sp_p3)

# Outer loop: 4 edges, A-B is a SINGLE uninterrupted EDGE_CURVE.
sp_ec_ab = f.edge_curve(sp_v0, sp_v1, f.line(sp_p0, f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
sp_ec_bc = f.edge_curve(sp_v1, sp_v2, f.line(sp_p1, f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
sp_ec_cd = f.edge_curve(sp_v2, sp_v3, f.line(sp_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
sp_ec_da = f.edge_curve(sp_v3, sp_v0, f.line(sp_p3, f.vector(f.direction((0.0, -1.0, 0.0)), 10.0)))

sp_outer_loop = f.edge_loop([
    f.oriented_edge(sp_ec_ab, True),
    f.oriented_edge(sp_ec_bc, True),
    f.oriented_edge(sp_ec_cd, True),
    f.oriented_edge(sp_ec_da, True),
])
sp_fob = f.face_outer_bound(sp_outer_loop)

# Inner wire (FACE_BOUND): triangle V1-V2-V3. V1 is a NEW, independent vertex
# offset 5e-8 in Z off edge AB's interior (x=5, midpoint of A-B) -- NOT a
# shared topological endpoint of edge AB.
in_p1 = f.cartesian_point((5.0, 0.0, 5.0e-8))  # V1 -- the genuine splitting vertex
in_p2 = f.cartesian_point((4.0, 2.0, 0.0))     # V2
in_p3 = f.cartesian_point((6.0, 2.0, 0.0))     # V3
in_v1 = f.vertex_point(in_p1)
in_v2 = f.vertex_point(in_p2)
in_v3 = f.vertex_point(in_p3)

import math as _math
_d12 = _math.dist((5.0, 0.0, 5.0e-8), (4.0, 2.0, 0.0))
_d31 = _math.dist((6.0, 2.0, 0.0), (5.0, 0.0, 5.0e-8))

in_ec_12 = f.edge_curve(
    in_v1, in_v2,
    f.line(in_p1, f.vector(f.direction((-1.0 / _d12, 2.0 / _d12, -5.0e-8 / _d12)), _d12)),
)
in_ec_23 = f.edge_curve(in_v2, in_v3, f.line(in_p2, f.vector(f.direction((1.0, 0.0, 0.0)), 2.0)))
in_ec_31 = f.edge_curve(
    in_v3, in_v1,
    f.line(in_p3, f.vector(f.direction((-1.0 / _d31, -2.0 / _d31, 5.0e-8 / _d31)), _d31)),
)

in_loop = f.edge_loop([
    f.oriented_edge(in_ec_12, True),
    f.oriented_edge(in_ec_23, True),
    f.oriented_edge(in_ec_31, True),
])
sp_fib = f.face_bound(in_loop, True)

sp_orig = f.cartesian_point((0.0, 0.0, 0.0))
sp_zdir = f.direction((0.0, 0.0, 1.0))
sp_xdir = f.direction((1.0, 0.0, 0.0))
sp_plc = f.axis2_placement_3d(sp_orig, sp_zdir, sp_xdir)
sp_plane = f.plane(sp_plc)

split_face = f.advanced_face([sp_fob, sp_fib], sp_plane)

# ── GOOD companion face (face[1]): valid 1x1 square at (20,0,0)-(21,1,0) ─────
g_p0 = f.cartesian_point((20.0, 0.0, 0.0))
g_p1 = f.cartesian_point((21.0, 0.0, 0.0))
g_p2 = f.cartesian_point((21.0, 1.0, 0.0))
g_p3 = f.cartesian_point((20.0, 1.0, 0.0))
g_v0 = f.vertex_point(g_p0)
g_v1 = f.vertex_point(g_p1)
g_v2 = f.vertex_point(g_p2)
g_v3 = f.vertex_point(g_p3)

g_ec_b = f.edge_curve(g_v0, g_v1, f.line(g_p0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
g_ec_r = f.edge_curve(g_v1, g_v2, f.line(g_p1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
g_ec_t = f.edge_curve(g_v2, g_v3, f.line(g_p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
g_ec_l = f.edge_curve(g_v3, g_v0, f.line(g_p3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

g_loop = f.edge_loop([
    f.oriented_edge(g_ec_b, True),
    f.oriented_edge(g_ec_r, True),
    f.oriented_edge(g_ec_t, True),
    f.oriented_edge(g_ec_l, True),
])

g_orig = f.cartesian_point((20.0, 0.0, 0.0))
g_zdir = f.direction((0.0, 0.0, 1.0))
g_xdir = f.direction((1.0, 0.0, 0.0))
g_plc = f.axis2_placement_3d(g_orig, g_zdir, g_xdir)
g_plane = f.plane(g_plc)

g_fob = f.face_outer_bound(g_loop)
g_face = f.advanced_face([g_fob], g_plane)

# ── Wire both into OPEN_SHELL -> SBSM -> product chain ───────────────────────
shell = f.open_shell([split_face, g_face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa249.stp")
