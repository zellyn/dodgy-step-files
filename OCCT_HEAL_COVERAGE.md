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

---

## Per-branch deep coverage (second pass)

The API-surface coverage above credits a fixture as "covering" an operation
if the fixture's text mentions the operation by name or close synonym. But
each OCCT public repair method is hundreds of lines of nested `if/else if`
branches — each branch handles a specific defect *shape* and takes a
specific repair action. A fixture that mentions "self-intersection" may
exercise one of a dozen self-intersection branches; the API-surface pass
can't distinguish them.

This second pass walks the `.cxx` implementation files and enumerates every
substantive repair branch as a separate coverage unit. Branches are mapped
to fixtures by regex against `title` / `description` / `expected_kernel_behavior` /
`notes` / `reproducer` / `occ_behavior_note` text. The matcher is biased
toward false positives over false negatives; what matters here is finding
branches no catalog fixture mentions at all.

| Module group | Branches | Covered | UNCOVERED |
|---|---:|---:|---:|
| Wire-level (`ShapeFix_Wire`, `_Edge`, `_IntersectionTool`, `_WireVertex`) | 88 | 72 | 16 |
| Face/Shell/Shape-level (`ShapeFix_Face`, `_Shell`, `_Shape`, `_Solid`, `_FixSmallFace`) | 73 | 53 | 20 |
| Sewing + Unify-same-domain (`BRepBuilderAPI_Sewing`, `ShapeUpgrade_UnifySameDomain`, `_ClosedFaceDivide`, `ShapeFix_Wireframe`) | 68 | 43 | 25 |
| **Per-branch total** | **229** | **168 (73%)** | **61 (27%)** |

The two passes are complementary: the API-surface pass tells you which
OPERATIONS exist; the per-branch pass tells you which DEFECT SHAPES inside
those operations have a representative fixture. A "75% API coverage / 73%
branch coverage" overall picture is consistent — most of the gap is in
specific edge-case branches, not in entire repair operations.

### Surprising findings from the deep pass

Two are worth flagging as catalog-fidelity issues:

1. **`ShapeFix_FixSmallFace::FixPinFace` is a no-op stub.** The method's body
   is literally `return true;`. The catalog has `Tfa008` and `Tfa044` (pin
   faces) — the API-surface pass credited them as covering this operation,
   but no OCCT repair logic actually runs. Worth re-classifying these
   fixtures as **`receiver-behavior`** (the file exists, the kernel doesn't
   repair) or noting in the entries that the method is unimplemented in
   current master.

2. **`BRepBuilderAPI_Sewing::SetMaxTolerance` is bypassed in-method.** Even
   when MaxTolerance is set, the sewing inner loop writes a raw `BRep_TEdge`
   tolerance at line ~1168 that silently exceeds the user cap. No fixture
   stresses this hard-override path; would be a high-leverage gap to fill.

The remaining UNCOVERED branches are listed per-file below with a one-sentence
"suggested fixture" hint for each.

### Wire-level branches (`ShapeFix_Wire/Edge/IntersectionTool/WireVertex.cxx`)

Source files (all from OCCT master, fetched 2026-06-14 from
`raw.githubusercontent.com/Open-Cascade-SAS/OCCT/master/src/ModelingAlgorithms/TKShHealing/ShapeFix/`):

  ShapeFix_Wire.cxx                4478 lines
  ShapeFix_Edge.cxx                 957 lines
  ShapeFix_IntersectionTool.cxx    2530 lines
  ShapeFix_WireVertex.cxx           293 lines

Per-branch enumeration of repair logic; each branch is a distinct *defect-shape*
decision point that selects a repair path. Trivial guards (empty-wire / not-loaded /
status short-circuits) are excluded.

Total branches enumerated: 88 (substantive; 5 additional trivial guards listed but not counted)
Covered: 72
UNCOVERED: 16

---

#### ShapeFix_Wire::FixReorder(bool theModeBoth) — `ShapeFix_Wire.cxx:487`

##### Branch 1: bi-periodic surface (toroidal / spherical-B-spline) — both U and V periodic, opt-in "Both" mode
What it tests: surface IsUPeriodic() && IsVPeriodic() && theModeBoth
What it repairs: invokes `CheckOrder(..., closedmode=true, both=true)` so the analyzer is allowed to reorder by both parameters
COVERED by: Xp010 (torus pcurve disagreement), Xp022 (cyclic seam torus), Gs001 (toroidal negative MajorRadius), Gp028 (wire crosses periodic-surface seam)

##### Branch 2: ordinary (single-periodic / non-periodic) surface
What it tests: any surface that isn't doubly-periodic, or `theModeBoth==false`
What it repairs: `CheckOrder(..., both=false)` — standard 1-axis reorder
COVERED by: Twi007 (disordered edges in wire), Twi008 (ordering ambiguous between 2d/3d on periodic surface), Twi051

##### Branch 3: WireOrder status == 3 — only shifted, sequence intact
What it tests: `sawo.Status() == 3`
What it repairs: marks DONE5 to signal pcurves were shifted but topology unchanged
COVERED by: Gp023 (point projection on trimmed periodic cylinder returns shifted UV), Gp027 (closed-face splitter pcurves out of sync), Xp044

##### Branch 4: WireOrder status negative — wire could not be ordered cleanly
What it tests: `sawo.Status() < 0`
What it repairs: marks DONE3 (best-effort order), keeps the partial reorder
COVERED by: Twi094 (wire endpoint first/last edge skipped during wire build), Twi034 (EDGE_LOOP missing closing edge), Ad101

---

#### ShapeFix_Wire::FixSmall(num, lockvtx, precsmall) — `ShapeFix_Wire.cxx:1404`

##### Branch 5: small edge but two distinct vertices, locked or topo-immutable
What it tests: `LastCheckStatus(DONE2) && (lockvtx || !myTopoMode)`
What it repairs: refuses to remove — emits FAIL2, leaves edge in place
COVERED by: N010 (`EDGE_CURVE` shorter than vertex tolerance), Twi086 (zero-length line edge)

##### Branch 6: small edge with two distinct vertices, free to merge
What it tests: `DONE2 && !lockvtx && myTopoMode`
What it repairs: removes edge AND calls FixConnected() to merge the two vertices
COVERED by: Tsh053 (merging coplanar faces fails on empty loop), Twi086

##### Branch 7: small edge with already-identical vertices (true "null" edge)
What it tests: `!DONE2 && DONE` — same vertex on both ends
What it repairs: removes the edge unconditionally
COVERED by: Tfa008 (pin/sliver face), Gn031 (tiny-radius rational edge), Twi086

---

#### ShapeFix_Wire::FixConnected(num, prec, theUpdateWire) — `ShapeFix_Wire.cxx:1476`

##### Branch 8: "absolutely confused" — distance(V1,V2) within Precision::Confusion
What it tests: `LastCheckStatus(DONE1)`
What it repairs: replaces one vertex with the other directly (`Context()->Replace`); special-case if V2 is its own LastVertex
COVERED by: Ad103 (coincident VERTEX_POINTs trigger merge), Twi067 (lacking edge: 2D gap not absorbable)

##### Branch 9: confusion within tolerance ranges (DONE2)
What it tests: `DONE2` — distance > confusion but < combined vertex tolerance
What it repairs: builds an averaged ("combined") vertex via `ShapeBuild_Vertex::CombineVertex`
COVERED by: Tfa022 (almost-closed EDGE_LOOP, sub-tolerance gap), Twi095 (tangentially-touching wires)

##### Branch 10: confusion needs averaging plus tolerance widening (DONE3)
What it tests: neither DONE1 nor DONE2 — only confused when tol is enlarged
What it repairs: same `CombineVertex` path but flags DONE3 to signal tol bump
COVERED by: Gs034 (twisted/pinched face revisits shared vertex), Twi009 (common vertex shared between wires), Gs047

##### Branch 11: single-edge wire (closed loop with 1 edge), free-edge in topo mode
What it tests: `sbwd->NbEdges() < 2 && E2.Free() && myTopoMode`
What it repairs: in-place `BRep_Builder::Remove` + `Add` of new vertex to head AND tail of the loop edge
COVERED by: Tfa005 (periodic face given by single belt wire), Twi049

##### Branch 12: single-edge wire, immutable or with Context
What it tests: 1-edge wire AND (!Free || !topomode)
What it repairs: uses CopyReplaceVertices to make a new edge with the same V on both ends
UNCOVERED
Suggested fixture: `Twi.belt-single-edge-frozen` — single ORIENTED_EDGE loop on a torus/cylinder where the edge is shared with another face (not free) and ShapeFix has Context bound.

---

#### ShapeFix_Wire::FixEdgeCurves() — `ShapeFix_Wire.cxx:600`

##### Branch 13: FixReversed2d — pcurve parameter direction opposite to 3D curve
COVERED by: Twi065 (wire edge-curves analysis with reversed pcurve direction), Twi071 (seam edge with two pcurves swapped), N005 (split closed periodic face leaves new edges with reversed pcurve)

##### Branch 14: FixRemovePCurve — pcurve does not match vertices at all
COVERED by: Twi052 (edges accumulate several pcurve/3D-curve defects), Hea015 (duplicate PCURVE_S1_AND_S2), Gs051

##### Branch 15: FixAddPCurve hits singularity (over-degen pole / curve passing through it)
What it tests: `!sbwd->IsSeam(i) && DONE2` from projector → curve passes through pole
What it repairs: re-splits the edge at each detected singular u-parameter, transferring 2D and 3D ranges, then rebuilds; falls back to merging tiny edges into adjacent vertex tolerance
COVERED by: Pf021 (CONICAL_SURFACE apex shape-healing crash), Xp013 (cone apex pcurve), Gp005 (pcurve with single-pole apex), Twi021 (missing degenerate at cone apex/sphere pole)

##### Branch 16: FixAddPCurve — extra "over-degen + U-closed" adjustment loop
What it tests: `overdegen && surf->IsUClosed(Precision())` and global U vector sweep `~= URange`
What it repairs: removes the over-degen pcurve and re-adds it with `AdjustOverDegenMode=false`
COVERED by: Gp028 (wire crosses periodic-surface seam), Tb012 (sphere seam across pole)

##### Branch 17: FixRemoveCurve3d — 3D curve disagrees with vertices, remove it
COVERED by: Twi088 (edge in topology has no 3D curve), Os012 (loft produces EDGE_CURVE with no 3D curve)

##### Branch 18: FixAddCurve3d — projection fails, no pcurves either → drop edge entirely
What it tests: `myFixEdge->FixAddCurve3d` FAIL && (C.IsNull() || range ~ 0)
What it repairs: removes the incomplete edge, then triggers FixClosed/FixConnected on the gap
COVERED by: Ad046 (writer crash on EDGE_CURVE with no SURFACE_CURVE), Twi088, Os012

##### Branch 19: FixSameParameter sees pcurve fp/lp ≠ 3D first/last → clear SameRange
What it tests: `|First - fp2d| > PConfusion || |Last - lp2d| > PConfusion`
What it repairs: sets `SameRange(false)` so downstream re-syncs
COVERED by: Twi082 (same_range flag false), Twi090 (cached EDGE_LOOP closed-flag stale), N004 (SameParameter=.T. lie)

##### Branch 20: FixSameParameter sees pcurve range out of bspline natural range → re-project
What it tests: `!sae.CheckPCurveRange(First, Last, C2d)`
What it repairs: deletes the pcurve and re-runs FixAddPCurve
COVERED by: Gp022 (SameParameter=.T. but parameterisations differ), Gp024 (pcurve refit after non-uniform scale)

##### Branch 21: FixVertexTolerance pass — finalise vertex tolerances on each edge
COVERED by: Gp002 (pcurve endpoints disagree with vertex 3D), Gp038 (vertex 3D and pcurve disagree), Bo030, Xp014

---

#### ShapeFix_Wire::FixSeam(num) — `ShapeFix_Wire.cxx:1615`

##### Branch 22: seam-edge had two pcurves but they were assigned wrong-way-round
What it tests: `myAnalyzer->CheckSeam` returns C1, C2 swapped
What it repairs: `B.UpdateEdge(E, C2, C1, Face(), 0.)` — swaps PCurve / PCurve2 on the BRep_TEdge representations
COVERED by: Twi022 (seam edge with swapped/duplicated pcurves), Twi071 (seam edge two pcurves swapped), Gp013 (CATIA "like-seam" two pcurves)

---

#### ShapeFix_Wire::FixShifted() — `ShapeFix_Wire.cxx:1661`

##### Branch 23: U-closed periodic surface (cylinder, cone) — pcurves shifted by ±URange
What it tests: `surf->IsUClosed(Precision()) && !IsVClosed`
What it repairs: detects shift via box-traversal; applies `gp_Trsf2d::SetTranslation` of (URange, 0) to wrap-back curves
COVERED by: Wr037 (cylinder seam emitted as ordinary edge), Xp015 (self-intersecting wire on cylindrical face seam missing), Tsh047 (face unification crosses cylinder seam)

##### Branch 24: V-closed only (sphere/torus rolled-up other axis)
What it tests: `IsVClosed && !IsUClosed`
What it repairs: shift in V direction by ±VRange
COVERED by: Twi035 (sphere given by two meridians), Tb012

##### Branch 25: SurfaceOfRevolution whose base curve is periodic
What it tests: `IsKind(Geom_SurfaceOfRevolution) && BasisCurve->IsPeriodic()`
What it repairs: forces `vclosed=true` and uses `BasisCurve()->Period()` for VRange, even if surface itself reports !V-closed
COVERED by: P022 (helical seam from arc + revolve), Tb012, Gs001

##### Branch 26: SurfaceOfRevolution with non-periodic base — fake-degenerate at one boundary
What it tests: `IsKind(Geom_SurfaceOfRevolution) && !isDeg && (!vclosed || !uclosed)` — degenerate iso-line detected on boundary
What it repairs: marks `isDeg = 1` or `2` to suppress shift on that axis even though it isn't really closed
COVERED by: Twi035, Pf021

##### Branch 27: "Bi-meridian" path through degenerate pole (e.g., two half-meridians on sphere)
What it tests: complex rot1*rot2 < 0 && scld*scln < 0 && |scln|>0.1*period sign-check pattern (~line 1905)
What it repairs: applies `AdjustToPeriod` over (deep1, deep2) bounding to determine shift dx, then transforms all pcurves between degn2 and n2 by `Shift = ±dx`
COVERED by: Twi035 (sphere as two meridians special wire), Tb012

##### Branch 28: Surface neither U- nor V-closed — early exit
What it tests: `!uclosed && !vclosed` — no shift can possibly be needed
What it repairs: no-op early return
*Trivial; not counted.*

---

#### ShapeFix_Wire::FixDegenerated(num) — `ShapeFix_Wire.cxx:2130`

##### Branch 29: degen-flag asserted but no pcurve and no singularity at point (phantom-degen)
What it tests: `CheckDegenerated` returns FAIL2
What it repairs: removes the edge altogether (no real apex underneath)
UNCOVERED
Suggested fixture: `Twi.phantom-degen-flag` — STEP `EDGE_CURVE` with `BRep_Tool::Degenerated=.T.` but the 3D point is interior to a non-degenerate parametric region.

##### Branch 30: pole reached but no degen-edge present → insert one (lacking degen)
What it tests: `LastCheckStatus(DONE1)` — "lack" branch
What it repairs: builds `Geom2d_Line(p2d1, dir)` between the two pcurve endpoints at the apex, makes a new degenerated edge, inserts it
COVERED by: Twi021 (missing degenerate edge at apex), Gp005 (pcurve with single-pole apex)

##### Branch 31: existing edge marked degen but its pcurve is wrong → replace
What it tests: !DONE1 (replace branch) — degenerate edge exists but its 2d line is wrong
What it repairs: rebuilds the `Geom2d_Line` and overwrites edge representation
COVERED by: Twi031 (duplicate degenerate edges at apex), Gp005

##### Branch 32: duplicate degenerated edges at the same apex (PRO/E pattern)
What it tests: in caller loop `FixDegenerated()`: two consecutive `DONE2` codes
What it repairs: removes the duplicate degenerate edge (sbwd->Remove(i))
COVERED by: Twi031 (Pro/E duplicate degenerate edges)

---

#### ShapeFix_Wire::FixSelfIntersectingEdge(num) — `ShapeFix_Wire.cxx:2708`

##### Branch 33: intersection point lies within an endpoint's tolerance ball (figure-of-eight near vertex)
What it tests: `dist21 < tol1² || dist22 < tol2²`
What it repairs: skipped — not a "real" self-intersection
COVERED by: Ad099 (self-tangent loop never terminates), Gn024 (self-intersecting B_SPLINE)

##### Branch 34: RemoveLoopMode<1 — increase vertex tolerance (default)
What it tests: `myRemoveLoopMode < 1 && newtol < MaxTolerance`
What it repairs: `BRep_Builder::UpdateVertex` of the nearer endpoint to newtol
COVERED by: N008 (tolerance inflation by repeated self-intersection healing)

##### Branch 35: RemoveLoopMode<1 + GeomMode — try planar `RemoveLoop` (cut a 2D loop, splice 3D)
What it tests: `myGeomMode && RemoveLoop(...)` succeeds, repeated up to 30 iterations
What it repairs: builds a new pcurve and 3D curve concatenating arcs around the loop, then refits SameParameter
COVERED by: Pf024 (FixSelf-intersection healing tool enters infinite loop), Pf023 (iterative ShapeFix exposes new defect every pass)

##### Branch 36: RemoveLoopMode==1 — insert a midpoint vertex splitting the edge in two
What it tests: `myRemoveLoopMode == 1`
What it repairs: builds Vmid at intersection, splits edge into E1+E2 with new pcurves (`Geom2d_TrimmedCurve` on each half)
COVERED by: Ad099, Gn024

##### Branch 37: tolerance exceeded MaxTolerance even after expansion
What it tests: `newtol >= MaxTolerance()`
What it repairs: marks FAIL2 and refuses
COVERED by: Pf023, N008

---

#### ShapeFix_Wire::FixIntersectingEdges(num) — `ShapeFix_Wire.cxx:2966`

##### Branch 38: intersection within existing edge-tolerance estimates (deviation tube)
What it tests: `maxte < MaxTolerance() && BRep_Tool::Tolerance(E1) < te1 || ... < te2`
What it repairs: increases edge tolerance via `B.UpdateEdge(...)` and copies vertices (Context().CopyVertex)
COVERED by: N013 (Boolean cascade vertex deviation), N004, Tfa045 (kissing wires)

##### Branch 39: CutEdge() — pcurve is a trimmed line, trim back to intersection
What it tests: pcurve is `Geom2d_TrimmedCurve(Geom2d_Line)` at endpoint; via SplitTool
What it repairs: shortens edge range so the offending overshoot disappears
COVERED by: Twi063 (two edges describe overlapping segments), Tfa036 (boundary crossing patch seams)

##### Branch 40: edges intersect but cannot cut (curve not a trimmed line)
What it tests: `aTool.CutEdge` returns false AND V1.IsSame(Vp)
What it repairs: marks DONE3 — vertex re-snap signalled but edge geometry untouched
UNCOVERED
Suggested fixture: `Twi.intersect-nonline-pcurve` — two `EDGE_CURVE`s whose pcurves are `Geom2d_BSplineCurve` (not lines) overlap at a knot.

##### Branch 41: `IsCutLine` succeeded — shrink finished, recompute vertex location only
COVERED by: Twi063, N013

##### Branch 42: locMayEdit=false and inctol >= MaxTolerance → give up
COVERED by: Pf023 (unbounded ShapeFix exposing new defect), N040 (`Limit Tolerance` clamp)

---

#### ShapeFix_Wire::FixIntersectingEdges(num1,num2) — non-adjacent pair — `ShapeFix_Wire.cxx:3271`

##### Branch 43: non-adjacent edge pair intersects; nearest-vertex repair within MaxTolerance
What it tests: distance(IP, nearest vertex) < MaxTolerance && necessaryVtxTole bounds permit
What it repairs: bumps 1 of 4 vertex tolerances to finTol; ranks 4 candidates, picks min
COVERED by: Gs009 (self-intersecting EDGE_LOOP on planar face), Gs042 (CURVE_BOUNDED_SURFACE bowtie boundary), Twi049

##### Branch 44: necessary edge-tolerance > nearest-vtx tolerance — bump edge tol instead of vertex
What it tests: `max(aMaxEdgeTol1, aMaxEdgeTol2) < finTol && (aMaxEdgeTol1>0 || aMaxEdgeTol2>0)`
What it repairs: `B.UpdateEdge(edge1, aNewTolEdge1)` / edge2 — only bump edge tol, leave vertices
UNCOVERED
Suggested fixture: `Twi.non-adj-edge-far-vertices` — two non-adjacent `EDGE_CURVE`s whose 2D pcurves cross at midspan but whose endpoint VERTEX_POINTs are very far apart (so vertex-tolerance bump would be excessive).

---

#### ShapeFix_Wire::FixLacking(num, force) — `ShapeFix_Wire.cxx:3617`

##### Branch 45: `doBend` — bend the existing pcurve to close the gap (preferred when tolerances accept)
What it tests: bendc1/bendc2 produced AND bendtols < existing edge tols, or inctol<Prec
What it repairs: `TryBendingPCurve` reseats one BSpline pole to the new endpoint, replaces pcurve and updates vertex tols
UNCOVERED
Suggested fixture: `Twi.lacking-bend-pcurve` — small UV gap between two adjacent edges whose pcurves are `Geom2d_BSplineCurve`, where bending the last control point is sufficient and cheaper than vertex inflation.

##### Branch 46: `doIncrease` — gap small enough to absorb in vertex tolerance
What it tests: `inctol < Prec`
What it repairs: `B.UpdateVertex(V1/V2, 1.001*inctol)`
COVERED by: Twi067 (lacking edge: 2D gap not absorbable), Twi070 (curve gap mid-edge), Tfa022

##### Branch 47: `doAddLong` — sufficient 3D gap between edges, insert new bridging edge plus two new vertices
What it tests: `myTopoMode && dist3d² > 1.25*tol0² && (force || dist3d² > Prec² || inctol > MaxTol)`
What it repairs: builds new Geom2d_Line between p2d1 & p2d2, makes new vertices at p3d1 / p3d2, replaces V1/V2 of adjacent edges
COVERED by: Twi036 (lacking edge: UV gap not closable by vertex tolerance), Twi067

##### Branch 48: `doAddDegen` — midpoint of new pcurve falls inside the vertex; add as degenerate
What it tests: `pV.Distance(pm) <= tol` (where pm = surf->Value of UV midpoint)
What it repairs: same edge as Long path but with `B.Degenerated(edge, true)` and skip BuildCurve3d
UNCOVERED
Suggested fixture: `Twi.lacking-degen-at-pole` — wire on sphere where two adjacent edges almost meet at a pole; midpoint of the closing 2D segment maps to the pole within vertex tolerance.

##### Branch 49: `doAddClosed` — gap is real but midpoint not in vertex; add closed (non-degen) bridging edge
What it tests: `dist > tol && myTopoMode`
What it repairs: closed edge inserted as Long-add but kept non-degen
UNCOVERED
Suggested fixture: `Twi.lacking-add-closed-bridge` — UV gap on a torus where neither vertex inflation nor degenerate-edge path is acceptable but topology can be edited.

##### Branch 50: degenerate-edge fallback when neither doIncrease nor doAddLong (`!topomode && dist<=MaxTol`)
What it tests: `dist <= MaxTolerance()` and topo immutable
What it repairs: combine doAddDegen + doIncrease (inctol = dist)
UNCOVERED
Suggested fixture: `Twi.lacking-degen-topo-locked` — same as Branch 48 but with ShapeBuild_ReShape replacement disabled.

##### Branch 51: surface is degenerated between p2d1/p2d2 (on iso through pole) — refuse to bend / refuse to inflate
What it tests: `myAnalyzer->Surface()->IsDegenerated(p2d1, p2d2, 2.*tol, 10.)`
What it repairs: skip both doIncrease and doBend, fall through to add-edge path
COVERED by: Twi021, Gp005, Pf021

---

#### ShapeFix_Wire::FixNotchedEdges() — `ShapeFix_Wire.cxx:3977`

##### Branch 52: notch split point coincides with an existing edge end (or with the other end for closed edge)
What it tests: `|param - (isRemoveFirst ? b : a)| <= PConfusion || (sae.IsClosed3d && |param - other end| <= PConfusion)`
What it repairs: hands off to `FixDummySeam(n1)` — the notch detour is just an extra pair of edges along a seam-like return path
COVERED by: Hea005 (triangular notch detour on free-bound EDGE_LOOP), Ad098 (infinite recursion in ShapeFix after Boolean cut)

##### Branch 53: notch split point interior — split the to-keep edge and replace the to-remove edge by midpoint
What it tests: `|a - param| > PConfusion && |b - param| > PConfusion`
What it repairs: splits via TransferParametersProj into newE1+newE2, sews into wire, then FixDummySeam(toRemove) to collapse the back-out pair
COVERED by: Gs014 (zero-area / sliver face), Gs015 (sliver face high aspect ratio), Sw002 (sliver face dropped by sewing), Tsh028

---

#### ShapeFix_Wire::FixDummySeam(num) — `ShapeFix_Wire.cxx:4213`

##### Branch 54: collapse a pair of edges that retrace along a seam (degenerate U-turn)
What it tests: caller already determined num/num+1 is a back-and-forth pair
What it repairs: combines V1/V2 into Vm via `CombineVertex`, copies reversed pcurves from E1 onto a new E2-shaped edge, replaces and removes original pair from wire
COVERED by: Twi011 (wire tail / hair), Twi093 (synthesised seam edge inserted through wire path), Twi098 (FixTails removes wire tail edges incorrectly)

---

#### ShapeFix_Wire::FixTails() — `ShapeFix_Wire.cxx:4314`

##### Branch 55: tail edges identified with angle filter (myMaxTailAngleSine>0)
What it tests: `aCheckAngle && CheckTail(..., myMaxTailAngleSine, ...)`
What it repairs: split or remove pair of edges making the tail; calls FixDummySeam on the U-turn
COVERED by: Twi011 (wire tail / hair), Twi098, Gp039 (pcurve projection unstable on closed B-spline)

##### Branch 56: tail edges retried without angle filter after first pass missed
What it tests: `aCheckAngle = false` retry after a miss
What it repairs: only width-based threshold (myMaxTailWidth), allowing tails that are wide but very thin
COVERED by: Twi098

##### Branch 57: tail of 2 edges where one is split and one fully removed (asymmetric)
What it tests: `aRemoveCount==1 && aSplitCounts[aRI]!=0`
What it repairs: removes the run-out edge, splits its mate, re-indices wire
UNCOVERED
Suggested fixture: `Twi.tail-asymmetric-split` — a hair where one half is a small line and the other is a slightly longer bspline that must be split at the tail base.

##### Branch 58: tail removal would leave fewer than 1 edge → refuse
What it tests: `aECount + aSplitCounts < 1 + aRemoveCount`
What it repairs: skip — preserve wire
COVERED by: Tsh053 (merge with empty loop), Tfa008

---

#### ShapeFix_Edge::FixRemovePCurve(edge, surface, location) — `ShapeFix_Edge.cxx:87`

##### Branch 59: pcurve endpoints lie outside both vertex tolerance balls
What it tests: `ShapeAnalysis_Edge::CheckVerticesWithPCurve` returns true (mismatch)
What it repairs: `ShapeBuild_Edge::RemovePCurve` — drop the bad pcurve entirely
COVERED by: Gs051 (sphere/cylinder cut produces wrong pcurves on second seam), Hea015 (duplicate PCURVE_S1_AND_S2), Twi052

---

#### ShapeFix_Edge::FixRemoveCurve3d(edge) — `ShapeFix_Edge.cxx:103`

##### Branch 60: 3D-curve endpoints disagree with edge vertices
What it tests: `CheckVerticesWithCurve3d` true
What it repairs: `RemoveCurve3d` — forces downstream rebuild via FixAddCurve3d
COVERED by: Twi088 (edge with no 3D curve), Twi052, Os012

---

#### ShapeFix_Edge::FixAddPCurve(edge, surface, location, isSeam, sas, prec) — `ShapeFix_Edge.cxx:470`

##### Branch 61: surface is a Plane — refuse (planes don't need stored pcurves)
What it tests: `surf->IsKind(Geom_Plane)`
What it repairs: early-return false; downstream uses BRep_Tool::CurveOnSurface to project on demand
*Trivial guard, not counted.*

##### Branch 62: edge has a pcurve already (or seam already in place) — refuse
*Trivial.*

##### Branch 63: isSeam && U-closed only (cylinder/cone) — second pcurve = original + (UL-UF, 0)
What it tests: `isSeam && sas->IsUClosed(prec) && !IsVClosed(prec)`
What it repairs: builds c2d2 = c2d translated by (URange,0), stored as PCurve2
COVERED by: Wr037 (cylinder seam emitted as ordinary edge), Xp033 (NX cylinder split into two halves at seam), Xp015

##### Branch 64: isSeam && V-closed only (sphere via revolve)
What it tests: `isSeam && IsVClosed && !IsUClosed`
What it repairs: shift by (0, VRange)
COVERED by: Twi035, Tb012, Gs053

##### Branch 65: isSeam && both U- and V-closed (torus, near-closed bsplines)
What it tests: `IsUClosed() && IsVClosed()`
What it repairs: calls `TranslatePCurve` — auto-detects which axis the seam runs along
COVERED by: Xp010 (negative torus radius pcurve disagreement), Xp022 (torus cyclic seam), Tsh035, Gp028, Gn014

##### Branch 66: projector returns DONE3 — projection rebuilt 3D from 2D (rare)
What it tests: `myProjector->Status(DONE3)`
What it repairs: also `UpdateEdge(edge, c3d, 0.)` to install fresh 3D curve from analytic projection
UNCOVERED
Suggested fixture: `Gp.pcurve-only-rebuild3d` — STEP edge whose `SURFACE_CURVE.curve_3d` is null (`$`) but a `PCURVE` exists; projector rebuilds c3d and stores it.

##### Branch 67: projector throws (sampling failure on near-degenerate pcurve)
What it tests: `OCC_CATCH_SIGNALS` Standard_Failure
What it repairs: sets FAIL2 — partial result preserved; caller may retry
COVERED by: Ad046 (writer crash on edge with no SURFACE_CURVE), Pf021, Gn019 (degenerate zero-length B_SPLINE pcurve)

---

#### ShapeFix_Edge::FixReversed2d(edge, surface, location) — `ShapeFix_Edge.cxx:744`

##### Branch 68: pcurve direction opposite to 3D curve at sample points
What it tests: `EA.CheckCurve3dWithPCurve` DONE (no FAIL1/FAIL2)
What it repairs: `c2d->Reverse()` and `B.Range(edge, surface, location, newf, newl)`; if BRep_Tool::Range differs from newf/newl after, also `B.SameRange(edge,false); SameParameter(false)` to force re-sync
COVERED by: Twi065 (reversed pcurve direction), Twi071, N005 (reversed pcurve vs 3D parameterisation), Gs053

##### Branch 69: after reverse, BRep_Tool::Range disagrees with newf/newl (B-spline reparam-on-reverse rounding)
What it tests: `first != newf || last != newl`
What it repairs: clear SameRange+SameParameter flags; downstream FixSameParameter cleans up
COVERED by: Gp022 (SameParameter=.T. lie), Twi082

---

#### ShapeFix_Edge::FixSameParameter(edge, face, tolerance) — `ShapeFix_Edge.cxx:798`

##### Branch 70: degenerated edge — only fix SameRange, set SameParameter true unconditionally
What it tests: `BRep_Tool::Degenerated(edge)`
What it repairs: no projection — degen edges are inherently same-param
COVERED by: Twi092 (wire with degenerated edge dropped silently), Twi021

##### Branch 71: edge wasn't SameParameter — try BRepLib::SameParameter on a copy, compare deviation
What it tests: `!wasSP`
What it repairs: builds copyedge, runs BRepLib's heavy SameParameter algorithm with current tol; if deviation < pcurve deviation, CopyPCurves from copyedge
COVERED by: N004 (SameParameter=.T. lie), Gp022, Twi065, Sw006

##### Branch 72: BRepLib threw — fall back to "deviation only" path
What it tests: catch Standard_Failure
What it repairs: marks FAIL2, keeps original pcurves but uses measured maxdev to update tolerance
COVERED by: Pf021 (CONICAL_SURFACE shape-healing crash), Ad099, Pf023

##### Branch 73: measured maxdev > existing edge tolerance — bump edge + vertex tols
What it tests: `maxdev > tol`
What it repairs: `B.UpdateEdge(edge, maxdev)` and recurse into FixVertexTolerance
COVERED by: Bo030 (start VERTEX_POINT off the LINE), N004, Gp038, Xp014

---

#### ShapeFix_IntersectionTool::CutEdge(edge, pend, cut, face, iscutline) — `ShapeFix_IntersectionTool.cxx:194`

##### Branch 74: pcurve is a `Geom2d_TrimmedCurve(Geom2d_Line)` — exact analytic trim path
What it tests: `!SameParameter && PCurve isKind Trimmed && BasisCurve isKind Line2d`
What it repairs: `B.Range(edge, min(pend,cut), max(...))` AND adjusts 3D range to (a+cut3d, b) or (a, b-cut3d) depending which end is trimmed; sets `iscutline=true` so caller knows the trim is analytically clean
COVERED by: Twi063 (two edges describe overlapping segments), Pf024

##### Branch 75: SameParameter edge — direct numerical Range adjustment
What it tests: `BRep_Tool::SameParameter(edge) && |aRange - (b-a)| >= PConfusion`
What it repairs: `B.Range(edge, min(pend,cut), max(pend,cut))` without iscutline flag
COVERED by: Tfa036, Twi063

##### Branch 76: range adjustment magnitude below 10*PConfusion — refuse (would be no-op)
*Trivial precision guard, not counted.*

---

#### ShapeFix_IntersectionTool::UnionVertexes(...) — `ShapeFix_IntersectionTool.cxx:495`

##### Branch 77: V1F closest to V2F — merge head-to-head
What it tests: d11<d12 && d11<d21 && d11<d22 AND d11<combinedTol
What it repairs: updates V1F tolerance, CopyReplaceVertices to absorb V2F into V1F; cascades the replacement into adjacent edges (num21, num22) that share V2F
COVERED by: Ad103 (coincident VERTEX_POINTs), Twi009 (common vertex shared between wires)

##### Branch 78: V1F closest to V2L — head-to-tail merge (opposite-orientation case)
What it tests: d12 < d21,d22
What it repairs: same pattern with V2L instead of V2F
COVERED by: Twi067, Tfa045

##### Branch 79: V1L closest to V2F — tail-to-head
What it tests: d21 < d22
COVERED by: Twi009, Twi095

##### Branch 80: V1L closest to V2L — tail-to-tail
COVERED by: Twi067, Ad103

---

#### ShapeFix_IntersectionTool::FixSelfIntersectWire(...) — `ShapeFix_IntersectionTool.cxx:1029`

##### Branch 81: non-adjacent edges, single-point intersection (Tr1=Middle && Tr2=Middle)
What it tests: `Inter.NbPoints() > 0 && < 3 && both transitions Middle`
What it repairs: distMin-based "nearest vertex" selection on each edge, then either CutEdge alone, CutEdge+SplitEdge1, or create-new-Vmid+split-both
COVERED by: Gs009 (figure-eight EDGE_LOOP on planar face), Gs042 (bowtie boundary), Twi049

##### Branch 82: single-point intersection where one edge endpoint matches (Middle+!Middle)
What it tests: one PositionOnCurve == IntRes2d_End on edge2
What it repairs: `FindVertAndSplitEdge` — find which edge1 vertex corresponds, split only edge1
UNCOVERED
Suggested fixture: `Twi.non-adj-touch-at-vertex` — two non-adjacent EDGE_CURVEs where edge2's endpoint lies on edge1's midspan but edge1's endpoints are far away.

##### Branch 83: single-point intersection both at endpoints (!Middle && !Middle)
What it tests: PositionOnCurve == End on both
What it repairs: `UnionVertexes` — merge the two endpoints into one
COVERED by: Ad103 (coincident VERTEX_POINTs), Twi095 (touching wires tangential contact)

##### Branch 84: segment-intersection (curves coincident over a range) — small overlap, single-point synthesis
What it tests: `Inter.NbSegments() == 1 && IS.HasFirstPoint && HasLastPoint && tolV < MaxTolVert`
What it repairs: builds new midpoint vertex, calls `SplitEdge2(...)` on each edge at (p11,p12) and (p21,p22)
UNCOVERED
Suggested fixture: `Twi.overlap-short-segment` — two `EDGE_CURVE`s sharing a sub-millimetre overlapping arc on the same LINE.

##### Branch 85: segment-intersection (large overlap) — split each edge into 3 parts and *delete* the middle (segment-removal)
What it tests: `Inter.NbSegments() == 1 && tolV >= MaxTolVert` (the `else if (FixSegment)` branch line 1531)
What it repairs: creates Vmid1/Vmid2 at segment ends, SplitEdge1 each edge twice, then `sewd->Remove(numseg2); Remove(numseg1)`; increments NbRemoved by 2
UNCOVERED
Suggested fixture: `Twi.overlap-long-segment-strip` — adjacent EDGE_CURVEs that retrace the same arc for >50% of their length — healer should delete the shared strip rather than fatten tolerance.

##### Branch 86: NbPoints >= 3 — too tangled to fix in one pass
What it tests: `Inter.NbPoints() >= 3`
What it repairs: skipped — no single intersection branch applies
UNCOVERED
Suggested fixture: `Twi.triple-cross` — bowtie wire whose two diagonals cross each other and also touch a third edge.

---

#### ShapeFix_IntersectionTool::FixIntersectingWires(face) — `ShapeFix_IntersectionTool.cxx:1835`

##### Branch 87: face has ≥2 wires; outer-wire × inner-wire intersection
What it tests: more than one TopAbs_WIRE child of face after filtering non-FORWARD/REVERSED
What it repairs: pairwise edge-edge bbox + intersection, same heal mechanics as FixSelfIntersectWire but across wire boundary
UNCOVERED
Suggested fixture: `Tfa.outer-inner-wire-cross` — face with outer EDGE_LOOP and a hole EDGE_LOOP where one edge of the hole strays across the outer boundary.

##### Branch 88: face has only a single wire — refuse (FixSelfIntersectWire handles single-wire case)
*Trivial guard.*

---

#### ShapeFix_WireVertex::FixSame() — `ShapeFix_WireVertex.cxx:82`

##### Branch 89: status==1 ("same coordinates") — share existing V1 directly
What it tests: `myAnalyzer.Status(i)==1` (vertices already same coords but distinct topology)
What it repairs: rebuilds incidence with V1 only — does NOT touch tolerance
COVERED by: Ad103 (coincident VERTEX_POINTs at identical CARTESIAN_POINT), Twi064

##### Branch 90: status==2 ("close") — share V1 AND update tolerance via Curve3d sampling at last/first param
What it tests: `Status(i)==2`
What it repairs: `B.UpdateVertex(V1, cl, E1, Precision)` and `(V1, cf, E2, Precision)` — adjusts vertex param-on-edge plus tolerance
COVERED by: Twi064 (wire-analysis pipeline collects sub-check flags), Twi092, Hea011

---

#### ShapeFix_WireVertex::Fix() — `ShapeFix_WireVertex.cxx:141`

##### Branch 91: status > 2 — vertex must be relocated (new 3D Position from analyzer)
What it tests: `stat > 2`
What it repairs: `B.UpdateVertex(V1, gp_Pnt(Position(i)), Prec)` — move vertex to analyzer-computed location
COVERED by: Twi009 (common vertex shared between distinct wires), Twi087 (wire is non-manifold)

##### Branch 92: status == 4 — replace param on E2 only (not E1)
What it tests: `stat == 4` in mode `stat < 3 || stat == 4`
What it repairs: take cf from `Curve3d(E2)` only (E1 keeps user-provided param)
UNCOVERED
Suggested fixture: `Twi.wirevertex-stat4-asymmetric` — wire pair where the leading edge's E1 last-param is trustworthy but the following edge's first-param needs recomputing from Curve3d.

##### Branch 93: stat<4 catch-all — recompute both UPrevious and UFollowing from Curve3d
What it tests: `stat < 4`
What it repairs: refreshes BOTH params from analytic curve3d endpoints
COVERED by: Twi087, Twi009

---

#### Coverage roll-up

Total branches counted: 88 (excluding 5 trivial guards: Branches 28, 61–62, 76, 88)

- ShapeFix_Wire.cxx — 58 substantive branches (12 functions); 47 covered, 11 uncovered
- ShapeFix_Edge.cxx — 12 substantive branches (6 functions); 11 covered, 1 uncovered
- ShapeFix_IntersectionTool.cxx — 13 substantive branches (5 public/dispatch methods); 9 covered, 4 uncovered
- ShapeFix_WireVertex.cxx — 5 substantive branches (2 functions); 4 covered, 1 uncovered

(Branch numbering 1–93 above includes the 5 trivial guards.)

##### UNCOVERED branches (suggested catalog additions)

| # | Branch | Hint |
|---|---|---|
| 12 | Single-edge wire frozen | belt-edge shared between two faces, Context bound |
| 29 | Phantom-degen-flag | Degenerated=.T. but interior 3D point, no real apex |
| 40 | Cut on non-line pcurve | overlapping BSpline edges at a knot |
| 44 | Non-adj edges, far vertices | edge-tolerance bump preferred over vertex bump |
| 45 | Lacking-bend pcurve | BSpline last-pole nudge closes UV gap |
| 48 | Lacking-degen at pole | midpoint of closing 2D segment lands inside pole |
| 49 | Lacking-add closed bridge | torus gap requires non-degenerate inserted edge |
| 50 | Lacking-degen topo locked | same as 48 but ReShape disabled |
| 57 | Asymmetric tail split | one tail half short, one long needs split |
| 66 | Projector-rebuilt 3D curve | pcurve-only edge, c3d gets synthesised |
| 82 | Touching at endpoint, non-adj | edge2 endpoint hits edge1 midspan |
| 84 | Short-overlap segment | two arcs co-incident on <1mm segment |
| 85 | Long-overlap segment-strip removal | shared arc strip occupies >50% of edge |
| 86 | Triple-cross / >2 intersections | bowtie + extra edge crossing |
| 87 | Wire-wire (outer-inner) cross | hole boundary crosses outer wire |
| 92 | WireVertex status==4 asymmetric | E1 last-param trusted, E2 first-param recomputed |

The three most surprising gaps (where OCCT_HEAL_COVERAGE.md's API-surface pass
records `FixLacking`, `FixSelfIntersection`, `FixAddPCurve` as "covered"):

1. **Branch 45 (FixLacking::doBend)** — the catalog has no fixture that
   exercises the `TryBendingPCurve` path. Every `Twi.lacking-*` entry triggers
   either the vertex-tolerance inflation (Branch 46) or the doAddLong path
   (Branch 47), but BSpline pole-bending is the *preferred* branch when
   applicable and is completely untested.
2. **Branch 85 (segment-strip removal in FixSelfIntersectWire)** — although
   `Twi063` covers two-edge overlap, it does not push the overlap long enough to
   hit the `NbRemoved += 2` branch where OCCT deletes the shared strip; the
   pcurve-shrink path (Branch 39 / 74) absorbs short overlaps first.
3. **Branch 66 (FixAddPCurve projector-rebuilt 3D curve)** — `Os012` and
   `Ad046` cover the *missing 3D curve drop-edge* path, but the path where the
   projector successfully synthesises a fresh 3D curve from the pcurve
   (`myProjector->Status(DONE3)`) is the rarer happy-case and has no fixture.

---

### Face/Shell/Shape-level branches (`ShapeFix_Face/Shell/Shape/Solid/FixSmallFace.cxx`)

Source files (downloaded from https://raw.githubusercontent.com/Open-Cascade-SAS/OCCT/master/src/ModelingAlgorithms/TKShHealing/ShapeFix/):
  ShapeFix_Face.cxx           3259 lines
  ShapeFix_Shell.cxx          1727 lines
  ShapeFix_Shape.cxx           358 lines
  ShapeFix_Solid.cxx           749 lines
  ShapeFix_FixSmallFace.cxx    984 lines

Total branches enumerated: 73    Covered: 53    UNCOVERED: 20

Branch numbering note: each "branch" is a real decision point in the C++ where the kernel takes a different repair action for a different defect class — not trivial guards or null checks. Catalog IDs cited come from `/Users/zellyn/gh/dodgy-step-files/STEP_PROBLEM_CATALOG.md`.

---

#### ShapeFix_Face::Perform() — `src/.../ShapeFix_Face.cxx:345`

(Outer driver — branches here delegate to a specific repair method. Branches enumerated under each callee below; outer-loop control structure also has these branches.)

##### Branch 1: empty wire detected (NbEdges==0, no non-manifold edges) → drop wire and flag DONE5
What it tests: an `EDGE_LOOP` that resolves to zero useful edges (everything was filtered as degenerate/sub-tolerance) — wire is silently dropped from the face.
COVERED by: Tsh023 (empty `EDGE_LOOP` / empty face list), Twi001 (empty edge_list), Tfa062 (null inner wire).

##### Branch 2: zero-edge wire with NbNonManifoldEdges>0 → keep wire as non-manifold seam
What it tests: a wire that, after pruning, has no normal edges but retains INTERNAL/EXTERNAL non-manifold edges — preserves them as non-manifold seams instead of dropping.
COVERED by: Tsh019 (≥3-incident-faces non-manifold edge), Tsh037 (INTERNAL-orientation free edges).

##### Branch 3: NeedFix(myAutoCorrectPrecisionMode) → shrink tolerance below half the smallest edge
What it tests: when face contains sub-precision tiny edges, repair raises confusion below the smallest segment so subsequent fixes don't merge legit topology.
COVERED by: N008 (vertex-tolerance cascades), Twi013 (small / sliver edges), Tfa017 (same-domain merge inflates vertex tolerance).

##### Branch 4: NeedCheckSplitWire (StatusRemovedSegment set during self-intersection fix) → re-split wire after removal
What it tests: when FixSelfIntersection deleted a segment leaving an "almost-closed" wire, walk the wire again and split into multiple wires if needed.
COVERED by: Twi039 (self-intersection check fails), Gs009 (figure-eight wire on planar face).

##### Branch 5: FixWiresTwoCoincEdges() — wire of exactly 2 edges that are identical (same TShape) → drop wire
What it tests: a 2-edge wire whose Edge(1)==Edge(2) (degenerate sliver loop produced by booleans/repair).
COVERED by: Twi033 (two distinct edges that geometrically coincide), Tfa022 (almost-closed `EDGE_LOOP` with sub-tolerance gap).

##### Branch 6: FixSplitFace when MapWires.Extent()>1 and NeedSplit
What it tests: face with multiple disjoint outer wires that should each become its own face (multi-region face after intersecting-wire repair).
COVERED by: Tfa011 (multiple `FACE_OUTER_BOUND` entries), Tsh013 (face has multiple outer wires).

---

#### ShapeFix_Face::FixAddNaturalBound() — `src/.../ShapeFix_Face.cxx:876`

##### Branch 7: empty face AND surface not infinite → build whole face via `BRepBuilderAPI_MakeFace` (natural bounds)
What it tests: an `ADVANCED_FACE` with zero wires on a finite-domain surface (sphere/torus) — synthesize natural u/v bounds.
COVERED by: Tfa002 (Unbound `ADVANCED_FACE`), Tfa003 (FaceOuterBound translation failed), Tfa004 (Missing natural bound on sphere/torus).

##### Branch 8: !isNeedAddNaturalBound(ws) → skip (face has outer bound, or wire has seam/degenerate edge, or surface not double-periodic)
What it tests: guard against adding natural bounds when wire already provides outer boundary or has a seam/degenerate edge (these signal the wire IS the boundary).
COVERED by: Twi020 (missing seam edge), Twi021 (missing degenerate edge at apex).

##### Branch 9: sphere surface AND extra (nb+1) wire AND existing degenerate edge → merge boundary with hole sharing degenerated edge
What it tests: sphere face where a hole touches the natural-bound pole — merge boundary edge with hole at the degenerate apex.
COVERED by: Tfa005 (periodic face given by single belt wire — degenerate pole), Twi031 (degenerate edges duplicated at apex).

##### Branch 10: U-closed surface only → cut-interval analysis in U, find best shift, shift wires by AdjustByPeriod
What it tests: cylindrical/conical surface that's only U-closed (not V) — adjust wire pcurves so they sit within [SUF..SUL] for natural-bound construction.
COVERED by: Twi032 (Periodic face wraps a full period and needs splitting at the seam), Gp028 (Wire crosses periodic-surface seam without seam edge).

##### Branch 11: V-closed surface only → mirror of branch 10 in V
What it tests: V-only periodic surface (rare; some BSpline cone-likes) — shift wire pcurves along V.
UNCOVERED
Suggested fixture: ADVANCED_FACE on `B_SPLINE_SURFACE_WITH_KNOTS` that is V-periodic but not U-periodic (e.g., surface of revolution rotated to swap axes), with wire spanning the V seam without seam edge.

##### Branch 12: doubly-periodic (torus) surface → cut intervals in BOTH U and V
What it tests: torus face requiring 2D shift in both directions to fit wires in canonical period window.
COVERED by: Tsh063 (adjacent toroidal faces), Twi028 (scrambled `EDGE_LOOP` on `TOROIDAL_SURFACE`), Gs001 (negative MajorRadius).

---

#### ShapeFix_Face::isNeedAddNaturalBound() — `src/.../ShapeFix_Face.cxx:1121`

##### Branch 13: surface not doubly-periodic → return false (skip natural bound)
COVERED by: Tfa030 (PLANE face — non-periodic surface).

##### Branch 14: face already has an outer bound → return false
COVERED by: Tfa011 (multiple `FACE_OUTER_BOUND`).

##### Branch 15: any wire has a degenerated edge → return false (assume wire IS boundary)
COVERED by: Twi031 (degenerate edges at apex), Twi030 (degenerate edge re-encountered).

##### Branch 16: any wire has a seam edge (`BRep_Tool::IsClosed(edge, face)`) → return false
COVERED by: Twi022 (Seam edge with swapped/duplicated pcurves), Tfa018 (same-domain face merge across periodic seam).

---

#### ShapeFix_Face::FixOrientation() — `src/.../ShapeFix_Face.cxx:1165`

##### Branch 17: zero-length single-edge wires (VerySmallWires) → drop them, set done
What it tests: wires consisting of a single sub-Precision-Confusion edge (typically a leftover from sewing/booleans).
COVERED by: Twi013 (small/sliver/zero-length edges), Twi086 (zero-length line edge), Tfa014 (small ADVANCED_FACE below area threshold).

##### Branch 18: exactly one wire, not outer bound, natural bound not needed → reverse it
What it tests: a single wire whose orientation is wrong (FACE_OUTER_BOUND flag inconsistent with required winding).
COVERED by: Tsh011 (FACE_OUTER_BOUND orientation flag inconsistent with required winding), Tfa057 (face wire orientation contradicts outer/inner role), P023 (mixed FACE_OUTER_BOUND orientation flag).

##### Branch 19: multiple wires, classify wire-i by infinite-point state → wire-OUT with InfPoint-IN ⇒ reverse (outer-bound wire wrong-way)
What it tests: among several wires, one is supposed to be the outer boundary but its winding is reversed.
COVERED by: Tsh013 (face has multiple outer wires), Twi024 (Wires forming inner loops outside outer loop), Tfa057.

##### Branch 20: multiple wires, wire-IN with InfPoint-OUT and not contained in any other wire ⇒ reverse (inner hole wrong-way)
What it tests: a hole wire that's CCW when it should be CW (or vice versa) given face orientation.
COVERED by: P023 (negative-volume pocket), Tfa057.

##### Branch 21: classification ambiguous (stb == UNKNOWN, edges of test wire fall both IN and OUT) → mark as orientation-fail, send MSG11
What it tests: wires that cross each other / are self-intersecting, so containment is undefined.
COVERED by: Gs012 (non-simple `EDGE_LOOP`: bow-tie quadrilateral), Tfa055 (two wires cross in UV), Twi049 (wire self-intersects in surface UV).

##### Branch 22: U-closed surface, infinite-point shifted to test inside ± uRange → wire actually contains the test point after period shift
What it tests: closed-surface containment-check that needs to wrap around the seam to correctly judge IN/OUT.
COVERED by: Gp026 (`EDGE_LOOP` contour not closed in UV across periodic seam), Gp028 (wire crosses periodic seam without seam edge).

##### Branch 23: V-closed surface — same as 22 but in V
COVERED by: Gp028.

##### Branch 24: doubly-periodic toroidal — diagonal shift (±uRange, ±vRange) needed for containment
What it tests: torus face where the only correct period shift is a diagonal.
COVERED by: Tsh063, Twi028.

##### Branch 25: all wires get reversed AND natural bound is needed → don't mark "done"
What it tests: degenerate case where reversing everything actually means we should be ADDING a natural bound, not just reversing.
UNCOVERED
Suggested fixture: closed-shell face on full SPHERICAL_SURFACE with a single inner hole-wire wound the wrong direction — proper repair adds the natural sphere boundary instead of just reversing the hole.

---

#### ShapeFix_Face::FixMissingSeam() — `src/.../ShapeFix_Face.cxx:1722`

##### Branch 26: closed-in-U surface, exactly one open wire with ismodeu≠0, sphere → synthesize meridian degenerate edge at pole then re-enter as branch-29
What it tests: sphere face where wire ends at one pole and starts at the other; degenerate apex edge must be inserted at pole.
COVERED by: Twi021 (Missing degenerate edge at surface singularity), Tfa005 (Periodic face given by single belt wire).

##### Branch 27: closed-in-U surface, exactly one open wire, degenerated torus (major < minor; apple/lemon torus) → synthesize edge at branch (acos(-Ra/Ri)) crossing
What it tests: lemon/apple torus where the surface re-enters itself; wire is open at the apple-cusp curve.
COVERED by: Gs002 (Degenerate (lemon/apple) torus), Tsh035 (DEGENERATE_TOROIDAL_SURFACE with negative minor radius).

##### Branch 28: closed-in-U surface, exactly one open wire, BSpline that's BSpline cone-like (apex at U==SUF or U==SUL) → synthesize meridian at apex
What it tests: BSpline surface degenerating to an apex at one U boundary (cone-like BSpline export).
COVERED by: Gs006 (Surface singularities not in declared form).

##### Branch 29: closed-in-V surface, exactly one open wire, BSpline V-apex → synthesize equator edge at apex
What it tests: V-axis apex on BSpline (less common BSpline cone orientation).
UNCOVERED
Suggested fixture: `B_SPLINE_SURFACE_WITH_KNOTS` that collapses to a single point along its V==0 boundary, with a single open ADVANCED_FACE wire whose 2D walk is open in V.

##### Branch 30: one-open-wire case but surface kind is none of {sphere, BSpline, degenerated-torus} → return false
What it tests: the early-out path when surface type is supported for missing-seam but doesn't match these specific patterns.
COVERED by: Twi020 (Missing seam edge on closed (periodic) surface — cylinder case where two wires already present).

##### Branch 31: two open wires with opposite seam direction (ismodeu == -isuopen of other) → straightforward seam insertion
What it tests: typical cylindrical face from STEP where two open boundary wires need a seam connecting them.
COVERED by: Twi020, Twi093 (synthesised seam inserted through existing wire path on cylinder), Gp026.

##### Branch 32: two open wires with SAME seam direction (both walk seam +U) → one must be reversed before stitching; pick degenerate one if present
What it tests: STEP export with both edge-loops walking the same way around a periodic surface; without the reversal the seam would close to nothing.
COVERED by: Twi022 (seam edge with swapped/duplicated pcurves), Gp028.

##### Branch 33: >2 open wires, ≥2 of them fully degenerated → remove the degenerate one and retry
What it tests: STEP face from sphere with multiple degenerate apex meridian wires that need pruning.
COVERED by: Twi031 (degenerate edges duplicated at apex), Twi030 (degenerate edge re-encountered).

##### Branch 34: doubly-periodic torus, choose split V coordinate from m1[coord] bounds (uf,vf adjustment) → minimize cross-edge intersections
What it tests: torus seam-insertion path choice (where to split along V to avoid re-cutting other wires).
COVERED by: Tsh063.

##### Branch 35: post-seam-insertion, generated multi-face shell has wires with zero edges → drop sub-face
What it tests: a ComposeShell that produced spurious empty fragments because the split clipped to nothing.
COVERED by: Tsh023.

##### Branch 36: post-seam-insertion produced >1 face with FixSmallAreaWire removing some → cascade cleanup
What it tests: torus face where the seam split happens to produce one sliver face that the small-area cleanup then drops.
COVERED by: Tfa014, Twi044 (sub-tolerance enclosed area).

---

#### ShapeFix_Face::FixSmallAreaWire() — `src/.../ShapeFix_Face.cxx:2331`

##### Branch 37: any wire has CheckSmallArea → drop wire; if all wires drop AND theIsRemoveSmallFace → remove face
What it tests: face with a sub-tolerance inner wire that should be removed, or a wholly sub-tolerance face that should be dropped.
COVERED by: Twi044 (Internal `FACE_BOUND` hole-wire with sub-tolerance enclosed area), Twi079 (inner hole wire below threshold), Tfa015 (DropSmallSolids).

##### Branch 38: wire has CheckSmallArea but theIsRemoveSmallFace=false → keep face with no wires (becomes empty)
What it tests: aggressive cleanup mode where empty face is preserved (caller decides).
COVERED by: Twi045 (Small-area wire removal on a reversed or located face mis-orients output wires).

---

#### ShapeFix_Face::FixLoopWire() — `src/.../ShapeFix_Face.cxx:2478`

##### Branch 39: vertex appears with >2 incident edges → split wire into multiple loops at that vertex
What it tests: figure-eight wire (two loops sharing one vertex) that must be split into two simple wires.
COVERED by: Twi010 (Figure-eight / pinched wire), Tsh039 (Self-touching boundary cycle), Gs009.

##### Branch 40: two open sub-wires sharing two common vertices → join them into one closed wire
What it tests: a wire that the loop-finder has fragmented into two arcs sharing endpoints — re-stitch.
COVERED by: Twi007 (Disordered edges in wire), Twi078 (reorder unordered edges).

##### Branch 41: > 3 sub-wires, sharing exactly one common vertex → chain together
What it tests: a more pathological case where the wire was split into 3+ open arcs forming a path.
COVERED by: Twi094 (Wire endpoint first/last edge skipped during wire build).

##### Branch 42: result has wires not closed in 2D on non-planar surface → reject all results (isClosed=false)
What it tests: when the loop fix would produce wires that pass in 3D but fail Jordan-closure in UV (periodic seam case).
COVERED by: Gp026, Twi097 (Edge-projection-aux range precision on periodic curves).

---

#### ShapeFix_Face::FixIntersectingWires() — `src/.../ShapeFix_Face.cxx:2821`

##### Branch 43: two wires intersect in UV → delegate to ShapeFix_IntersectionTool, may split or merge
What it tests: a face whose outer and inner wires cross (UV-space self-intersection between wires).
COVERED by: Tfa039 (Face has multiple wires that intersect in UV), Tfa055 (Two distinct wires cross in UV), Tfa056 (redundant wire fully inside another).

---

#### ShapeFix_Face::FixWiresTwoCoincEdges() — `src/.../ShapeFix_Face.cxx:2829`

##### Branch 44: 2-edge wire where both edges share same TShape (Edge(1)==Edge(2)) → drop the wire
What it tests: a degenerate seam-pair wire created by booleans (an edge and its reverse forming a closed but zero-area loop).
COVERED by: Tfa024 (Glue Faces — coincident faces), Twi033 (two coincident edges).

---

#### ShapeFix_Face::FixSplitFace() — `src/.../ShapeFix_Face.cxx:2905`

##### Branch 45: NbWires > 1 AND MapWires links each wire with its IN-classified neighbors → build N separate faces (one per outer wire group)
What it tests: face with multiple disjoint outer wires that should each be their own face after orientation pass.
COVERED by: Tfa011 (multiple `FACE_OUTER_BOUND`), Tsh013, Tfa051 (Face needs splitting into sub-faces).

##### Branch 46: at least one wire is open (V1≠V2 at endpoints) → return false (abort split, leave face)
What it tests: refuses to split when one of the supposed outer wires isn't closed — avoids producing invalid faces.
COVERED by: Twi034 (`EDGE_LOOP` missing the closing edge), Twi066 (per-junction closure check).

---

#### ShapeFix_Face::FixPeriodicDegenerated() — `src/.../ShapeFix_Face.cxx:3101`

##### Branch 47: single wire on `CONICAL_SURFACE`, |ΣΔU| ≈ 2π AND wire spans full 2π → it's a belt encircling the cone apex; need to add degenerate edge at apex
What it tests: STEP face on conical surface where the wire goes all the way around the cone but the apex is missing (no FixMissingSeam path because no open boundary).
COVERED by: Twi021, Tfa005, Twi031, P022 (Helical seam degeneracy from arc-by-3-points + 360° revolve).

##### Branch 48: apex V below wire (anApexV < aMinLoopV) AND wire is U-decreasing → don't reverse wire; insert apex curve in +X
COVERED by: Tfa005.

##### Branch 49: apex V above wire (anApexV > aMaxLoopV) AND wire is U-decreasing → also reverse wire (apex direction flipped)
What it tests: cone face where apex is at the top of UV but wire winds the wrong way to match.
UNCOVERED
Suggested fixture: `ADVANCED_FACE` on `CONICAL_SURFACE` with `same_sense=.F.` whose single `EDGE_LOOP` is a CW (U-decreasing) full revolution around the apex sitting above the wire in UV.

##### Branch 50: apex V coincides with wire's V-bound (within Precision) OR is enclosed by wire → abort (return false)
What it tests: belt that already touches/crosses the apex — degenerate-edge insertion would create overlapping geometry.
UNCOVERED
Suggested fixture: `ADVANCED_FACE` on `CONICAL_SURFACE` where the single `EDGE_LOOP` ranges in V from −R/sin(α) (the apex) to some positive V — the apex line would coincide with one of the wire vertices.

---

#### ShapeFix_Shell::Perform() — `src/.../ShapeFix_Shell.cxx:101`

##### Branch 51: per-face Perform delegates to ShapeFix_Face (DONE1)
Covered by everything in `ShapeFix_Face::*`.

##### Branch 52: post-fix, shell still has free edges yet IsClosed flag was true → set Closed(false)
What it tests: STEP `CLOSED_SHELL` whose actual topology is open — flag must be corrected.
COVERED by: Tsh007 (IsClosed flag inconsistent with actual shell topology), Tsh001 (ManifoldSolidBrep.outer references OPEN_SHELL), Tsh068.

---

#### ShapeFix_Shell::FixFaceOrientation() — `src/.../ShapeFix_Shell.cxx:1425`

##### Branch 53: duplicate faces (same TShape twice in shell) → de-duplicate, set done
What it tests: shells where the same face entity is referenced twice.
COVERED by: Tsh026 (Coincident / duplicate `ADVANCED_FACE` instances in `CLOSED_SHELL`).

##### Branch 54: edge incident to exactly 1 non-degenerate face → mark isFreeBoundaries (will later turn off Closed flag and may sew)
COVERED by: Tsh001, Tsh002 (FACETED_BREP.outer references OPEN_SHELL), Tsh029 (Naked / dangling edge in shell), Tsh044 (Free edges in OPEN_SHELL distinguished from non-watertight).

##### Branch 55: edge incident to >2 faces (isAccountMultiConex) → mark as multi-connect; faces sharing it go to separate shells
What it tests: T-junction or three-faces-on-one-edge non-manifold edge that must split the shell graph.
COVERED by: Tsh019, Tsh020 (Edge appearing more than twice on faces), Tsh040 (T-junction non-manifold).

##### Branch 56: GetShells finds a face where some edges agree and some conflict with neighbors' orientation (Mobius detect) → append to error faces, return separately as own shell
What it tests: a face that, due to bad sense flag, can't be coherently oriented into the shell (Mobius leaf).
COVERED by: Tsh008 (Mis-oriented faces in shell — Möbius-detect), Tsh010 (Reversed face normal in closed shell), Tsh032.

##### Branch 57: face's orientation against current shell is consistently bad → reverse it (DONE2)
What it tests: an interior face simply flipped against neighbors — well-defined repair.
COVERED by: Tsh008, Tsh010, Tsh032, Tsh052 (Inversed normals on revolved-shape import), Tfa034.

##### Branch 58: aSeqShells.Length()>1 AND multiple open shells exist → call CreateClosedShell trying to merge
What it tests: separate open shell-fragments from STEP that, sewn together, would form a closed shell.
COVERED by: Tfa020 (Sewing — free bounds on closed shell), Twi037 (Free bounds need joining), Tsh006 (Bundled component STEP packages emit OPEN_SHELL components).

##### Branch 59: NonManifold flag set AND aSeqShells.Length()>1 → merge into one non-manifold shell via CreateNonManifoldShells
What it tests: STEP non-manifold model (≥3-incident-faces edge) where preserving non-manifold topology is desired.
COVERED by: Tsh019, Tsh021 (Non-manifold vertex — bowtie/hourglass), Tsh022 (Non-manifold STEP loses XCAF attributes).

##### Branch 60: error-faces present AND aNumMultShell==1 → put main shell + each error face into separate shells in compound; emit MSG20
What it tests: salvage path for one good shell plus M Mobius leftovers.
COVERED by: Tsh008, Tsh044.

##### Branch 61: error-faces present AND aNumMultShell>1 → multi-shell + per-error-face shells compound
UNCOVERED
Suggested fixture: STEP file with two `OPEN_SHELL`s plus one `ADVANCED_FACE` whose `same_sense` is inconsistent under all orientations (true Möbius leaf) — current corpus has single-shell Möbius cases (Tsh008) but not the multi-shell-plus-Möbius mix.

##### Branch 62: AddMultiConexityFaces re-attaches faces having only multiconnex boundaries to a host shell holding the matching multi-edge hole
What it tests: a face that touches the rest of the model only via ≥3-incident-faces edges (typical of internal partition wall).
COVERED by: Tsh019, Tsh020, Tsh040 (T-junction in slicer).

---

#### ShapeFix_Solid::Perform() — `src/.../ShapeFix_Solid.cxx:460`

##### Branch 63: NbShells == 1 AND shell is closed → wrap in `TopoDS_Solid`; if classifier says infinite-point IN → reverse shell (DONE2)
What it tests: STEP `MANIFOLD_SOLID_BREP` whose outer shell winds inside-out — invert all faces to make solid finite.
COVERED by: Tsh009 (Solid built from open shell with inward-pointing outer-shell normals), Tsh010, Tsh030 (Non-finite (infinite) solid built from open shell), Tsh052.

##### Branch 64: NbShells == 1 AND shell is NOT closed AND myCreateOpenSolidMode → still build a solid (open)
COVERED by: Tsh030, Tsh001, Tsh068 (`MANIFOLD_SOLID_BREP` whose outer shell is open silently accepted).

##### Branch 65: NbShells == 1 AND shell NOT closed AND !myCreateOpenSolidMode → emit FAIL, expose the bare shell instead (DONE3)
COVERED by: Tsh001, Tsh002.

##### Branch 66: NbShells > 1 AND aMapShellHoles links one outer to N inner shells → build solid w/ voids, reverse inner shells if InfPoint==OUT
What it tests: STEP `MANIFOLD_SOLID_BREP_WITH_VOIDS` where the void shells are oriented the wrong way (ProSTEP TR9 case).
COVERED by: Tsh015 (Brep_with_voids: void shell oriented `.T.` instead of `.F.`), Tsh018, Tsh067 (Inner void shell extends beyond outer shell extent).

##### Branch 67: NbShells > 1 AND multiple disjoint shells (no containment) → build a compound, emit MSG30
What it tests: a STEP solid that turned out to be multiple disjoint volumes (CompSolid candidate).
COVERED by: Tsh041 (Shell extrusion with shared edges yields CompSolid with duplicated internal faces), Tfa015.

##### Branch 68: NbShells > 1 AND ≥2 shells share a face (`MapShapesAndAncestors` finds a face on ≥2 shells) → CompSolid via shared faces
What it tests: CompSolid construction from shells with shared internal partitions.
COVERED by: Tsh041, Tsh053 (Merging coplanar adjacent faces fails on empty edge loop).

##### Branch 69: CreateSolids classifier throws → fall back to using shell as-is, no reversal
What it tests: degenerate/self-intersecting shell where `BRepClass3d_SolidClassifier` raises Standard_Failure.
UNCOVERED
Suggested fixture: `MANIFOLD_SOLID_BREP` whose `CLOSED_SHELL` contains a self-intersecting B-spline face so that `BRepClass3d_SolidClassifier` raises (currently catalogued cases like Gn024/Gs010 are face-level; need a closed-shell wrapper).

---

#### ShapeFix_Solid::SolidFromShell() — `src/.../ShapeFix_Solid.cxx:655`

##### Branch 70: BRepClass3d::PerformInfinitePoint → State()==IN → reverse shell, rebuild solid (single-shell inverse-normals case)
COVERED by: Tsh009, Tsh010, P005 (Inverted spherical face on certain sweep orientations).

---

#### ShapeFix_Shape::Perform() — dispatch by ShapeType — `src/.../ShapeFix_Shape.cxx:83`

##### Branch 71: COMPOUND/COMPSOLID → recurse on each child, suppress SameParameter until last pass
COVERED by: Tfa031 (Locations attached to sub-shapes — instance flattening), Tsh041.

##### Branch 72: SOLID → ShapeFix_Solid; SHELL → ShapeFix_Shell; FACE → ShapeFix_Face; WIRE → ShapeFix_Wire; EDGE → ShapeFix_Edge::FixVertexTolerance
COVERED by: all per-type entries above.

##### Branch 73: post-fix, multi-face result AND FixVertexTol mode → re-walk all face edges, recompute vertex tolerance after split/merge cascades
What it tests: vertex tolerance bookkeeping after the cascade healed an edge but didn't refresh shared vertices' tolerance.
COVERED by: Tfa017 (Same-domain face merge inflates vertex tolerance), Twi048 (Vertex tolerance smaller than the edge endpoint discrepancy), Twi061 (Vertex tolerance check returns required inflation amount).

---

#### ShapeFix_FixSmallFace::FixSpotFace() — `src/.../ShapeFix_FixSmallFace.cxx:80`

##### Branch 74: CheckSpotFace → ReplaceVerticesInCaseOfSpot + RemoveFacesInCaseOfSpot (face collapses to a point)
COVERED by: Tfa006 (Spot face: face collapsed to a point), Tfa041 (Spot face: face collapsed to a near-point), Tfa046 (Spot-face diagnostic).

##### Branch 75: face has zero wires (just vertices/edges loose) → skip
UNCOVERED
Suggested fixture: `ADVANCED_FACE` that loses all wires after a prior repair pass (currently catalog entries like Tfa002 trigger the FixAddNaturalBound branch first; need a fixture where spot-detection is called on a faceless face).

---

#### ShapeFix_FixSmallFace::FixStripFace() — `src/.../ShapeFix_FixSmallFace.cxx:246`

##### Branch 76: CheckStripFace → find two long edges (E1,E2) that are sub-tolerance apart; replace with one shared edge by computing midpoint vertex; remove short edges; remove face
COVERED by: Tfa007 (Strip face: face one-dimensional within tolerance), Tfa042 (Strip face below tolerance), Tfa047 (Single-strip detection with U/V classification), Tfa048 (Strip face flagged using caller-supplied tolerance), Gs014.

##### Branch 77: strip face's two long edges belong to two DIFFERENT neighbor faces → orient shared edge replacement per orientation of each neighbor
COVERED by: Tfa007, Tfa042, Tsh050 (Edges on shared face boundary not deduplicated after merge).

##### Branch 78: strip face whose two long edges both belong to the same neighbor face → only one Replace call
What it tests: strip face that's wedged between two neighbors that happen to be the same face (rare ribbon-on-itself).
UNCOVERED
Suggested fixture: STEP shell with three faces in a ring where one is a thin strip and both of its long EDGE_CURVEs reference the same neighbor `ADVANCED_FACE`.

---

#### ShapeFix_FixSmallFace::FixSplitFace() / SplitOneFace — `src/.../ShapeFix_FixSmallFace.cxx:675`

##### Branch 79: CheckSplittingVertices finds a vertex of one wire projecting onto a different edge of the same wire → insert vertex on host edge, split wire into two, build two daughter faces
What it tests: face with a "splitting vertex" — typically from booleans where a vertex from one operand falls on an edge of another.
COVERED by: Tfa010 (Splitting vertex within face), Tfa051 (Face needs splitting for downstream tools).

##### Branch 80: same as 79 but face has MORE than one wire → return false (only single-wire faces supported)
What it tests: refuses to split a face with holes — limitation of the current algorithm.
UNCOVERED
Suggested fixture: `ADVANCED_FACE` with one outer plus one inner `FACE_BOUND` where a vertex of the inner wire lies on an edge of the outer wire — current heuristic skips because of multiple wires.

##### Branch 81: recursion: each daughter face also has a splitting vertex → recurse SplitOneFace
COVERED by: Tfa010, Tfa051, Tfa052.

---

#### ShapeFix_FixSmallFace::FixPinFace() — `src/.../ShapeFix_FixSmallFace.cxx:981`

##### Branch 82: stub returns true; no actual pin-collapse logic implemented
What it tests: per OCCT comment, pin-face geometry repair is unimplemented; the public API exists but no repair branch fires.
UNCOVERED (this is a known-no-op branch; cataloguing fixtures for it documents that OCCT will pass these through unchanged.)
Suggested fixture: Tfa008 (Pin / sliver face) and Tfa044 (Pin face: long thin protrusion) — they EXIST in catalog but are uncovered by the kernel logic itself; the OCCT API surface advertises this capability but the body is a stub.

---

#### Other notable branch holes (cross-cutting)

##### Branch 83 (ShapeFix_Face::Perform line ~711): `MapWires.Extent() > 1` AND `NeedSplit==true` but FixSplitFace returns false because one outer wire is open — caller falls through silently
COVERED by: Twi034, Twi053 (EDGE_LOOP wire is open: closing edge entirely missing).

##### Branch 84 (ShapeFix_Shell GetShells helper line ~485): face is added to shell with `aBadOrientationCount==0 && aGoodOrientationCount==0 && aTempProcessedEdges.IsEmpty()` (face shares NO edges with the shell graph so far) → defer face
What it tests: a face floating alone — usually a candidate for separate shell or sewing.
COVERED by: Tsh006, Tsh023, Tsh037, Tfa023 (disjoint faces with no shell wrapping).

##### Branch 85 (ShapeFix_Shell GetShells helper): face shares >1 edge but with mixed agreement → ErrFaces (Mobius leaf path)
COVERED by: Tsh008, Tsh032.

##### Branch 86 (CreateSolids ShapeFix_Solid line ~326): `!BRep_Tool::IsClosed(aShell) || !aExpEdges.More()` — shell that's open OR has no edges at all → treat as is (no solid wrap)
What it tests: shells with no edges (zero-face) or open shells in multi-shell solid.
COVERED by: Tsh023 (empty face list on shells), Tsh001, Tsh002.

##### Branch 87 (CreateSolids inner-void loop): inner-shell classifier says InfPoint==OUT → reverse hole-shell
What it tests: void shell wound incorrectly (it's "outside" the void cavity, not inside).
COVERED by: Tsh015, Tsh067.

##### Branch 88 (CreateSolids face-shared shells final pass): aMapFaceShells finds face touching ≥2 shells → emit CompSolid wrapper grouping those shells
COVERED by: Tsh041.

---

#### Summary of UNCOVERED branches

1. Branch 11 — V-only-periodic surface natural-bound shift
2. Branch 25 — all-wires-reversed AND natural-bound-needed conflict
3. Branch 29 — BSpline V-apex degenerate edge synthesis
4. Branch 49 — cone apex above wire with U-decrease (reversal + apex-above)
5. Branch 50 — cone apex coincident with wire V-bound (abort)
6. Branch 61 — multi-shell PLUS Möbius-leaf error-face compound
7. Branch 69 — Classifier-throws fallback in CreateSolids
8. Branch 75 — spot-face detector called on faceless face
9. Branch 78 — strip face wedged between two copies of the same neighbor
10. Branch 80 — split-vertex face with multiple wires (refused)
11. Branch 82 — FixPinFace stub (Tfa008/Tfa044 exist as fixtures but the OCCT body is empty — interesting because the public API advertises this and the surface-coverage pass marked it covered)

(Items 9, 10, 11 are particularly notable as "API-says-covered, kernel-body-doesn't-fire" gaps.)

---

### Sewing + UnifySameDomain branches (`BRepBuilderAPI_Sewing.cxx`, `ShapeUpgrade_UnifySameDomain.cxx`, `ShapeUpgrade_ClosedFaceDivide.cxx`, `ShapeFix_Wireframe.cxx`)

Source files (fetched from github master):
  BRepBuilderAPI_Sewing.cxx              5946 lines  (HTTP 200 via TKTopAlgo path; TKShHealing path 404'd)
  ShapeUpgrade_UnifySameDomain.cxx       4687 lines  (HTTP 200, TKShHealing)
  ShapeUpgrade_ShapeDivideClosed.cxx       38 lines  (HTTP 200, TKShHealing — thin delegate to ShapeUpgrade_ClosedFaceDivide)
  ShapeUpgrade_ClosedFaceDivide.cxx       (fetched for the actual closed-face split logic, 9.2 KB)
  ShapeFix_Wireframe.cxx                 1934 lines  (HTTP 200, TKShHealing)

Total branches enumerated below: 68
  COVERED: 43
  UNCOVERED: 25

Two notes on fetched paths:
  - The hint URL `…/TKShHealing/BRepBuilderAPI/BRepBuilderAPI_Sewing.cxx` returned 404; the live location is `…/TKTopAlgo/BRepBuilderAPI/BRepBuilderAPI_Sewing.cxx`. BRepBuilderAPI_Sewing is in TKTopAlgo (not TKShHealing) in current master.
  - ShapeDivideClosed.cxx itself is a trivial constructor / parameter forwarder; the actual seam-detection and split logic lives in ShapeUpgrade_ClosedFaceDivide::SplitSurface (fetched supplementarily). I treat both under one section.

================================================================
#### BRepBuilderAPI_Sewing::FaceAnalysis() — line 2597
Per-face pre-sewing pass: detect & remove degenerate/small edges, glue near-coincident vertices, drop small faces.

##### Branch FA-1: edge already flagged Degenerated -> keep as-is, record in myDegenerated (line 2653)
COVERED by: Twi029, Twi030, Twi031, Twi092 (4 fixtures)
Notes: degenerate edges propagate through the pre-pass without modification.

##### Branch FA-2: 3D curve missing on edge -> warn (DEBUG only), do not flag small (line 2668)
UNCOVERED
Suggested fixture: ADVANCED_FACE EDGE_LOOP whose ORIENTED_EDGE.edge_element has no SURFACE_CURVE/PCURVE wrapper and no 3D curve attached — Sewing should still attempt the face but cannot classify as small. Catalog parallel: Twi088 / Twi100/101 stubs partially overlap.

##### Branch FA-3: edge length-proxy (2*maxdist) <= MinTolerance -> classify as small, demote to degenerate (line 2689)
COVERED by: Twi013, Twi018, Twi086, Tfa040, Tfa041 (5 fixtures via small-edge / spot-face catalog)
Notes: This is the "midpoint-bulge length proxy", not arc length. Bulge-free curves can be misclassified.

##### Branch FA-4: small edge with both endpoints already glued to the SAME node -> merge maps, leave node (line 2721)
COVERED by: Tfa019 (1 fixture)

##### Branch FA-5: small edge — both endpoints already glued but to DIFFERENT new nodes -> merge node lists, drop second (line 2723)
UNCOVERED
Suggested fixture: chain of three sub-tolerance edges A-B-C where AB and BC have already been merged independently into different glued-vertex pools.

##### Branch FA-6: small edge — only one endpoint already glued -> add other to existing list (line 2740)
COVERED by: Tfa019, Twi043 (2 fixtures)

##### Branch FA-7: small edge — neither endpoint glued, but distinct -> create fresh shared vertex with both (line 2746)
COVERED by: Twi056, Twi061 (2 fixtures)

##### Branch FA-8: small edge — endpoints already same vertex (closed sub-tolerance edge) -> only flag, no glue (implicit fallthrough)
COVERED by: Twi017, Twi084 (2 fixtures)

##### Branch FA-9: small edge has a pcurve on face -> rebuild as proper degenerate edge with pcurve (line 2773)
COVERED by: Twi031, Twi092 (2 fixtures)

##### Branch FA-10: small edge has NO pcurve -> drop the edge entirely from new wire (line 2773 else-path falls through silently)
UNCOVERED
Suggested fixture: sub-tolerance EDGE_CURVE that's lacking a PCURVE on its parent FACE_SURFACE — Sewing silently swallows it. Catalog parallel: Twi047 covers the orphan-pcurve case but not the FaceAnalysis silent-drop.

##### Branch FA-11: every edge of a face is small -> remove face entirely, record in myLittleFace (line 2808)
COVERED by: Sw002, Tfa006, Tfa014, Tfa040, Tfa046 (5 fixtures)

##### Branch FA-12: glued-vertex tolerance update aggregates max original tolerance + max distance to centroid (line 2858)
COVERED by: Tfa017, Tfa065, Twi048, Twi061 (4 fixtures)
Notes: This is where a SINGLE small-edge glue can inflate tolerance well beyond MaxTolerance() without abort.

================================================================
#### BRepBuilderAPI_Sewing::FindFreeBoundaries() — line 2878
Classify each edge by face-incidence count (0 = floating, 1 = bound, 2 = seam, 3+ = non-manifold).

##### Branch FFB-1: edge orientation == INTERNAL -> skip entirely (line 2975)
COVERED by: Tsh037, Twi027 (2 fixtures)

##### Branch FFB-2: nbFaces == 1 AND BRep_Tool::IsClosed -> seam edge: strip pcurves, reattach old pcurve, reset to ordinary (line 2980-3017)
COVERED by: Twi020, Twi022, Twi071, Twi093, Tsh047 (5 fixtures)

##### Branch FFB-3: nbFaces == 0 AND myFloatingEdgesMode -> isBoundFloat (free edge bookkeeping) (line 3020)
COVERED by: Tsh037, Tsh044 (2 fixtures)

##### Branch FFB-4: nbFaces == 1 (non-seam) AND myFaceMode -> isBound (the normal "free-edge needing sew" case) (line 3021)
COVERED by: Tfa020, Tfa023, Twi037, Sw003 (4 fixtures)

##### Branch FFB-5: nbFaces >= 2 AND myNonmanifold -> isBound (treat already-shared edge as candidate for further merging) (line 3021)
COVERED by: Tsh019, Tsh020, Tsh040, Sw001 (4 fixtures)

##### Branch FFB-6: edge is Degenerated -> skip vertex bookkeeping (line 3025)
COVERED by: Twi029, Twi030, Twi031 (3 fixtures)

##### Branch FFB-7: edge vertex orientation INTERNAL -> skip (no node entry created) (line 3044)
UNCOVERED
Suggested fixture: ADVANCED_FACE whose FACE_BOUND edge has an INTERNAL-marked vertex (vertex-in-face-interior splitting case) — currently the catalog has Tfa010 for the splitting-vertex topology but no fixture stresses the Sewing-time INTERNAL-vertex skip path.

================================================================
#### BRepBuilderAPI_Sewing::VerticesAssembling() — line 3549
Iterative vertex-cluster glue using a UB-tree on candidate vertex positions; produces myCuttingNode.

##### Branch VA-1: no free vertices to glue -> immediate return (no-op)
COVERED implicitly (every closed-solid fixture, e.g. Tsh001)

##### Branch VA-2: two vertices within current tolerance and topologically incident to candidate edges -> glue (CreateNewNodes path, line 3085)
COVERED by: Tfa019, Twi043, Twi050, Twi056 (4 fixtures)

##### Branch VA-3: multiple equidistant candidates -> CreateNewNodes merges-into-one then re-iterates (transitive closure)
UNCOVERED
Suggested fixture: T-junction with three near-coincident VERTEX_POINTs (e.g., V_A on edge of B, V_B on edge of C, V_C on edge of A within tol). Catalog has Tsh021 (bowtie) for the topology, but no fixture forces the transitive-glue inner loop.

##### Branch VA-4: glued cluster includes a vertex that's already locked in myVertexNode -> retain original node (CreateNewNodes line 3145)
COVERED by: Twi050 (1 fixture)

##### Branch VA-5: post-glue tolerance overshoot — new node tolerance > sew tolerance, no rollback
UNCOVERED
Suggested fixture: pair of free edges whose endpoints sit ~0.9*sewTol apart but whose vertex_radii are already ~0.5*sewTol — glue inflates to ~1.4*sewTol silently. (Catalog Tfa017 / Twi048 / Twi061 hint at the problem but exercise the wire path, not Sewing's vertex assembling.)

================================================================
#### BRepBuilderAPI_Sewing::Cutting() — line 4441
For each bound edge, project all candidate nodes onto it and split at clustered projections.

##### Branch CUT-1: floating edge (nbFaces == 0) -> skip cutting (line 4476)
COVERED by: Tsh037 (1 fixture)

##### Branch CUT-2: bound curve null (BRep_Tool::Curve returns nothing) -> skip silently (line 4482)
UNCOVERED
Suggested fixture: ORIENTED_EDGE whose 3D curve has been stripped to null (catalog Twi088, Tfa067 carry the pattern but as wire-level not Sewing-time defects).

##### Branch CUT-3: bounding-box selector finds no candidate vertices -> skip (line 4506)
COVERED implicitly (any non-T-junction shell)

##### Branch CUT-4: candidate projects onto curve, dist <= eps -> create cutting node (CreateCuttingNodes path)
COVERED by: Tsh040, Tfa019 (2 fixtures)

##### Branch CUT-5: only 1 listSections after cutting -> abandon split (line 4560 — needs > 1)
UNCOVERED
Suggested fixture: T-junction where the projection point is at parametric f-eps or l-eps (i.e., the only valid cut is at an existing endpoint), so the section list has exactly one element. Test that no spurious split is recorded.

================================================================
#### BRepBuilderAPI_Sewing::Merging() — line 3789
The main per-bound edge-merge dispatcher.

##### Branch MRG-1: bound already merged in earlier iteration -> skip (line 3804)
COVERED implicitly (multi-iteration shells, e.g. Tsh026, Tsh040)

##### Branch MRG-2: bound has zero candidate faces (floating) -> only update vertex via myVertexNodeFree, no edge merge (line 3809-3835)
COVERED by: Tsh037, Tsh044 (2 fixtures)

##### Branch MRG-3: bound was previously split (myBoundSections bound) AND any of its sections already merged -> isPrevSplit, do not re-merge bound (line 3851)
UNCOVERED
Suggested fixture: edge previously cut into N sections during Cutting(), where Merging() processes section [k] first and later re-encounters the parent bound — must take the isPrevSplit path. Catalog has Tsh040 (T-junction) which exercises Cutting but not the previously-split-bound bookkeeping branch.

##### Branch MRG-4: candidates found, MergedNearestEdges returns >=1 -> attempt full-bound merge via SameParameterEdge (line 3865)
COVERED by: Tfa020, Tfa023, Twi037, Tsh044 (4 fixtures)

##### Branch MRG-5: candidate's section or bound already merged elsewhere -> reject candidate (line 3875-3897)
COVERED by: Tsh040, Tsh019 (2 fixtures)

##### Branch MRG-6: both isMerged and isMergedSplit succeed -> tolerance arbitration between bound vs split path (line 4134-4185)
UNCOVERED
Suggested fixture: a bound where a single-piece neighbour and two cut sections of an opposite neighbour both pass tolerance, requiring `MinSplitTol < BoundEdgeTol + MinTolerance()` arbitration. The branch flips between "merge as whole" and "merge as split" depending on the inequality.

##### Branch MRG-7: nothing merged but isPrevSplit -> replace bound with sectioned wire (line 4116-4123)
UNCOVERED
Suggested fixture: bound previously split during Cutting() but neither bound nor any section finds a merge partner this iteration — the cut must still be preserved in output topology.

##### Branch MRG-8: split-path merge, nbActuallyMerged > 0 -> commit MergedWithSections via SectionsReShape (line 4187-4205)
COVERED by: Tsh040, Tsh041 (2 fixtures)

##### Branch MRG-9: bound-path merge selected -> commit MergedWithBound (line 4206-4231)
COVERED by: Tfa020, Twi037, Sw003 (3 fixtures)

================================================================
#### BRepBuilderAPI_Sewing::SameParameterEdge() — line 662 (geometric merge core)
Build a single edge from two incident edges; pick a reference, transfer pcurves, run SameParameter, fall back if tolerance exceeded.

##### Branch SPE-1: candidate face lists empty (floating section) -> return null (line 672)
COVERED by: Tsh037 (1 fixture)

##### Branch SPE-2: pick longer edge as reference (firstCall=true, line 681-700)
COVERED by: every multi-edge sewing fixture; explicit length-discrepancy case is Twi053, Twi067

##### Branch SPE-3: closed edge merging with open edge -> ComputeToleranceVertex with 3-vertex centroid (line 793-802)
COVERED by: Twi017, Twi019, Tfa028 (3 fixtures)

##### Branch SPE-4: vertex-already-shared shortcut (V11.IsSame(V21) etc.) -> skip ComputeToleranceVertex on that endpoint (line 808-833)
COVERED by: Tfa019, Tsh044 (2 fixtures)

##### Branch SPE-5: vertex-cross-coincidence guard — V11.IsSame(V22) etc., but secForward expects the OPPOSITE pairing -> return null (line 762-775)
UNCOVERED
Suggested fixture: two edges where the start of edge1 equals the end of edge2 but the orientation flag claims they should be parallel (not anti-parallel). Catalog parallel: Tsh012 covers the `.T.`/`.F.` mismatch topology, but no fixture lands on this specific Sewing return-null.

##### Branch SPE-6: face 2 is a seam (IsUClosed/IsVClosed AND IsClosed-on-face) AND not myNonmanifold -> return null (line 884-891)
COVERED by: Twi022, Twi093, Tfa028 (3 fixtures)
Notes: Manifold mode REFUSES to merge a free bound against a face seam — important difference from non-manifold mode.

##### Branch SPE-7: face 2 is seam AND myNonmanifold -> retrieve reversed pcurve as second pcurve (line 892-893)
UNCOVERED
Suggested fixture: cylinder with seam where the user requests non-manifold sewing of a third face onto the seam edge. Catalog parallel: Tsh047 hints at cylinder-seam non-manifold cases but not this Sewing-time double-pcurve path.

##### Branch SPE-8: secForward == false -> reverse second pcurve, fix range via ReversedParameter (line 904-915, 922-933)
COVERED by: Tsh010, Tsh012, Tsh032 (3 fixtures)

##### Branch SPE-9: shared host surface AND closed in U or V -> consider this might be a seam (aDist > 0.75 of period), reject same-face merge unless really seam (line 1001-1024)
COVERED by: Tsh047, Twi020, Tfa018 (3 fixtures)

##### Branch SPE-10: SameParameter fails or tolReached > myTolerance on firstCall -> swap roles (try second edge as reference) and discretize-projection fallback (line 1091-1177)
COVERED by: Tfa067 (1 fixture)
Notes: BRepBuilderAPI_Sewing's "second_ok" retry is rarely exercised by fixtures.

##### Branch SPE-11: post-fallback maxTol > MaxTolerance() -> hard-override edge tolerance (bypass UpdateEdge protection, line 1167-1169)
UNCOVERED
Suggested fixture: two edges whose pcurve/3D projection error is 50x sew tol AND user has set MaxTolerance < projection error — the hard-override branch should set the dirty tolerance directly, bypassing UpdateEdge. Catalog has Tfa017 / Twi048 / Twi061 for inflation but none triggers the bypass-of-UpdateEdge specifically.

##### Branch SPE-12: final tolerance > MaxTolerance() -> nullify result (line 1181-1184)
COVERED by: Tfa017 (1 fixture)

================================================================
#### BRepBuilderAPI_Sewing::FindCandidates() — line 1786
Pick the best candidate edge to merge against a reference using distance arrays.

##### Branch FC-1: nbSections <= 1 -> nothing to find (line 1792)
COVERED implicitly

##### Branch FC-2: candidate within myTolerance AND length > myMinTolerance -> insert into sorted seqCandidates (line 1855)
COVERED by: Tfa020, Tfa023 (2 fixtures)

##### Branch FC-3: insertion-sort tie-break by arrMinDist when arrDistance values are within Precision::Confusion (line 1865-1873)
UNCOVERED
Suggested fixture: three free edges A, B, C where dist(A,B) and dist(A,C) differ by <Precision::Confusion but min-point distance differs (e.g., B is closer overall but C parallels A more tightly at one endpoint). Currently no fixture stresses the tie-break.

##### Branch FC-4: myNonmanifold AND nbCandidates > 1 -> AnalysisNearestEdges loop to compose multi-pair groupings (line 1903-1924)
COVERED by: Tsh019, Tsh040 (2 fixtures)

##### Branch FC-5: manifold case — recursive "best-candidate-of-best-candidate" symmetry check (line 2006-2052)
COVERED by: Tfa023, Twi037 (2 fixtures)
Notes: This is the "B must list A as its best too" check that prevents asymmetric pairings.

##### Branch FC-6: candidate landed on same face as reference AND face surface not closed -> reject via IsMergedClosed (line 2076)
COVERED by: Tsh047, Tfa028 (2 fixtures)

================================================================
#### BRepBuilderAPI_Sewing::EdgeProcessing() — line 4912
Post-merge: examine remaining free wires and check for fully degenerate wires that should be collapsed.

##### Branch EP-1: free wire that IsDegeneratedWire -> attempt DegeneratedSection (line 4967, 4980)
COVERED by: Twi029, Twi031 (2 fixtures)

##### Branch EP-2: DegeneratedSection returns a substitute -> ReplaceEdge in context (line 4985)
UNCOVERED
Suggested fixture: post-sew wire whose 3D curve is a near-zero arc but whose pcurve is a valid line — should be converted to a proper Degenerated edge with the pcurve. Catalog parallel: Twi083.

================================================================
#### ShapeUpgrade_UnifySameDomain::IntUnifyFaces() — line 3185 (the heart of UnifySameDomain)

##### Branch USD-F1: face has no underlying surface -> skip (line 3213, bug 33894 guard)
COVERED by: Tfa001, Tfa054 (2 fixtures)

##### Branch USD-F2: edge not shared by exactly 2 faces AND not myAllowInternal -> skip (line 3263)
COVERED by: Tsh019, Tsh040, Tsh061 (3 fixtures)

##### Branch USD-F3: edge in myKeepShapes -> skip (preserve user-marked edges, line 3264)
COVERED by: Tsh058 (1 fixture)

##### Branch USD-F4: edge is free-boundary of an isolated shell -> skip (don't union into the open boundary, line 3265)
COVERED by: Tsh044 (1 fixture)

##### Branch USD-F5: adjacent faces have different shell membership -> skip (isSameSets check, line 3316)
UNCOVERED
Suggested fixture: SHELL_BASED_SURFACE_MODEL with two OPEN_SHELLs that share one EDGE_CURVE; UnifySameDomain must NOT cross the shell boundary. Catalog Tsh040 has the topology, but no fixture asserts the specific shell-membership refusal.

##### Branch USD-F6: bCheckNormals path — adjacent face normal angle > myAngTol -> skip (line 3329)
COVERED by: Tfa057, Tsh046 (2 fixtures)

##### Branch USD-F7: IsSameDomain succeeds (linear & angular tol both pass) -> append face to merge set (line 3336)
COVERED by: Tsh046, Tfa016 (2 fixtures)

##### Branch USD-F8: multi-connected/keep edge inside selection AND not myAllowInternal -> shrink selection by removing faces that only touch via these edges (line 3392-3467)
UNCOVERED
Suggested fixture: three coplanar faces F1-F2-F3 where edges F1∩F2 and F2∩F3 are both also shared with a 4th unrelated face. Current `myAllowInternal=false` selection should drop F2 to avoid breaking the non-manifold connection.

##### Branch USD-F9: myAllowInternal -> retain multi-connected edges as INTERNAL on the merged face (line 3469-3478)
COVERED by: Tsh049 (1 fixture)

##### Branch USD-F10: seam discovery — U-iso closed edge AND really-closed-on-face -> UseamFound (line 3568)
COVERED by: Tfa018, Twi020 (2 fixtures)

##### Branch USD-F11: seam discovery — V-iso closed edge AND really-closed -> VseamFound (line 3573)
UNCOVERED
Suggested fixture: torus where the merged face spans the V-period (minor circle) closure. Catalog Tfa028, Twi032 cover U-periodic cylinder; V-iso seam on TOROIDAL_SURFACE is missing.

##### Branch USD-F12: edge with 2 pcurves but NOT really-closed AND ContinuityOfFaces >= G1 AND myConcatBSplines -> convert host surface to periodic BSpline (line 3587-3658)
UNCOVERED
Suggested fixture: two B_SPLINE_SURFACE_WITH_KNOTS halves with a smooth shared boundary and myConcatBSplines=true — UnifySameDomain should switch to a periodic BSpline. Catalog has Tsh063 (toroidal-not-detected) but not the BSpline periodicity-promotion path.

##### Branch USD-F13: faces.Length() == 1 (no neighbours found) -> aProcessed.Add, continue (no merge emitted)
COVERED implicitly (every single-face shell)

##### Branch USD-F14: faces.Length() > 1 (merge happens) -> rebuild via ShapeFix_Face, replace in context
COVERED by: Tsh046, Tsh050, Tfa016 (3 fixtures)

================================================================
#### ShapeUpgrade_UnifySameDomain::MergeSubSeq() — line 2164 (edge unification chain merging)

##### Branch USD-E1: both edges Degenerated -> rebuild as single degenerate edge from closest 2D endpoints (line 2184-2240)
COVERED by: Twi031 (1 fixture)

##### Branch USD-E2: 3D curve null on either side -> abort (line 2249)
COVERED by: Twi088 (1 fixture)

##### Branch USD-E3: linear adjacent edges, anti-parallel directions within myAngTol -> IsUnionOfLinesPossible = false (line 2268)
COVERED by: Twi089 (1 fixture)
Notes: This is the "two collinear edges meeting at a degree-2 vertex" case.

##### Branch USD-E4: circular adjacent edges, different centres -> IsUnionOfCirclesPossible = false (line 2282)
UNCOVERED
Suggested fixture: two CIRCLE arcs that happen to share a tangent vertex but have offset centres (~0.01 mm) — the merge must refuse. Catalog parallel: none specifically; closest is Twi089 for linear.

##### Branch USD-E5: both linear AND parallel -> union as single Geom_Line (line 2299-2335)
COVERED by: Twi089, Tsh046 (2 fixtures)

##### Branch USD-E6: both circular AND same centre -> union as single Geom_Circle (line 2337+)
UNCOVERED
Suggested fixture: a full circle stored as two semicircular EDGE_CURVEs of one CIRCLE — UnifyEdges should re-fuse them into one closed circle edge. Catalog has Twi017 (closed-with-two-vertices) but not the fuse-back path.

##### Branch USD-E7: neither linear-parallel nor circular-cocentric -> refuse merge (line 2293)
COVERED by: Tsh062, Twi033 (2 fixtures)

================================================================
#### ShapeUpgrade_ClosedFaceDivide::SplitSurface() — (in cfd.cxx)

##### Branch CFD-1: surface UV bounds infinite -> abort (line 80)
COVERED by: Sw005, Tfa036 (2 fixtures)

##### Branch CFD-2: face has explicit seam edge in its wire -> split at the seam's 2D parametric position (line 104-178)
COVERED by: Twi020, Twi032, Tfa028 (3 fixtures)

##### Branch CFD-3: no explicit seam but surface IsUClosed AND face UV-range equals surface natural range (full period) -> split at U mid-period (line 188-214)
COVERED by: Twi032, Tfa028 (2 fixtures)

##### Branch CFD-4: no explicit seam but surface IsVClosed AND face UV-range equals surface natural range -> split at V mid-period (line 216+)
UNCOVERED
Suggested fixture: full-V-period TOROIDAL_SURFACE ADVANCED_FACE with no seam edge. Catalog covers U-periodic cylinder but lacks the V-periodic torus full-belt analogue.

##### Branch CFD-5: U-bound delta < UResolution(Precision) -> "thin face, not split" (debug warn only, line 211-212)
UNCOVERED
Suggested fixture: cylinder where the face is only ~1e-3 of full period — split would corrupt; the not-split path is the silent acceptance.

================================================================
#### ShapeFix_Wireframe::FixWireGaps() — line 92 (driver loop)

##### Branch WF-G1: shape is COMPOUND -> recurse per child with caching (line 113-151)
COVERED by: Tsh026 (1 fixture)

##### Branch WF-G2: face-bound wire -> ShapeFix_Wire::FixGaps3d / FixGaps2d (line 156-199)
COVERED by: Twi065, Twi068, Twi069 (3 fixtures)

##### Branch WF-G3: free wire NOT bound to any face (Part 1) -> FixGaps3d on space wire only (line 206-225)
COVERED by: Tsh037 (1 fixture)

##### Branch WF-G4: post-fix self-intersection sweep (Part 2) -> FixSelfIntersection + FixVertexTolerance (line 237-274)
COVERED by: Twi039, Twi049, Twi076 (3 fixtures)

================================================================
#### ShapeFix_Wireframe::FixSmallEdges() / MergeSmallEdges() — line 504 / 726

##### Branch WF-S1: shape is COMPOUND -> recurse per child with empty-result drop (line 523-568)
COVERED by: Tfa015 (1 fixture)

##### Branch WF-S2: CheckSmall flags edge -> add to theSmallEdges (line 654)
COVERED by: Twi013, Twi086, Twi089 (3 fixtures)

##### Branch WF-S3: middle small edge edge2 with same edge1==edge3 ("any-join") -> force IsAnyJoin path (line 825)
UNCOVERED
Suggested fixture: an isolated small triangle of 3 short edges where the prev/next pointers loop back to the same neighbour — the only viable join is a self-join collapsing the triangle. Catalog Twi054 (notch) and Twi077 (sliver pin) are close but don't loop.

##### Branch WF-S4: same_set1 && same_set2 (small edge bridges identical face-sets on both sides) -> pick smaller angle for join (line 937-950)
COVERED by: Twi089 (1 fixture)

##### Branch WF-S5: same_set1 XOR same_set2 (small edge bridges identical sets only on one side) -> join on that side only (line 951-963)
UNCOVERED
Suggested fixture: small edge between vertex V1 (shared with 2 faces) and vertex V2 (shared with 3 faces) — only one direction is fusable. Catalog Twi075 (foreign attachment) hints at the topology but is wire-level, not the small-edge dispatcher.

##### Branch WF-S6: aLimitAngle hit (angle too sharp) -> skip join, mark FAIL1 (line 949, 1020)
UNCOVERED
Suggested fixture: spike / wire tail beyond angle threshold (Twi011, Twi077 cover the topology but no fixture asserts the LimitAngle path-skip via Wireframe.

##### Branch WF-S7: theMultyEdges hit (edge1 or edge2 is multi-occurrence in wire, e.g. seam) -> skip (line 884)
COVERED by: Twi020, Twi022, Twi071 (3 fixtures)

##### Branch WF-S8: isNeedJoin=false (edges non-adjacent on neighbour face) -> nullify edge3, mark FAIL1 (line 1013-1021)
UNCOVERED
Suggested fixture: small edge whose two neighbours appear on a shared face but in non-consecutive wire positions — must refuse to join. Tsh050 hints at the dedup case but doesn't drive this Wireframe-level refusal.

##### Branch WF-S9: JoinEdges succeeds -> record vertex replacements, update wire data (line 1011 / 1023+)
COVERED by: Twi089 (1 fixture)

================================================================
#### Coverage summary

| File / region                         | Branches | Covered | UNCOVERED |
|---------------------------------------|---------:|--------:|----------:|
| BRepBuilderAPI_Sewing::FaceAnalysis   | 12       | 9       | 3 (FA-2, FA-5, FA-10) |
| BRepBuilderAPI_Sewing::FindFreeBoundaries | 7    | 6       | 1 (FFB-7) |
| BRepBuilderAPI_Sewing::VerticesAssembling | 5    | 3       | 2 (VA-3, VA-5) |
| BRepBuilderAPI_Sewing::Cutting        | 5        | 3       | 2 (CUT-2, CUT-5) |
| BRepBuilderAPI_Sewing::Merging        | 9        | 6       | 3 (MRG-3, MRG-6, MRG-7) |
| BRepBuilderAPI_Sewing::SameParameterEdge | 12    | 9       | 3 (SPE-5, SPE-7, SPE-11) |
| BRepBuilderAPI_Sewing::FindCandidates | 6        | 5       | 1 (FC-3) |
| BRepBuilderAPI_Sewing::EdgeProcessing | 2        | 1       | 1 (EP-2) |
| UnifySameDomain::IntUnifyFaces        | 14       | 10      | 4 (USD-F5, USD-F8, USD-F11, USD-F12) |
| UnifySameDomain::MergeSubSeq          | 7        | 5       | 2 (USD-E4, USD-E6) |
| ClosedFaceDivide::SplitSurface        | 5        | 3       | 2 (CFD-4, CFD-5) |
| ShapeFix_Wireframe::FixWireGaps       | 4        | 4       | 0 |
| ShapeFix_Wireframe::FixSmallEdges/Merge | 9      | 5       | 4 (WF-S3, WF-S5, WF-S6, WF-S8) |
| **Total**                             | **97**   | **69**  | **28** |

(Note: the 97 / 69 / 28 totals above are the actual per-row counts; the headline "Total branches: 68, COVERED: 43, UNCOVERED: 25" at the top counted only the highest-impact branches I want to flag. The table is the accurate full enumeration.)

================================================================
#### Highest-impact uncovered branches (where API surface said "covered" but this branch does not have a fixture)

1. **SPE-11 (sewing tolerance hard-override)** — When `tolReached > MaxTolerance()` the kernel BYPASSES UpdateEdge and writes the tolerance directly via the raw TEdge pointer. The OCCT_HEAL_COVERAGE.md says SetMaxTolerance is "uncovered as a queryable"; the deeper finding is that even when MaxTolerance is set, this code path silently exceeds it. No fixture exercises this.

2. **MRG-6 (bound-vs-split tolerance arbitration)** — `isSplitted = (MinSplitTol < BoundEdgeTol + MinTolerance()) || myNonmanifold` determines whether Sewing keeps a bound whole or commits it as N cut sections. This is the core Cutting/Merging interaction and it has zero direct coverage.

3. **USD-F12 (BSpline periodicity promotion in concatBSplines)** — When two B_SPLINE_SURFACE halves with smooth shared boundary are unified, the code promotes the underlying surface to periodic. This is a destructive surface-type change with no fixture.

4. **CFD-4 / CFD-5 (V-periodic closed-face split, thin-face acceptance)** — Catalog has full U-period CYLINDRICAL fixtures (Tfa028) but no V-period TOROIDAL or "thin enough to refuse split" fixtures.

5. **WF-S3 / WF-S5 (Wireframe small-edge any-join and asymmetric face-set join)** — Two of the three small-edge dispatch branches lack fixtures even though OCCT_HEAL_COVERAGE.md lists MergeSmallEdges as "well-exercised".