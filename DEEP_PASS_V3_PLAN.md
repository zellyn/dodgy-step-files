# Deep-pass v3 — rich-prose defect-class enumeration

> Successor to v1.3.0's `OCCT_HEAL_COVERAGE_V2.md`. The v2 pass enumerated 3,399 branches with 1-2 sentences per branch ("here's a branch, here's its rough defect class"). v3's goal is to make each branch's description **good enough to (a) recreate the defect input, or (b) be falsified by an adversarial reader** — i.e. minimum-reproducer + falsifiable-claim per branch.

## State-of-play (anyone picking up mid-stream: start here)

**Stage**: Validation slice in flight — 20 high-leverage OCCT methods being re-passed with the rich-prose schema. If validation looks good, scale to all 320 OCCT methods + 151 mesh methods.

**Outputs land in**:
- `/tmp/v3-deep-<method-id>.json` — one file per method worker
- `OCCT_HEAL_COVERAGE_V3.md` — aggregated rich-prose coverage map (not written yet; will appear after first scaled pass)
- This doc — methodology + plan + slice contents

**To resume after a session restart**:
1. `ls /tmp/v3-deep-*.json` — see what's already enumerated
2. Compare against the 20-method validation list in §"Validation slice" below
3. Launch a new worker for any missing method using the prompt template in §"Worker prompt template"
4. After all 20 done, validate the schema by adversarial-reading 2-3 random outputs (does the prose meet the falsifiability bar?)
5. If yes, scale to remaining 300 methods. If no, refine the schema, re-run the slice.

## Rich-prose schema (per branch)

Each branch in a worker's JSON output carries:

```json
{
  "defect_class_id": "ShapeFix_Wireframe.MergeSmallEdges.tangent_divergence_above_angular_tol",
  "file_line": "ShapeFix_Wireframe.cxx:894",
  "brief": "1-sentence summary",
  "falsifiable_claim": "Without this branch, the kernel would [specific wrong outcome]. Test: [observation that distinguishes correct from incorrect behavior].",
  "minimal_reproducer": "Construct [specific input shape with concrete parameter values]. Trigger by [specific kernel call]. Expected without branch: [bad result]. Expected with branch: [correct result].",
  "defect_axis": "input-shape | healer-state | kernel-pair | conformance-probe | encoding | tolerance | ...",
  "introducing_commit_hint": "if known from comment / commit reference / Mantis ID above the branch",
  "search_anchors": ["…", "…"]
}
```

**Falsifiability bar**: an adversarial agent reading the description should be able to either (a) write a STEP fixture that demonstrates the defect, or (b) say "no, this isn't a real defect class because X". If the description is too vague for either, the worker must produce richer prose.

## Methodology for big functions (>300 lines)

Two-level decomposition:

**Pass 1 — outline worker** (1 agent per big function): reads the whole function, produces a structured phase outline:
```
ShapeFix_Wireframe::MergeSmallEdges (1200 lines, 65 branches)
├─ Phase A (lines 735–820): candidate-pair discovery — N branches
├─ Phase B (lines 821–1020): geometry/tangent validation — N branches
└─ ...
```
Output: `/tmp/v3-outline-<method-id>.json` (small JSON with phase boundaries + brief per-phase descriptions)

**Pass 2 — section workers** (1 per phase): each gets the outline + their phase's 100–300 lines, produces rich per-branch descriptions per the schema above.

For methods <300 lines, skip pass 1 and go straight to pass 2.

## Validation slice (20 methods)

These 20 methods exercise the methodology against cases where we already know there's interesting content:

### Large singletons (7) — need pass-1 outline + pass-2 section workers
- `ShapeFix_Wireframe.MergeSmallEdges` (1200 lines, 65 branches)
- `ShapeUpgrade_UnifySameDomain.IntUnifyFaces` (1129 lines, 62 branches)
- `ShapeFix_IntersectionTool.FixSelfIntersectWire` (798 lines, 43 branches)
- `ShapeFix_FaceConnect.Build` (770 lines, 37 branches)
- `ShapeFix_IntersectionTool.FixIntersectingWires` (695 lines, 51 branches)
- `ShapeFix_Face.FixMissingSeam` (604 lines, 26 branches)
- `BRepBuilderAPI_Sewing.SameParameterEdge` (517 lines, 30 branches)

### Cases with known-interesting findings (13)
- `ShapeAnalysis_ShapeTolerance.InTolerance` — VERTEX `tol >= valmax` looks like a source bug
- `ShapeFix_FixSmallFace.FixPinFace` — no-op stub; fixtures Tfa008/Tfa044 exercise nothing
- `BRepLib.EncodeRegularity` — thin wrapper; real logic in ContinuityOfFaces
- `BRepLib.ContinuityOfFaces` — G2 principal-curvature-direction-alignment branch is UNCOVERED
- `BRepLib.SameParameter` (486-line overload) — `BSpline_C0_DISCONTINUITY` + arc-length-reparam logic
- `ShapeUpgrade_ConvertCurve2dToBezier.Compute` + `ShapeUpgrade_ClosedFaceDivide.SplitSurface` — intricate periodic-surface seam handling, 127 branches
- `ShapeFix_Wire.FixSelfIntersection` — medium-size core repair
- `ShapeFix_Face.FixOrientation` — Möbius detection, periodic wrap-around
- `ShapeAnalysis_Wire.CheckLoop` — multi-vertex-loop heuristic
- `ShapeFix_Edge.FixAddPCurve` — seam-on-doubly-closed-surface, ProSTEP path
- `ShapeFix_Wireframe.FixSmallEdges` + `ShapeFix_Wireframe.FixWireGaps` — gap detection
- `ShapeUpgrade_UnifySameDomain.MergeSeq` + `MergeSubSeq` — sequence merging

## Worker prompt template

(Use this for each method. Substitute `{METHOD_ID}`, `{FILE_PATH}`, `{LINE_RANGE}`, `{OUTLINE_HINT}`.)

```
You are a per-method DEFECT-CLASS ENUMERATOR for OCCT healing coverage v3.

Your target: `{METHOD_ID}` in {FILE_PATH} lines {LINE_RANGE}.
{OUTLINE_HINT}  (only for pass-2 section workers; contains phase-A through phase-F descriptions)

Fetch the source via WebFetch from
https://raw.githubusercontent.com/Open-Cascade-SAS/OCCT/master/{FILE_PATH}

For EACH if/else if branch in this method (or this phase, if pass-2), produce a record matching the v3 schema:
- defect_class_id, file_line, brief
- falsifiable_claim (specific wrong outcome + observation that distinguishes)
- minimal_reproducer (specific input shape with parameter values + how to trigger)
- defect_axis, introducing_commit_hint (if shown), search_anchors

The bar: an adversarial agent reading your description should be able to (a) write a STEP fixture demonstrating the defect, OR (b) say "no, this isn't a real defect class because X". If you can't write a description rich enough for either, mark the branch `low_confidence: true` and explain why.

Output JSON to `/tmp/v3-deep-{METHOD_ID}.json` (replace dots with underscores in id).

READ-ONLY. No code copying — only prose-laundered descriptions.
```

## Progress tracker (update as we go)

| Method | Status | Output file | Worker agent ID |
|---|---|---|---|
| (large singletons) | | | |
| ShapeFix_Wireframe.MergeSmallEdges | pending | `/tmp/v3-deep-ShapeFix_Wireframe_MergeSmallEdges.json` | |
| ... | | | |

(This table will be filled in as workers complete.)
