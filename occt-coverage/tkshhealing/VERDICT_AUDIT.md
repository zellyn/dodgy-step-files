# TKShHealing coverage-verdict adversarial audit

Audit of `occt-coverage/tkshhealing/problems.json` (60 problem classes: 35 COVERED / 20
PARTIAL / 5 GAP), produced by a separate agent. Per house rule, no sweep verdict is
trusted without independent structural verification: for every row below, the fixture's
actual `.stp` bytes were read entity-by-entity (not just its header comment) and cross-checked
against its `STEP_PROBLEM_CATALOG.md` entry and the claimed OCCT mechanism.

Methodology: 20/35 COVERED sampled (stratified across small- and large-fixture-count
problems), all 5/5 GAP audited adversarially with hard catalog re-search, 8/20 PARTIAL
sampled with "is the missing variant really missing" re-search. Two parallel audit passes
plus the author's own direct reads; every GAP finding and the one PARTIAL overturn were
independently re-verified against raw bytes by the report author before inclusion.

## Headline

| Verdict class | Sampled | AGREE (verdict correct) | OVERTURN | Error rate |
|---|---:|---:|---:|---:|
| COVERED | 20 / 35 | 20 | 0 | **0%** verdict-level; but 2/20 problems (10%) cite at least one fixture that does *not* genuinely exercise the mechanism (verdict survives on other cited fixtures) |
| PARTIAL | 8 / 20 | 7 | 1 | **12.5%** — one problem's "missing variant" claim is factually wrong; a clean fixture exists uncited |
| GAP | 5 / 5 | 5 | 0 | **0%** — all 5 GAP calls independently confirmed, one (`tkshh-splitting-vertex-face`) confirmed exhaustively (17/17 candidate fixtures read) |

**Bottom line**: the original agent's verdicts are structurally sound at the pass/fail
level (0 outright false COVERED, 0 false GAP). The one real defect found is a **coverage
under-count**: `tkshh-edge-missing-pcurve` should be upgraded from PARTIAL to (at minimum)
a stronger PARTIAL / COVERED, because fixture **Gp012** — sitting in the same catalog
section (`§12.2a pcurve`) as fixtures the agent *did* cite for this exact problem — cleanly
demonstrates the subvariant its own notes call "missing." This points to an incomplete
catalog search rather than a bad reading of evidence. Secondary finding: 2 of ~55 individual
fixture *citations* inside otherwise-correct COVERED entries are keyword-adjacent rather
than genuine (listed below); dropping them doesn't change either verdict.

## GAP audit (5/5, adversarial)

| problem_id | original verdict | AGREE/OVERTURN | evidence |
|---|---|---|---|
| `tkshh-splitting-vertex-face` | GAP | **AGREE** | Read all 17 catalog fixtures titled for `CheckSplittingVertices`/`FixSplitFace` (Tfa010, Tfa079, Tfa085, Tfa094, Tfa098, Tfa104, Tfa117, Tfa118, Tfa129, Tfa136, Tfa145, Tfa149, Tfa163, Tfa169, Tfa173, Tfa183, Tfa210, Tfa239 — 18 checked, one over the claimed count). Every one either (a) encodes the "splitting" vertex as a genuine shared topological endpoint (`Tfa010`'s bottom edge is pre-split at V7; `Tfa094`'s inner wire reuses outer hex vertex `#12` verbatim) — exactly the case OCCT's own `V.IsSame(V1)\|\|V.IsSame(V2)` guard skips — or (b) tests an unrelated `FixSplitFace` code path (multi-zone split, tangent splitter, out-of-range splitter, coincident sliver, NURBS containment bias, 3-edge non-manifold vertex, degenerate zero-length edge, open inner wire, N>5-edge star hub). `Tfa129`'s own comment describes a T-vertex that has **no corresponding STEP entity at all**. Zero of 18 fixtures place an unattached vertex projecting onto an unrelated edge's interior — the actual `CheckSplittingVertices` trigger. |
| `tkshh-sliver-solid` | GAP | **AGREE** | Only candidate, `Tfa015`, read directly: it is a bare `ADVANCED_FACE` on an `OPEN_SHELL` (`SHELL_BASED_SURFACE_MODEL`) — no `MANIFOLD_SOLID_BREP`/`CLOSED_SHELL`/`TopoDS_SOLID` anywhere in the file. `ShapeFix_FixSmallSolid::IsValidInput` requires solid/comp-solid input, so this fixture structurally cannot reach the cited healer; it's a small-*face* fixture mislabeled by its comment as small-*solid*. |
| `tkshh-solid-unstructured-multishell` | GAP | **AGREE** | Grepped catalog for `ShapeFix_Solid` — all hits (`Tsh083`, `Tsh102`, `Tsh185`, `Tsh186`) are single-shell precondition/state-reset bugs, not the `NbShells!=1` `CreateSolids`/`CollectSolids` point-containment classification branch. The nearest candidates (`Bo003`, `Tsh015`, `Tsh067`) all target `BREP_WITH_VOIDS` schema-level orientation semantics (`RWStepShape_RWBrepWithVoids`), a distinct translator path from the healer's generic shell-nesting classifier. No plain unstructured-compound-of-shells fixture found. |
| `tkshh-indirect-elementary-surface-axes` | GAP | **AGREE** | `grep -c CONICAL_SURFACE` across all `step-examples/` (41 hits) shows every semi-angle value is positive; no negative-determinant `AXIS2_PLACEMENT_3D` feeds a `PLANE`/`CYLINDRICAL_SURFACE`/`CONICAL_SURFACE` directly anywhere. All catalog "left-handed"/"mirror"/"negative determinant" hits (`A024`, `P018`, `Pmi068`, `Ps004`, `Tsh033`) are `MAPPED_ITEM`/assembly-placement mirroring — a different mechanism (`ShapeCustom_DirectModification`/`IsIndirectSurface` acts on the surface's own frame, not a component transform) — matching the audited agent's own distinction. |
| `tkshh-wire-duplicate-coincident-vertex-instances` | GAP | **AGREE** | The closest existing coverage (`tkshh-wire-adjacent-vertex-gap`: `Twi003/Twi043/Twi056/Twi238`/etc.) is confirmed to test a materially different mechanism — `ShapeFix_Wire::FixConnected`, pairwise, wire-sequential-only (`Twi238`'s own catalog entry cites line 558, `Twi056` line-verified as "consecutive edges" gap). The GAP's claimed mechanism (`ShapeFix_EdgeConnect::Build`/`ShapeFix_WireVertex::FixSame`, midpoint-of-bounding-box merge of an arbitrary *group* of coincident vertices, not necessarily wire-consecutive) has no dedicated fixture; `Ad103` (nearest catalog hit) is explicitly a runtime use-after-free robustness bug on a second merge pass, not the initial-merge mechanism. |

## COVERED sample (20/35)

Full per-fixture detail in the sampling pass; summarized here. All 20 verdicts **AGREE**
at the problem level — no fixture set failed to demonstrate its claimed mechanism overall.
Two problems carry one weak/wrong individual fixture citation (verdict still holds on the
remaining cited fixtures):

| problem_id | verdict | AGREE/OVERTURN | evidence |
|---|---|---|---|
| `tkshh-curve-projection-degenerate-parametrization` | COVERED | AGREE | Gs029 (reversed TRIMMED_CURVE range), Gp129 (degenerate collapsed B-spline), Gp037 (unbounded pcurve) — three distinct, genuinely-encoded subvariants. |
| `tkshh-curve-tolerance-closure-detection` | COVERED | AGREE | Gn039/Gn071/Gn101 verified as distinct `IsClosed` subvariants (near-closure-tolerance, Bezier pole-equality, composite-curve internal gap). |
| `tkshh-edge-3d-2d-parameterization-mismatch` | COVERED | AGREE | Gp022/Twi082/Gp130 — distinct range-mismatch / SameRange-flag / knot-domain-compression mechanisms, all live-wired. |
| `tkshh-edge-pcurve-reversed` | COVERED | AGREE | Gp054/Twi062/Gp043 — TRIMMED_CURVE range-not-inverted, UV-direction-reversed, stale B-spline knots. |
| `tkshh-edge-self-intersecting` | COVERED | AGREE | Twi103/Twi269/Gn024 — figure-eight wire, degenerate self-loop edge, figure-eight B-spline control polygon; distinct encodings. |
| `tkshh-face-area-exceeds-threshold` | COVERED | AGREE | Tfa013, Tfa052 — single-face and closed-shell variants, both genuine. |
| `tkshh-face-missing-seam-edge` | COVERED | AGREE | Twi020/Gp137/Xp015 — missing seam, period-shift-after-seam, cylinder seam+self-intersect; distinct. |
| `tkshh-face-period-wrapped-uv-placement` | COVERED | AGREE | Tfa207/Gp137 — seam-straddling wire bbox and UV period placement genuinely distinct from the seam-*edge* problem despite Gp137 appearing in both lists. |
| `tkshh-face-wire-orientation-wrong` | COVERED | **AGREE, weak citation** | Tfa236/Twi024 genuine (real `FACE_OUTER_BOUND`/`FACE_BOUND` .T./.F. sense flags on a live `ADVANCED_FACE`). **Twi113 is a bad citation**: it's a bare `GEOMETRIC_CURVE_SET` of two raw `EDGE_LOOP`s with *no* `FACE_OUTER_BOUND`/`FACE_BOUND` entity at all — confirmed by direct byte read — so it cannot exercise `ShapeFix_Face::FixOrientation`; its "outer_rect"/"inner_hole" naming is cosmetic label text, not bound typing. Verdict unaffected (Tfa236/Twi024 suffice). |
| `tkshh-faceconnect-unshared-boundary-edges` | COVERED | AGREE | Tfa019/Tsh079/Tsh108 — duplicate-vertex crack and shell-sewing tolerance-mismatch variants. |
| `tkshh-pcurve-collapse-onto-surface-singularity` | COVERED | AGREE | Gp157/Gp160/Tfa200 — three distinct `CONICAL_SURFACE` near-apex-projection angles. |
| `tkshh-same-surface-fragmented-faces` | COVERED | AGREE | Tfa016/Tsh046/N003 — redundant internal edge, kinked-chain, vertex-tolerance-on-merge. |
| `tkshh-seam-pcurves-swapped` | COVERED | AGREE | Twi022/Twi268/Gp011 — duplicated/aliased SEAM_CURVE pcurve, genuinely distinct instances. |
| `tkshh-shape-unbaked-location-transform` | COVERED | **AGREE, weak citation** | Tsh082 genuine (two faces with distinct non-identity placements feeding `RemoveLocations`). **N143 is a bad citation**: confirmed by direct byte read — single bare `EDGE_CURVE` in a `GEOMETRIC_CURVE_SET`, no `AXIS2_PLACEMENT_3D`/`TopLoc_Location` transform anywhere in the file; its comment describes an unrelated null-pointer robustness bug in `MakeNewShape`, not an "unbaked transform" input. Verdict unaffected (Tsh082/N143's-siblings A067 etc. suffice). |
| `tkshh-shell-inconsistent-face-orientation` | COVERED | AGREE | Tsh070/Tsh122/Tsh149 — multiconnect-edge, across-edge propagation, hexagonal-shell orientation; distinct. |
| `tkshh-solid-globally-inverted-shell` | COVERED | AGREE | Bo024/Ps001/Tsh010 — all-inward, all-inward-consistent, single-face-reversed; 3 genuinely distinct subcases. |
| `tkshh-spot-face` | COVERED | AGREE | Tfa006/Tfa072/Gs014 verified. |
| `tkshh-strip-face` | COVERED | AGREE | Tfa007/Tfa048/Gs014 verified. |
| `tkshh-surface-closure-vs-declared-periodicity-mismatch` | COVERED | AGREE | Gs081/Gs140/Tfa197 — IsUClosed/IsVClosed/periodic-cache-bypass; distinct mechanisms. |
| `tkshh-tolerance-out-of-range` | COVERED | AGREE | N040/N097/N168 — LimitTolerance bloat/no-op/double-mutation; distinct subcases. |

## PARTIAL sample (8/20)

| problem_id | verdict | AGREE/OVERTURN | evidence |
|---|---|---|---|
| `tkshh-closed-edge-full-period-unsplit` | PARTIAL | AGREE | Twi019 verified: genuine full-period CIRCLE `EDGE_CURVE` (start==end vertex `#7`), live-wired through `EDGE_LOOP→FACE_OUTER_BOUND→ADVANCED_FACE→OPEN_SHELL`; covers only the base split mechanism. Catalog search for "infinite endpoint"/"swapped parameter order"/Offset-Trimmed-wrapper knot-snap synonyms: no hits — claimed-missing subvariants genuinely absent. |
| `tkshh-edge-crossing-surface-singularity` | PARTIAL | AGREE | Xp013 verified: apex vertex `#9=(0,0,0)` is an edge *endpoint* at the cone apex (triangle corner), not an edge whose *interior* crosses the apex, matching the notes' own characterization. No fixture found for the interior-crossing split or over-degenerate pole+seam rebuild branch. |
| `tkshh-edge-curve-inconsistent-with-vertex-removed` | PARTIAL | AGREE | Gp151 verified: CIRCLE pcurve trimmed `[5.5, 0.8]` straddling 2π is a genuine `CheckPCurveRange` input, but wrapped in a bare `GEOMETRIC_CURVE_SET` (self-documented oracle-invisible, consistent corpus convention, not overclaimed). `FixRemoveCurve3d` mirror-path (stale 3D curve discarded) has no dedicated fixture. |
| `tkshh-edge-missing-3d-curve` | PARTIAL | AGREE | Catalog search for "geometry-less edge"/"neither curve nor pcurve" found nothing beyond cited fixtures; the specific `ShapeFix_Wire.cxx:744-759` edge-removal path is genuinely undemonstrated. |
| `tkshh-edge-missing-pcurve` | PARTIAL | **OVERTURN → should be upgraded** | Found **`Gp012`** (`§12-2a-pcurves`, same section as several cited fixtures, but itself uncited anywhere in `problems.json`): `SEAM_CURVE('',#10,(#19,$),.PCURVE_S1.)` on a live `CYLINDRICAL_SURFACE`/`ADVANCED_FACE`/`OPEN_SHELL` — a clean, single-defect fixture for exactly the subvariant the notes call "missing" ("a clean dedicated fixture is missing" for the seam-pair pcurve case). Independently re-verified byte-for-byte by the report author; `Gp012` is confirmed absent from every `fixture_ids` list in `problems.json`. This is a genuine miss (incomplete catalog search), not a disagreement about evidence quality. |
| `tkshh-face-closed-surface-unsplit-at-seam` | PARTIAL | AGREE | Grepped `TOROIDAL_SURFACE` + seam/split/closed and V-closed-fallback/near-full-period synonyms — all hits are different problems (orientation-partial-closure, seam pcurve param mismatch, degenerate-torus normal-flip). No doubly-closed-torus recursive-split or V-closed-only fixture found; also independently confirmed the nearby `Tfa038` (sphere/torus missing outer bound) belongs to the separate `tkshh-face-natural-bound-missing` problem, not this one — no miscategorization. |
| `tkshh-face-intersecting-wires` | PARTIAL | AGREE | Catalog search for "3-edge reconstruction"/">50% overlap"/collinear-overlap synonyms: zero hits. Missing subvariant confirmed absent. |
| `tkshh-face-natural-bound-missing` | PARTIAL | AGREE | Catalog search for pole+hole-merge / sphere-natural-bound synonyms: zero hits. `ShapeFix_Face.cxx:937-983` pole-touching-hole-merge subvariant genuinely undemonstrated. |

## Notes on method limitations

- COVERED/PARTIAL samples (20/35, 8/20) are not exhaustive; the 15 unsampled COVERED and
  12 unsampled PARTIAL entries carry the same prior-agent methodology and were spot-checked
  only via the GAP-adjacent cross-referencing above, not read fixture-by-fixture.
- The `Gp012` overturn suggests other PARTIAL "missing variant" claims may have similar
  misses — the failure mode (fixture exists in the ~45,460-line catalog under a section the
  agent didn't fully re-scan) is structural, not one-off. A full re-sweep of all 20 PARTIAL
  notes against catalog full-text search would likely find 1-3 more.
- GAP coverage is the strongest result in this audit: all 5 were adversarially re-searched
  with synonym/entity-pattern grep sweeps beyond what the original agent's notes cite, and
  all 5 held.
