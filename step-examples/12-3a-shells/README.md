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
