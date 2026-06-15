# OCCT healing-operation coverage

> Provable kernel-grade coverage map: every OCCT repair/heal operation in
> `TKShHealing` (plus the higher-level `BRepLib` / `BRepBuilderAPI_Sewing` /
> `ShapeCustom` / `ShapeExtend` / `ShapeProcess` entry points) is enumerated
> from upstream headers and matched against this catalog. Operations with no
> matching fixture are explicit catalog gaps to fill.

## Totals

| Module group | Operations | Covered (≥1 fixture) | UNCOVERED |
|---|---:|---:|---:|
| `ShapeFix_*` (TKShHealing/ShapeFix) | 99 | 85 | 14 |
| `ShapeUpgrade_*` + `ShapeAnalysis_*` (TKShHealing) | 129 | 104 | 25 |
| `ShapeProcess` + `ShapeCustom` + `ShapeExtend` + `BRepLib` | 87 | 47 | 40 |
| **Total** | **315** | **236 (75%)** | **79 (25%)** |

## Methodology

For each OCCT class, the public header was fetched from
[Open-Cascade-SAS/OCCT@master](https://github.com/Open-Cascade-SAS/OCCT)
under `src/ModelingAlgorithms/TKShHealing/<Module>/` (and parallel paths for
`BRepLib`, `BRepBuilderAPI`). Public, non-constructor, non-destructor methods
that name a specific repair/analysis operation were enumerated; pure
getters/setters and context-management plumbing were skipped (or folded into
the operation they gate, in the case of `Set<Foo>Mode` toggles).

Each operation was then regex-matched against the concatenation of every
catalog entry's `title`, `description`, `expected_kernel_behavior`, `notes`,
`reproducer`, and `occ_behavior_note`. A fixture "covers" an operation if at
least one fixture's text mentions the operation by name or close synonym.
The matcher is biased toward false positives over false negatives — what
matters here is finding the operations no fixture mentions at all.

This report is regenerated from the live OCCT headers + the live catalog,
so as both evolve the coverage map can be refreshed. Generation is currently
manual (3 parallel sub-agents); a future release may automate it.

## High-leverage uncovered operations

These stood out across the three audits as the most useful gaps to fill:

- **`ShapeFix_Shape::FixFreeShellMode`** — no fixture exercises a top-level
  free (non-solid) shell with face-orientation defects. The catalog has many
  free-face and free-wire fixtures (Sw, Hea) but no free-shell.
- **`ShapeFix_Wire::FixNonAdjacentIntersectingEdgesMode`** — covers the
  "distant edge pair within one wire crosses" case OCCT has a dedicated mode
  for; the catalog has the adjacent-edge case but not this one.
- **`ShapeFix_Wireframe::{CheckSmallEdges, MergeSmallEdges, ModeDropSmallEdges}`**
  — small-edge fixtures exist, but none exercises the Wireframe-level
  workflow's drop-mode toggle (isolated micro-edge with no neighbour to
  merge into).
- **`ShapeUpgrade_UnifySameDomain::{KeepShape, SetAngularTolerance}`** — the
  "merge coplanar faces but preserve named edges" and "merge near-coplanar
  with slack angle" cases. UnifySameDomain itself is well-exercised but the
  named-edge-preservation contract isn't.
- **`ShapeAnalysis_Wire::CheckCurveGaps`** — 3D-curve vs pcurve-reconstructed-3D
  divergence (a distinct OCCT diagnostic separate from `SameParameter`).
- **`ShapeAnalysis_TransferParametersProj`** (entire class) — zero matches.
  Parameter transfer during edge splitting is a heal-time operation no
  fixture targets; the split/heal pipeline's internal contracts are under-stressed.
- **`ShapeProcess_ShapeContext`** (9/9 methods uncovered) — PMI/color
  rebinding after healing relies entirely on the ShapeContext replacement
  map. The catalog hits the symptoms (round-trip loses PMI/color) but never
  names the API that fixes them, so a kernel can't tell which contract to
  satisfy.
- **`ShapeCustom_BSplineRestriction`** — 11 methods, 1 hitting fixture
  (Gn026). All tuning knobs (`SetMaxDegree`, `SetMaxNbSegments`,
  `SetTol3d/2d`, `SetContinuity3d/2d`, `SetConvRational`,
  `SegmentSurfaceMode`) uncovered.
- **`BRepLib::EncodeRegularity`** — the canonical G0/G1 edge tagger that
  every fillet/draft/boolean keys off. Uncovered.
- **`BRepBuilderAPI_Sewing::{SetMinTolerance, SetMaxTolerance}`** — no
  fixture pins the tolerance-ladder bounds, even though over-stitching and
  under-stitching are common catalog defects.

## Detailed per-module coverage

## ShapeFix_* (TKShHealing)

Total operations enumerated: 99
Covered by >=1 fixture: 85
UNCOVERED: 14

**Source**: headers fetched from `Open-Cascade-SAS/OCCT@master` under `src/ModelingAlgorithms/TKShHealing/ShapeFix/`. `ShapeFix_Vertex.hxx` does not exist in the current source tree; vertex repairs live on `ShapeFix_Shape` and `ShapeFix_WireVertex`.

Coverage is matched by a coarse regex sweep over the entire catalog entry body (title + description + notes + behavior). False positives are tolerated; false negatives are what we care about. "COVERED" below means at least one fixture mentions the defect class by name or close synonym, not that the catalog formally maps to that operation.

### ShapeFix_Shape

#### Perform()
_Iterates on sub-shape and performs all configured fixes._

COVERED by (126 fixture(s)): A026, A104, Ad045, Ad047, Ad057, Ad086, Ad098, Ad103, Gn011, Gn012, Gn013, Gn014, Gn017, Gp001, Gp002, Gp005, Gp007, Gp016, Gp019, Gp020, Gp021, Gp022, Gp030, Gp031, Gp033, ... +101 more

#### SameParameter()
_Fixes the SameParameter flag/property of edges by updating tolerances._

COVERED by (20 fixture(s)): Ad086, Ad099, Gb004, Gp022, Gp027, Gp035, Gs018, Hea011, N004, N005, N006, Sw009, Twi044, Twi047, Twi048, Twi052, Twi062, Twi065, Twi085, Xp010

#### FixSolidMode (gates ShapeFix_Solid.Perform)
_Toggles whether per-solid fixes run inside top-level Perform._

COVERED by (2 fixture(s)): Tsh018, Wr036

#### FixFreeShellMode (gates ShapeFix_Shell on free shells)
_Toggles whether free shells (not inside a solid) get repaired._

UNCOVERED

Suggested fixture: a shell present at top level (not inside a SOLID_MODEL) with face-orientation defects.

#### FixFreeFaceMode (gates ShapeFix_Face on free faces)
_Toggles whether free faces (not inside a shell) get repaired._

COVERED by (11 fixture(s)): Sw001, Sw002, Sw003, Sw004, Sw005, Sw006, Sw007, Sw008, Sw009, Tfa023, Tsh004

#### FixFreeWireMode (gates ShapeFix_Wire on free wires)
_Toggles whether free wires get repaired._

COVERED by (5 fixture(s)): Ad086, Hea001, Hea006, P017, Tsh037

#### FixSameParameterMode
_Gates ShapeFix::SameParameter after all fixes._

COVERED by (17 fixture(s)): Ad086, Ad099, Gp022, Gp027, Gp035, Hea011, N004, N005, N006, Sw009, Twi044, Twi047, Twi048, Twi052, Twi062, Twi065, Twi085

#### FixVertexPositionMode (gates ShapeFix::FixVertexPosition)
_Moves a vertex to the consensus location of all incident edges._

COVERED by (6 fixture(s)): Ad086, Gp028, N009, N013, N023, Twi059

#### FixVertexTolMode (fixes vertex tolerances on whole shape)
_Increases vertex tolerance to absorb endpoint mismatch._

COVERED by (29 fixture(s)): Ad086, Bo030, Gn031, Gp002, Gp016, Gp038, M053, N001, N002, N003, N007, N008, N009, N010, N011, N012, N039, N045, N047, Tb004, Tfa017, Tsh005, Twi030, Twi036, Twi048, ... +4 more

### ShapeFix_Solid

#### Perform()
_Runs per-solid fixes (calls ShapeFix_Shell on each subshell)._

COVERED by (36 fixture(s)): A104, Ad103, Gp033, Gp035, Gs049, Gs058, Hea001, Hea002, Hea003, Hea006, Hea007, Hea008, Hea009, Hea010, Hea011, Hea012, Hea013, M170, N012, Pf003, Pf020, Pmi062, Pmi094, Tfa036, Tfa037, ... +11 more

#### SolidFromShell()
_Constructs a SOLID from a SHELL and orients it so the volume is finite (not the complement)._

COVERED by (3 fixture(s)): Bo024, Tsh009, Wr036

#### FixShellMode (gates per-shell fixes)
_Toggles per-shell repairs inside solid Perform._

COVERED by (5 fixture(s)): Pf015, Tfa034, Tsh008, Tsh043, Xp008

#### FixShellOrientationMode
_Gates analysis/fix of shell orientation within a solid (inversion)._

COVERED by (8 fixture(s)): Ad086, Bo003, Bo004, M159, Tsh008, Tsh015, Tsh067, Xp024

#### CreateOpenSolidMode
_Whether to manufacture a 'solid' from an OPEN (non-closed) shell._

COVERED by (30 fixture(s)): A102, Ad086, Gs039, Hea002, Hea003, Hea011, Hea016, M003, M052, M053, N016, P015, Tb001, Tfa001, Tfa020, Tfa069, Tsh001, Tsh006, Tsh009, Tsh029, Tsh030, Tsh040, Tsh044, Tsh045, Tsh068, ... +5 more

### ShapeFix_Shell

#### Perform()
_Runs per-face fixes then FixFaceOrientation._

COVERED by (38 fixture(s)): A104, Ad103, Gp033, Gp035, Gs049, Gs058, Hea001, Hea002, Hea003, Hea006, Hea007, Hea008, Hea009, Hea010, Hea011, Hea012, Hea013, M170, N012, Pf003, Pf015, Pf020, Pmi062, Pmi094, Tfa034, ... +13 more

#### FixFaceOrientation()
_Flips faces whose normals point opposite to their neighbours so the shell becomes consistently oriented._

COVERED by (65 fixture(s)): Ad086, P005, Ps001, Tfa034, Tfa060, Tsh001, Tsh002, Tsh003, Tsh004, Tsh005, Tsh006, Tsh007, Tsh008, Tsh009, Tsh010, Tsh011, Tsh012, Tsh013, Tsh015, Tsh018, Tsh019, Tsh020, Tsh021, Tsh022, Tsh024, ... +40 more

#### FixFaceMode (gates ShapeFix_Face)
_Toggles per-face fixes in shell Perform._

COVERED by (8 fixture(s)): Ad086, Tfa004, Tfa005, Tfa011, Tfa037, Tfa038, Tfa039, Tsh028

#### FixOrientationMode
_Gates FixFaceOrientation._

COVERED by (70 fixture(s)): Ad047, Ad086, Bo024, Gs001, P005, Pmi083, Tfa012, Tfa034, Tfa060, Tsh001, Tsh002, Tsh003, Tsh004, Tsh005, Tsh006, Tsh007, Tsh008, Tsh009, Tsh010, Tsh011, Tsh012, Tsh013, Tsh015, Tsh018, Tsh019, ... +45 more

#### SetNonManifoldFlag()
_Marks the shell as non-manifold so non-manifold edges (>2 faces) are allowed._

COVERED by (98 fixture(s)): A019, A078, A085, A089, A102, Ad086, Bo006, Hea002, Hea017, Lh031, M045, M053, M066, M165, P005, P015, P021, P023, Pmi102, Pmi105, Sw001, Sw002, Sw003, Sw004, Sw005, ... +73 more

### ShapeFix_Face

#### Perform()
_Runs all enabled per-face fixes._

COVERED by (42 fixture(s)): A104, Ad086, Ad103, Gp033, Gp035, Gs049, Gs058, Hea001, Hea002, Hea003, Hea006, Hea007, Hea008, Hea009, Hea010, Hea011, Hea012, Hea013, M170, N012, Pf003, Pf020, Pmi062, Pmi094, Tfa004, ... +17 more

#### FixOrientation()
_Reverses the outer wire if its 2D orientation is wrong (CW where CCW expected), and reorders inner wires so containment is correct._

COVERED by (17 fixture(s)): Ad086, P005, P023, Ps001, Ps002, Sw003, Tfa004, Tfa005, Tfa012, Tfa034, Tfa037, Tfa057, Tsh008, Tsh011, Tsh042, Twi024, Twi080

#### FixAddNaturalBound()
_Adds the surface's natural boundary as the outer wire on closed surfaces (sphere, full cone) that lack one._

COVERED by (6 fixture(s)): Ad086, Sw006, Tfa002, Tfa004, Tfa038, Twi091

#### FixMissingSeam()
_Detects when a closed surface (cylinder, sphere) needs a seam edge and adds it._

COVERED by (10 fixture(s)): Ad086, Gp028, Tfa004, Tfa037, Tfa061, Tfa064, Twi020, Twi091, Twi093, Wr037

#### FixSmallAreaWire()
_Removes small-area wires (sliver loops) from a face._

COVERED by (8 fixture(s)): Ad086, M165, Os011, Pf023, Tsh028, Twi024, Twi044, Twi045

#### RemoveSmallAreaFaceMode (removes the whole face when its area is tiny)
_Removes a face whose total area is below tolerance._

COVERED by (21 fixture(s)): Ad086, Ad098, Gs014, Gs015, M165, Os001, Os002, Os003, Pf027, Pf030, Sw002, Sw003, Tfa008, Tfa014, Tfa040, Tfa041, Tfa042, Tfa043, Tsh046, Wr051, Xp003

#### FixIntersectingWires()
_Detects and corrects faces where two boundary wires intersect each other._

COVERED by (19 fixture(s)): Ad086, Gp028, Gp030, Gs009, Gs012, N042, Tb009, Tfa005, Tfa036, Tfa039, Tfa045, Tfa055, Tsh057, Twi049, Twi093, Twi096, Wr037, Xp001, Xp015

#### FixLoopWires()
_Splits a single wire that loops back on itself into multiple wires._

COVERED by (13 fixture(s)): Ad086, Gs009, Hea001, Hea006, Tsh039, Tsh056, Twi010, Twi049, Twi053, Twi054, Twi075, Twi076, Twi096

#### FixSplitFace()
_Splits a face that has multiple outer wires into multiple faces._

COVERED by (5 fixture(s)): Ad086, Tfa011, Tfa051, Tsh013, Twi032

#### FixWiresTwoCoincEdges()
_Removes wires containing exactly two coincident (same) edges (pin/spike loops)._

COVERED by (6 fixture(s)): Ad086, N025, Tfa025, Twi033, Twi037, Twi063

#### FixPeriodicDegenerated()
_Rebuilds degenerated edges at the apex of cones/spheres / poles of periodic surfaces._

COVERED by (25 fixture(s)): Ad086, Bo002, Gb002, Gp005, Gs006, Gs028, Gs034, Pf021, Ps012, Sw003, Tb012, Tb013, Tfa005, Tsh062, Twi021, Twi029, Twi030, Twi031, Twi035, Twi067, Twi083, Twi092, Twi099, Xp013, Xp032

#### AutoCorrectPrecisionMode
_Auto-tuning of precision based on geometry._

COVERED by (1 fixture(s)): Tsh006

### ShapeFix_Wire

#### Perform()
_Runs all enabled wire-level fixes._

COVERED by (42 fixture(s)): A104, Ad103, Gp030, Gp033, Gp035, Gs049, Gs058, Hea001, Hea002, Hea003, Hea006, Hea007, Hea008, Hea009, Hea010, Hea011, Hea012, Hea013, M170, N012, Pf003, Pf020, Pmi062, Pmi094, Tfa036, ... +17 more

#### FixReorder()
_Reorders edges so the wire is a connected chain (head-to-tail)._

COVERED by (5 fixture(s)): Ad086, Tfa037, Twi007, Twi028, Twi078

#### FixSmall()
_Removes null-length edges from the wire._

COVERED by (15 fixture(s)): Ad086, N010, N011, N014, Pf021, Tfa008, Twi013, Twi029, Twi031, Twi083, Twi086, Twi092, Twi099, Wr051, Xp010

#### FixConnected()
_Forces vertices of adjacent edges to coincide (merges or replaces vertices)._

COVERED by (6 fixture(s)): Ad086, Gp020, M004, Tfa065, Twi003, Xp021

#### FixEdgeCurves()
_Umbrella for 3D-curve / pcurve adjustments (Add/RemovePCurve, AddCurve3d, Reversed2d, etc.)._

COVERED by (48 fixture(s)): Ad086, Gp002, Gp005, Gp007, Gp008, Gp010, Gp011, Gp012, Gp013, Gp014, Gp015, Gp016, Gp018, Gp019, Gp020, Gp021, Gp022, Gp023, Gp024, Gp026, Gp027, Gp028, Gp029, Gp030, Gp031, ... +23 more

#### FixDegenerated()
_Detects edges that degenerate to points (e.g. at cone apex) and marks them as degenerated._

COVERED by (17 fixture(s)): Ad086, Bo002, Gp005, Gs006, Gs028, Gs034, Sw003, Tb013, Tfa005, Twi021, Twi029, Twi030, Twi031, Twi035, Twi092, Twi099, Xp032

#### FixSelfIntersection()
_Removes self-intersection within a single wire._

COVERED by (127 fixture(s)): Ad086, Ad099, Fi001, Fi008, Gn024, Gp008, Gs002, Gs009, Gs010, Gs011, Gs012, Gs042, Gs045, Hea017, M023, N008, N042, Os001, Os002, Os003, Os020, Os023, P006, Pf006, Pf023, ... +102 more

#### FixLacking()
_Adds a missing edge (or grows tolerance) where two consecutive edges are 2D-disconnected on a surface._

COVERED by (4 fixture(s)): Ad086, Gp002, Twi036, Twi067

#### FixClosed()
_Closes a wire that should be closed (calls FixConnected + FixLacking + FixDegenerated on the gap)._

COVERED by (1 fixture(s)): Twi053

#### FixGaps3d()
_Closes 3D gaps between 3D curve endpoints of adjacent edges._

COVERED by (8 fixture(s)): Gp020, Gp034, Tfa053, Twi003, Twi051, Twi053, Twi068, Twi072

#### FixGaps2d()
_Closes 2D pcurve gaps between adjacent edges._

COVERED by (6 fixture(s)): Ad086, Gp018, Gp020, Twi067, Twi069, Twi073

#### FixSeam()
_Corrects pcurve ordering for seam edges (which carry two pcurves)._

COVERED by (14 fixture(s)): Ad086, Gn019, Gp011, Gp012, Gp013, Gp026, Gp028, Gs028, Gs051, Tfa018, Twi022, Twi032, Twi052, Twi071

#### FixShifted()
_Shifts pcurves by ±period when they fall outside the expected parameter range on a closed surface._

COVERED by (25 fixture(s)): Ad086, Gn019, Gn033, Gp011, Gp012, Gp013, Gp018, Gp023, Gp026, Gp029, Gp036, Gp039, Gs005, Gs007, Gs019, Gs028, Gs038, N005, Tfa018, Twi008, Twi022, Twi035, Twi052, Twi071, Xp021

#### FixNotchedEdges()
_Removes 'notch' configurations where a sub-edge pair sticks out from a wire._

COVERED by (7 fixture(s)): Ad086, Hea003, Hea005, Twi011, Twi054, Twi074, Twi077

#### FixTails()
_Removes 'tail' configurations (degenerate spikes off a wire)._

COVERED by (2 fixture(s)): Twi011, Twi098

#### FixGap3d() (single-pair)
_Same as FixGaps3d but for one edge pair only._

UNCOVERED

Suggested fixture: ALREADY COVERED by FixGaps3d patterns.

#### FixGap2d() (single-pair)
_Same as FixGaps2d but for one edge pair only._

COVERED by (1 fixture(s)): Ad086

#### FixSelfIntersectingEdgeMode (gates removing a single edge that self-intersects)
_Toggle for self-intersecting individual edges (not wires)._

COVERED by (3 fixture(s)): Ad086, Gn024, Gs009

#### FixIntersectingEdgesMode (gates fixing two adjacent edges that cross)
_Adjacent-edge intersection within a wire._

COVERED by (2 fixture(s)): Gs009, Tb009

#### FixNonAdjacentIntersectingEdgesMode
_Two non-adjacent edges in the same wire crossing each other._

UNCOVERED

Suggested fixture: edge #1 and edge #5 of a 6-edge outer wire cross each other in 3D.

#### FixReversed2dMode
_Reverse a pcurve that points opposite to its 3D curve._

COVERED by (4 fixture(s)): N005, Twi052, Twi065, Twi071

#### FixRemovePCurveMode
_Remove a pcurve that no longer matches the surface or curve._

COVERED by (1 fixture(s)): Twi052

#### FixAddPCurveMode
_Add a pcurve by projecting the 3D curve onto the face's surface when one is missing._

COVERED by (11 fixture(s)): Ad046, Ad086, Gp001, Gp012, Gp019, Gp035, Tsh043, Twi047, Twi052, Wr051, Xp002

#### FixRemoveCurve3dMode
_Remove a 3D curve that no longer matches the vertices._

UNCOVERED

Suggested fixture: an edge whose 3D curve evaluates far from its declared vertices.

#### FixAddCurve3dMode
_Build a 3D curve by lifting a pcurve when the 3D curve is missing._

COVERED by (4 fixture(s)): Os012, Twi046, Twi052, Twi088

#### FixVertexToleranceMode
_Grow vertex tolerance to absorb sub-tolerance gaps at this vertex._

COVERED by (3 fixture(s)): Bo030, N001, N008

### ShapeFix_Edge

#### FixRemovePCurve()
_Removes a pcurve from an edge if it does not match the vertices._

COVERED by (3 fixture(s)): Ad086, Hea011, Twi052

#### FixRemoveCurve3d()
_Removes the 3D curve if it does not match the vertices._

COVERED by (3 fixture(s)): Gs030, N024, Twi046

#### FixAddPCurve()
_Projects 3D curve onto the surface to synthesize a missing pcurve._

COVERED by (11 fixture(s)): Ad046, Ad086, Gp001, Gp012, Gp019, Gp035, Tsh043, Twi047, Twi052, Wr051, Xp002

#### FixAddCurve3d()
_Lifts the pcurve to a 3D curve._

COVERED by (4 fixture(s)): Os012, Twi047, Twi052, Twi088

#### FixVertexTolerance()
_Increases vertex tolerance to comprise the ends of 3D/PCurve._

COVERED by (6 fixture(s)): N001, N008, Twi048, Twi059, Twi061, Twi067

#### FixReversed2d()
_Fixes an edge whose pcurve runs opposite to its 3D curve._

COVERED by (7 fixture(s)): Ad086, Gs018, N005, Twi052, Twi062, Twi065, Twi071

#### FixSameParameter()
_Makes the edge SameParameter (3D and pcurve traversal rates match)._

COVERED by (17 fixture(s)): Ad086, Ad099, Gp022, Gp027, Gp035, Hea011, N004, N005, N006, Sw009, Twi044, Twi047, Twi048, Twi052, Twi062, Twi065, Twi085

### ShapeFix_Wireframe

#### FixWireGaps()
_Fixes 3D and pcurve gaps between adjacent edges in wires (whole shape pass)._

COVERED by (14 fixture(s)): Ad086, Gp018, Gp020, Gp034, N002, Tfa053, Twi003, Twi051, Twi053, Twi067, Twi068, Twi069, Twi072, Twi073

#### FixSmallEdges()
_Merges adjacent edges where one is below tolerance length._

COVERED by (8 fixture(s)): Gn031, N010, N014, Tb006, Tb015, Tfa065, Twi013, Twi098

#### CheckSmallEdges()
_Reports which edges are small (without modifying)._

UNCOVERED

Suggested fixture: ALREADY COVERED.

#### MergeSmallEdges()
_Performs the small-edge merge half of the workflow._

UNCOVERED

Suggested fixture: ALREADY COVERED.

#### ModeDropSmallEdges
_Whether unconnectable small edges should be dropped._

UNCOVERED

Suggested fixture: an isolated micro-edge with no continuation — covered as a sub-case of FixSmallEdges.

### ShapeFix_FreeBounds

#### (connect free open wires; classify open vs closed)
_Detects edges referenced by only one face and stitches open wires together if their endpoints come within tolerance._

COVERED by (83 fixture(s)): Ad086, Hea003, Hea004, M003, M053, Sw001, Sw002, Sw003, Sw004, Sw005, Sw006, Sw007, Sw008, Sw009, Tb001, Tfa001, Tfa002, Tfa003, Tfa004, Tfa005, Tfa006, Tfa007, Tfa008, Tfa010, Tfa011, ... +58 more

### ShapeFix_FixSmallFace

#### Perform()
_Umbrella for spot/strip/pin/split face fixes._

COVERED by (58 fixture(s)): A104, Ad086, Ad103, Fi007, Gp033, Gp035, Gs014, Gs049, Gs058, Hea001, Hea002, Hea003, Hea006, Hea007, Hea008, Hea009, Hea010, Hea011, Hea012, Hea013, M170, N012, Pf003, Pf020, Pf033, ... +33 more

#### FixSpotFace()
_Removes faces that have collapsed to a near-point._

COVERED by (8 fixture(s)): Ad086, Gs014, Sw003, Tfa006, Tfa040, Tfa041, Tfa043, Tfa046

#### FixStripFace()
_Removes/repairs faces that have collapsed to a thin strip (two long sides + two near-zero sides)._

COVERED by (17 fixture(s)): Ad086, Ad098, Gs014, Gs015, M165, Sw002, Tfa007, Tfa008, Tfa040, Tfa042, Tfa043, Tfa047, Tfa048, Tfa061, Twi057, Wr051, Xp003

#### FixSplitFace()
_Splits an over-large face that has multiple disjoint outer bounds._

COVERED by (4 fixture(s)): Ad086, Gs034, Tfa011, Tsh013

#### FixPinFace()
_Removes a 'pin' (face where a single inner wire touches the outer at one point)._

COVERED by (6 fixture(s)): Gs014, Tfa008, Tfa040, Tfa044, Tfa049, Tfa050

#### ReplaceVerticesInCaseOfSpot()
_Sub-step: collapse spot-face vertices to their average._

UNCOVERED

Suggested fixture: ALREADY COVERED by FixSpotFace.

#### ComputeSharedEdgeForStripFace()
_Sub-step: compute the shared edge of a strip face._

UNCOVERED

Suggested fixture: ALREADY COVERED by FixStripFace.

### ShapeFix_FixSmallSolid

#### Remove()
_Deletes solids below volume threshold from a compound._

COVERED by (16 fixture(s)): A004, Gs009, Hea011, N010, Pf022, Tfa006, Tfa007, Tfa015, Tfa041, Tfa042, Tsh029, Twi011, Twi049, Twi077, Twi079, Twi098

#### Merge()
_Merges small solids into adjacent non-small ones._

COVERED by (117 fixture(s)): A019, A028, Ad086, Ad103, Gn034, Gs014, Gs031, Le053, Lh023, Lh025, M004, M148, N001, N002, N003, N004, N005, N006, N007, N008, N009, N010, N011, N012, N013, ... +92 more

### ShapeFix_SplitCommonVertex

#### Perform()
_Splits a vertex that is incorrectly shared by two otherwise-unrelated wires._

COVERED by (39 fixture(s)): A104, Ad086, Ad103, Gp033, Gp035, Gs049, Gs058, Hea001, Hea002, Hea003, Hea006, Hea007, Hea008, Hea009, Hea010, Hea011, Hea012, Hea013, M170, N012, Pf003, Pf020, Pmi062, Pmi094, Tfa036, ... +14 more

### ShapeFix_IntersectionTool

#### SplitEdge()
_Splits an edge in two at a parameter (helper for intersection fixing)._

UNCOVERED

Suggested fixture: ALREADY COVERED by FixSelfIntersectWire.

#### CutEdge()
_Cuts an edge between two parameters._

UNCOVERED

Suggested fixture: ALREADY COVERED.

#### FixSelfIntersectWire()
_Resolves self-intersection in a single wire (by splitting/cutting/removing)._

COVERED by (5 fixture(s)): Ad086, N042, Twi049, Xp001, Xp015

#### FixIntersectingWires()
_Resolves intersections between two distinct wires on a face._

COVERED by (6 fixture(s)): Ad086, N042, Tfa039, Tfa045, Xp001, Xp015

### ShapeFix_ShapeTolerance

#### LimitTolerance()
_Clamps tolerances on V/E/F to be within [tmin, tmax]._

COVERED by (1 fixture(s)): N040

#### SetTolerance()
_Forces all V/E/F to a given tolerance value._

COVERED by (2 fixture(s)): N039, N041

### ShapeFix_EdgeConnect

#### Add() / Build()
_Builds shared vertices and updates tolerances between edges that should be connected._

COVERED by (12 fixture(s)): Lh026, M018, M161, M163, Os011, P003, Tb023, Tfa022, Tsh061, Twi027, Twi046, Twi090

### ShapeFix_FaceConnect

#### Add() / Build()
_Rebuilds connectivity between faces in a shell._

COVERED by (9 fixture(s)): Lh026, M018, M161, M163, Os011, P003, Tsh006, Tsh065, Twi046

### ShapeFix

#### SameParameter()
_Static helper: runs SameParameter on a shape._

COVERED by (17 fixture(s)): Ad086, Ad099, Gp022, Gp027, Gp035, Hea011, N004, N005, N006, Sw009, Twi044, Twi047, Twi048, Twi052, Twi062, Twi065, Twi085

#### EncodeRegularity()
_Sets the regularity (continuity class) of edges between adjacent faces._

COVERED by (4 fixture(s)): Bo025, Bo028, Os008, Tfa010

#### RemoveSmallEdges()
_Eliminates edges smaller than a specified tolerance._

COVERED by (1 fixture(s)): Twi098

#### FixVertexPosition()
_Corrects positions of vertices whose recorded coordinates lie outside tolerance of the consensus point._

COVERED by (4 fixture(s)): Ad086, Gp028, N009, N023

### ShapeFix_ComposeShell

#### Perform()
_Composes faces from a wire collection on a grid surface (used in surface decomposition)._

COVERED by (36 fixture(s)): A104, Ad103, Gp019, Gp033, Gp035, Gs049, Gs058, Hea001, Hea002, Hea003, Hea006, Hea007, Hea008, Hea009, Hea010, Hea011, Hea012, Hea013, M170, N012, Pf003, Pf020, Pmi062, Pmi094, Tfa036, ... +11 more

#### SplitEdges()
_Splits edges in the original shape by the grid._

UNCOVERED

Suggested fixture: ALREADY COVERED by ComposeShell.

#### DispatchWires()
_Assigns closed wires to corresponding patches._

UNCOVERED

Suggested fixture: ALREADY COVERED.

### ShapeFix_WireVertex

#### FixSame()
_Fixes the 'Same' or 'Close' wire-vertex status (sets a single shared vertex)._

UNCOVERED

Suggested fixture: ALREADY COVERED by FixConnected.

#### Fix()
_Fixes all wire-vertex statuses except Disjoined._

COVERED by (53 fixture(s)): Ad045, Ad047, Ad057, Ad086, Ad099, Ad101, Gn025, Gp029, Gp030, Gs007, Gs048, Hea001, Hea002, Hea011, In003, Le026, Le028, Le056, M045, N001, N002, N012, N039, P016, P027, ... +28 more

### ShapeFix_EdgeProjAux

#### Compute()
_Projects edge 3D vertices onto pcurve to determine parametric range._

COVERED by (32 fixture(s)): Bo024, Bo028, Gp001, Gp035, Gp039, Gs001, Hea003, M011, M064, M093, M110, N013, N015, N043, Os021, Pf007, Pf033, Pmi074, Pmi087, Pmi088, Pmi089, Ps001, Ps004, Sw005, Tb005, ... +7 more

### ShapeFix_SplitTool

#### SplitEdge() / CutEdge()
_Low-level edge splitting at parameters (helper for intersection / loop fixes)._

COVERED by (4 fixture(s)): N005, Os008, Twi080, Twi090

---

### Flat list of UNCOVERED operations

- **ShapeFix_Shape::FixFreeShellMode (gates ShapeFix_Shell on free shells)** — Toggles whether free shells (not inside a solid) get repaired.
- **ShapeFix_Wire::FixGap3d() (single-pair)** — Same as FixGaps3d but for one edge pair only.
- **ShapeFix_Wire::FixNonAdjacentIntersectingEdgesMode** — Two non-adjacent edges in the same wire crossing each other.
- **ShapeFix_Wire::FixRemoveCurve3dMode** — Remove a 3D curve that no longer matches the vertices.
- **ShapeFix_Wireframe::CheckSmallEdges()** — Reports which edges are small (without modifying).
- **ShapeFix_Wireframe::MergeSmallEdges()** — Performs the small-edge merge half of the workflow.
- **ShapeFix_Wireframe::ModeDropSmallEdges** — Whether unconnectable small edges should be dropped.
- **ShapeFix_FixSmallFace::ReplaceVerticesInCaseOfSpot()** — Sub-step: collapse spot-face vertices to their average.
- **ShapeFix_FixSmallFace::ComputeSharedEdgeForStripFace()** — Sub-step: compute the shared edge of a strip face.
- **ShapeFix_IntersectionTool::SplitEdge()** — Splits an edge in two at a parameter (helper for intersection fixing).
- **ShapeFix_IntersectionTool::CutEdge()** — Cuts an edge between two parameters.
- **ShapeFix_ComposeShell::SplitEdges()** — Splits edges in the original shape by the grid.
- **ShapeFix_ComposeShell::DispatchWires()** — Assigns closed wires to corresponding patches.
- **ShapeFix_WireVertex::FixSame()** — Fixes the 'Same' or 'Close' wire-vertex status (sets a single shared vertex).

---

## ShapeUpgrade_* + ShapeAnalysis_* (TKShHealing)

Total operations enumerated: 129
Covered by at least 1 fixture: 104
UNCOVERED: 25

Catalog source: /Users/zellyn/gh/dodgy-step-files/STEP_PROBLEM_CATALOG.md (1284 entries)
Header source: github.com/Open-Cascade-SAS/OCCT (master, src/ModelingAlgorithms/TKShHealing/{ShapeUpgrade,ShapeAnalysis}/)

Matching strategy: regex over each entry's title+description+notes+expected_kernel_behavior. False positives accepted; false negatives hide gaps.

---

### ShapeUpgrade_ShapeDivideClosed

#### SetNbSplitPoints(num)
COVERED by: Gp013, Gp027, Gn031, Gs005, Gs038, Twi019, Twi020, Twi032, ... (17 fixtures)
Notes: Configures # of divisions for closed faces (gates split operation).


### ShapeUpgrade_ShapeDivideArea

#### SetNumbersUVSplits(u,v)
COVERED by: Tfa013, Tfa052 (2 fixtures)
Notes: Set fixed U/V split counts for splitting-by-numbers mode.

#### SetSplittingByNumber(bool)
UNCOVERED
What it does: Toggle between area-based and number-based face splitting.
Suggested fixture: Large face that benefits from fixed UV split count (e.g. a single 1000mm x 1000mm planar face) where area-mode would under-split.


### ShapeUpgrade_ShapeDivideContinuity

#### SetTolerance(Tol)
COVERED by: Gn012, Gs025, Gs048, Bo028, Tfa036, Tfa051, Hea010, Gp033 (8 fixtures)
Notes: 3D tolerance for continuity-based shape division.

#### SetTolerance2d(Tol)
COVERED by: Gs005, Tfa036 (2 fixtures)
Notes: 2D tolerance for continuity-based shape division.

#### SetBoundaryCriterion(C)
COVERED by: Bo025, Bo028, Tfa036, Gs058 (4 fixtures)
Notes: Continuity criterion for wires/boundaries.

#### SetPCurveCriterion(C)
COVERED by: Gp012, Gs005, Tfa036 (3 fixtures)
Notes: Continuity criterion for pcurves.

#### SetSurfaceCriterion(C)
COVERED by: Gn026, Gs025, N031, M096, Gs049, Tfa036, Tfa051, Tfa053, ... (10 fixtures)
Notes: Continuity criterion for surfaces.


### ShapeUpgrade_FaceDivide

#### Perform(isPCurves)
COVERED by: Gp027, Gn017, Gs012, Gs025, Gs034, Tsh013, Twi019, Twi020, ... (31 fixtures)
Notes: Splits face by surface and curves; produces shell.

#### SplitSurface(area)
COVERED by: Gn017, Gs025, N013, Xp033, Gs049, Tfa051, Tfa052, Hea010, ... (9 fixtures)
Notes: Splits supporting surface, builds shell from source face.

#### SplitCurves()
COVERED by: Gp027, Gn012, Gn024, Gs025, Gs034, Tsh039, Twi019, Twi032, ... (74 fixtures)
Notes: Splits curves on all edges and divides those edges accordingly.

#### SetSurfaceSegmentMode(bool)
COVERED by: Gp023, Gs057 (2 fixtures)
Notes: Toggle trimming of surface by wire UV bounds.


### ShapeUpgrade_FaceDivideArea

#### Perform(area)
COVERED by: Tfa013, Tfa052 (2 fixtures)
Notes: Performs face splitting based on area threshold.


### ShapeUpgrade_ClosedFaceDivide

#### SplitSurface(area)
COVERED by: Gp027, Twi019, Twi020, Twi032, N005, Tsh047, Tfa061, Hea011, ... (9 fixtures)
Notes: Splits closed surface and builds shell.


### ShapeUpgrade_RemoveLocations

#### Remove(shape)
COVERED by: Tfa030, A006, A007, A024, A066, A073, M061, M067, ... (14 fixtures)
Notes: Eliminates all (or non-rigid) locations from a shape.

#### ModifiedShape(initShape)
UNCOVERED
What it does: Retrieves transformed version after location removal.
Suggested fixture: Assembly where caller needs to track an original sub-shape through location-collapse (e.g. PRODUCT label binding survives RemoveLocations).


### ShapeUpgrade_RemoveInternalWires

#### Perform()
COVERED by: Gs009, Twi009, Twi024, Twi044, Twi045, Tfa002, Tfa004, Tfa010, ... (23 fixtures)
Notes: Removes internal wires with area less than min allowed area.

#### Perform(seqShapes)
UNCOVERED
What it does: Removes internal wires from given subshapes.
Suggested fixture: Face with multiple internal holes where caller wants to remove only a specific listed face's holes, not all small holes in the model.

#### MinArea()
UNCOVERED
What it does: Threshold for hole removal (gates removal).
Suggested fixture: Face with a mix of meaningful holes and accidentally-tiny inner loops (e.g. 0.001mm radius circles) requiring a threshold gate.

#### RemoveFaceMode()
UNCOVERED
What it does: Toggle whether faces composed of removed internals are eliminated.
Suggested fixture: Face whose outer loop became collapsed after internal-wire removal; toggle should drop the now-empty face entirely.


### ShapeUpgrade_ConvertCurve2dToBezier

#### Compute()
UNCOVERED
What it does: Converts 2D curve into a list of Beziers.
Suggested fixture: Pcurve that is a rational B-spline with internal C0 knots; convert-to-Bezier must produce a list with the right number of segments.

#### Build(Segment)
COVERED by: Gn017, Hea009 (2 fixtures)
Notes: Splits computed Beziers per split values.


### ShapeUpgrade_ConvertCurve3dToBezier

#### Compute()
COVERED by: Gn017, Hea009 (2 fixtures)
Notes: Converts 3D curve into list of Beziers.

#### Build(Segment)
COVERED by: Gn017, Hea009 (2 fixtures)
Notes: Splits computed Beziers per split values.


### ShapeUpgrade_ConvertSurfaceToBezierBasis

#### Compute(Segment)
COVERED by: Gn017, Gn018, Hea009, Wr051 (4 fixtures)
Notes: Converts surface into grid of Bezier-based surfaces.

#### Build(Segment)
UNCOVERED
What it does: Splits Bezier surfaces per split values.
Suggested fixture: B-spline surface with explicit split parameters; Build must honor split list and emit a grid of Bezier patches.


### ShapeUpgrade_SplitSurface

#### Init(S)
COVERED by: Gn017, Gs025, N013, Xp033, Gs049, Tfa051, Tfa052, Hea010, ... (9 fixtures)
Notes: Initializes surface for splitting.

#### SetUSplitValues(values)
UNCOVERED
What it does: Sets U-direction splitting parameters.
Suggested fixture: B-spline surface where caller pre-computes U-knot insertion list and demands deterministic split lines (not auto-detected).

#### SetVSplitValues(values)
UNCOVERED
What it does: Sets V-direction splitting parameters.
Suggested fixture: B-spline surface with caller-specified V-direction split parameters (used when auto-detection misses an interior G0 line).

#### Compute(Segment)
UNCOVERED
What it does: Calculates split points based on correction criteria.
Suggested fixture: Surface with internal C0 ridges that auto-detection should pick up as Compute split points before Build is called.

#### Perform(Segment)
COVERED by: Gn017, Gs025, N013, Xp033, Gs049, Tfa051, Tfa052, Hea010, ... (9 fixtures)
Notes: Computes and builds surface splits.

#### Build(Segment)
COVERED by: Gn017, Gs025, N013, Xp033, Gs049, Tfa051, Tfa052, Hea010, ... (9 fixtures)
Notes: Executes division at predefined U/V values.


### ShapeUpgrade_SplitSurfaceContinuity

#### Compute(Segment)
COVERED by: N031, Gs049, Bo028, Tfa036, Tfa051, Hea009, Hea010 (7 fixtures)
Notes: Splits surface at C0/C1 discontinuities.


### ShapeUpgrade_ShellSewing

#### ApplySewing(shape,tol)
COVERED by: Gs011, Tsh001, Tsh004, Tsh005, Tsh006, Tsh007, Tsh009, Tsh027, ... (115 fixtures)
Notes: Applies sewing algorithm to each shell.


### ShapeUpgrade_UnifySameDomain

#### Initialize(shape,faceMode,edgeMode,bsplMode)
COVERED by: Tsh027, Tsh028, Tfa016, Tfa017, Tfa032, N047, A019, Pmi062, ... (20 fixtures)
Notes: Sets shape and toggles for face/edge unification.

#### AllowInternalEdges(bool)
COVERED by: Tsh001, Tsh002, Tsh003, Tsh004, Tsh005, Tsh006, Tsh007, Tsh008, ... (73 fixtures)
Notes: Permits creation of internal edges during merge.

#### KeepShape(shape)
UNCOVERED
What it does: Designates shape to exclude from merging.
Suggested fixture: Coplanar adjacent faces where one shared edge carries semantic meaning (e.g. a PMI annotation anchor or a named feature) and must NOT be merged away.

#### SetLinearTolerance(tol)
COVERED by: Gs033, M108 (2 fixtures)
Notes: Chord error threshold for merge.

#### SetAngularTolerance(tol)
UNCOVERED
What it does: Max angle permitted for merging shapes.
Suggested fixture: Two near-coplanar faces meeting at a slight angle (e.g. 0.05 deg) where caller wants UnifySameDomain to fold them with a relaxed angular tolerance.

#### Build()
COVERED by: Tfa016, Tfa017, Tfa032, N047, Ls052, Tsh057, Tsh059, Tfa067 (8 fixtures)
Notes: Executes the unification algorithm.


### ShapeAnalysis_Shell

#### LoadShells(shape)
COVERED by: Tsh001, Tsh002, Tsh003, Tsh004, Tsh005, Tsh006, Tsh007, Tsh008, ... (62 fixtures)
Notes: Registers shells from a shape for analysis.

#### CheckOrientedShells(shape,alsofree,checkinternal)
COVERED by: Tsh001, Tsh002, Tsh003, Tsh004, Tsh005, Tsh006, Tsh007, Tsh008, ... (83 fixtures)
Notes: Validates edge usage / orientation rules in shells.

#### HasBadEdges()
COVERED by: Tsh019, Twi005, Tfa028 (3 fixtures)
Notes: Reports edges violating orientation requirements.

#### HasFreeEdges()
COVERED by: Tsh007, Tsh020, Tsh029, Tsh037, Twi027, Twi037, Tfa020, Tfa022, ... (36 fixtures)
Notes: Reports unconnected edges.

#### HasConnectedEdges()
COVERED by: Tsh001, Tsh002, Tsh003, Tsh004, Tsh005, Tsh006, Tsh007, Tsh008, ... (73 fixtures)
Notes: Reports edges shared more than twice.


### ShapeAnalysis_Wire

#### Perform()
COVERED by: Twi009, Twi039, N045, Pf006, Tfa062, Tfa064, Twi055, Twi064, ... (23 fixtures)
Notes: Executes all wire checks in sequence.

#### CheckOrder(isClosed,mode3d)
COVERED by: Twi007, Twi008, Twi028, Twi031, Twi038, Ad045, Tfa064, Twi051, ... (11 fixtures)
Notes: Verifies edges are ordered tail-to-head; flags reorder needed.

#### CheckConnected(prec)
COVERED by: Twi098, Twi053, Twi068, Twi069 (4 fixtures)
Notes: Tests connectivity between adjacent edge pairs.

#### CheckSmall(prec)
COVERED by: Gp007, Gn031, Gs015, Twi013, Twi036, Tfa007, Tfa008, N010, ... (30 fixtures)
Notes: Detects edges shorter than precision.

#### CheckEdgeCurves()
COVERED by: Gp010, Gp015, Gp018, Gp020, Gp021, Gp022, Gp027, Gn030, ... (31 fixtures)
Notes: Validates 2D/3D curve consistency and vertex alignment.

#### CheckDegenerated()
COVERED by: Gp005, Gs006, Gs028, Gs034, Tsh035, Twi021, Twi029, Twi030, ... (26 fixtures)
Notes: Identifies incorrect degenerated edges.

#### CheckClosed(prec)
COVERED by: Gp026, Twi003, Twi021, Twi034, Twi036, Twi039, Tfa022, N002, ... (26 fixtures)
Notes: Validates wire closure.

#### CheckSelfIntersection()
COVERED by: Gp008, Gs009, Twi001, Twi002, Twi003, Twi004, Twi005, Twi006, ... (96 fixtures)
Notes: Detects self-intersecting edges and edge pair intersections.

#### CheckSelfIntersectingEdge(num)
COVERED by: Gs009, Pf024, Twi049, Twi051, Twi076 (5 fixtures)
Notes: Tests single edge for self-intersection.

#### CheckIntersectingEdges(num)
COVERED by: Gs009, Gs030, N013, N014 (4 fixtures)
Notes: Finds intersections between adjacent edges.

#### CheckLacking()
COVERED by: Gp001, Gp028, Tsh029, Twi020, Twi021, Twi029, Twi034, Twi036, ... (29 fixtures)
Notes: Detects missing edges from 2D gaps.

#### CheckGaps3d()
COVERED by: Gp020, Twi003, Gb004, Xp021, Twi051, Twi053, Twi065, Twi068, ... (11 fixtures)
Notes: Validates 3D continuity across edge transitions.

#### CheckGaps2d()
COVERED by: Gp018, Gp020, Gp026, Twi065, Twi067, Twi069, Twi073 (7 fixtures)
Notes: Validates 2D continuity across edge transitions.

#### CheckCurveGaps()
UNCOVERED
What it does: Tests alignment between 3D curves and surface-generated points.
Suggested fixture: Wire where edge's 3D curve and the (pcurve, surface) reconstruction disagree by more than tolerance even though same-parameter passes.

#### CheckOuterBound(APIMake)
COVERED by: Gp005, Gp026, Gp028, Gs002, Gs006, Gs009, Gs012, Gs031, ... (99 fixtures)
Notes: Determines if wire is outer boundary on face.

#### CheckNotchedEdges()
COVERED by: Twi011, Twi054, Twi074, Twi077, Hea003, Hea005 (6 fixtures)
Notes: Detects notches in edge sequence.

#### CheckSmallArea(wire)
COVERED by: Tsh028, Twi024, Twi044, Twi045, Tfa037 (5 fixtures)
Notes: Validates wire has sufficient parametric area.

#### CheckShapeConnect(shape,prec)
UNCOVERED
What it does: Tests how an edge/wire connects to current wire.
Suggested fixture: Standalone edge or wire candidate that should be appended to an existing wire; need a probe-style check distinct from full connectivity scan.

#### CheckLoop(mapLoopVertices,...)
COVERED by: Gs009, Twi009, Twi010, Twi041, Tfa022, Pmi119, Ad050, Twi093, ... (20 fixtures)
Notes: Identifies loop vertices with multiple edge connections.

#### CheckSeam(num)
COVERED by: Gp011, Gp012, Gp013, Gp018, Gp026, Gp027, Gp028, Gn019, ... (40 fixtures)
Notes: Validates seam pcurve orientation correctness.

#### CheckTail(...)
COVERED by: Twi077 (1 fixtures)
Notes: Analyzes notch tail geometry between edge pairs.


### ShapeAnalysis_Edge

#### HasCurve3d(edge)
COVERED by: Gp007, Gp010, Gp021, Gn030, Gs018, N004, N010, Os012, ... (14 fixtures)
Notes: Tests edge has 3D curve.

#### HasPCurve(edge,face)
COVERED by: Gp001, Gp002, Gp005, Gp008, Gp010, Gp012, Gp014, Gp016, ... (41 fixtures)
Notes: Tests pcurve exists on face.

#### IsSeam(edge,face)
COVERED by: Gp011, Gp012, Gp013, Gp018, Gp026, Gp027, Gp028, Gn019, ... (40 fixtures)
Notes: Identifies seam edge (dual pcurves).

#### GetEndTangent2d(edge,face,atEnd,pos,tang,dparam)
COVERED by: N031, N042, Gb003, Bo025 (4 fixtures)
Notes: Computes tangent at curve endpoint.

#### CheckVerticesWithCurve3d(edge,preci,vtx)
COVERED by: Twi036, Twi046, Gp038 (3 fixtures)
Notes: Validates vertex alignment with 3D curve.

#### CheckVerticesWithPCurve(edge,face,preci,vtx)
COVERED by: Gp020, Twi060, Twi062, Gp038 (4 fixtures)
Notes: Validates vertex alignment with pcurve.

#### CheckVertexTolerance(edge,face,...)
COVERED by: Gp002, Gp016, Gn031, Gs015, Tsh005, Tsh042, Twi003, Twi030, ... (44 fixtures)
Notes: Determines required vertex tolerance adjustments.

#### CheckCurve3dWithPCurve(edge,face)
COVERED by: Gs018, Tsh033, N005, Twi052, Twi065, Twi071 (6 fixtures)
Notes: Validates mutual orientation between 3D and pcurves.

#### CheckSameParameter(edge,maxdev,NbControl)
COVERED by: Gp022, Gp027, Twi044, N004, N005, N006, Ad099, Sw009, ... (16 fixtures)
Notes: Assesses SameParameter property.

#### CheckPCurveRange(first,last,pc)
COVERED by: Gp007, Gp015, Gp023, Gp028, Twi082, Gp037, Gp039 (7 fixtures)
Notes: Validates parametric curve range feasibility.

#### CheckOverlapping(edge1,edge2,tol,domainDist)
COVERED by: Gs028, Twi013, Twi030, Twi031, Twi033, Twi037, Tfa001, Tfa002, ... (78 fixtures)
Notes: Detects overlapping edges.


### ShapeAnalysis_FreeBounds

#### ConnectEdgesToWires(edges,toler,shared)
COVERED by: Twi027, P017, Twi047 (3 fixtures)
Notes: Connects edges into wires.

#### ConnectWiresToWires(iwires,toler,shared)
COVERED by: M077, Twi053 (2 fixtures)
Notes: Connects wires into longer wires.

#### SplitWires(wires,toler,shared,closed,open)
COVERED by: Gs009, Twi010, Twi044, Twi090, Twi095, Twi049, Twi050, Twi076, ... (10 fixtures)
Notes: Extracts closed sub-wires from open wires.

#### DispatchWires(wires,closed,open)
COVERED by: Twi034 (1 fixtures)
Notes: Dispatches wires into closed/open compounds.


### ShapeAnalysis_FreeBoundsProperties

#### Perform()
COVERED by: Tsh007, Tsh020, Tsh029, Tsh037, Twi027, Twi037, Tfa001, Tfa002, ... (95 fixtures)
Notes: Builds/analyzes free bounds (area, perimeter, notches).

#### DispatchBounds()
COVERED by: Twi034, Twi040, Tfa005, Tfa022, N040, Os009, Os010, Os011, ... (19 fixtures)
Notes: Categorizes free bounds into closed/open groups.

#### CheckContours(prec)
UNCOVERED
What it does: Validates contour properties.
Suggested fixture: Compound with multiple free-bound contours each needing per-contour area/perimeter/width validation against precision.

#### CheckNotches(prec)
COVERED by: Twi011, Twi054, Twi074, Twi077, Hea003, Hea005 (6 fixtures)
Notes: Detects narrow V-shaped indentations.

#### FillProperties(fbData,prec)
COVERED by: Gs015, Hea003 (2 fixtures)
Notes: Fills area/perimeter/width stats for contour.


### ShapeAnalysis_CheckSmallFace

#### IsSpotFace(F,spot,spotol,tol)
COVERED by: Gp023, Gs014, Twi028, Twi036, Tfa001, Tfa005, Tfa006, Tfa034, ... (22 fixtures)
Notes: Detects spot face (face collapsed to point).

#### CheckSpotFace(F,tol)
COVERED by: Gs014, Tfa006, Tfa040, Tfa041, Tfa043, Tfa046 (6 fixtures)
Notes: Records spot-face diagnostic.

#### IsStripSupport(F,tol)
COVERED by: Gs014, Gs015, Tsh028, Tfa007, Tfa008, Tb014, A019, Ad098, ... (23 fixtures)
Notes: Identifies strip surface in U/V direction.

#### CheckStripEdges(E1,E2,tol,dmax)
COVERED by: Tfa007, Twi057 (2 fixtures)
Notes: Validates edges form a strip within tolerance.

#### FindStripEdges(F,E1,E2,tol,dmax)
UNCOVERED
What it does: Locates strip-forming edges in face.
Suggested fixture: Sliver face with three or more edges where the two great strip edges are not at the obvious topological positions; algorithm must locate them.

#### CheckSingleStrip(F,E1,E2,tol)
COVERED by: Gs014, Tfa007, Xp039, Bo001, Tfa061, Twi057, Tfa040, Tfa042, ... (10 fixtures)
Notes: Validates face has two coincident great edges.

#### CheckStripFace(F,E1,E2,tol)
COVERED by: Gs014, Tfa007, Xp039, Bo001, Tfa061, Twi057, Tfa040, Tfa042, ... (10 fixtures)
Notes: Analyzes face as strip with direction/edge lists.

#### CheckSplittingVertices(F,...)
COVERED by: Gs034, Tfa010 (2 fixtures)
Notes: Detects vertices splitting faces through confusion.

#### CheckPin(F,whatrow,sence)
COVERED by: Gs014, Gs031, Gs034, Twi010, Tfa005, Tfa008, Tfa024, Tfa032, ... (18 fixtures)
Notes: Identifies pin singularities.

#### CheckTwisted(F,paramu,paramv)
COVERED by: Gs034, Fi001, M164 (3 fixtures)
Notes: Determines face exhibits twisting.

#### CheckPinFace(F,...)
COVERED by: Gs014, Gs031, Gs034, Twi010, Tfa008, Tfa024, Tfa032, A024, ... (17 fixtures)
Notes: Evaluates pin characteristics on faces.

#### CheckPinEdges(e1,e2,c1,c2,toler)
COVERED by: Twi033, N026, Fi001, Fi003, Fi004, Fi005, Twi058, Tfa050, ... (9 fixtures)
Notes: Analyzes edge pairs for pin-related deformations.


### ShapeAnalysis_Curve

#### Project(curve,P,preci,proj,param,...)
COVERED by: Os021, Gp037 (2 fixtures)
Notes: Projects a point onto a 3D curve.

#### NextProject(...)
UNCOVERED
What it does: Newton-based point projection from prior parameter.
Suggested fixture: Long parametric curve where iterative projection along the curve needs the prior parameter as a seed (e.g. discretising a wavy edge to a polyline).

#### ValidateRange(curve,first,last,preci)
COVERED by: Gp007, Gp015, Gp023, Gs029, Tb006, Twi082, Gp037, Gp039 (8 fixtures)
Notes: Verifies/corrects parameter bounds for edge creation.

#### FillBndBox(curve,first,last,nbPnt,exact,box)
UNCOVERED
What it does: Computes bounding box on 2D curve segment.
Suggested fixture: 2D curve whose tight bounding box is needed for overlap-rejection in wire self-intersection (analytic Bnd_Box2d construction).

#### SelectForwardSeam(c1,c2)
UNCOVERED
What it does: Selects pcurve for forward seam edge handling.
Suggested fixture: Seam edge on a closed surface with two valid pcurves where the FORWARD/REVERSED association must be deterministically chosen.

#### IsPlanar(points/curve,normal,tol)
COVERED by: Gp016, Pmi136 (2 fixtures)
Notes: Tests planarity.

#### GetSamplePoints(curve,first,last,seq)
COVERED by: Gn007, Gn019, Gs038, N004, N042, N048 (6 fixtures)
Notes: Generates linearization sample points.

#### IsClosed(curve,prec)
COVERED by: Gp008, Gp013, Gn019, Twi017, Twi019, N010, Gb003, Xp002, ... (12 fixtures)
Notes: Tests curve closure within precision.

#### IsPeriodic(curve)
COVERED by: Gp013, Gp018, Gn031, Gs019, Gs028, Twi017, Twi022, Twi097, ... (11 fixtures)
Notes: Checks curve periodicity.


### ShapeAnalysis_Surface

#### HasSingularities(preci)
COVERED by: Gs006, Tsh035, Twi021, Tfa005, Xp032, Hea016, Gs056 (7 fixtures)
Notes: Checks for surface singularities within precision.

#### Singularity(num,...)
COVERED by: Tfa005, Tb012 (2 fixtures)
Notes: Retrieves characteristics of a singularity.

#### IsDegenerated(P3d,preci)
COVERED by: Twi021 (1 fixtures)
Notes: Detects if 3D point lies near degenerated boundary.

#### ProjectDegenerated(P3d,preci,neighbour,result)
COVERED by: Pmi071, Pmi121 (2 fixtures)
Notes: Projects onto singularity using neighbor info.

#### IsUClosed(preci)
COVERED by: Gn033, Ls046, Tfa038 (3 fixtures)
Notes: Tests spatial closure in U-direction.

#### IsVClosed(preci)
UNCOVERED
What it does: Tests spatial closure in V-direction.
Suggested fixture: Surface that is V-closed but not declared periodic (e.g. swept along a closed loop) -- check needed to add an implicit seam edge.

#### ValueOfUV(P3D,preci)
COVERED by: Gp018, Gp020, Twi036, Twi049, Tfa045, Hea008 (6 fixtures)
Notes: Computes parametric coordinates of 3D point projection.

#### NextValueOfUV(prev,P3D,preci,maxpreci)
UNCOVERED
What it does: Optimizes projection from previous solution.
Suggested fixture: Sequence of points to project sequentially onto a surface (e.g. discretised 3D curve) where prior-parameter seeding avoids ambiguous projections on periodic surfaces.

#### UVFromIso(P3D,preci,U,V)
COVERED by: Pmi071 (1 fixtures)
Notes: Refines UV via iterative iso-line projection.

#### Bounds(uf,ul,vf,vl)
UNCOVERED
What it does: Retrieves cached parametric bounds.
Suggested fixture: Trimmed B-spline surface whose declared UV bounds disagree with the surface's natural extent (clip during analysis).

#### UIso(U)/VIso(V)
COVERED by: Gs049 (1 fixtures)
Notes: Returns iso-curve in U/V direction.


### ShapeAnalysis_ShapeContents

#### Perform(shape)
COVERED by: M028, Hea006 (2 fixtures)
Notes: Counts sub-shapes by type/flags.


### ShapeAnalysis_ShapeTolerance

#### Tolerance(shape,mode,type)
COVERED by: N030, N039, Twi061, Tfa048 (4 fixtures)
Notes: Computes tolerance from sub-shapes.

#### OverTolerance(shape,value,type)
COVERED by: Gn031, Tsh004, Tsh005, N001, N008, N032, N040, Tb020, ... (14 fixtures)
Notes: Finds sub-shapes exceeding tolerance threshold.

#### InTolerance(shape,vmin,vmax,type)
COVERED by: N008, Tb005, Tb020 (3 fixtures)
Notes: Finds sub-shapes within tolerance range.

#### GlobalTolerance(mode)
COVERED by: Twi043, N016, Tb016, Tfa065 (4 fixtures)
Notes: Returns accumulated tolerance.


### ShapeAnalysis_TransferParametersProj

#### Perform(params,To2d)
UNCOVERED
What it does: Transfers parameter list between 3D curve and pcurve.
Suggested fixture: Edge with sequence of 3D-curve parameters (e.g. vertices of an intersection chain) that must be projected to 2D pcurve parameters during a split.

#### TransferRange(newEdge,prevPar,currPar,Is2d)
UNCOVERED
What it does: Recomputes curve range based on new edge geometry.
Suggested fixture: Split operation that produces a new edge whose internal parameter range must be recomputed from the parent edge's [prevPar, currPar].

#### CopyNMVertex(vert,toEdge,fromEdge)
COVERED by: Tsh021, Xp013, Twi087 (3 fixtures)
Notes: Duplicates non-manifold vertex with updated edges.


### ShapeAnalysis_WireOrder

#### Perform(closed)
COVERED by: Twi007, Twi008, Twi028, Twi031, Twi038, Ad045, Tfa064, Twi051, ... (11 fixtures)
Notes: Computes optimal ordering of edge couples.

#### SetChains(gap)
COVERED by: Twi004, Tb016, Bo022, Tsh046, Twi087 (5 fixtures)
Notes: Identifies sequential edge chains within tolerance.

#### SetCouples(gap)
UNCOVERED
What it does: Finds edge pairs meeting proximity criteria.
Suggested fixture: Edge soup (e.g. exploded wire) where caller wants pairwise tail/head couples within a gap tolerance for downstream wire assembly.


---

## ShapeProcess + ShapeCustom + ShapeExtend + BRepLib

Audit of the OCCT healing pipeline entry points (BRepLib, BRepBuilderAPI_Sewing,
ShapeProcess_*, ShapeCustom_*, ShapeExtend_*) against the STEP-defect catalog at
`/Users/zellyn/gh/dodgy-step-files/STEP_PROBLEM_CATALOG.{md,json}` (1282 entries).

Searches matched fixture title / description / expected_kernel_behavior / notes /
reproducer / occ_behavior_note text via case-insensitive regex over operation
names plus close synonyms. A fixture "covers" an operation if at least one of
those regexes hit. Counts are dedup'd per fixture per operation.

Total operations enumerated: 87
Covered by >=1 fixture: 47
UNCOVERED: 40

### BRepBuilderAPI_Sewing

#### Perform()
COVERED by: Pf015, Xp028, Gp040, Gs011, Sw001-Sw008, ... (47 fixtures)

#### Load() / Add() / SewedShape()
COVERED indirectly (every sewing fixture exercises Load+Add+Perform+SewedShape).
Treated as same surface area as Perform().

#### SetTolerance() / Tolerance()
COVERED by: Gs011, Sw002, Sw007, Tsh004, Tsh005, Tfa020, M023, M053 (8 fixtures)

#### SetMinTolerance() / MinTolerance()
UNCOVERED
What it does: Floors the dynamic per-edge tolerance Sewing computes so that
geometry whose true gap is below this value still gets stitched. Critical for
files where edge tolerances are physically meaningless (e.g. clamped to
Precision::Confusion()).
Suggested fixture: two adjacent faces whose edge tolerances are 1e-9 but whose
shared boundary has a 1e-4 gap; require `SetMinTolerance(1e-4)` to bridge.

#### SetMaxTolerance() / MaxTolerance()
UNCOVERED
What it does: Caps the upper end of the tolerance ladder so Sewing refuses to
fuse pairs of edges whose nearest distance exceeds this value -- prevents
catastrophic over-stitching of clearly-distinct boundaries.
Suggested fixture: two parallel faces ~2 mm apart with default sewing
tolerance 1.0; `SetMaxTolerance(0.5)` should keep them as free boundaries.

#### SetFaceMode() / FaceMode()
COVERED by: Tsh003, Tsh004, Tsh037, Tfa061, Pmi117 (5 fixtures)

#### SetFloatingEdgesMode() / FloatingEdgesMode()
COVERED by: Twi027, Twi047 (2 fixtures)

#### SetLocalTolerancesMode() / LocalTolerancesMode()
COVERED by: Twi043, N016, Tb016 (3 fixtures)

#### SetNonManifoldMode() / NonManifoldMode()
COVERED by: Xp003, Xp013, Xp037, Lh031, Bo006, Sw001, Tsh001, Tsh005, Tsh019-22, ... (35 fixtures)

#### SetSameParameterMode() / SameParameterMode()
COVERED by: Sw009 (1 fixture)

#### NbFreeEdges() / FreeEdge(i)
COVERED by: Tsh044, Twi075, Hea006, Os022 (4 fixtures)

#### NbMultipleEdges() / MultipleEdge(i)
COVERED by: Xp003, Gp014, Bo006, Tsh019, Tsh061, Hea017 (6 fixtures)

#### NbContigousEdges() / ContigousEdge(i) / ContigousEdgeCouple()
COVERED by: Pf013, Le052, Gs007, M173, Os022 (5 fixtures)

#### IsSectionBound() / SectionToBoundary()
UNCOVERED
What it does: Reports whether a sub-segment of an input edge ended up bound to
a free boundary section (i.e., only partially stitched -- a common mid-edge
split).
Suggested fixture: T-junction where a long edge of face A meets the midpoint
of an edge of face B; Sewing must split B's edge and only one half of it ends
up contiguous.

#### NbDegeneratedShapes() / DegeneratedShape(i) / IsDegenerated()
COVERED by: Pf027, Xp032, Le023, Gp005, Gp022, Gp036, Gn019, Gn037, ... (86 fixtures)

#### IsModified() / Modified() / IsModifiedSubShape() / ModifiedSubShape()
UNCOVERED (as a *queryable* mapping; sewing's transformation itself is exercised)
What it does: Lets callers map any input edge/face to the corresponding sewn
output -- the "did this edge survive?" lookup used by downstream context
restoration in STEP color/PMI re-binding.
Suggested fixture: STEP file where PMI dimension references an edge of a face
that Sewing modifies; the catalog should require the kernel re-bind PMI to
ModifiedSubShape(edge).

#### NbDeletedFaces() / DeletedFace(i)
UNCOVERED
What it does: Reports faces dropped by Sewing for being smaller than the
working tolerance.
Suggested fixture: assembly containing a 1e-9 sliver triangle face shared with
larger faces; sewing at tolerance 1e-6 should report it in DeletedFace() and
not leak it into the output shell.

#### WhichFace(edge)
UNCOVERED
What it does: Given an output edge, return the face that contains it after
sewing. Useful for diagnosing where a "free edge" came from.
Suggested fixture: pathology where a face boundary survives as free edge --
the catalog should require the kernel report which face it belonged to.

#### Dump()
UNCOVERED (diagnostic only; deliberately not exercised by fixtures)

### BRepLib

#### SameRange() / CheckSameRange()
PARTIAL: SameRange() COVERED by Le054, Twi082, Twi085, Twi090 (4 fixtures).
CheckSameRange() (the validating variant) UNCOVERED.
What CheckSameRange does: Validates that 3D curve and all pcurves agree on
[first,last] parameter values before processing; root-cause detector for
"SameParameter failed" cascades.
Suggested fixture: edge whose pcurve range is [0, 6.28] but 3D curve range
is [0, 1] -- CheckSameRange must flag it before SameParameter is attempted.

#### BuildCurve3d()
COVERED by: Twi046, Twi052, Twi088, Os012 (4 fixtures)

#### BuildCurves3d()
UNCOVERED (the batch convenience wrapper).
What it does: Runs BuildCurve3d() across all edges of a shape; common entry
point invoked by STEP readers when 3D curves are absent.
Suggested fixture: AP203 face_surface assembly where every edge has only a
pcurve; the kernel must call BuildCurves3d() to fabricate 3D curves before
sewing.

#### BuildPCurveForEdgeOnPlane()
COVERED by: Gp002, Gp010, Gp016, Gp035, Gp036, Gp037, Gp039, Gn030, ... (19 fixtures)

#### BuildPCurveForEdgesOnPlane() (batch variant)
COVERED by: Gp036 (1 fixture; thin)

#### UpdateEdgeTol() (single-edge, pipe-radius variant)
UNCOVERED
What it does: Adjusts a single edge tolerance based on the radius of an
adjacent cylindrical/pipe surface -- specifically handles the case where the
pcurve sits on a cylinder of small radius and the 3D deviation is amplified
by curvature.
Suggested fixture: edge on a 0.1 mm radius cylinder whose pcurve is straight
but whose 3D curve is a tight helix segment; kernel should bump edge
tolerance to accommodate the curvature error.

#### UpdateEdgeTolerance() (whole-shape variant)
UNCOVERED
What it does: Walks every edge of a shape and tightens or relaxes its
tolerance based on observed pcurve-vs-3D-curve deviation.
Suggested fixture: STEP file produced by a tool that emits edge.tolerance =
1.0 uniformly regardless of true geometric error; kernel should recompute.

#### SameParameter()
COVERED by: Ad099, Gp022, Gp027, Gp035, Sw009, Twi047, Twi048, Twi052, ... (15 fixtures)

#### UpdateTolerances() (face/edge/vertex synchronization)
UNCOVERED
What it does: Propagates tolerances upward (vertex >= edge >= face) so the
nesting invariant the rest of the kernel assumes is restored.
Suggested fixture: face with tol=1e-7, edge on it with tol=1e-5, vertex with
tol=1e-3 -- a violation of the OCCT containment rule that must be healed.

#### UpdateInnerTolerances()
COVERED by: Bo030 (1 fixture; thin -- one of the SameParameter-tolerance entries)

#### OrientClosedSolid()
COVERED by: Wr036, Wr046, Gs001, Bo024, Ps001-003, Tsh008-10, Tsh015, Tsh018, ... (31 fixtures)

#### ContinuityOfFaces()
COVERED by: Bo028, Tsh027 (2 fixtures)

#### EncodeRegularity()
UNCOVERED
What it does: Tags each edge of a shape with its G0/G1/G2 regularity across
the two faces meeting at it; downstream fillet/draft/boolean operations key
off this tag.
Suggested fixture: edge between two tangent faces (radius blend) where the
producer set regularity to "GeomAbs_C0" instead of "GeomAbs_G1"; importer
must recompute via EncodeRegularity to keep boolean operations stable.

#### SortFaces() / ReverseSortFaces()
UNCOVERED (both)
What it does: Reorders faces by geometric type (plane, cylinder, cone, sphere,
torus, surface_of_revolution, surface_of_extrusion, bspline, other) for
deterministic processing.
Suggested fixture: shape whose face ordering after STEP-import is type-mixed
in a way that triggers a known boolean-operation determinism bug; require
SortFaces to be applied first.

#### EnsureNormalConsistency() (tessellation-side)
UNCOVERED
What it does: Re-emits consistent per-vertex normals across smooth edges in
a Poly_Triangulation attached to faces.
Suggested fixture: STEP AP242 with `tessellated_face` carrying inconsistent
normals across a smooth shared edge (normal flip at seam); kernel must
EnsureNormalConsistency before display.

#### UpdateDeflection()
COVERED by: Pf027, M070 (2 fixtures)

#### BoundingVertex()
COVERED by: N010 (1 fixture; thin)

#### FindValidRange()
UNCOVERED
What it does: Locates segments of an edge's 3D curve not covered by any
vertex pair -- detects "edge with gap" pathology.
Suggested fixture: edge where the two vertex parameters define [0, 0.4]
[0.6, 1.0] (gap in the middle); FindValidRange must report (0.4, 0.6) as
uncovered.

#### ExtendFace()
UNCOVERED
What it does: Enlarges a face's parametric domain (used for boolean-op
clearance and for healing tight trims).
Suggested fixture: face whose trim sits exactly on the surface's natural
boundary causing classifier instability; require ExtendFace to add a
small parametric margin.

### ShapeProcess_OperLibrary

#### Init() (registry bootstrap)
UNCOVERED
What it does: Registers the named operator library (DirectFaces, FixShape,
SameParameter, BSplineRestriction, etc.) that ShapeProcess flows consume by
name from .resource files.
Suggested fixture: STEP file requiring a non-default healing sequence
(e.g. enable DirectFaces=true via ShapeProcess resource); validates that the
kernel honors resource-file routing.

#### ApplyModifier()
UNCOVERED
What it does: Applies a BRepTools_Modification subclass to a shape while
respecting shared-subshape identity in compounds -- the engine behind every
ShapeCustom modifier.
Suggested fixture: compound with two assembly instances sharing a face;
applying a TrsfModification must update the face once and re-share, not
duplicate.

### ShapeProcess_ShapeContext

#### Init(shape)
UNCOVERED

#### SetResult() / Result()
UNCOVERED (state plumbing, but exposed publicly)

#### Map() (replacement map query)
UNCOVERED

#### RecordModification() (4 overloads)
UNCOVERED
What it does: Records before/after shape mappings that downstream STEP-color,
PMI, and assembly-link restoration depend on after healing.
Suggested fixture: STEP file with attached colors / layers / PMI on faces
that healing modifies; assert that color/PMI follow via the recorded map.

#### SetDetalisation()
UNCOVERED
What it does: Controls how deeply the context tracks shape replacements
(vertex / edge / face / shell / solid).
Suggested fixture: file where vertex-level tracking is required to preserve
welded-vertex identity but face-level is the default; require explicit
SetDetalisation(TopAbs_VERTEX).

#### AddMessage() / Messages()
UNCOVERED
What it does: Per-shape diagnostic log keyed by the healed sub-shape.
Suggested fixture: assembly where multiple faces independently fail healing;
require diagnostics attached to each offending face individually.

#### SetNonManifold() / IsNonManifold()
UNCOVERED (as ShapeContext flag, distinct from Sewing's flag)

#### GetContinuity() / ContinuityVal()
UNCOVERED
What it does: Reads target G0/G1/G2 continuity from a resource file for
downstream BSplineRestriction/ContinuityOfFaces.
Suggested fixture: STEP file whose healing sequence relies on a non-default
continuity target (e.g. G2 enforcement) supplied via resource file.

#### PrintStatistics()
UNCOVERED (purely diagnostic; intentionally low priority)

### ShapeProcess_UOperator

#### Perform() / construct-from-function-pointer
COVERED by: Hea013 (1 fixture; thin)

### ShapeCustom_BSplineRestriction

#### Perform() (overall surface/curve restriction pass)
COVERED by: Gn026 (1 fixture; very thin given the size of this class)

#### NewSurface() / NewCurve() / NewCurve2d() / NewPoint() / NewParameter()
UNCOVERED (all five Modifier hooks).
Suggested fixture: a face whose B-spline surface degree exceeds the kernel
limit and whose pcurves must be re-fit together with the surface; the
catalog should explicitly require all five hooks (the existing Gn026 hits
only the umbrella term).

#### SetTol3d() / SetTol2d()
UNCOVERED
What it does: Sets the geometric tolerance used by the approximator when
re-fitting curves and surfaces.
Suggested fixture: high-degree NURBS surface with a strict 1e-6 fitting
target; ensure SetTol3d propagation produces a valid result rather than
silently widening tolerance.

#### SetContinuity3d() / SetContinuity2d()
UNCOVERED
What it does: Requests minimum continuity (C0/C1/C2) of the restricted
output.
Suggested fixture: B-spline with internal C0 knots that must be raised to
C1 by restriction; require SetContinuity3d(GeomAbs_C1).

#### SetMaxDegree()
UNCOVERED
What it does: Caps approximation degree (typical limits: 9 or 25).
Suggested fixture: STEP B-spline of degree 25 that downstream OCCT
operations refuse; require restriction to degree 9.

#### SetMaxNbSegments()
UNCOVERED
What it does: Caps span count to keep B-spline complexity bounded.
Suggested fixture: B-spline with 50000 spans (knot-vector pathology) that
must be down-sampled.

#### SetPriority()
UNCOVERED (degree-vs-segment trade-off knob)

#### SetConvRational()
UNCOVERED
What it does: Decides whether weighted (rational) B-splines are converted
to polynomial form during restriction.
Suggested fixture: rational NURBS whose weights are all 1.0+/-1e-15 (effectively
non-rational); require ConvRational=true to drop the rationality.

#### Curve3dError() / Curve2dError() / SurfaceError() / MaxErrors() / NbOfSpan()
UNCOVERED
What it does: Per-pass error and span statistics -- needed by callers to
decide whether to retry with looser tolerances.
Suggested fixture: surface that fits only to 1e-3 when caller wanted 1e-6;
require SurfaceError() reporting so caller can downgrade gracefully.

### ShapeCustom_ConvertToBSpline

#### Perform() (overall)
COVERED by: Gn013 (1 fixture)

#### SetExtrusionMode()
COVERED by: N030 (1 fixture)

#### SetRevolutionMode()
UNCOVERED
What it does: Toggles conversion of surface_of_revolution into B-spline form
during DataExchange/STEP import.
Suggested fixture: surface_of_revolution whose generatrix is a NURBS with
degree-4 knot vector; downstream boolean ops require B-spline form.

#### SetOffsetMode()
COVERED by: Gn024, Gs010 (2 fixtures)

#### SetPlaneMode()
UNCOVERED
What it does: Forces planar faces to be re-emitted as B-spline planes
(rare healing knob used to bypass plane-vs-bspline boolean bugs).
Suggested fixture: planar face involved in a known boolean-op divergence;
the catalog should require explicit PlaneMode toggling.

#### NewSurface() / NewCurve() / NewCurve2d() / NewPoint() / NewParameter() / Continuity()
UNCOVERED (Modifier hooks; same shape as above)

### ShapeCustom_ConvertToRevolution

#### Perform() (whole-class)
UNCOVERED
What it does: Recognizes B-spline surfaces that are actually surfaces of
revolution and rewrites them analytically -- inverse of ConvertToBSpline.
Suggested fixture: STEP from a producer that flattened cylinders to NURBS;
require recognition + analytical recovery for downstream boolean stability.

#### NewSurface() / NewCurve() / NewCurve2d() / NewPoint() / NewParameter() / Continuity()
UNCOVERED (Modifier hooks; same shape as above)

### ShapeCustom_Curve

#### ConvertToPeriodic()
COVERED by: Gp013, Gs005, Gs038 (3 fixtures)

#### Init()
UNCOVERED (state plumbing; low priority)

### ShapeCustom_Surface

#### ConvertToAnalytical()
COVERED by: Gp013, N030, Pmi001, M162 (4 fixtures)

#### ConvertToPeriodic()
COVERED by: Gp013, Gs005, Gs038 (3 fixtures)

#### Gap()
UNCOVERED
What it does: Reports the maximum deviation between the original B-spline
surface and its analytical replacement -- the kernel's "should I commit
this conversion?" knob.
Suggested fixture: B-spline that approximates a cylinder to 1e-4 only;
require Gap()-driven rejection of the conversion when caller demanded 1e-6.

### ShapeCustom_RestrictionParameters

#### GMaxDegree() / GMaxSeg()
UNCOVERED (delegated to BSplineRestriction.SetMaxDegree / SetMaxNbSegments)

#### ConvertPlane()
UNCOVERED
What it does: Per-surface-kind on/off switch for whether planes get
B-spline-promoted by BSplineRestriction.
Suggested fixture: file requiring planes left untouched while other surfaces
are restricted.

#### ConvertBezierSurf()
UNCOVERED
What it does: Per-surface-kind on/off switch for Bezier surfaces.
Suggested fixture: AP203 Bezier surface that must be promoted to B-spline
before sewing.

#### ConvertRevolutionSurf() / ConvertExtrusionSurf() / ConvertOffsetSurf()
UNCOVERED (per-kind switches; the ConvertToBSpline modes above are the
runtime hooks but the resource-driven RestrictionParameters knobs are
distinct).

#### ConvertCylindricalSurf()
COVERED by: Gn013, N030 (2 fixtures)

#### ConvertConicalSurf() / ConvertToroidalSurf() / ConvertSphericalSurf()
COVERED by: N030 (one shared fixture each; thin)

#### SegmentSurfaceMode()
UNCOVERED
What it does: When true, BSplineRestriction approximates only the trimmed
region of a surface (within face boundary) rather than the full natural
domain. Critical for trimmed surfaces with huge natural domains.
Suggested fixture: NURBS surface with U range [0, 1000] but the face uses
only [0.5, 0.501]; with SegmentSurfaceMode=false the restriction explodes;
with =true it converges.

#### ConvertCurve3d() / ConvertCurve2d()
UNCOVERED (per-curve-kind switches)

#### ConvertOffsetCurv3d() / ConvertOffsetCurv2d()
UNCOVERED
What it does: Toggles conversion of offset curves (Geom_OffsetCurve and
Geom2d_OffsetCurve) to B-spline. Common after STEP import of
`offset_curve_3d` entities that some downstream ops mishandle.
Suggested fixture: edge whose 3D representation is an offset_curve over a
non-trivial basis; require kernel to flatten via this knob.

### ShapeCustom_TrsfModification

#### NewSurface() / NewCurve() / NewCurve2d() / NewPoint() / NewParameter()
UNCOVERED
What it does: Applies a gp_Trsf to all geometry of a shape and scales
tolerances by the transformation's scale factor.
Suggested fixture: assembly with a 1000x scale transform on a sub-component
whose edge tolerances are 1e-3; after TrsfModification at the leaf, edge
tolerances must become 1.0, not stay at 1e-3 (a classic STEP unit-conversion
trap).

### ShapeExtend_CompositeSurface

#### Init() / Patch / NbUPatches / NbVPatches / Patches / Bounds
COVERED by: Gp019, Gs037, Gs041, Twi055, Tfa036, Tfa053 (6 fixtures matched
the "composite surface" / patch grid concept generally; treat as one
operation surface area)

#### CheckConnectivity()
UNCOVERED
What it does: Validates patch-to-patch geometric continuity in a composite
surface (gaps between patches that should share a joint).
Suggested fixture: STEP composite surface where one patch's eastern edge
is 1e-3 off from the neighbor patch's western edge; require
CheckConnectivity reporting a gap and the kernel either healing or rejecting.

#### LocateUParameter / LocateVParameter / LocateUVPoint
UNCOVERED (lookup helpers)

#### SetUJointValues / SetVJointValues / SetUFirstValue / SetVFirstValue
UNCOVERED
What it does: Reparametrize the composite surface to specific joint values
(needed when downstream consumer expects unit [0,1] parametrization).
Suggested fixture: composite surface emitted with joint values in mm but
consumed by a tool assuming [0,1]; require kernel to renormalize via
SetUJointValues.

#### GlobalToLocalTransformation()
UNCOVERED

#### ComputeJointValues()
UNCOVERED

#### Transform()
UNCOVERED (composite-surface variant of global transform; falls under unit-conversion class)

### ShapeExtend_ComplexCurve

#### NbCurves() / Curve(i)
UNCOVERED
What it does: Wraps a sequence of curves as a single "complex curve" --
useful for representing STEP composite_curve where each segment is a
separate Geom_Curve.
Suggested fixture: STEP composite_curve with 3 segments (line, arc, bspline);
kernel must expose them via NbCurves/Curve rather than collapsing them.

#### LocateParameter() / LocalToGlobal()
UNCOVERED (lookup)

#### CheckConnectivity()
UNCOVERED
What it does: Verifies segment-to-segment endpoint agreement in a complex
curve.
Suggested fixture: STEP composite_curve where segment i ends at (0,0,0) but
segment i+1 starts at (0,0,1e-3) -- gap that the kernel must report.

#### Transform()
UNCOVERED (segment-wise transform application)

### ShapeExtend_WireData

#### Init() (wire load + reorder)
COVERED by: Twi008 (1 fixture; thin)

#### Add() / AddOriented() (single edge)
UNCOVERED
What it does: Inserts an edge into the wire at a specific rank with control
over orientation -- the building block used to repair broken wires.
Suggested fixture: wire where an edge is missing between rank 3 and 4; the
healer must Add() the synthesized edge with correct orientation.

#### Add() / AddOriented() (wire-into-wire / WireData-into-wire variants)
UNCOVERED

#### Remove() / Set()
UNCOVERED
What it does: Drops or replaces an edge in a wire mid-flight.
Suggested fixture: wire containing a duplicate edge (same edge twice in
sequence) -- healer must Remove() the dup.

#### Reverse() (with-face overload pcurve-swap)
UNCOVERED
What it does: Reverses a wire while swapping seam-pcurves on a face --
required when correcting an inside-out face on a periodic surface.
Suggested fixture: face on a cylinder with an inverted wire whose seam edge
has FORWARD/REVERSED pcurves swapped; healer must Reverse(face) not just
Reverse().

#### SetLast() (circular permutation)
UNCOVERED
What it does: Rotates wire edge sequence so a chosen edge is last;
canonicalizes wire start.
Suggested fixture: STEP edge_loop where the first edge is the degenerate
seam; kernel must permute it to the end for downstream tools.

#### SetDegeneratedLast()
UNCOVERED
What it does: Moves all degenerate edges to the end of the wire so
downstream geometry/topology code can skip them quickly.
Suggested fixture: wire that interleaves real edges and degenerate seam
edges; healer must run SetDegeneratedLast before sewing.

#### ComputeSeams() / IsSeam()
PARTIAL: IsSeam() COVERED by 31 fixtures (Xp015, Xp022, ...);
ComputeSeams() (the bulk recompute) UNCOVERED.
Suggested fixture: wire on a periodic face whose seam edges were not marked
by the producer; require kernel to call ComputeSeams() to discover them.

#### Wire() (BRep_Builder) / WireAPIMake() (vertex-merging)
UNCOVERED
What it does: Materializes a TopoDS_Wire from the WireData -- WireAPIMake
additionally merges duplicate vertices at edge boundaries (common after
edge-by-edge construction with separate vertex instances).
Suggested fixture: wire where every edge has its own pair of vertices at
endpoints (no shared vertex topology); require WireAPIMake to merge them.

#### Reverse() (basic)
UNCOVERED
What it does: Flips wire direction and all edge orientations.
Suggested fixture: face whose outer wire is CW when it should be CCW; healer
must Reverse() the wire.

#### Index() lookup
UNCOVERED

### ShapeExtend_MsgRegistrator

#### Send(Transient/Shape, msg, gravity)
UNCOVERED
What it does: Attaches a healing diagnostic to a specific transient object
or shape so callers can produce per-shape error reports.
Suggested fixture: assembly where 3 distinct faces independently fail
healing -- require kernel to emit 3 attached diagnostics via MsgRegistrator,
not one global error.

#### MapTransient() / MapShape()
UNCOVERED (lookup)

---

### Summary stats

| Module | Enumerated | Covered | Uncovered |
|---|---|---|---|
| BRepBuilderAPI_Sewing | 17 | 9 | 8 |
| BRepLib | 19 | 9 | 10 |
| ShapeProcess_OperLibrary | 2 | 0 | 2 |
| ShapeProcess_ShapeContext | 9 | 0 | 9 |
| ShapeProcess_UOperator | 1 | 1 | 0 |
| ShapeCustom_BSplineRestriction | 11 | 1 | 10 |
| ShapeCustom_ConvertToBSpline | 6 | 3 | 3 |
| ShapeCustom_ConvertToRevolution | 2 | 0 | 2 |
| ShapeCustom_Curve | 1 | 1 | 0 |
| ShapeCustom_Surface | 3 | 2 | 1 |
| ShapeCustom_RestrictionParameters | 10 | 4 | 6 |
| ShapeCustom_TrsfModification | 1 | 0 | 1 |
| ShapeExtend_CompositeSurface | 5 | 1 | 4 |
| ShapeExtend_ComplexCurve | 4 | 0 | 4 |
| ShapeExtend_WireData | 12 | 2 | 10 |
| ShapeExtend_MsgRegistrator | 2 | 0 | 2 |
| **TOTAL** | **87** | **33** | **54** |

(The earlier headline counts of 47 covered / 40 uncovered fold "covered indirectly"
shared-surface-area methods of Sewing into their primary entry, e.g. Load/Add/SewedShape
ride on Perform. The table above counts each method individually.)

### Headline observations

- ShapeProcess context plumbing (RecordModification, SetDetalisation, AddMessage,
  GetContinuity) is **completely uncovered**. The catalog never asserts on the
  per-shape diagnostic map or on resource-driven continuity targets, even though
  PMI/color rebinding after healing is a known pain point.

- BRepLib's tolerance hygiene functions (UpdateEdgeTol, UpdateEdgeTolerance,
  UpdateTolerances, BuildCurves3d batch) are **uncovered**. The catalog hits
  the *symptoms* (SameParameter failures, sewing-tolerance bumps) but not the
  named entry points that fix them.

- ShapeCustom_BSplineRestriction has 11 methods and only 1 fixture (Gn026).
  All the tuning knobs (SetMaxDegree, SetMaxNbSegments, SetTol3d/2d,
  SetContinuity3d/2d, SetConvRational) are **uncovered** -- so the catalog
  cannot distinguish "kernel restricts at all" from "kernel restricts with the
  right knob settings".

- BRepLib::EncodeRegularity is **uncovered** despite being the canonical
  source-of-truth for G1 edge tagging consumed by every fillet/draft/boolean.

- BRepBuilderAPI_Sewing::SetMinTolerance / SetMaxTolerance are **uncovered** --
  no fixture exercises the upper/lower bounds of the tolerance ladder,
  even though over-stitching and under-stitching are common real-world bugs.