# §12.3a — Shell / orientation defects (Tsh-prefix)

Closed/open shell topology issues: non-manifold edges, inconsistent face orientation, hole-in-solid problems, shell sewing failures, missing `oriented_closed_shell` wrappers, and solid-vs-shell type confusion.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.3a) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Bo001](Bo001.stp) | Outer shell of a solid is empty (zero faces) |
| [Bo002](Bo002.stp) | MANIFOLD_SOLID_BREP with dangling shell reference (outer points to a non-existent entity) |
| [Bo003](Bo003.stp) | Two void shells of one solid are nested inside each other |
| [Bo004](Bo004.stp) | Closed shell encloses an unrepresented cavity (genus mismatch) |
| [Bo005](Bo005.stp) | Shell whose orientation flags admit no globally consistent normal (Möbius-like) |
| [Bo006](Bo006.stp) | One edge is shared by three or more faces in a 2-manifold shell |
| [Bo007](Bo007.stp) | A face appears twice in the same shell |
| [Bo008](Bo008.stp) | Sub-shape attached at the wrong topological level |
| [Bo022](Bo022.stp) | Shell is internally disconnected (two face groups never share an edge) |
| [Bo024](Bo024.stp) | Closed shell whose face orientations imply negative volume |
| [Bo025](Bo025.stp) | Two ADVANCED_FACEs on duplicate CYLINDRICAL_SURFACEs share a smooth (G1) edge mis-tagged as a sharp crease |
| [Bo027](Bo027.stp) | Per-vertex normals supplied for a triangulated face are inconsistent across smooth edges |
| [Bo028](Bo028.stp) | Two adjacent faces meet C1-discontinuously across a shared edge |
| [Bo030](Bo030.stp) | EDGE_CURVE start VERTEX_POINT lies off the underlying LINE: inner-vertex tolerance smaller than the deviation it bounds |
| [Bo031](Bo031.stp) | Void shell of a solid that translates to nothing at all: the solid is still built from the outer shell and the surviving void |
| [Ps001](Ps001.stp) | Negative-volume cube: every face normal points inward |
| [Ps002](Ps002.stp) | FACE_OUTER_BOUND traversed CW; inner loop traversed CCW |
| [Ps003](Ps003.stp) | Single ADVANCED_FACE with same_sense flipped on outer skin |
| [Ps004](Ps004.stp) | Left-handed AXIS2_PLACEMENT_3D on a child shape |
| [Ps005](Ps005.stp) | Two MANIFOLD_SOLID_BREPs at identical coordinates in one SHAPE_REPRESENTATION |
| [Ps006](Ps006.stp) | Self-overlapping shell: one face double-covers a region of another |
| [Ps007](Ps007.stp) | Assembly child placed at identity instead of intended offset |
| [Ps008](Ps008.stp) | Inch-valued coordinates labeled as millimetres |
| [Ps009](Ps009.stp) | Flatness tolerance attached to geometrically adjacent wrong face |
| [Ps010](Ps010.stp) | ORIENTED_EDGE.orientation=.F. on every half-edge of a wire |
| [Ps011](Ps011.stp) | Hollow body lost its inner void: BREP_WITH_VOIDS exported as MANIFOLD_SOLID_BREP |
| [Ps012](Ps012.stp) | Sweep silently truncated to a CONICAL_SURFACE |
| [Ps013](Ps013.stp) | Chiral part mirrored by silent X-coordinate negation |
| [Ps014](Ps014.stp) | Position tolerance frame cites datum compartments in wrong order |
| [Ps015](Ps015.stp) | Multi-instance NAUO collapsed by transform-equality dedup to single instance |
| [Sw001](Sw001.stp) | Three or more faces share a boundary edge after sewing (non-manifold result) |
| [Sw002](Sw002.stp) | Sliver face silently dropped by sewing |
| [Sw003](Sw003.stp) | Degenerate face (collapsed wire) marked as such by sewing but accepted upstream |
| [Sw004](Sw004.stp) | Fast-sewing face has null surface reference |
| [Sw005](Sw005.stp) | Fast-sewing face host surface has infinite extent |
| [Sw006](Sw006.stp) | Fast-sewing face whose parametric bounds are tighter than surface natural bounds |
| [Sw007](Sw007.stp) | Fast-sewing cannot find the canonical vertex for a wire endpoint |
| [Sw008](Sw008.stp) | Fast-sewing cannot match candidate EDGE_CURVE to global edge table: same endpoints but different underlying curves (LINE vs degree-1 B_SPLINE_CURVE_WITH_KNOTS) |
| [Sw009](Sw009.stp) | `same_parameter` flag-skip trap during fast sewing |
| [Tsh001](Tsh001.stp) | ManifoldSolidBrep.outer references OPEN_SHELL |
| [Tsh002](Tsh002.stp) | FACETED_BREP.outer references OPEN_SHELL |
| [Tsh003](Tsh003.stp) | Closed solid round-trips as SHELL_BASED_SURFACE_MODEL/OPEN_SHELL (SpaceClaim regression) |
| [Tsh004](Tsh004.stp) | Sheet bodies imported in place of solids (FEA pipeline) |
| [Tsh005](Tsh005.stp) | Solid demoted by stricter receiver tolerance ("clean in FreeCAD, broken in SolidWorks") |
| [Tsh006](Tsh006.stp) | Bundled component STEP packages emit OPEN_SHELL components |
| [Tsh007](Tsh007.stp) | `IsClosed` flag inconsistent with actual shell topology |
| [Tsh008](Tsh008.stp) | Mis-oriented faces in shell (Möbius-detect) |
| [Tsh009](Tsh009.stp) | Solid built from open shell with inward-pointing outer-shell normals |
| [Tsh010](Tsh010.stp) | Reversed face normal in closed shell ("inside-out" shading) |
| [Tsh011](Tsh011.stp) | `FACE_OUTER_BOUND` orientation flag inconsistent with required winding |
| [Tsh012](Tsh012.stp) | Mixed `.T.`/`.F.` flags on `ORIENTED_EDGE` mismatched against parameter direction |
| [Tsh013](Tsh013.stp) | Face has multiple outer wires (face needs splitting into disjoint regions) |
| [Tsh015](Tsh015.stp) | Brep_with_voids: void shell oriented `.T.` instead of `.F.` (ProSTEP TR9) |
| [Tsh018](Tsh018.stp) | Volume orientation mismatch between `LastShape()` and parent solid |
| [Tsh019](Tsh019.stp) | Non-manifold edge (≥3 incident faces) in shell or solid |
| [Tsh020](Tsh020.stp) | Edge appearing only once or more than twice on faces (Q064 non-2-manifold) |
| [Tsh021](Tsh021.stp) | Non-manifold vertex (bowtie / hourglass / fan-of-fans) |
| [Tsh022](Tsh022.stp) | Non-manifold STEP loses XCAF attributes (color/PMI) on read |
| [Tsh023](Tsh023.stp) | Empty `EDGE_LOOP` / empty face list on shells |
| [Tsh024](Tsh024.stp) | `CONNECTED_FACE_SET` containing non-face entities |
| [Tsh026](Tsh026.stp) | Coincident / duplicate `ADVANCED_FACE` instances in `CLOSED_SHELL` |
| [Tsh027](Tsh027.stp) | Coincident-but-not-shared faces between adjacent solids |
| [Tsh028](Tsh028.stp) | `STYLED_ITEM` attached to sub-tolerance sliver `ADVANCED_FACE` (lost / mis-bound on healing) |
| [Tsh029](Tsh029.stp) | Naked / dangling edge in shell (free edges, LOTAR integrity defect) |
| [Tsh030](Tsh030.stp) | Non-finite (infinite) solid built from open shell |
| [Tsh032](Tsh032.stp) | Single `ADVANCED_FACE` with `same_sense=.F.` flipped inward in `CLOSED_SHELL` (Thingi10K cluster) |
| [Tsh033](Tsh033.stp) | Mirrored block instances flip surface direction with parameter-space curves |
| [Tsh035](Tsh035.stp) | `DEGENERATE_TOROIDAL_SURFACE` with negative minor radius and same `EDGE_CURVE` reused with opposite senses (orientation ambiguity) |
| [Tsh036](Tsh036.stp) | Revolved shape imported with complementary (reversed) angle |
| [Tsh037](Tsh037.stp) | Free wires/edges in compound (Q029, F080 — no faces, INTERNAL orientation) |
| [Tsh039](Tsh039.stp) | Self-touching boundary cycle (figure-eight wire after triangulation) |
| [Tsh040](Tsh040.stp) | `EDGE_CURVE` shared across two `OPEN_SHELL`s in one `SHELL_BASED_SURFACE_MODEL` (T-junction mis-classified as non-manifold by slicer) |
| [Tsh041](Tsh041.stp) | Shell extrusion with shared edges yields CompSolid with duplicated internal faces |
| [Tsh042](Tsh042.stp) | `bad vertex`: vertex misplaced relative to incident edges |
| [Tsh043](Tsh043.stp) | Multi-face shell needs orchestrated face-by-face plus shell-wide healing (e.g., OPEN_SHELL with two ADVANCED_FACEs where one has same_sense=.F. flipped relative to neighbour) |
| [Tsh044](Tsh044.stp) | Free edges in OPEN_SHELL distinguished from non-watertight defects (e.g., two adjacent ADVANCED_FACEs each define their own EDGE_CURVE on a common boundary instead of sharing one) |
| [Tsh045](Tsh045.stp) | `MANIFOLD_SOLID_BREP` whose outer shell loses the closed flag after face unification |
| [Tsh046](Tsh046.stp) | Adjacent same-domain faces fail to merge across linear-edge chain |
| [Tsh047](Tsh047.stp) | Same-domain face unification crosses cylinder seam and produces non-manifold result |
| [Tsh048](Tsh048.stp) | Same-domain face unification corrupts shape with mirrored sub-instance |
| [Tsh049](Tsh049.stp) | Internal edges lost during shell-level face merge |
| [Tsh050](Tsh050.stp) | Edges on shared face boundary not deduplicated after merge |
| [Tsh051](Tsh051.stp) | Shell shared-face union loses location when REPRESENTATION_MAP / AXIS2_PLACEMENT_3D ref_direction encodes a non-unit (scaled) DIRECTION |
| [Tsh052](Tsh052.stp) | Inversed normals on revolved-shape import |
| [Tsh053](Tsh053.stp) | Merging coplanar adjacent faces fails with construction error on shape with empty edge loop |
| [Tsh054](Tsh054.stp) | Merging adjacent same-surface faces crashes when input has chained placements |
| [Tsh055](Tsh055.stp) | Merging adjacent same-surface faces with opposite normals returns inverted face |
| [Tsh056](Tsh056.stp) | Merging adjacent same-surface faces hangs on a face whose wire forms a figure-eight |
| [Tsh057](Tsh057.stp) | Merging near-tangent adjacent ADVANCED_FACEs (PLANE normals differ ~1e-4 rad, shared EDGE_CURVE with mismatched vertex z) returns self-overlapping face |
| [Tsh058](Tsh058.stp) | Adjacent same-surface face merge ignores edge-preservation request |
| [Tsh059](Tsh059.stp) | Coplanar-face merge history map omits intermediate shapes (multiple ADVANCED_FACEs aliasing the same FACE_OUTER_BOUND and same PLANE) |
| [Tsh060](Tsh060.stp) | Same-surface face merge runs quadratically across disjoint shells |
| [Tsh061](Tsh061.stp) | Merging same-surface faces around a non-manifold interior edge corrupts topology |
| [Tsh062](Tsh062.stp) | Merging adjacent same-surface faces returns topologically invalid shape (OPEN_SHELL of multiple CYLINDRICAL_SURFACE faces with degenerate seam edges where two distinct VERTEX_POINTs share coords) |
| [Tsh063](Tsh063.stp) | Adjacent toroidal faces with identical parameters are not detected as same-surface |
| [Tsh064](Tsh064.stp) | Same-surface face merge edge-removal history contract is undocumented |
| [Tsh065](Tsh065.stp) | Tessellated shell with shared nodes between adjacent triangulated faces |
| [Tsh066](Tsh066.stp) | Same `CLOSED_SHELL` referenced from two `MANIFOLD_SOLID_BREP` entities |
| [Tsh067](Tsh067.stp) | Inner void shell extends beyond outer shell extent (void poking through) |
| [Tsh068](Tsh068.stp) | `MANIFOLD_SOLID_BREP` whose outer shell is open (not closed) silently accepted |
| [Tsh069](Tsh069.stp) | CheckOrientedShells Normal-Flip Detection |
| [Tsh070](Tsh070.stp) | FixFaceOrientation Multiconnect-Edge Classification |
| [Tsh071](Tsh071.stp) | BadEdges Detection for Mismatched Edge Ordering |
| [Tsh072](Tsh072.stp) | FreeEdges Detection for Non-Closed Shells |
| [Tsh073](Tsh073.stp) | Perform Context State Reuse Vulnerability |
| [Tsh074](Tsh074.stp) | Duplicate faces in shell |
| [Tsh075](Tsh075.stp) | Non-orientable Möbius shell |
| [Tsh076](Tsh076.stp) | Shell-count escalation on decomposition |
| [Tsh077](Tsh077.stp) | Empty CLOSED_SHELL |
| [Tsh078](Tsh078.stp) | Möbius-strip orientation contradiction |
| [Tsh079](Tsh079.stp) | ShapeUpgrade_ShellSewing.Apply two-shell sew vertex-tolerance mismatch gap |
| [Tsh080](Tsh080.stp) | ShapeFix_Shell.FixFaceOrientation cascade-fix star-shaped junction incomplete propagation |
| [Tsh081](Tsh081.stp) | ShapeAnalysis_Shell.LoadShells multiple-shell input iteration order affects healing |
| [Tsh082](Tsh082.stp) | ShapeUpgrade_RemoveLocations.MakeNewShape stale location reference during traversal |
| [Tsh083](Tsh083.stp) | ShapeFix_Solid.SolidFromShell open-shell-as-solid promotion non-closure detection |
| [Tsh084](Tsh084.stp) | ShapeAnalysis_Shell.CheckOrientedShells closed-shell self-test |
| [Tsh085](Tsh085.stp) | ShapeFix_Shell.FixFaceOrientation transition-point |
| [Tsh086](Tsh086.stp) | ShapeUpgrade_ShellSewing.Prepare two-orientation merge |
| [Tsh087](Tsh087.stp) | ShapeFix_Shell.Perform face-removal during iteration |
| [Tsh088](Tsh088.stp) | ShapeAnalysis_Shell.LoadShells orientation-from-compound |
| [Tsh089](Tsh089.stp) | ShapeUpgrade_RemoveInternalWires tolerance-based removal |
| [Tsh090](Tsh090.stp) | ShapeFix_Shell.FixFaceOrientation single-face shell |
| [Tsh091](Tsh091.stp) | ShapeUpgrade_ShellSewing.Apply degenerate-face sliver |
| [Tsh092](Tsh092.stp) | ShapeAnalysis_Shell.CheckOrientedShells nested-shell cavity |
| [Tsh093](Tsh093.stp) | ShapeFix_Shell.Perform empty-output handling |
| [Tsh094](Tsh094.stp) | ShapeFix_Shell.FixFaceOrientation duplicate-face removal |
| [Tsh095](Tsh095.stp) | ShapeUpgrade_ShellSewing.ApplySewing self-intersecting shell |
| [Tsh096](Tsh096.stp) | ShapeAnalysis_Shell.CheckOrientedShells degenerate-face |
| [Tsh097](Tsh097.stp) | ShapeFix_Shell.Perform context-state accumulation |
| [Tsh098](Tsh098.stp) | ShapeUpgrade_RemoveLocations.Remove location-after-traversal |
| [Tsh099](Tsh099.stp) | ShapeAnalysis_Shell.CheckOrientedShells one-face-shell |
| [Tsh100](Tsh100.stp) | ShapeFix_Shell.FixFaceOrientation tangent-edge propagation |
| [Tsh101](Tsh101.stp) | ShapeUpgrade_ShellSewing.Apply tolerance-driven merge |
| [Tsh102](Tsh102.stp) | ShapeFix_Solid.SolidFromShell hollow-solid cavity loss |
| [Tsh103](Tsh103.stp) | ShapeAnalysis_Shell.FreeEdges seam-edge classification |
| [Tsh104](Tsh104.stp) | ShapeFix_Shell.FixFaceOrientation reverse-edge propagation |
| [Tsh105](Tsh105.stp) | ShapeAnalysis_Shell.CheckOrientedShells unconnected components |
| [Tsh106](Tsh106.stp) | ShapeUpgrade_RemoveInternalWires shell-level skip |
| [Tsh107](Tsh107.stp) | ShapeFix_Shell.Perform double-orient oscillation |
| [Tsh108](Tsh108.stp) | ShapeUpgrade_ShellSewing.Apply zero-tolerance |
| [Tsh109](Tsh109.stp) | ShapeFix_Shell.Perform rejection orphan vertices |
| [Tsh110](Tsh110.stp) | ShapeUpgrade_ShellSewing tolerance-scale interaction |
| [Tsh111](Tsh111.stp) | ShapeAnalysis_Shell.CheckOrientedShells torus topology |
| [Tsh112](Tsh112.stp) | ShapeFix_Shell.FixFaceOrientation T-junction ambiguity |
| [Tsh113](Tsh113.stp) | ShapeUpgrade_RemoveInternalWires edge-loop aliasing |
| [Tsh114](Tsh114.stp) | wedge near-tangent dihedral angle |
| [Tsh115](Tsh115.stp) | orientation flag mismatch (CLOSED_SHELL single face) |
| [Tsh116](Tsh116.stp) | lone inverted face in 6-face cube |
| [Tsh117](Tsh117.stp) | aliased EDGE_LOOP (inner bound references outer of another face) |
| [Tsh118](Tsh118.stp) | 5-face open box (missing top, free edges on rim) |
| [Tsh119](Tsh119.stp) | ShapeFix_Shell.Perform unused-vertex retention |
| [Tsh120](Tsh120.stp) | ShapeAnalysis_Shell.CheckOrientedShells uniform-orientation wrong direction |
| [Tsh121](Tsh121.stp) | ShapeUpgrade_ShellSewing.ApplySewing tolerance-cascade |
| [Tsh122](Tsh122.stp) | ShapeFix_Shell.FixFaceOrientation across-edge propagation |
| [Tsh123](Tsh123.stp) | ShapeAnalysis_Shell.BadEdges adjacent-face mismatch |
| [Tsh124](Tsh124.stp) | ShapeUpgrade_RemoveInternalWires faces-with-multiple-internal-wires |
| [Tsh125](Tsh125.stp) | ShapeFix_Shell.Perform recursive context |
| [Tsh126](Tsh126.stp) | ShapeAnalysis_Shell.CheckOrientedShells coplanar-faces |
| [Tsh127](Tsh127.stp) | ShapeUpgrade_ShellSewing.Apply different-shell-tolerances |
| [Tsh128](Tsh128.stp) | ShapeFix_Shell.FixFaceOrientation early-exit |
| [Tsh129](Tsh129.stp) | ShapeFix_Shell.Perform compound-input |
| [Tsh130](Tsh130.stp) | ShapeAnalysis_Shell.CheckOrientedShells closed-shell-with-free-edges |
| [Tsh131](Tsh131.stp) | ShapeUpgrade_ShellSewing.Apply already-sewn |
| [Tsh132](Tsh132.stp) | ShapeFix_Shell.FixFaceOrientation flat-shell |
| [Tsh133](Tsh133.stp) | ShapeUpgrade_RemoveLocations.Remove top-down |
| [Tsh134](Tsh134.stp) | CheckOrientedShells edge-tolerance |
| [Tsh135](Tsh135.stp) | ShapeUpgrade_ShellSewing.Apply face-with-multiple-edges-to-merge |
| [Tsh136](Tsh136.stp) | ShapeFix_Shell.FixFaceOrientation degenerate-shell-empty |
| [Tsh137](Tsh137.stp) | ShapeAnalysis_Shell.LoadShells nested-compound |
| [Tsh138](Tsh138.stp) | ShapeFix_Shell.Perform repeated-call-state |
| [Tsh139](Tsh139.stp) | ShapeFix_Shell.FixFaceOrientation cylindrical-shell |
| [Tsh140](Tsh140.stp) | ShapeAnalysis_Shell.CheckOrientedShells curved-faces |
| [Tsh141](Tsh141.stp) | ShapeUpgrade_ShellSewing.Apply self-sewing |
| [Tsh142](Tsh142.stp) | ShapeFix_Shell.Perform overlapping-faces |
| [Tsh143](Tsh143.stp) | ShapeAnalysis_Shell.BadEdges shared-edge-with-different-curves |
| [Tsh144](Tsh144.stp) | ShapeFix_Shell.FixFaceOrientation T-shaped-non-manifold |
| [Tsh145](Tsh145.stp) | ShapeAnalysis_Shell.CheckOrientedShells one-face-shell-edge-cases |
| [Tsh146](Tsh146.stp) | ShapeUpgrade_ShellSewing.Apply different-tolerance-per-face |
| [Tsh147](Tsh147.stp) | ShapeFix_Shell.Perform fix-then-revert |
| [Tsh148](Tsh148.stp) | ShapeAnalysis_Shell.FreeEdges count-zero |
| [Tsh149](Tsh149.stp) | ShapeFix_Shell.FixFaceOrientation hexagonal-shell |
| [Tsh150](Tsh150.stp) | ShapeAnalysis_Shell.CheckOrientedShells thin-shell |
| [Tsh151](Tsh151.stp) | ShapeUpgrade_ShellSewing.Apply asymmetric-tolerance |
| [Tsh152](Tsh152.stp) | ShapeFix_Shell.Perform large-shell-pagination |
| [Tsh153](Tsh153.stp) | ShapeAnalysis_Shell.LoadShells with-deeply-nested-compound |
| [Tsh154](Tsh154.stp) | ShapeFix_Shell.FixFaceOrientation pyramid-with-apex |
| [Tsh155](Tsh155.stp) | ShapeAnalysis_Shell.CheckOrientedShells with-degenerate-shell |
| [Tsh156](Tsh156.stp) | ShapeUpgrade_ShellSewing.Apply mismatch-curve-types |
| [Tsh157](Tsh157.stp) | ShapeFix_Shell.Perform circular-fix-dependency |
| [Tsh158](Tsh158.stp) | ShapeAnalysis_Shell.BadEdges seam-edge-direction |
| [Tsh159](Tsh159.stp) | ShapeFix_Shell.FixFaceOrientation tetrahedron-flipped |
| [Tsh160](Tsh160.stp) | ShapeAnalysis_Shell.CheckOrientedShells inverted-trace |
| [Tsh161](Tsh161.stp) | ShapeUpgrade_ShellSewing.Apply with-history-tracking |
| [Tsh162](Tsh162.stp) | ShapeFix_Shell.Perform reports-fixed-but-still-broken |
| [Tsh163](Tsh163.stp) | ShapeAnalysis_Shell.FreeEdges edge-by-vertex-coincidence |
| [Tsh164](Tsh164.stp) | ShapeFix_Shell.Perform with-context-pollution |
| [Tsh165](Tsh165.stp) | ShapeAnalysis_Shell.CheckOrientedShells multi-component |
| [Tsh166](Tsh166.stp) | ShapeUpgrade_ShellSewing.Apply face-with-same-base |
| [Tsh167](Tsh167.stp) | ShapeFix_Shell.FixFaceOrientation with-empty-loop |
| [Tsh168](Tsh168.stp) | ShapeAnalysis_Shell.LoadShells skipping-non-shell |
| [Tsh169](Tsh169.stp) | ShapeFix_Shell.Perform shell-with-floating-faces |
| [Tsh170](Tsh170.stp) | ShapeAnalysis_Shell.CheckOrientedShells with-zero-tolerance |
| [Tsh171](Tsh171.stp) | ShapeUpgrade_ShellSewing.Apply with-cross-shell-intersection |
| [Tsh172](Tsh172.stp) | ShapeFix_Shell.FixFaceOrientation with-3-faces-sharing-vertex |
| [Tsh173](Tsh173.stp) | ShapeAnalysis_Shell.LoadShells with-recursive-compound |
| [Tsh174](Tsh174.stp) | ShapeFix_Shell.FixFaceOrientation with-empty-shell-after-fix |
| [Tsh175](Tsh175.stp) | ShapeAnalysis_Shell.CheckOrientedShells with-self-touching-shell |
| [Tsh176](Tsh176.stp) | ShapeUpgrade_ShellSewing.Apply with-coincident-but-different-orientation |
| [Tsh177](Tsh177.stp) | ShapeFix_Shell.Perform infinite-loop-detection |
| [Tsh178](Tsh178.stp) | ShapeAnalysis_Shell.FreeEdges with-degenerate-edges |
| [Tsh179](Tsh179.stp) | ShapeFix_Shell.FixFaceOrientation hex-prism orientation propagation oscillation |
| [Tsh180](Tsh180.stp) | ShapeAnalysis_Shell.CheckOrientedShells single-face zero-area |
| [Tsh181](Tsh181.stp) | ShapeUpgrade_ShellSewing.Apply bridge tolerance too large |
| [Tsh182](Tsh182.stp) | ShapeFix_Shell.Perform face removal with shared edge |
| [Tsh183](Tsh183.stp) | ShapeAnalysis_Shell.LoadShells with-shell-marker-but-no-faces |
| [Tsh184](Tsh184.stp) | ShapeFix_Shell.FixFaceOrientation duplicate-face inconsistency |
| [Tsh185](Tsh185.stp) | ShapeFix_Solid.Perform context-stale-state cumulative fixes |
| [Tsh186](Tsh186.stp) | ShapeFix_Solid.SolidFromShell orientation-infinite-point non-closed shell |
| [Tsh187](Tsh187.stp) | BRepBuilderAPI_Sewing.AnalysisNearestEdges section-bound-lookup gate |
| [Tsh188](Tsh188.stp) | ShapeFix_Shell.Perform progress-abort inconsistent-status |
| [Tsh189](Tsh189.stp) | ShapeAnalysis_Shell.BadEdges uninitialized compound |
| [Tsh190](Tsh190.stp) | ShapeAnalysis_Shell.FreeEdges uninitialized compound |
| [Tsh191](Tsh191.stp) | ShapeFix_Shell.FixFaceOrientation multi-connected edge unbounded |
| [Tsh192](Tsh192.stp) | ShapeFix_Shell.Perform closed-flag sync-failure |
| [Tsh193](Tsh193.stp) | ShapeUpgrade_ShellSewing.Apply tolerance-boundary classification |
| [Tsh194](Tsh194.stp) | ShapeAnalysis_Shell.BadEdges uninitialized extent |
| [Tsh195](Tsh195.stp) | ShapeFix_Shell.FixFaceOrientation duplicate faces undetected |
| [Tsh196](Tsh196.stp) | ShapeFix_Shell.FixFaceOrientation multi-connected edge unbounded loop |
| [Tsh197](Tsh197.stp) | ShapeFix_Shell.FixFaceOrientation shells extraction loss |
| [Tsh198](Tsh198.stp) | ShapeFix_Shell.Perform context null initialize |
| [Tsh199](Tsh199.stp) | Duplicate faces orientation inconsistency |
| [Tsh200](Tsh200.stp) | BadEdges uninitialized extent |
| [Tsh201](Tsh201.stp) | Multi-connected edge unbounded iteration |
| [Tsh202](Tsh202.stp) | Context null-initialize state accumulation |
| [Tsh203](Tsh203.stp) | Sewing distance tolerance filter gap |
| [Tsh204](Tsh204.stp) | Duplicate faces orientation inconsistency |
| [Tsh205](Tsh205.stp) | Shells extraction partition loss |
| [Tsh206](Tsh206.stp) | Context null state accumulation |
| [Tsh207](Tsh207.stp) | Progress abort inconsistent error state |
| [Tsh208](Tsh208.stp) | Closed flag sync failure |
| [Tsh209](Tsh209.stp) | U-closed seam-edge period wrapping |
| [Tsh210](Tsh210.stp) | Shell tolerance iteration filtering |
| [Tsh211](Tsh211.stp) | Degenerate edge-only wire removal |
| [Tsh212](Tsh212.stp) | Mixed wire/edge orientation conflict |
| [Tsh213](Tsh213.stp) | Wire collection type-filter gate |
| [Tsh214](Tsh214.stp) | ShapeFix_Shell.FixFaceOrientation.duplicate_faces_undetected |
| [Tsh215](Tsh215.stp) | ShapeFix_Shell.Perform.context_null_initialize |
| [Tsh216](Tsh216.stp) | ShapeFix_Shell.Perform.progress_abort_inconsistency |
| [Tsh217](Tsh217.stp) | ShapeFix_Shell.Perform.closed_flag_sync_failure |
| [Tsh218](Tsh218.stp) | ShapeFix_Shell.FixFaceOrientation.shells_extraction_loss |
| [Tsh219](Tsh219.stp) | duplicate_faces_undetected |
| [Tsh220](Tsh220.stp) | multiconnect_edge_loop_unbounded |
| [Tsh221](Tsh221.stp) | context_null_initialize |
| [Tsh222](Tsh222.stp) | closed_flag_sync_failure |
| [Tsh223](Tsh223.stp) | shells_extraction_loss |
| [Tsh224](Tsh224.stp) | ShapeFix_Shell.FixFaceOrientation duplicate_faces_undetected |
| [Tsh225](Tsh225.stp) | ShapeFix_Shell.FixFaceOrientation multiconnect_edge_loop_unbounded |
| [Tsh226](Tsh226.stp) | ShapeFix_Shell.FixFaceOrientation shells_extraction_loss |
| [Tsh227](Tsh227.stp) | ShapeFix_Shell.FixFaceOrientation error_faces_mebius_assumption |
| [Tsh228](Tsh228.stp) | ShapeFix_Shell.Perform closed_flag_sync_failure |
| [Tsh229](Tsh229.stp) | Missing or incorrect faces in displayed STEP file |
| [Tsh230](Tsh230.stp) | Surface from STEP file wrongly imported / tessellated (self-intersecting NURBS net) |
| [Tsh231](Tsh231.stp) | Revolve 288°-360° band triggers SURFACE_OF_REVOLUTION bound flip |
| [Tsh232](Tsh232.stp) | Fusion 360 fillet-junction three-valent `ORIENTED_EDGE` in `CLOSED_SHELL` |
| [Tsh233](Tsh233.stp) | Two `MANIFOLD_SOLID_BREP`s sharing the same `OPEN_SHELL` entity reference |
| [Tsh234](Tsh234.stp) | Compound of a normal solid + an isolated sliver solid at 0.5% of its volume |
| [Tsh235](Tsh235.stp) | Compound of a normal solid + a width-factor needle sliver adjacent to it (Merge disposition) |
| [Tsh236](Tsh236.stp) | Two nested `CLOSED_SHELL`s with no `BREP_WITH_VOIDS` wrapper (unstructured shell soup, containment classification) |
| [Tsh237](Tsh237.stp) | Two disjoint `CLOSED_SHELL`s with no `BREP_WITH_VOIDS` wrapper (unstructured shell soup, compound-of-2-solids classification) |
| [Tsh238](Tsh238.stp) | Compound of a normal solid + an isolated volume-threshold sliver, reached via the `dropsmallsolids` operator context |
| [Tsh239](Tsh239.stp) | Compound of a normal solid + an adjacent width-factor sliver, reached via the `dropsmallsolids` operator context (Merge disposition) |
| [Tsh240](Tsh240.stp) | Second independent `BREP_WITH_VOIDS` nested-void solid, geometry distinct from Tsh015 |
| [Tsh241](Tsh241.stp) | Cone-apex degenerate edge referenced from the bounds of TWO different `ADVANCED_FACE`s |
| [Tsh242](Tsh242.stp) | Post-merge leftover free-boundary wire loop of negligible extent, collapsed by sewing |
| [Tsh243](Tsh243.stp) | Within-tolerance gap but candidate edge shorter than the min-length floor: rejected as a spurious sliver |
| [Tsh244](Tsh244.stp) | Within-tolerance gap but sampled-point coverage below ~50%: insufficient-overlap rejection |
| [Tsh245](Tsh245.stp) | Purpose-built equidistant candidate tie-break AND reciprocity-asymmetric configuration |
| [Tsh246](Tsh246.stp) | Two face-hosted candidate edges of unequal length: the longer becomes the parametrization reference |
| [Tsh247](Tsh247.stp) | Two faces sharing one real `EDGE_CURVE` with genuinely tangent (G1) geometry: default read-path continuity encoding |
| [Tsh248](Tsh248.stp) | Three shells (two cylindrical, one planar) meet along one 3D line: N-way non-manifold merge candidate disambiguation |
| [Tsh249](Tsh249.stp) | Three genuinely-fragmented, 50%-overlapping free-edge sections chained into one non-manifold edge via transitive adjacency |
| [Tsh250](Tsh250.stp) | Two stacked full-period cylindrical shells whose facing seam candidate carries only one explicit 2D curve representation |
| [Tsh251](Tsh251.stp) | Face-hosted gap candidate whose achieved merge tolerance exceeds a caller-declared cap: the merge is nullified, not returned out-of-spec |
| [Tsh252](Tsh252.stp) | Partial-overlap (80%-coverage) gap candidate: achieved merge tolerance tracks the inset distance, not the true perpendicular gap |
| [Tsh253](Tsh253.stp) | Two adjacent (not coincident) coplanar faces whose shared-boundary candidate is traversed in opposite directions on each side |
| [Tsh254](Tsh254.stp) | Genuine cross-item shared EDGE_CURVE: identical entity reused by two SHELL_BASED_SURFACE_MODEL items in one non-manifold representation, orientation reversed |
| [Tsh255](Tsh255.stp) | I-DEAS-style legacy STP: two distinct EDGE_CURVE entities sharing one Name string, second entity's own (wrong) geometry silently discarded in favor of name-matched reuse |
| [Tsh256](Tsh256.stp) | FACE_BASED_SURFACE_MODEL drops one failing member face (null surface), builds the rest |
| [Tsh257](Tsh257.stp) | RECTANGULAR_COMPOSITE_SURFACE drops one failing patch (illegal-type parent_surface), builds the rest |
| [Tsh258](Tsh258.stp) | Closed OPEN_SHELL tetrahedron promoted to a genuine solid under non-manifold read mode (tier-3-confirmed, not just shape(N)) |
| [Tsh259](Tsh259.stp) | Small-area internal hole wire removal cascades into removing a whole neighboring face built on the same edges |
| [Tsh260](Tsh260.stp) | Non-conformal T-junction: free edge's endpoints hang on the interior of an unrelated longer edge, split by sewing's Cutting node insertion |
