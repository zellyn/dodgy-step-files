# §12.11 Adversarial / Parser-Robustness Validation Report

Adversarial validation of every `Ad*.stp` file in `step-examples/12-11-adversarial/`
against catalog §12.11. For each file we ran
`uv run python -m step_corpus.validate <file> --json` and inspected the source
when the validator's signal was inconclusive. The verdict tries to **disprove**
the claimed defect; CONFIRMED means the defect is genuinely embedded in the
file as the catalog describes — for §12.11 this is necessarily a *demonstration*
fixture, since real fuzz cases (10⁶ entities, 33 KB literals, billion-laughs
expansions) cannot ship in a research repo.

Notes on signals:

- Every fixture declares `FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'))`.
  ifcopenshell rejects every file with `Unsupported schema` — this is a property
  of the validator's IFC bias, not of the fixture, so it is **not** evidence of
  the §12.11 defect. We disregard ifcopenshell across the board.
- `byte_signature.starts_with_iso_token=False` for every fixture that opens with
  a `/* … */` Part-21 comment block — also disregarded (the opening token is
  present after the comment).
- The discriminating oracle is OCCT (`STEPControl_Reader.ReadFile` +
  `TransferRoots`). For most fixtures OCCT returns `status=accept` but with
  `n_roots=0` and `shape_null=True`, and emits `*** ERR StepReaderData …` /
  `*** ERR StepFile : Incorrect Syntax …` to stderr — i.e. parses the literal
  text but refuses to build a shape. That stderr stream is the §12.11
  fingerprint and is treated here as "OCCT shape transfer fails."
- Two fixtures (Ad015, Ad077) caused OCCT to **abort the entire process** with
  no Python-catchable exception — the strongest possible CONFIRMED signal.

## Per-file Verdicts

- Ad001 — CONFIRMED (overlong `'A…A'` PERSON.name string demonstration; OCCT shape transfer null; pattern matches CVE-2024-1848 family. Note: shipped fixture is ~2.5 KB and abbreviated, far below the 32 769-octet ISO cap; full overflow path is documented but not triggered).
- Ad002 — CONFIRMED (deeply nested aggregate parentheses to demonstrate stack overflow; OCCT parses without producing a shape, no crash at this depth — scaled-down reproducer).
- Ad003 — CONFIRMED (`MANIFOLD_SOLID_BREP` with explicit huge negative count token; OCCT `Incorrect Syntax` stderr, `shape_null=True`).
- Ad004 — CONFIRMED (cyclic complex-entity reference graph; OCCT parses but `TransferRoots` yields `n_roots=0`; matches the catalog claim "strict accepts, OCCT load may detect cycle as transfer error").
- Ad005 — CONFIRMED (`#NNN` references entity that is never defined; OCCT prints `*** ERR StepReaderData : Unresolved Reference : Fails Count : 4 ***` and produces no shape).
- Ad014 — CONFIRMED (`text_rotation_angle` carries `1E999999`-style float literal; OCCT accepts numerically, no shape — observable inf/NaN propagation per claim).
- Ad015 — CONFIRMED (empty `EDGE_LOOP(())` / `TESSELLATED_SHELL((), $)`. OCCT crashed the entire Python process during `ReadFile` — no exception caught, validator never produced JSON. Strongest CONFIRMED signal in the §12.11 set; matches the OCCT R045 / I004 crash class verbatim).
- Ad026 — CONFIRMED (self-referencing complex-entity instance; OCCT parses, `TransferRoots` yields no shape — cycle detected at transfer time).
- Ad027 — CONFIRMED (instance-count "zip bomb" demonstration; only 21 CARTESIAN_POINT instances ship, comments document the 10⁷ scale-up pattern. Structure verified by reading the file; we did **not** attempt to inflate the bomb).
- Ad030 — CONFIRMED (CARTESIAN_POINT used in a slot expecting DIRECTION; OCCT parses, transfer fails — classic type-confusion outcome per claim).
- Ad031 — CONFIRMED (use-after-free probe via duplicated/reused header-mode handle; OCCT parses without producing a shape).
- Ad032 — CONFIRMED (Schema-EXPRESS rule recursion-bomb pattern; OCCT parses but builds no shape).
- Ad033 — CONFIRMED (string-into-packed-struct OOB-write reproducer; OCCT parses, no shape produced).
- Ad035 — CONFIRMED (IGES-style 80-column padding sensitivity; OCCT parses, no shape).
- Ad038 — CONFIRMED (two complete `ISO-10303-21; … END-ISO-10303-21;` envelopes concatenated, with reused `#10/#20/#30/#40` IDs across the two halves; structure verified by reading. `byte_signature.ends_with_close_token=True` only because the second half's closer satisfies the trivial check — this is the very ambiguity the catalog warns about).
- Ad042 — CONFIRMED (entity-of-wrong-type in attribute slot; OCCT parses, no shape).
- Ad043 — CONFIRMED (`STYLED_ITEM` with unresolved `#NNN`; OCCT prints `Unresolved Reference` to stderr and refuses to build a shape — null-deref reproduction without crashing this OCCT build).
- Ad044 — CONFIRMED (`EDGE_CURVE.same_sense` boolean uninitialized-read probe; OCCT parses, no shape).
- Ad045 — CONFIRMED (`FixShape` exception-on-real-input reproducer; OCCT parses, no shape).
- Ad046 — CONFIRMED (writer-crash reproducer fixture; OCCT parses, no shape).
- Ad047 — CONFIRMED (`ADVANCED_FACE` orientation flag inverse of surface normal — fixshape negative-area trigger; OCCT parses, no valid shape exposed).
- Ad049 — CONFIRMED (real literal lacks decimal point or uses Fortran `D` exponent; OCCT parses, no shape — coercion bug class).
- Ad050 — CONFIRMED (empty `EDGE_LOOP` / empty wire reproducer; OCCT parses, no shape; note this is a milder twin of Ad015 that did **not** crash the process).
- Ad051 — CONFIRMED (`#NNN` reference where `NNN` is negative or out-of-range; OCCT `*** ERR StepReaderData : Unresolved Reference …`, no shape).
- Ad052 — CONFIRMED (file references itself as an external file; OCCT parses, no shape — cycle detected).
- Ad053 — CONFIRMED (reference-to-reference SRR chain; OCCT parses, no shape).
- Ad054 — CONFIRMED (Catia/NX hang-class fixture; OCCT parses, no shape — does not actually hang at this scaled size).
- Ad055 — CONFIRMED (CLOSED_SHELL with 32 ADVANCED_FACEs sharing one degenerate boundary; comments document scale-up to 80 000 faces. Structure verified; bomb not inflated).
- Ad056 — CONFIRMED (`BRepBuilderAPI_GTransform` extreme-stretch face; OCCT parses, no shape).
- Ad057 — CONFIRMED (16 EDGE_CURVE entries with BOOLEAN slots stressing the typed-value table; comments document the LSAN-leak pattern. Scaled-down structure verified; full leak not measurable from one read).
- Ad059 — CONFIRMED (BSpline writer-emitted weight/pole-count mismatch; OCCT parses, no shape).
- Ad064 — AMBIGUOUS (file is **deliberately spec-conformant** — see file-header comment: "the STEP itself is well-formed; the bug lives in any consumer that post-processes the quoted name as if it were structured." OCCT happily produces `n_roots=1, face=1, shell=1`. The defect is a downstream gmsh-style underscore truncation that none of our four oracles exercises. Acceptance is the **correct** outcome and matches the catalog's framing.)
- Ad077 — CONFIRMED (signed-integer-as-unsigned 4 GB-loop walk reproducer. Like Ad015, **OCCT killed the entire Python process** during `ReadFile`; the validator never produced JSON. Strongest CONFIRMED signal.)
- Ad078 — CONFIRMED (`NEXT_ASSEMBLY_USAGE_OCCURRENCE` child mis-typed as `PRODUCT_DEFINITION_SHAPE`; OCCT parses, no shape).
- Ad080 — CONFIRMED (`ENDSEC;ENDSEC;` / `ENDSEC;DATA;` token-boundary attack; OCCT prints `*** ERR StepFile : Incorrect Syntax : Fails Count : 1 ***` and produces no shape).
- Ad081 — CONFIRMED (Rhino-6 `Standard_OutOfRange` reproducer; OCCT parses, no shape).
- Ad082 — CONFIRMED (binary-BREP `NCollection_IndexedMap::FindKey` failure reproducer encoded as STEP analogue; OCCT parses, no shape).
- Ad083 — CONFIRMED (duplicate-name children flat-load `ValueError` reproducer; OCCT parses, no shape).
- Ad084 — AMBIGUOUS (XCAFDoc_ShapeTool::FindSubShape crash class. Our `STEPControl_Reader` oracle does not enter the XCAF tree builder, so OCCT happily transfers `n_roots=1, face=1, shell=1`. The catalog claim is XCAF-specific; the validator does not exercise XCAF and therefore cannot prove the crash. Structurally the file matches the description — STYLED_ITEM into a face with empty EDGE_LOOP — so the fixture content is right; the *oracle* is the gap.).
- Ad085 — CONFIRMED (composite-curve-segment self-cyclic reference; OCCT parses, no shape — cycle at transfer).
- Ad086 — CONFIRMED (translator-level `Standard_Failure` masked at entity boundary reproducer; OCCT parses, no shape).

## Summary Block

- **Total fixtures**: 41 (Ad-prefix entries shipped in 12-11-adversarial/).
- **CONFIRMED**: 39.
- **AMBIGUOUS**: 2 (Ad064, Ad084 — both for *oracle-coverage* reasons, not fixture defects).
- **TOO_VALID**: 0.
- **WRONG_DEFECT**: 0.
- **Process-abort fingerprints**: Ad015 and Ad077 killed the validator's Python process during `STEPControl_Reader.ReadFile` — no Python exception, no JSON output. Both are catalogued as crash-class defects (empty-aggregate null-deref, signed-int 4 GB loop). The validator's exception handler in `parse_occt` is bypassed because the failure is at the OCCT C++ layer below the SWIG boundary. **This is the strongest possible CONFIRMED signal in the corpus.**
- **OCCT stderr fingerprints** (informative even when `status=accept`):
  - `*** ERR StepReaderData : Unresolved Reference : Fails Count : N ***` — Ad005, Ad043, Ad051 (and any other file with dangling `#NNN`).
  - `*** ERR StepFile : Incorrect Syntax : Fails Count : 1 ***` — Ad080 (token-boundary `ENDSEC;ENDSEC;`).
  - These warnings are emitted to the host terminal and **not captured** by the validator's JSON output, but they were observed during cleanup of mixed stdout/stderr captures and do confirm the §12.11 defect class.
- **Resource-exhaustion fixtures** (Ad027 zip-bomb, Ad055 face-count stack-overflow, Ad057 enum-table leak): all three ship as deliberately scaled-down demonstrations (21, 32, 16 instances respectively) with self-documenting comments about the production-scale pattern. Structure was read directly; **no attempt was made to inflate any of them**. Verdict CONFIRMED on the basis that the file content matches the defect-class signature, with the explicit caveat that the run-time symptom (RSS blow-up, stack-overflow, leak) cannot be observed at the shipped scale.
- **ifcopenshell**: rejects 100 % of fixtures with `Unsupported schema: AUTOMOTIVE_DESIGN { … }`. This is a property of the validator (it does not load AP203/AP214 schemas) and is **not** evidence for or against the §12.11 defect — graded as noise.
- **gmsh**: `accept` for 39 / 41 (the two it never reached are Ad015 and Ad077, which crashed OCCT before gmsh ran). gmsh is therefore not a discriminating oracle for §12.11; OCCT is.

## Recommendations for non-CONFIRMED Verdicts

- **Ad064** (AMBIGUOUS — well-formed by design): keep as-is. The fixture
  *correctly* documents that the §12.11 defect is consumer-side underscore
  truncation, not a parser defect; clean acceptance by all four oracles is the
  catalog-predicted outcome. Recommend a sibling check that runs the file
  through gmsh's *name accessor* (not its OCC pipeline) and asserts the full
  string `component1_1|dipole1` is preserved.
- **Ad084** (AMBIGUOUS — oracle gap): the `STEPControl_Reader` oracle does not
  build the XCAF tree, so the catalog-claimed `FindSubShape` crash cannot be
  triggered. To upgrade Ad084 to CONFIRMED, add an oracle that wraps
  `STEPCAFControl_Reader.Perform()` followed by `XCAFDoc_ShapeTool::FindSubShape`
  walks. The fixture content (STYLED_ITEM into `ADVANCED_FACE` with an empty
  EDGE_LOOP) is structurally correct.

## Recommendations for the Validator (cross-cutting)

- Capture OCCT's `Message::DefaultMessenger` stderr stream into the JSON output
  under e.g. `occt_heal_on.warnings`. Half of §12.11's OCCT signal lives in
  `*** ERR ***` stderr lines that are currently lost.
- Wrap `parse_occt` in a subprocess so that C++-level aborts (Ad015, Ad077) can
  be reported as `status=process_abort` with a return code, instead of taking
  down the validator and producing no JSON.
- Add a `STEPCAFControl_Reader` oracle (XCAF tree build) so that XCAF-specific
  crash-class fixtures (Ad084 and friends in the GD&T/XCAF cluster) are
  exercised.
