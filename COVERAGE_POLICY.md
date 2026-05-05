# Coverage Policy

Rules for deciding when a newly-mined kernel defect warrants its own catalog entry vs. extending an existing one.

## Goal

The catalog aims to be an inventory of problematic STEP files: the full spectrum of inputs a B-rep CAD kernel might plausibly encounter and need to have an opinion about. The corpus is intended as a checklist of *inputs*; deciding whether a kernel handles each input *correctly* is a separate concern (graded by tests living in the kernel's own repo).

A kernel that cleanly handles every fixture in the corpus has, at minimum, parity with OCCT's accumulated 30-year defect-handling experience. Beyond that, a kernel can be graded by how *well* it handles each (cleanly reject, heal, accept, etc. — design-dependent).

## Acceptance criterion: the bug-report search test

**Practical completeness rule:** someone encounters a problematic STEP file in the wild, characterizes the problem in their own words well enough to file a really good bug against a CAD kernel. They search this catalog with the language from their bug report. They should find a matching entry.

This is the catalog's *usability* criterion, and it doubles as a *completeness* metric. If a plausible bug report can't find a matching entry, we have a gap. Conversely, if a search query returns wildly irrelevant entries, the catalog text is too OCCT-API-shaped to be discoverable.

### Implications for entry phrasing

1. **Use the language people in the wild use.** "Non-watertight shell", "naked edges", "wrong units", "model appears tiny", "STEP file scaled by 1000×", "PMI lost on round-trip", "kernel crashed on import", "face inside-out", "tolerance too small", "duplicate vertex", "sliver triangle". These are the search terms; they need to appear in titles, descriptions, or keywords.
2. **Avoid OCCT-API-only jargon.** A bug-reporter who has never read OCCT source won't search for "ShapeFix_Wire::FixSelfIntersectingEdge". They'll search "self-intersecting wire" or "wire crosses itself".
3. **Synonyms matter.** Same defect goes by many names: "non-watertight" / "leaky" / "naked edges" / "free edges" / "open shell" / "not closed" all describe the same problem class. An entry should mention multiple synonyms in its description.
4. **Symptom-first phrasing helps discoverability.** "Face appears inside-out after import" is more searchable than "FACE_OUTER_BOUND.orientation flipped". Both should be present, with the symptom phrasing leading.
5. **Sender attribution becomes a search term.** "STEP file from Pro/E that crashes the kernel" is a common query; the entry's `Sender` field needs to be discoverable.

### The search-test suite

`step_corpus._bug_search` plus `tests/test_bug_search.py` codify this:

- A list of canonical bug-report-style queries (representative of what people might search).
- For each query, the tool returns the top-k catalog entries by relevance.
- The test asserts that each query finds the expected entry within a max-rank threshold.
- Failing queries become gap-fill targets.

Sample canonical queries the corpus should answer:

```
"STEP file imported with units in mm but coordinates appear in inches"
"shell appears non-manifold after import"
"B-spline curve has wrong number of weights"
"face has zero area after Boolean operation"
"PMI annotations lost during round-trip"
"kernel crashes on loading specific entity"
"file looks tiny — 1000× too small"
"duplicate vertices not getting merged"
"thin sliver triangles in mesh"
"missing face in shell"
"wire boundary self-intersects"
"surface of revolution with wrong axis"
"can't read STEP file from CATIA"
"file declares AP203 but uses AP242 entities"
"comment inside string literal breaks parser"
"BOM character at start of file"
"file uses lower-case ISO-10303-21"
```

Each query is a question the corpus must answer with at least one entry whose title/description matches the searcher's intent.

## Three sources of catalog entries

1. **Find** — defects that exist in real STEP files in the wild. Mined from OCCT source, OCCT git log, OCCT Mantis tracker, FreeCAD/CadQuery/build123d/pythonocc/SolveSpace issue trackers, vendor knowledge bases (Autodesk / PTC / SolidWorks / Onshape / Siemens / Eng-Tips), commercial translator vendor pages (CADfix / TransMagic / Datakit / Capvidia / Theorem / Tech Soft 3D HOOPS Exchange / Spatial 3D InterOp / CAD Exchanger), CVE/OSS-Fuzz/Talos, quaoar.su blog + Analysis Situs, BRL-CAD step-g + Rhino/openNURBS, academic literature (Patrikalakis / Ju Tao / Tsinghua / BrepGen), ISO 10303-21 spec + LoC FDD, prostep ivip / AFNeT / PDES whitepapers, ABC / Fusion 360 Gallery / DeepCAD / Thingi10K datasets, StackExchange / Reddit / OCCT forum, patent literature (Spatial / ITI / Theorem / Autodesk / PTC / Siemens), KiCad MCAD / Eng-Tips niche forums.
2. **Deduce** — defects implied by the ISO 10303 spec but maybe not yet observed in the wild. For every spec feature, ask: "what if someone emitted this in a way the spec technically allows but no kernel anticipates?". Every Edition-3 control directive, every AP242 surface subtype, every cross-product of "spec feature × spec edge case" is fair game. Examples: `\X4\` with valid UCS-4 codepoints in surrogate range; multi-DATA-section file with cross-section references via `@section_name#NNN`; `RECTANGULAR_COMPOSITE_SURFACE` whose patch grid is non-uniform; `composite_curve_segment` chain with `transition_code = .DISCONTINUOUS.` at every joint.
3. **Dream up** — defects creatively designed to break kernels. Cross-product defects that combine N defect classes into one file (sliver edge × periodic surface × seam × unit mismatch). Time-bomb defects (geometry exactly at a tolerance boundary). Pathological-success defects (file loads cleanly but produces semantically wrong geometry — a swept solid silently becomes a truncated cone, a Boolean union silently drops an inner void). Adversarial / fuzz inputs (already covered in §12.11 but expandable).

OCCT covers (1) heavily but only fragmentary (2) and (3). The corpus should aspire to the full spectrum; OCCT's coverage is a floor, not a ceiling.

## Foundational principle: catalog of problems, not solutions

OCCT is a primary source of evidence that defects exist in the wild. OCCT's specific *solutions* (its tolerance-bumping, its `ShapeFix_*` algorithms, its choice to silently heal rather than reject) are **one valid kernel-design response**, not a prescription for new kernels.

When writing or updating an entry, observe:

- **Problem descriptions are physical / topological / semantic, not OCCT-API-shaped.**
  - GOOD: "tiny sliver between two near-coincident vertices, formed during a Boolean cut"
  - GOOD: "non-watertight shell where two faces meet at sub-feature distance but don't share an edge"
  - GOOD: "pcurve and 3D curve disagree about where the edge actually is"
  - BAD: "input that triggers `ShapeFix_Wire::FixSelfIntersectingEdge`"
- **Solution classes are kernel-design-agnostic.** Describe what a kernel should *achieve*, not how OCCT achieves it.
  - GOOD: "remove the sliver while preserving wire connectivity"
  - GOOD: "merge near-coincident vertices and re-stitch the shell"
  - GOOD: "reconstruct one curve from the other and report the residual deviation as a quality metric"
  - GOOD: "reject as malformed with a diagnostic citing the offending edge". If a kernel chooses not to heal, that's a valid response.
  - BAD: "call `ShapeFix_Wire::FixSelfIntersectingEdge`"
  - BAD: "tolerance-bump the vertex to absorb the intersection"
- **Avoid magic numbers in solution prose.** OCCT bakes in tolerances (`1e-7`, `Precision::Confusion`, etc.) because OCCT's algorithms need them. A kernel using exact arithmetic, interval arithmetic, or relative tolerance has different needs. Phrase the solution in terms of the *invariant* the kernel should preserve, not the numeric threshold.
  - GOOD: "the deviation should be reduced below the kernel's working precision"
  - GOOD: "the resulting wire must be connected within whatever tolerance the kernel uses for vertex equality"
  - BAD: "deviation must be < 1.0e-7 mm"
  - OK in problem description: "two vertices at coordinates (0,0,0) and (1e-7, 0, 0); the kernel must decide whether they're the same point". Tolerance numbers describing the *input* are unavoidable; tolerance numbers prescribing the *output* are not.
- **Vendor conventions are noted, not prescribed.** "SolidWorks emits `TOROIDAL_SURFACE` with negative MajorRadius to encode an orientation flip" is a *fact about senders*, not a *requirement on receivers*. A new kernel may choose to reject negative radii as malformed and require upstream tools to fix. Use language like "to support files from CAD tool X, a kernel may interpret negative MajorRadius as ..." rather than "kernels must interpret ...".
- **`Expected validation` field is decoupled.** That field records what OCCT/gmsh/ifcopenshell actually do today, used as a CI regression check (DRIFT detection on kernel updates). It is *not* a prescription for new kernels; those are free to do something different from OCCT and still pass the corpus.
- **Sources cite OCCT** as evidence that a problem exists in the wild. Citations like "OCCT 0023456 (Mantis)" or "OCCT path:line" are evidence-pointers, not solution-pointers.

The result is that a model (or human) writing a new kernel can read a catalog entry, understand the *problem*, and design a solution that's potentially better than OCCT's (using exact arithmetic, cleaner reject semantics, different tolerance models) and still pass the corpus.

### Where OCCT-specific language is OK

- **`Sources` field**: citations to evidence in OCCT.
- **`Notes` field**: when characterizing observed behavior of OCCT or another kernel under test ("Validation observed: OCCT segfaults via ..."). This documents what kernels do today, useful context for kernel implementers.
- **`Sender` field**: when a defect is sender-attributable, name the producer.

### Where OCCT-specific language is NOT OK

- **`Description` field**: describe the input shape and its problem in physical/topological terms.
- **`Reproducer recipe` field**: describe the entity-level construction; don't reference OCCT API methods.
- **`Expected kernel behavior` field**: describe the solution class, not OCCT's algorithm.

## Problem statements imply solutions — say what's wrong, not what to do

Each entry pairs a STEP file with a description of *why* it is problematic. A well-written description names the violated invariant; the solution falls out implicitly from naming the problem.

The reader should not have to guess what's wrong. Equally, they should not be told what algorithm to apply. The implicit solution comes from the problem statement.

### Worked examples of the implicit-solution principle

| Problem statement | Implicit solution (kernel chooses how) |
|---|---|
| "shell is not watertight: two faces meet at sub-feature distance but don't share an edge" | make it watertight (sew, merge vertices, reject as malformed; kernel's choice) |
| "tiny sliver triangle with two near-coincident vertices" | remove or absorb the sliver while preserving incident topology |
| "pcurve and 3D curve disagree about where the edge actually is" | reconcile them (recompute, reproject, reject; kernel's choice) |
| "negative torus MajorRadius: a SolidWorks-vintage convention indicating face-orientation flip" | decide whether to honor the vendor convention or reject as malformed (vendor-compat policy is kernel's choice) |
| "self-intersecting wire: outer boundary crosses itself in the parametric domain of its host face" | resolve the self-intersection somehow |
| "knot multiplicities sum to n+degree+2 instead of n+degree+1, an invalid B-spline" | reject as malformed, or coerce by dropping/inserting a knot, kernel's choice |
| "FILE_SCHEMA declares AP242 but file uses AP203-only entities" | resolve the schema mismatch (use the actually-present entities, reject, warn) |

Notice that in each case:

- The problem statement is *physical / topological / semantic*, about the shape and what's wrong with it, not about OCCT.
- The implicit solution is *one or more invariants that should hold after handling*: the shell becomes watertight, the wire becomes simple, the curves agree, etc.
- The catalog never says "use algorithm X". The kernel chooses based on its own design philosophy.
- "Reject as malformed" is always a valid implicit solution; a kernel doesn't have to heal.

### Style: "what's wrong" vs "what the kernel should do"

Reframe entries to lead with what's wrong:

| Drift toward solution-prescriptive | Reframed as problem-statement |
|---|---|
| "kernel should call `ShapeFix_Wire::FixSelfIntersectingEdge` to absorb the loop" | "wire boundary self-intersects in the parametric domain at a single point" |
| "kernel should bump vertex tolerance to 1e-3 to absorb the gap" | "two vertices that share an incident edge are positioned 1e-3 apart in 3D space" |
| "kernel should heal by inserting a degenerate seam edge" | "face on a closed cylindrical surface is bounded by a wire that closes in 3D but is open in UV (gap of one period)" |
| "kernel should split the face into N patches" | "single ADVANCED_FACE references a RECTANGULAR_COMPOSITE_SURFACE spanning multiple patches" |

The reframed versions are the catalog convention. They tell the kernel implementer *what's there*; the kernel decides what to do.

### Worked example: a complete entry under this style

```markdown
### Twi-XX — Wire bounding a face is not closed: 3D endpoints meet, UV endpoints don't

- **Category**: §12.3b wire-loop / pcurve
- **Sources**: OCCT git log fa342b1, ProSTEP UG `ug_exhaust-A.stp #284920` cited in OCCT comment
- **Sender**: ProSTEP UG export pipeline
- **Description**: A FACE_OUTER_BOUND on a `CYLINDRICAL_SURFACE` consists of edges
  whose 3D-curve endpoints meet at shared VERTEX_POINTs (the wire is closed in
  3D), but whose 2D pcurve endpoints in the surface's UV parameter space differ
  by ±2π (the wire is open in UV — it has not been "shifted" into a single
  period band). The kernel must decide whether the wire is meaningfully closed.
- **Reproducer recipe**: A face on a cylinder of radius R centered on the Z-axis,
  bounded by a single EDGE_LOOP with two ORIENTED_EDGE entries: a vertical line
  (3D) whose pcurve runs from (U=0, V=0) to (U=0, V=h), followed by a horizontal
  line (3D) whose pcurve runs from (U=2π, V=h) to (U=2π, V=0). The 3D start
  vertex of the second edge equals the 3D end vertex of the first (both are at
  (R, 0, h)); but the pcurve U values differ by 2π.
- **Expected kernel behavior**: The wire's UV pcurves should be in a consistent
  parameter band before the face is treated as bounded. Either shift one edge's
  pcurve by ±period to align with its neighbor, reject the input as malformed,
  or consider the wire's 3D closure sufficient and synthesize the missing UV
  representation. Choice of strategy is kernel-design-dependent.
- **Notes**: Validation observed: OCCT silently shifts the pcurves via
  ShapeFix_Wire::FixShifted before face-bound validity is checked.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a`
```

The Description names the violated invariant ("wire is closed in 3D but open in UV"). The Reproducer is entity-level, no kernel API. The Expected kernel behavior names valid solution classes without prescribing one. The Notes documents OCCT's actual behavior as evidence.

## "What is a distinct entry?": the kernel-branch rule

**One catalog entry per distinct kernel-branch.** If two defective inputs flow through the same kernel decision point and trigger the same fix code, they're variants of one entry. If they take different decision branches inside the same `Fix*()` method, they're separate entries.

### Examples

#### `ShapeFix_Wire::FixSelfIntersectingEdge`

Catalog as separate entries:

- `Twi-XX-a`: pcurve self-intersection on a *planar* face (kernel splits via 2D parameter space)
- `Twi-XX-b`: pcurve self-intersection on a *cylindrical/periodic* surface near the seam (kernel takes the period-handling branch)
- `Twi-XX-c`: 3D-curve self-intersection independent of any surface (different code path)

Catalog as ONE entry (don't split):

- "Self-intersection at parameter t=0.3" vs "self-intersection at t=0.7": same code path, just different inputs.

#### `ShapeAnalysis_Wire::CheckOrder` status flags

- `STATUS_OK` (no defect): no entry.
- `STATUS_DONE1` ("reordered, success"): the *input* with an out-of-order wire is one entry.
- `STATUS_DONE2` ("reordered with reversal"): distinct input pattern (some edges need flipping, not just reordering); **separate entry**.
- `STATUS_FAIL` ("could not reorder"): the input that defeats the reorder algorithm; **separate entry**.

### Quick rule

Ask: "Could a kernel handle defect A correctly while still failing on defect B?" If yes, they're separate entries.

## "Is the catalog already covering this?": the search rule

Before adding a new entry, search:

1. The catalog markdown for the OCCT method/class name (`grep -n FixSelfIntersectingEdge STEP_PROBLEM_CATALOG.md`).
2. The catalog JSON for relevant entity-type tokens cited by the OCCT method's doc comment.
3. The "Sources" field of nearby entries — many existing entries already cite the OCCT method.

If a covering entry exists, prefer:
- Adding a `**See also**: <new-id>` cross-reference if you're adding a sub-variant.
- Splitting the existing entry into multiple if you discover it conflated several distinct branches.
- Extending the existing entry's `**Notes**:` with the newly-discovered nuance if it's truly the same input pattern.

## Sub-status detection

When mining a `ShapeFix_*` method:

1. Read its full implementation, not just the header. Each branch (`if`/`else if`) often handles a different input class.
2. Note which input characteristic determines the branch (e.g., "is the edge degenerate?", "is the surface periodic?", "is the wire closed?").
3. Each branch with a distinguishing input characteristic = candidate for its own entry.

Don't split for:

- Tolerance-threshold branches that just adjust the algorithm's precision (same input class, different precision response).
- Status-flag-only differences (DONE1 vs DONE2 may signal the same input handled with different success messages).

Split for:

- Input-shape-determined branches (the input has a feature that selects the branch).
- Vendor-specific branches (a comment says "for SolidWorks" or "for ProSTEP UG"; that's a sender-attributable variant).
- Recovery-vs-rejection branches (the same input class can take "recover" or "reject" paths depending on a secondary condition).

## License-cleanliness and searchability are the same job

OCCT is LGPL. We use OCCT as **evidence** that a defect class exists in the wild. We do not create derivative works of OCCT — we describe the *input pattern* that triggers OCCT's handling code, in shape-and-topology terms anyone could observe in any STEP file regardless of OCCT.

The legal cleanliness and the search-discoverability goals point in the same direction: rephrase OCCT-API-shaped descriptions into bug-reporter language. An entry that reads "input that triggers `ShapeFix_Wire::FixSelfIntersectingEdge` via the absorbing-vertex-tolerance branch" is both:

- **Less searchable**: a bug-reporter searches "wire crosses itself", not the OCCT method name.
- **More LGPL-derivative**: it paraphrases OCCT's algorithmic structure rather than independently characterizing the input.

Whereas an entry that reads "wire boundary self-intersects at a single point in the parametric domain of its host face: two adjacent edges' pcurves cross before reaching the shared vertex" is:

- **More searchable**: matches "self-intersecting wire", "wire crosses itself", "boundary intersects".
- **Independently observable**: anyone can verify the defect by inspecting the input STEP file's entity graph; OCCT plays no role in the description.

### Mining-from-OCCT process

When mining defects from OCCT source:

1. ✅ **Read OCCT to identify the branch condition**: what input pattern takes the kernel into a particular Fix*/Check* path.
2. ✅ **Characterize the input pattern in shape-and-topology language**: what's true of the malformed input that wouldn't be true of a clean one.
3. ✅ **Construct a reproducer from scratch**: entity-level, license-clean, never extracted from OCCT test data.
4. ✅ **Cite OCCT path:line as `Sources` evidence** that the defect class exists in the wild.
5. ❌ **Never paraphrase OCCT's algorithm** in `Description` or `Expected kernel behavior`.
6. ❌ **Never echo OCCT's tolerance constants** as solution prescriptions. Magic numbers are OK only when they're algorithmic constants (π) or schema-mandated (25.4 mm-per-inch).
7. ❌ **Never echo OCCT's internal bug-ID format verbatim** in titles. "PRO7656" → "Pro/E vintage builds emit ..."
8. ❌ **Never copy doc-comment prose** even with reordering. Generate the description independently from the input characterization.

The result is provably independent of OCCT: the catalog describes inputs (which exist in the world, license-free), references OCCT only as evidence, and offers no algorithm for handling.

## Sub-status fixture-file expansion

If we split an entry into N sub-variants, do we need N fixture `.stp` files?

**Yes**: each canonical entry gets its own `.stp` per the fixture style guide. Fixtures are minimal so the file-count cost is small (~50-300 lines per fixture).

But: if two sub-variants share 95% of their entity scaffolding and differ only in a single attribute value, consider:

1. Naming them with a consistent suffix (`Twi045a.stp`, `Twi045b.stp`).
2. Keeping the catalog entries as separate rows but linking them with `**See also**:`.
3. Letting the validator's `_fixture_lint` allow the suffix pattern.

Current convention: no suffixes used yet. If gap-fill produces many close variants, we'll add the suffix convention to `CONTRIBUTING.md`.

## Out-of-scope

The catalog deliberately does NOT cover:

- **Implicit healings**: defects OCCT silently normalizes without a named `Fix*()` method. Source-mining can't find these directly; detection requires fuzzing OCCT and observing what it normalizes.
- **Boolean-result-correctness**: defects that only manifest in the *output* of a Boolean op, not the input STEP. These belong in a kernel's own test suite, not in this corpus.
- **Performance regressions tied to specific kernel versions**: beyond §12.10's scaled-down representatives, kernel-version-specific timing pathologies are out of scope.
- **Visualization-only defects**: issues that affect rendering but not parsing or shape transfer.

## Coverage aspirations

### Find (mined-from-source)

- ≥95% of `ShapeFix_*::Fix*()` and `ShapeAnalysis_*::Check*()` public methods covered.
- ≥80% of OCCT Mantis bug IDs cited in source/git-log covered.
- ≥75% of `BRepCheck_*` invariant detectors covered.
- ≥10 representative entries from BOPAlgo, BRepFilletAPI, BRepOffsetAPI per module.

### Deduce (spec-derived)

- For every section of ISO 10303-21 Ed.3 that defines a syntactic feature, ≥1 fixture exercising it both correctly and incorrectly.
- For every AP242 entity subtype mentioned in the spec, a fixture demonstrating each of its defect-prone attribute patterns.
- Every Edition-3 control directive form (`\X\`, `\X2\`, `\X4\`, `\S\`, `\P{X}\`, `\F\`, `\N\`, `\PE\`, `\Q\x`) has both well-formed and malformed fixture variants.

### Dream up (synthesized)

- Cross-product defects combining 2+ defect classes in a single file.
- Time-bomb defects with geometry exactly at a tolerance boundary.
- Pathological-success defects: files that load cleanly but produce semantically wrong geometry.

Don't aim for byte-equivalence with OCCT's defect set. Aim for the broader inventory.
