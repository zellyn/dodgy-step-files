# Tier-2 D — new catalog entries (staging)

These entries are staged for integration into `STEP_PROBLEM_CATALOG.md`. Do not edit the
live catalog or `problems.json` from this worktree — the integrator merges these and flips the
corresponding scoreboard verdict (see `TIER2_D_VERDICTS.md`).

Two GAPs were targeted:

- `sew-cutting-hanging-vertex-split` (exchange GAP) — **CLOSED** by the fixture below (Tsh260).
- `tkshh-indirect-elementary-surface-axes` (tkshhealing GAP) — **NO fixture shipped**; re-confirmed
  STRUCTURALLY-UNREACHABLE via a standard `STEPControl_Reader` read. Full evidence in
  `TIER2_D_VERDICTS.md`. The existing `problems.json` `coverage_verdict: GAP` +
  `VERIFICATION: STRUCTURALLY-UNREACHABLE` note remains correct and needs no change.

---

### Tsh260 — Non-conformal T-junction: free edge's endpoints hang on the interior of an unrelated longer edge, split by sewing's Cutting node insertion
- **Category**: §12.3a shells (sub-class: sewing hanging-vertex / T-junction conformalization — `sew-cutting-hanging-vertex-split`)
- **Sources**: occt-coverage GAP audit, `exchange/problems.json` `sew-cutting-hanging-vertex-split` (`BRepBuilderAPI_Sewing::Cutting` `BRepBuilderAPI_Sewing.cxx:3655-3687`; `CreateCuttingNodes` `:4449-4463`; `CreateSections` `:4532-4535,4581-4590`; `ProjectPointsOnCurve` `:4308-4364`). This class had been re-scored PARTIAL→GAP (BACKLOG.md §(e), Wave-4 adjudication) after two independent sessions FAILED to reproduce Cutting firing — the withdrawal keyed on `Sewing::IsModified(edge)` (which stays False across a Cutting split) and on ambiguous single-hanging-vertex or shared-corner geometries. This fixture reproduces the split by result-topology inspection instead, using the geometry the class actually requires: a free edge whose *whole span* lies strictly interior to a longer edge.
- **Description**: An `OPEN_SHELL` with TWO coplanar (z=0) triangular `ADVANCED_FACE`s, each on a `PLANE` (normal +Z). Face LONG carries a full-length reference edge `EDGE_CURVE` running x=1, y:[0,2] (apex off at (-3,1,0)). Face SHORT carries a free candidate `EDGE_CURVE` running x=1, y:[0.5,1.5] (apex off at (5,1,0)). The candidate edge's BOTH endpoints — (1,0.5,0) and (1,1.5,0) — lie STRICTLY in the interior of LONG's reference edge and share NO vertex with it: a genuine non-conformal T-junction (the two edges look connected in 3D but the topology does not share a node). No pcurves; both faces are planar quadric-free triangles reusing the corpus's 3D-`EDGE_CURVE`-only convention (as in Tsh246).
- **Reproducer recipe**: `OPEN_SHELL` with two planar triangular `ADVANCED_FACE`s; one face hosts a long straight `EDGE_CURVE` (x=1, y:[0,2]); the other hosts a shorter straight `EDGE_CURVE` (x=1, y:[0.5,1.5]) whose two endpoints are strictly interior to the long edge's span and are not topologically shared with it.
- **Expected kernel behavior**: when the shape is passed through `BRepBuilderAPI_Sewing` (the standard shell-sewing / STEP-shell-stitching pass), detect the two hanging vertices projecting onto the interior of the long reference edge and split that edge at the projected parameters (`Cutting`/`CreateCuttingNodes`/`CreateSections`), so the shared boundary becomes conformal; the single long edge is replaced by three collinear sub-edges partitioned exactly at the interior nodes.
- **Notes**: Why we believe this test is valid — RUNTIME-SCAFFOLD verified against this fixture's own bytes (this worktree's `validation/.venv`, OCP/OCCT 7.8.1). `STEPControl_Reader.ReadFile` → `TransferRoots` loads shape_null=False with 2 faces and 6 unique edges (`TopTools_IndexedMapOfShape`), the long reference edge `[(1,0,0),(1,2,0)]` present intact. Feeding the read shape to `BRepBuilderAPI_Sewing(1e-2, sew=True, analysis=True, cutting=True, nonmanifold=False)` and calling `Perform()` yields a result with 7 unique edges in which the long reference edge is GONE and is replaced by exactly three collinear sub-edges — `[(1,0,0),(1,0.5,0)]`, `[(1,0.5,0),(1,1.5,0)]`, `[(1,1.5,0),(1,2,0)]` — cut precisely at the two hanging vertices (1,0.5,0)/(1,1.5,0) contributed by Face SHORT's candidate edge; `NbContigousEdges()==1` (the middle section merges with the candidate). This is a genuine `Cutting` edge split reachable from a plain STEP read plus the sewing pass — the runtime-scaffold demonstration BACKLOG.md §(e) recorded as never yet produced. Note `Sewing::IsModified(long_edge)` returns False (OCCT does not register Cutting sections under `Modified`), which is why prior IsModified-keyed probes missed it; the split is unambiguous in the result topology (three new interior nodes with no other possible source). Sewing is NOT on the default STEP read path (default read leaves the T-junction non-conformal), so this fixture is oracle-invisible to the shape-count oracle and requires the sewing scaffold to observe. Synonyms: "hanging vertex T-junction sewing split STEP", "BRepBuilderAPI_Sewing Cutting interior node edge split", "free edge endpoint on interior of another edge conformalize", "CreateCuttingNodes projected node edge partition", "non-conformal shell T-junction sew".
- **Byte assertion**: count_entity_def(b'PLANE') == 2
- **Byte assertion**: count_entity_def(b'ADVANCED_FACE') == 2
- **Byte assertion**: count_entity_def(b'EDGE_CURVE') == 6
- **Byte assertion**: count_entity_def(b'OPEN_SHELL') == 1
- **Tier-3 assertion**: shape_null == False
- **Tier-3 assertion**: n_faces_total == 2
- **Tier-3 assertion**: n_edges_total == 6
- **Tier-3 assertion**: face[0].surface_type == "plane"
- **Tier-3 assertion**: face[1].surface_type == "plane"
- **OCC behavior**: silent-accept; the default STEP read path loads the 2-face shell as shape(1) with the T-junction left NON-conformal (long edge unsplit, hanging vertices dangling) — no diagnostic is emitted. The conformalizing edge split only occurs when the shape is passed through `BRepBuilderAPI_Sewing::Perform()` (the sewing scaffold), at which point `Cutting` splits the long edge into three sub-edges at the two interior projection nodes.
- **Fixture path**: `step-examples/12-3a-shells/Tsh260.stp`
- **Severity**: P2
- **Model impact**: Non-conformal T-junctions arriving from STEP shell/surface models (mesh-to-BRep exports, multi-patch stitching, imported tessellations) leave the geometry topologically disconnected at the hanging vertex even though it looks watertight; consumers that skip the sewing/Cutting pass (or query connectivity from the raw read) see a spurious free boundary and a missing shared node, and downstream boolean/meshing/watertightness checks fail until the edge is split to conformalize the shared boundary.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=shape(14) ifc=schema_n/a`
