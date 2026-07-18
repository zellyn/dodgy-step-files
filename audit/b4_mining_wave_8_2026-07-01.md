# B4 Mining Wave-8 Audit — 2026-07-01

## Background

Wave-7 (34.8% novelty) tapped the AP242 Ed.3 seam for the first time and confirmed it as the
highest-yield untapped source: 4 of the 8 novel defects came from Ed.3 entities. But wave-7 only
sampled 4 of the 21 new Ed.3 entities: `ANNOTATION_TO_ANNOTATION_LEADER_LINE`, `BASIC_ROUND_HOLE`
(+ `BASIC_ROUND_HOLE_OCCURRENCE`), `TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION`, and (mistagged as Ed.3
but shipping in `Pmi147`) `GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION`. Wave-7's DEFERRED items
DEF-II/JJ/KK/OO have since been merged into the catalog as `Pmi144`–`Pmi147`, so those Ed.3 entity
classes are exhausted.

Wave-8 mines:

- **The remaining ~16 AP242 Ed.3 entities** — the leader-line family (`ANNOTATION_PLACEHOLDER_LEADER_LINE`,
  `ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE`, `ANNOTATION_TO_MODEL_LEADER_LINE`,
  `AUXILIARY_LEADER_LINE`), the APLL point family (`APLL_POINT`, `APLL_POINT_WITH_SURFACE`), the
  assembly-hole family (`BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY`), the length-constrained topology
  family (`BOUNDED_CURVE_WITH_LENGTH`, `CONNECTED_EDGE_SUB_SET`, `EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT`,
  `EDGE_BOUNDED_CURVE_WITH_LENGTH`, `SUBPATH`), the item-level topology-geometry associations
  (`GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION`, `TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION`), and the
  data-equivalence family (`DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION`,
  `DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION`).
- **OCCT GitHub issues + PRs 2024–2026** — the recently-migrated GitHub tracker exposes specific
  producer/consumer bugs invisible in the archived MANTIS range mined in waves 6/7.
- **Fusion 360 → Creo circular-chamfer** — PTC community expert diagnosis: single-face
  `CONICAL_SURFACE` with one internal edge instead of the split-at-180° pair Creo expects.
- **Onshape 2024 STEP color import regression** — a shipping April-2024 regression not covered by
  wave-6 CATIA/Fusion color entries.

---

## Sources Chosen

| # | Source | Why chosen |
|---|--------|-----------|
| 1 | **steptools.com AP242 Ed.3 change notes** (`notes_ap242e3.html`) — remaining 16 of 21 new entities | Wave-7 opened this seam; 16 entity classes untouched; each is a candidate for the "Ed.2 reader silently drops" defect class captured in Pmi144–Pmi147 |
| 2 | **OCCT GitHub Issues & PRs 2024–2026** (`Open-Cascade-SAS/OCCT`) — PRs #407, #448, #1318, #1327; Issues #1283, #382, #349, #507, #541, #512, #1081, #1327 | Post-MANTIS tracker; specific reproducers and root causes; wave-7 covered pre-2020 MANTIS and 2020–22 MANTIS; 2024–2026 GitHub is unmined |
| 3 | **PTC Community — Circular Chamfer Import Faulty** (`community.ptc.com` post 27769) | MartinHanak diagnosis: Fusion 360 emits `CONICAL_SURFACE` as one continuous 360° face with one internal edge; Creo cannot process; distinct from Boolean-union coplanar-face duplicate topology (line 4186) |
| 4 | **Onshape 2024 STEP color import regression** (forum thread 23763) | April-2024 shipping behaviour change; per-face color chain silently produces default palette; distinct from wave-6 CATIA/Fusion color drops |
| 5 | **FreeCAD 2025 regressions** (`FreeCAD/FreeCAD` #30266, #22825) | Post-v1.0 issues not in wave-7's #20889 seam |

Sources evaluated but not primary:
- OCCT MANTIS 0033xxx — tracker requires authentication for individual bug pages; the GitHub
  migration surfaces the same defects with more detail
- BambuStudio #5197/#5208 — issue reports lack STEP entity detail (users provide no file dump)

---

## Defect Catalog (25 defects sampled)

Format per entry: pattern, entities, source, novelty judgment.

---

### E01 — AP242 Ed.3 `ANNOTATION_PLACEHOLDER_LEADER_LINE` entity dropped by Ed.2 readers

**Pattern:** STEP AP242 Ed.3 file with a PMI `ANNOTATION_PLACEHOLDER` (an annotation slot where the
final callout will be filled by a downstream tool, e.g., a serial-number stamp) linked to its
attachment point via `ANNOTATION_PLACEHOLDER_LEADER_LINE`; Ed.2 / AP214 readers do not recognise
either entity; both are silently dropped. The block's B-rep geometry loads correctly.

**Entities:** `ANNOTATION_PLACEHOLDER_LEADER_LINE` (Ed.3 new), `ANNOTATION_PLACEHOLDER`,
`DRAUGHTING_ANNOTATION_OCCURRENCE`

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.5

**Novel?** YES — analogous to `Pmi144` (`ANNOTATION_TO_ANNOTATION_LEADER_LINE`), but this is the
placeholder-slot leader (source is a placeholder, not a completed annotation); Pmi144 covers
annotation→annotation leader, not annotation→placeholder or placeholder→geometry. **NOVEL** (new
Ed.3 entity distinct from the four already-in-corpus Ed.3 leader-line entities).

---

### E02 — AP242 Ed.3 `ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE` dropped by Ed.2 readers

**Pattern:** STEP AP242 Ed.3 file with an annotation placeholder occurrence (the instance of a
placeholder within a specific drawing view) whose leader line is captured atomically as
`ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE`; Ed.2 / AP214 readers drop the entity;
downstream tools that populate placeholders lose the connection between the placeholder occurrence
and its leader.

**Entities:** `ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE` (Ed.3 new),
`ANNOTATION_OCCURRENCE`

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.5

**Novel?** YES — atomic occurrence+leader carrier distinct from Pmi144 (link between two completed
annotations) and E01 (separate leader entity for a placeholder). **NOVEL** (distinct Ed.3 entity).

---

### E03 — AP242 Ed.3 `ANNOTATION_TO_MODEL_LEADER_LINE` dropped by Ed.2 readers — annotation-to-3D-geometry leader link absent

**Pattern:** STEP AP242 Ed.3 file with a PMI callout whose leader arrow ends on a specific 3D face
of the model (as opposed to landing on another annotation). The link is expressed by
`ANNOTATION_TO_MODEL_LEADER_LINE`; Ed.2 / AP214 readers drop the entity, so the leader-target
association is lost. The B-rep and the annotation both load, but downstream inspection tools cannot
determine which face the leader points at.

**Entities:** `ANNOTATION_TO_MODEL_LEADER_LINE` (Ed.3 new), `ADVANCED_FACE`, `ANNOTATION_OCCURRENCE`

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.5

**Novel?** YES — Pmi144 covers annotation→annotation, `Pmi147` covers per-item geometry reference
(GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION), but this is the leader-line-to-geometry link entity
specifically. **NOVEL** (distinct Ed.3 entity: leader→3D-model target).

---

### E04 — AP242 Ed.3 `AUXILIARY_LEADER_LINE` dropped by Ed.2 readers — secondary leader lost

**Pattern:** STEP AP242 Ed.3 file with a PMI callout that has a primary leader plus an auxiliary
(second) leader that points at a related secondary reference (e.g., a symmetric feature). The
auxiliary leader is carried by `AUXILIARY_LEADER_LINE`; Ed.2 readers drop the entity, so the
callout appears with only one leader after import. Users looking at the imported drawing miss the
symmetric-feature indication entirely.

**Entities:** `AUXILIARY_LEADER_LINE` (Ed.3 new), `DRAUGHTING_ANNOTATION_OCCURRENCE`

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.5

**Novel?** YES — the "secondary/auxiliary leader" class isn't covered by any Pmi entry; Pmi053
covers single-point leader curve degeneracy (a wire defect within a leader), not a whole missing
auxiliary leader. **NOVEL**.

---

### E05 — AP242 Ed.3 `APLL_POINT` and `APLL_POINT_WITH_SURFACE` dropped by Ed.2 readers — leader endpoint absent

**Pattern:** STEP AP242 Ed.3 file where an `ANNOTATION_PLACEHOLDER_LEADER_LINE` uses `APLL_POINT`
(annotation-placeholder-leader-line point) to declare its endpoints — one of which is an
`APLL_POINT_WITH_SURFACE` that ties the endpoint to a specific `ADVANCED_FACE`. Ed.2 readers drop
both point entity types; the leader's endpoint metadata is lost even if the outer leader-line
container survives.

**Entities:** `APLL_POINT`, `APLL_POINT_WITH_SURFACE` (both Ed.3 new)

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.5

**Novel?** YES — a point-primitive Ed.3 class specific to placeholder-leader lines; distinct from
Pmi053 (leader curve degeneracy) and P016 (annotation point on wrong plane). **NOVEL**.

---

### E06 — AP242 Ed.3 `BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY` dropped by Ed.2 readers — assembly-level hole occurrence lost

**Pattern:** STEP AP242 Ed.3 assembly file (two parts linked in a `NEXT_ASSEMBLY_USAGE_OCCURRENCE`
chain) with a drilled hole authored at the part level via `BASIC_ROUND_HOLE`, but with an assembly-
context instance of that hole encoded as `BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY`. Ed.2 / AP214
readers drop the assembly-context occurrence entity; the part-level hole B-rep and (if wave-7's
Pmi145 is present) part-level `BASIC_ROUND_HOLE` feature semantic load, but the assembly-level
identity is lost, so CAM/inspection tools cannot correlate the hole to its assembly position.

**Entities:** `BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY` (Ed.3 new); `NEXT_ASSEMBLY_USAGE_OCCURRENCE`

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4

**Novel?** YES — `Pmi145` (wave-7 DEF-JJ) covers `BASIC_ROUND_HOLE` + `BASIC_ROUND_HOLE_OCCURRENCE`
at the part level; the assembly-context occurrence is a distinct entity. **NOVEL**.

---

### E07 — AP242 Ed.3 `BOUNDED_CURVE_WITH_LENGTH` dropped by Ed.2 readers — explicit length constraint lost

**Pattern:** STEP AP242 Ed.3 file with a `BOUNDED_CURVE` (e.g., a `B_SPLINE_CURVE_WITH_KNOTS`
arc segment) whose length is authored explicitly as a rigid constraint via `BOUNDED_CURVE_WITH_LENGTH`;
this Ed.3 entity carries the mathematically-computed length as an attribute so that downstream
tools can enforce it without re-integrating. Ed.2 readers drop the entity; the curve geometry
loads but the length-invariant is not accessible. In a length-constrained kinematic mechanism or a
length-critical printed-wire application, the constraint is silently absent.

**Entities:** `BOUNDED_CURVE_WITH_LENGTH` (Ed.3 new), `B_SPLINE_CURVE_WITH_KNOTS`

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4

**Novel?** YES — no existing catalog entry captures "explicit length-attribute on a curve entity";
wave-7 mined the retired `edge_with_length` (line 6894) but that's the *deprecated* Ed.2 entity —
this is the *new* Ed.3 replacement, which is a different class of defect (drop of the new entity,
not schema-version mismatch). **NOVEL**.

---

### E08 — AP242 Ed.3 `CONNECTED_EDGE_SUB_SET` dropped by Ed.2 readers — edge-loop sub-grouping lost

**Pattern:** STEP AP242 Ed.3 file with an `EDGE_LOOP` whose edges are additionally grouped by
`CONNECTED_EDGE_SUB_SET` — Ed.3's mechanism for identifying a semantic sub-region of an edge loop
(e.g., "the C1-continuous portion of a fillet chain"). Ed.2 readers drop the entity; the outer
edge loop still loads but the sub-grouping metadata is gone.

**Entities:** `CONNECTED_EDGE_SUB_SET` (Ed.3 new), `EDGE_LOOP`, `ORIENTED_EDGE`

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4

**Novel?** YES — no existing catalog entry treats edge-loop sub-grouping. The nearest is Tsh232
(three-valent ORIENTED_EDGE), which is a wire-topology defect, not a subgroup-of-loop entity drop.
**NOVEL**.

---

### E09 — AP242 Ed.3 `EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT` dropped by Ed.2

**Pattern:** STEP AP242 Ed.3 file with an edge-based topological representation whose overall
length is constrained (used for length-critical routing tables in wire-harness/pipe applications).
Ed.2 readers drop the entity; the edge-based representation still loads under the un-constrained
`EDGE_BASED_WIREFRAME_REPRESENTATION` fallback, but the length-invariant is absent.

**Entities:** `EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT` (Ed.3 new)

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4

**Novel?** YES — parallel to E07 but at the topological-representation level rather than the curve
level. **NOVEL**.

---

### E10 — AP242 Ed.3 `EDGE_BOUNDED_CURVE_WITH_LENGTH` dropped by Ed.2 readers

**Pattern:** STEP AP242 Ed.3 file with an edge-bounded curve carrying an explicit length attribute;
Ed.2 readers drop it. Distinct from E07 in that the length is on an edge-bounded curve entity
(coupling curve geometry to edge topology) rather than a bare bounded curve.

**Entities:** `EDGE_BOUNDED_CURVE_WITH_LENGTH` (Ed.3 new), `EDGE_CURVE`

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4

**Novel?** YES — third length-constraint variant, distinct from E07 (bare curve) and E09
(topological representation). **NOVEL** (but consider merging E07/E09/E10 into one composite
fixture if synthesis is expensive; the underlying class is "Ed.3 length-constraint entity
silently dropped, curve/edge/topology variants").

---

### E11 — AP242 Ed.3 `SUBPATH` dropped by Ed.2 readers — partial-path segment lost

**Pattern:** STEP AP242 Ed.3 file with a `PATH` (an ordered list of oriented edges) that has a
labelled `SUBPATH` — a semantic sub-region of the path, e.g., "the interior corner segment". Ed.2
readers drop the entity; the outer PATH survives but the SUBPATH annotation is lost. Feature
recognition that keys off SUBPATH labels (e.g., automated pocket-milling toolpath generation)
cannot recover the labelling.

**Entities:** `SUBPATH` (Ed.3 new), `PATH`, `ORIENTED_EDGE`

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4

**Novel?** YES — no catalog entry treats path sub-segments. **NOVEL**.

---

### E12 — AP242 Ed.3 `GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION` and `TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION` dropped

**Pattern:** STEP AP242 Ed.3 file where PMI annotations link to specific topological *items*
(individual edges/vertices) via `GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION` and the inverse
`TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION`. Ed.2 readers drop both entities. Distinct from `Pmi146`
(TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION) which associates whole models rather than individual items,
and from `Pmi147` (GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION) which is a per-item locator rather
than a bidirectional link entity.

**Entities:** `GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION`, `TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION`
(both Ed.3 new)

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4

**Novel?** YES — model-level vs item-level associations are separate Ed.3 entity classes; both
model-level (Pmi146) and per-item locator (Pmi147) are in catalog, but the item-level *bidirectional
association* pair (E12) is not. **NOVEL**.

---

### E13 — AP242 Ed.3 `DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION` dropped by Ed.2 readers

**Pattern:** STEP AP242 Ed.3 file with data-equivalence metadata — a claim that this file's data is
equivalent to some reference under specific criteria (e.g., "this simplified representation is
equivalent to the full CAD model at the reference tolerance"). The claim is encoded via
`DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION`. Ed.2 readers drop the entity; downstream QA
tools that would validate the equivalence claim don't know the claim was made.

**Entities:** `DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION` (Ed.3 new)

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4

**Novel?** YES — no catalog entry treats data-equivalence claims. **NOVEL**.

---

### E14 — AP242 Ed.3 `DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION` dropped

**Pattern:** STEP AP242 Ed.3 file with an equivalence-inspection assertion (a record that the file
has been checked for equivalence under specific criteria and passed). `DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION`
is the entity. Ed.2 readers drop it; the QA-provenance record is lost.

**Entities:** `DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION` (Ed.3 new)

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4

**Novel?** YES — companion to E13, a distinct entity for the inspection (as opposed to assertion)
half. **NOVEL** (but a strong merge candidate with E13 into one fixture that carries both entities).

---

### E15 — OCCT PR #407 / Issue #383 — NIST AP242 Ed.3 file `nist_stc_07_asme1_ap242-e3.stp` crashes datum-axis reader on colinear directions

**Pattern:** STEP AP242 Ed.3 file (NIST-PMI reference file `nist_stc_07_asme1_ap242-e3.stp`)
containing a datum-axis definition with two direction arrays whose contents happen to be colinear
in the specific bit-pattern encoding used by the file. OCCT ≤ 7.8's `STEPCAFControl_Reader.cxx:3007`
passes consecutive *array indices* (`Lower()`, `Lower()+1`, `Lower()+2`) into `gp_Dir.SetCoord()`
instead of *values* (`Value(Lower())`, `Value(Lower()+1)`, `Value(Lower()+2)`). Both direction
vectors thus receive the coordinates `(1, 2, 3)` regardless of file content; the subsequent
`gp_Ax2(aPnt, aDir, aDirR)` constructor calls `gp_Dir::CrossCross()` which raises
"result vector has zero norm" because the two directions are literally identical. Transfer fails
with "Step Reader: Failed to transfer nodes"; no geometry is loaded from the file.

**Entities:** `DATUM_REFERENCE_MODIFIER`, `AXIS2_PLACEMENT_3D` / `DIRECTION` arrays

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/383 and
https://github.com/Open-Cascade-SAS/OCCT/pull/407 (both fixed in OCCT 8.0)

**Novel?** YES — the mechanism is a producer-independent reader defect: any AP242 Ed.3 file with
the specific datum-axis chain triggers it (verified against NIST). No catalog entry captures "OCCT
reads array indices instead of array values → identical directions → CrossCross zero-norm exception
during datum-axis construction." The general "gp_Dir CrossCross zero-norm" fault mode isn't in the
catalog either. **NOVEL** (high-confidence, precisely described mechanism).

---

### E16 — OCCT PR #448 — Every OCCT-written AP242 file (~7.x through pre-8.0) has malformed FILE_SCHEMA with extra `.` between schema name and version triple

**Pattern:** Every STEP file that OCCT 7.x through pre-8.0 wrote in AP242 mode declares
`FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF. {1 0 10303 442 1 1 4 }'))` —
note the literal `.` (period) between `MIM_LF` and the ` {1 0 10303 442 1 1 4 }` version tuple.
The Part 21 grammar requires the schema name followed by whitespace and the version tuple; the
extra dot is not part of the schema-name grammar and strict Part 21 validators may reject the
declaration. Downstream readers that string-match the schema name may fail to recognise the AP242
schema and either fall back to AP203/AP214 (silently dropping AP242-specific PMI/tolerance
entities) or reject the file outright.

**Entities:** `FILE_SCHEMA` (P21 header)

**Source:** https://github.com/Open-Cascade-SAS/OCCT/pull/448 (patch removes the dot in
`StepAP214_Protocol.cxx:27`; the malformed string was in the codebase for years)

**Novel?** YES — line 615 covers *some* FILE_SCHEMA malformations (`_MIM` vs `_MIM_LF`, mixed case)
and line 44231 covers Ed.1 header + Ed.2 enum, but neither captures "producer inserts extra `.`
between schema name and version tuple." This is a specific, precisely-encoded producer-side header
defect: the entire OCCT-written AP242 catalog from ~7.x through 7.9 carries this string. **NOVEL**
(high-confidence, bytes-verifiable).

---

### E17 — OCCT PR #1318 — STEP writer infinite loop on oversized raw string with indentation prefix

**Pattern:** STEP file being *written* by OCCT ≤ 7.9 where a raw STEP string attribute (e.g., a
`DESCRIPTION` field containing a URL, a long path, or a base64 payload) is long enough that after
`StepData_StepWriter::AddString()` prepends an indentation prefix, the remaining columns in the
72-character output buffer are insufficient to hold *any* portion of the pending text. The writer
enters a flush-and-reindent loop that never makes progress; the writer hangs indefinitely, producing
no output file. The trigger requires (a) a string long enough that it must be split, and (b) the
current output-column position such that after indent, the free width is zero or negative.

**Entities:** STEP writer output buffer (`StepData_StepWriter::AddString()`); triggered by any
long string attribute in an entity being written

**Source:** https://github.com/Open-Cascade-SAS/OCCT/pull/1318 ("avoid infinite loop in STEP
writer"): "Split oversized raw STEP strings ... instead of repeatedly flushing the current line
when the text cannot fit into the 72-character buffer. Drop indentation for continuation lines
when the indented prefix would leave no room for the pending text."

**Novel?** YES — no catalog entry captures "72-character line-continuation buffer underrun causes
STEP writer infinite loop." Le048 (long line handling) covers reader-side long-line resilience,
not writer-side buffer arithmetic. **NOVEL** (high-confidence — the mechanism is fully described in
the PR text; the trigger is a long enough string attribute).

---

### E18 — OCCT Issue #1327 / FreeCAD #30266 — OCCT 8.0 STEP writer omits curved surfaces (regression from OCCT 7.x)

**Pattern:** STEP file being *written* by OCCT 8.0 (LibPack 3.5.0 for FreeCAD) from a shape
containing curved (B-spline / conic) surfaces. The writer regression causes some of the curved
surfaces to be silently absent from the output file: the shell/face topology exports, but the
underlying `B_SPLINE_SURFACE_WITH_KNOTS` / `CYLINDRICAL_SURFACE` entity references are missing or
null. Downstream slicers produce completely wrong toolpaths. The defect is regression-only: OCCT
7.x from the same source produces a correct STEP.

**Entities:** `ADVANCED_FACE`, `B_SPLINE_SURFACE_WITH_KNOTS`, `CYLINDRICAL_SURFACE`; writer path
(introduced in OCCT 8.0)

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/1327 (Step Export Regression);
https://github.com/FreeCAD/FreeCAD/issues/30266 (FreeCAD companion, "LibPack OCCT 8 - broken STEP
export")

**Novel?** NEAR-MISS — P007 covers "high-curvature B-spline flattens between OCCT versions"
(consumer-side re-tessellation), but E18 is a *writer*-side entity-omission regression, not a
tessellation-quality change. The output STEP is missing surface entities that should be present,
not producing coarser meshes. However the observable pattern ("STEP writer regression, curved
surfaces lost, OCCT version-dependent") overlaps with M162 (fillet-face misclassification, writer
regression). Judgment: the specific *entity-omission* nature of E18 (surface entities missing from
the DATA section entirely, not misclassified) is distinct enough. **NOVEL** (writer omission of
surface entities is a distinct class from writer misclassification and from consumer re-tessellation).

---

### E19 — OCCT Issue #382 — Single `CYLINDRICAL_SURFACE` face imports with wrong topology or tessellation

**Pattern:** STEP file containing one `ADVANCED_FACE` on a `CYLINDRICAL_SURFACE`; OCCT reads the
face but the resulting `TopoDS_Face` has wrong topology or tessellation (visually broken vs
other CAD systems); the mechanism is not yet root-caused in the OCCT tracker.

**Entities:** `ADVANCED_FACE`, `CYLINDRICAL_SURFACE`

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/382

**Novel?** NO — Gs185 covers "CONICAL_SURFACE imports as circle" and there are numerous entries
for single-face import defects (e.g., Gn174, P021). Without a root-cause reproducer this is a
duplicate of the existing single-face-import defect class. **HIT** (existing entries adequately
cover the "single analytical surface imports wrongly" pattern).

---

### E20 — OCCT Issue #349 — `bldc_driver.STEP` shows missing/incorrect faces in DRAW test harness

**Pattern:** STEP file (`bldc_driver.STEP` from a BLDC motor driver design) that FreeCAD renders
correctly but OCCT's own DRAW test harness misses several faces on import. No root cause is yet
established.

**Entities:** unspecified — reporter has not narrowed down the entity types

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/349

**Novel?** NO — without a specific mechanism identified, this is a generic instance of the "STEP
file imports incompletely in OCCT" class that is well-covered by A102, P015, Tsh003, etc. **HIT**.

---

### E21 — Fusion 360 → Creo circular chamfer: `CONICAL_SURFACE` emitted as single 360° face with one internal edge

**Pattern:** STEP file produced by Autodesk Fusion 360 containing a circular chamfer (the edge
between a hole and a flat face). Fusion emits the chamfer as one `ADVANCED_FACE` on a `CONICAL_SURFACE`
covering the full 360°, with the seam represented as one internal `EDGE_CURVE` between the two
periodic boundary vertices. PTC Creo Parametric expects (per PTC MartinHanak's community-expert
diagnosis) periodic surfaces to be split at 180° into two half-faces; Creo cannot process the
single-face encoding and drops the chamfer entirely. The same file opens correctly in SolidWorks,
FreeCAD, Rhino, and ZW3D — only Creo fails. Fusion emits `CONICAL_SURFACE not processed` upon
Creo import.

**Entities:** `ADVANCED_FACE`, `CONICAL_SURFACE` (full 360° extent), internal `EDGE_CURVE` seam

**Source:** https://community.ptc.com/t5/3D-Part-Assembly-Design/Circular-chamfer-import-faulty/td-p/27769

**Novel?** YES — line 4186 is the *opposite* pattern (Boolean union leaves an artificial internal
edge between two abutting co-conical faces that should be merged); E21 is *one* full-360° face with
one internal seam edge that some receivers require to be split. This is a producer-consumer
convention mismatch specific to periodic surfaces. No existing catalog entry captures "producer
emits single 360° periodic conical face with internal seam edge; receiver requires 180° split.".
**NOVEL** (high-confidence — the entity structure is precisely describable).

---

### E22 — Onshape April-2024 STEP color regression: per-face colors silently lost on import (unspecified STEP producer)

**Pattern:** STEP file (unspecified producer; the source thread mentions FreeCAD displays colors
correctly) that Onshape imported with correct per-face colors in January 2024 but silently imports
without any color (default palette) in April 2024, with identical import settings. Workaround: round-
trip through FreeCAD v1.0.0 RC2 as STEP re-export, then import to Onshape (restores colors).

**Entities:** `STYLED_ITEM`, `COLOUR_RGB`, `PRESENTATION_STYLE_ASSIGNMENT` chain

**Source:** https://forum.onshape.com/discussion/23763/step-import-missing-colors-has-the-step-file-import-process-been-changed

**Novel?** NO — A068 ("Color of root label not exported through XCAF"), Xp025 (colors lost on OCCT
re-export), OCCT MANTIS 0031809 (wave-7 D16, HIT via A068), and Onshape/Fusion color-drop entries
in wave-6 collectively cover the "STEP file color chain silently lost on import" class. This is a
specific Onshape build regression but the input-pattern (STEP file with STYLED_ITEM + COLOUR_RGB
chain, receiver drops colors) is fully covered. **HIT**.

---

### E23 — OCCT Issue #541 — KiCad-exported STEP round-trip loses origin AND corrupts colors, OCCT-version dependent

**Pattern:** STEP file produced by KiCad (using OCCT 7.8.1 with `TDocStd_XLinkTool` copying source
models into the destination XCAFDoc) exhibits distinct color and origin outcomes across three OCCT
re-export versions: OCCT 7.6.0 (bad origin, good colors), 7.7.0 (bad origin, good colors), 7.8.0
(bad origin, bad colors). The origin translation is wrong across all three; the colors survive
until 7.8.0 and then are lost — implicating a regression in the 7.7→7.8 XCAFDoc color chain.

**Entities:** `SHAPE_REPRESENTATION` / `CARTESIAN_POINT` origin; `STYLED_ITEM` + `COLOUR_RGB` chain
handled via `TDocStd_XLinkTool` copy

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/541 (also cross-referenced in KiCad
issue `kicad!19065`)

**Novel?** NEAR-MISS — Xp025 covers "origin displaced + colors lost on OCCT re-export." However
E23 pinpoints a specific cross-version regression on the `TDocStd_XLinkTool` copy path (the
XML-serialized XCAFDoc looks weird), which is a distinct producer-side mechanism from Xp025's
generic re-export. Judgment: **HIT** — Xp025 is close enough; the KiCad-specific tool path doesn't
change the input-pattern signature at the STEP-file level (any file that round-trips through the
XLinkTool copy exhibits the same output).

---

### E24 — FreeCAD 2025 STEP export: `Access Violation` when target directory is Windows Desktop (path-handling regression)

**Pattern:** FreeCAD dev 2025-09-30 export to STEP or STL directly to Windows Desktop fails with
"Access Violation"; export to a subfolder of Desktop works; export to Desktop with previous dev
version (2025-09-02) also worked.

**Entities:** N/A — file-system path handling, not STEP content

**Source:** https://github.com/FreeCAD/FreeCAD/issues/24361

**Novel?** NO — this is an OS-path-handling regression, not a STEP-content defect. Not applicable
to the STEP corpus. **HIT** (out of scope).

---

### E25 — AP242 Ed.3 combined-entity fixture: single file exercising ALL retained Ed.3 associations at once

**Pattern:** Meta-fixture idea — a single STEP AP242 Ed.3 file that contains one instance of each
remaining Ed.3 association/leader entity (E01–E14, minus the individual singletons) to stress-test
whether Ed.2 readers gracefully report a Void status for the entire Ed.3 module rather than
crashing on the first unrecognized entity. This is a *coverage* fixture, not a distinct defect.

**Entities:** all Ed.3 new entities listed above

**Source:** derived from the AP242 Ed.3 change notes taken as a whole

**Novel?** NO — this is a synthesis strategy, not a defect. Belongs in the B4.5d fixture-synthesis
plan rather than the mining audit. **N/A**.

---

## Unique Novel Count

After removing merges/duplicates:
- **Novel:** E01, E02, E03, E04, E05, E06, E07, E08, E09, E10, E11, E12, E13, E14, E15, E16, E17, E18, E21 = **19**
- **HIT / non-defect / out of scope:** E19, E20, E22, E23, E24, E25 = 6

Sampled defects: **25**  
Novel: **19**  
Novelty: **19 / 25 = 76.0%**

Caveats on the novelty count:
- E07/E09/E10 (three length-constraint variants) could plausibly be merged into ONE fixture that
  demonstrates the class; if merged, novel drops to 17 → 17/23 = 73.9%.
- E13/E14 (assessment/inspection halves of data-equivalence) could be merged; if merged, novel
  drops further to 16 → 16/22 = 72.7%.
- Conservative merged count: **16 novel / 22 unique = 72.7%**.

Either way, wave-8 is well above the wave-7 rate (34.8%) — reflecting that the AP242 Ed.3 seam is
genuinely 21-entities-wide and wave-7 only touched 4.

---

## Novelty Summary Table

| ID | Short name | Novel? |
|----|-----------|--------|
| E01 | AP242 Ed.3 `ANNOTATION_PLACEHOLDER_LEADER_LINE` dropped | **YES** |
| E02 | AP242 Ed.3 `ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE` dropped | **YES** |
| E03 | AP242 Ed.3 `ANNOTATION_TO_MODEL_LEADER_LINE` dropped | **YES** |
| E04 | AP242 Ed.3 `AUXILIARY_LEADER_LINE` dropped | **YES** |
| E05 | AP242 Ed.3 `APLL_POINT` / `APLL_POINT_WITH_SURFACE` dropped | **YES** |
| E06 | AP242 Ed.3 `BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY` dropped | **YES** |
| E07 | AP242 Ed.3 `BOUNDED_CURVE_WITH_LENGTH` dropped | **YES** |
| E08 | AP242 Ed.3 `CONNECTED_EDGE_SUB_SET` dropped | **YES** |
| E09 | AP242 Ed.3 `EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT` dropped | **YES** |
| E10 | AP242 Ed.3 `EDGE_BOUNDED_CURVE_WITH_LENGTH` dropped | **YES** |
| E11 | AP242 Ed.3 `SUBPATH` dropped | **YES** |
| E12 | AP242 Ed.3 `GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION` / inverse dropped | **YES** |
| E13 | AP242 Ed.3 `DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION` dropped | **YES** |
| E14 | AP242 Ed.3 `DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION` dropped | **YES** |
| E15 | OCCT #383/#407: NIST AP242 Ed.3 datum-axis reader confuses indices vs values → `CrossCross` zero-norm | **YES** |
| E16 | OCCT #448: every OCCT-written AP242 file has extra `.` in FILE_SCHEMA string | **YES** |
| E17 | OCCT #1318: STEP writer infinite loop on oversized raw string with indent prefix | **YES** |
| E18 | OCCT #1327 / FreeCAD #30266: OCCT 8 STEP writer regression drops curved surface entities | **YES** |
| E19 | OCCT #382: single `CYLINDRICAL_SURFACE` face imports wrong | NO (generic single-face import) |
| E20 | OCCT #349: `bldc_driver.STEP` missing faces in DRAW | NO (no mechanism identified) |
| E21 | Fusion 360 → Creo: circular chamfer as single 360° `CONICAL_SURFACE` with internal seam | **YES** |
| E22 | Onshape April-2024 color regression | NO — A068 / Xp025 |
| E23 | OCCT #541: KiCad round-trip origin+colors, OCCT-version regression | NO — Xp025 |
| E24 | FreeCAD 2025 Desktop export Access Violation | NO (OS path, out of scope) |
| E25 | AP242 Ed.3 combined-entity meta-fixture | N/A (synthesis strategy) |

**Novel count (raw sampling):** 19 / 25 = 76.0%  
**Novel count (with E07/E09/E10 merge, E13/E14 merge):** 16 / 22 = 72.7%

---

## Novelty Rate Comparison

| Wave | Sources | Defects sampled | Novel count | Novelty rate |
|------|---------|----------------|-------------|-------------|
| Wave 1 | OCCT/FreeCAD/CadQuery (early FOSS) | ~130 | ~32 | 24.6% |
| Wave 2 | OCE/FreeCAD-extended/KiCad | ~120 | ~13 | 10.5% |
| Wave 3 | KiBot/Blender-addon/deeper FOSS | ~100 | ~9 | 9.3% |
| Wave 4 | HOOPS Exchange / Inventor / OCCT-new / Academic | 35 | 12 | 34.3% |
| Wave 5 | FreeCAD-new / OCCT V8 / non-standard STEP forum | 25 | 7 | 28.0% |
| Wave 6 | OCCT MANTIS pre-2020 / Fusion 360 / CATIA V5-V6 / NIST AP242 / CAM forums | 30 | 14 | 46.7% |
| Wave 7 | Slicers / ISO 10303-21 Ed.3 / AP242 Ed.3 (partial) / OCCT MANTIS 2020-22 / FreeCAD v1.0 | 23 | 8 | 34.8% |
| **Wave 8** | **AP242 Ed.3 remaining 16 entities + OCCT GitHub 2024-2026 + Fusion→Creo chamfer** | **25** | **19 (16 after merges)** | **76.0% (72.7% merged)** |

Wave-8's high novelty rate reflects the untapped Ed.3 entity seam: wave-7 sampled only 4 of the 21
new Ed.3 entities. Wave-8 covers 15 more Ed.3 entities (E01–E14). At current pace, 3–4 more waves
would exhaust the Ed.3 entity seam entirely; each subsequent wave will likely show lower novelty as
the seam closes.

---

## Wave Trend

```
Wave 1: 24.6%  ████████████████████████░
Wave 2: 10.5%  ██████████░
Wave 3:  9.3%  █████████░
Wave 4: 34.3%  ██████████████████████████████████░
Wave 5: 28.0%  ████████████████████████████░
Wave 6: 46.7%  ██████████████████████████████████████████████░
Wave 7: 34.8%  ██████████████████████████████████░
Wave 8: 76.0%  ████████████████████████████████████████████████████████████████████████████░
```

**Wave trend line:** `24.6% → 10.5% → 9.3% → 34.3% → 28.0% → 46.7% → 34.8% → 76.0%`

---

## DEFERRED List — Novel defects for B4.5d fixture synthesis

Tags continue from wave-7's DEF-HH through DEF-OO. Wave-8 assigns DEF-PP through DEF-EEE.

### DEF-PP: AP242 Ed.3 `ANNOTATION_PLACEHOLDER_LEADER_LINE` dropped by Ed.2 readers (E01)

STEP AP242 Ed.3 file with a minimal cube `MANIFOLD_SOLID_BREP` (6-face 10×10×10 mm) plus one PMI
`ANNOTATION_PLACEHOLDER` (unfilled callout slot at `(15, 0, 5)`) linked to a top-face `SHAPE_ASPECT`
via `ANNOTATION_PLACEHOLDER_LEADER_LINE('pl_leader',#placeholder,#face_top_sa,$)`. File header
declares `{1 0 10303 442 4 1 4}` (AP242 Ed.3). Expected: Ed.3 readers resolve the placeholder+leader
pair; Ed.2 / AP214 readers produce Void transfer status; cube geometry still loads.

**Section:** §12-7-pmi  
**Confidence:** HIGH (entity precisely named in Ed.3 §4.5)  
**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html  
**Oracle verify needed?** No — accept-live-oracle: OCCT drops the Ed.3 entity, and that IS the defect.

---

### DEF-QQ: AP242 Ed.3 `ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE` dropped (E02)

STEP AP242 Ed.3 file with a `DRAUGHTING_ANNOTATION_OCCURRENCE` whose leader is fused into a single
`ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE('...', #occ, #leader_endpoints)` atomic entity
(distinct from DEF-PP's separate placeholder + leader entity pair). Ed.3 readers resolve the atomic
occurrence; Ed.2 readers drop it. Cube geometry co-present.

**Section:** §12-7-pmi  
**Confidence:** HIGH  
**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html  
**Oracle verify needed?** No — same accept-live-oracle pattern as Pmi144–Pmi147.

---

### DEF-RR: AP242 Ed.3 `ANNOTATION_TO_MODEL_LEADER_LINE` dropped (E03)

STEP AP242 Ed.3 file with a position tolerance callout linked by
`ANNOTATION_TO_MODEL_LEADER_LINE('atml_1',#annot,#face_top,$)` to a specific `ADVANCED_FACE` of a
cube. Ed.3 readers resolve the annotation→3D-face link; Ed.2 readers drop the entity, so downstream
inspection tools cannot determine which face the leader points at.

**Section:** §12-7-pmi  
**Confidence:** HIGH  
**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html  
**Oracle verify needed?** No — accept-live-oracle.

---

### DEF-SS: AP242 Ed.3 `AUXILIARY_LEADER_LINE` dropped (E04)

STEP AP242 Ed.3 file with a symmetric-feature callout (single position tolerance) that has a primary
leader AND a secondary `AUXILIARY_LEADER_LINE('aux_leader',#annot,#face_symm,$)` pointing at a
mirror feature. Ed.3 readers resolve both leaders; Ed.2 readers drop the auxiliary, so the imported
callout appears with only the primary leader (silently missing the symmetric-feature indication).

**Section:** §12-7-pmi  
**Confidence:** HIGH  
**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html  
**Oracle verify needed?** No — accept-live-oracle.

---

### DEF-TT: AP242 Ed.3 `APLL_POINT` and `APLL_POINT_WITH_SURFACE` dropped (E05)

STEP AP242 Ed.3 file where `ANNOTATION_PLACEHOLDER_LEADER_LINE` endpoints are declared as
`APLL_POINT` entities (one plain `APLL_POINT(x,y,z)` and one `APLL_POINT_WITH_SURFACE(x,y,z,#face)`
that ties the endpoint to a face). Ed.3 readers resolve the endpoint chain; Ed.2 readers drop both
point entities; leader-line container (if it survives) has orphan endpoint references.

**Section:** §12-7-pmi  
**Confidence:** HIGH  
**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html  
**Oracle verify needed?** No — accept-live-oracle.

---

### DEF-UU: AP242 Ed.3 `BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY` dropped (E06)

STEP AP242 Ed.3 assembly file (parent product P0, child product P1 linked by
`NEXT_ASSEMBLY_USAGE_OCCURRENCE`) where P1 has a drilled through-hole with:
(a) part-level `BASIC_ROUND_HOLE` (as in `Pmi145`);
(b) assembly-level `BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY('brh_asm_occ_1',$,$,#nauo,#brh)`
    binding the hole feature to its assembly-context occurrence.
Ed.3 readers expose the hole at both part and assembly levels; Ed.2 readers drop the
assembly-context occurrence; CAM/inspection tools can locate the hole per-part but not per-assembly.

**Section:** §12-7-pmi (or §12-6-assembly)  
**Confidence:** MEDIUM (entity signature requires AP242 Ed.3 schema for the `_IN_ASSEMBLY` subclass)  
**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html  
**Oracle verify needed?** No — accept-live-oracle.

---

### DEF-VV: AP242 Ed.3 length-constrained curve/topology triad (E07 + E09 + E10 merged)

STEP AP242 Ed.3 file demonstrating all three length-constraint entities in one fixture:
(a) a `BOUNDED_CURVE_WITH_LENGTH('bcwl',#bspline_curve,POSITIVE_LENGTH_MEASURE(37.5))` on a
    B-spline curve;
(b) an `EDGE_BOUNDED_CURVE_WITH_LENGTH` on the corresponding `EDGE_CURVE`;
(c) an `EDGE_BASED_TOPOLOGICAL_REPRESENTATION_WITH_LENGTH_CONSTRAINT` collecting the edges at the
    topological-representation level.
Ed.3 readers resolve all three constraint entities and expose the length invariant; Ed.2 readers
drop all three; curve geometry still loads but the length-invariant is silently absent — a
wire-harness routing or gasket-length application would fail to enforce the constraint.

**Section:** §12-3-curves (or §12-2b-nurbs)  
**Confidence:** MEDIUM (three distinct Ed.3 entities; ensure they layer correctly)  
**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4  
**Oracle verify needed?** No — accept-live-oracle.

---

### DEF-WW: AP242 Ed.3 `CONNECTED_EDGE_SUB_SET` dropped (E08)

STEP AP242 Ed.3 file with a face whose `EDGE_LOOP` has 8 oriented edges; a
`CONNECTED_EDGE_SUB_SET('c1_fillet_chain',(#e3,#e4,#e5))` groups edges 3–5 as a semantic
sub-region (labelled `c1_fillet_chain`). Ed.3 readers expose the sub-grouping; Ed.2 readers drop
the entity; the edge-loop still loads with all 8 edges but the semantic sub-region is silently gone.

**Section:** §12-4-topology  
**Confidence:** MEDIUM  
**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4  
**Oracle verify needed?** No — accept-live-oracle.

---

### DEF-XX: AP242 Ed.3 `SUBPATH` dropped (E11)

STEP AP242 Ed.3 file with a `PATH` (ordered list of `ORIENTED_EDGE`) that has a
`SUBPATH('interior_corner_segment',(#oe3,#oe4))` labelling edges 3–4 as a named sub-region.
Ed.3 readers expose the sub-path; Ed.2 readers drop the entity; the PATH still loads but the
sub-region labelling is lost. Automated pocket-milling toolpath generation that keys off SUBPATH
labels cannot recover the labelling.

**Section:** §12-4-topology  
**Confidence:** MEDIUM  
**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4  
**Oracle verify needed?** No — accept-live-oracle.

---

### DEF-YY: AP242 Ed.3 item-level topology-geometry association pair dropped (E12)

STEP AP242 Ed.3 file with PMI annotations linking to specific topological *items* via
`GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION('g2t_item',#face,#edge)` and its inverse
`TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION('t2g_item',#edge,#face)`. These are the item-level companions
to `Pmi146`'s model-level `TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION` pair. Ed.3 readers resolve the
item-level associations; Ed.2 readers drop them. Distinct from `Pmi147` (`GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION`)
which is a locator entity; E12 is a bidirectional link.

**Section:** §12-7-pmi  
**Confidence:** MEDIUM (requires AP242 Ed.3 schema knowledge for these two subclasses)  
**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4  
**Oracle verify needed?** No — accept-live-oracle.

---

### DEF-ZZ: AP242 Ed.3 data-equivalence assertion+inspection pair dropped (E13 + E14 merged)

STEP AP242 Ed.3 file with a QA-provenance record: a `DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION('deca_1',...)`
asserting that this file's simplified representation is equivalent to a full CAD model under
specific criteria, plus a `DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION('deci_1',...)`
recording that the equivalence has been inspected and passed. Ed.3 readers expose both records;
Ed.2 readers drop them; QA workflows that would consume the equivalence claim silently receive
nothing.

**Section:** §12-13-provenance (or a new §12-13-ap242-metadata section if provenance doesn't
exist)  
**Confidence:** MEDIUM (entities are precisely named in the Ed.3 notes but the exact attribute
tables need Part 1 lookup)  
**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html §4.4  
**Oracle verify needed?** No — accept-live-oracle.

---

### DEF-AAA: OCCT #383/#407 — NIST AP242 Ed.3 datum-axis reader confuses indices vs values → `CrossCross` zero-norm exception (E15)

STEP AP242 Ed.3 file matching the structure of NIST's `nist_stc_07_asme1_ap242-e3.stp`: contains
a `DATUM` with a `DATUM_REFERENCE_MODIFIER` whose axis is defined through the specific chain that
OCCT reads via `STEPCAFControl_Reader.cxx:3007` — three `TColStd_HArray1OfReal` direction arrays
whose `Lower()` indices are 1, 2, 3. Pre-fix OCCT (≤ 7.9) passes indices 1/2/3 into `gp_Dir.SetCoord()`
instead of the array values, so both directions receive `(1,2,3)`, are colinear, and `gp_Ax2`
raises "result vector has zero norm" via `gp_Dir::CrossCross()`. Post-fix (OCCT 8.0) uses `Value(Lower())`
and reads the correct coordinates. Cube geometry co-present as carrier B-rep.

**Section:** §12-7-pmi  
**Confidence:** HIGH (mechanism precisely described in issue #383; the STEP entity chain triggers
the defect in any AP242 file with the datum-axis encoding)  
**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/383, https://github.com/Open-Cascade-SAS/OCCT/pull/407  
**Oracle verify needed?** No — the defect IS the OCCT reader behavior; live oracle IS the failure
mode.

---

### DEF-BBB: OCCT #448 — every OCCT-written AP242 file has `FILE_SCHEMA` with extra `.` between schema name and version triple (E16)

STEP file with `FILE_SCHEMA` declaration exactly as OCCT 7.x through pre-8.0 wrote it:
`FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF. {1 0 10303 442 1 1 4 }'));` — the
literal `.` (period) between `MIM_LF` and the version tuple. The DATA section contains a minimal
cube `MANIFOLD_SOLID_BREP` plus a single AP242-specific `GEOMETRIC_TOLERANCE` (flatness 0.05 mm).
Expected: strict Part 21 validators reject the schema declaration; permissive readers may fall
back to AP203/AP214 handling and silently drop the AP242-specific tolerance entity; the malformed
schema string is precisely `_MIM_LF. {` (with the dot) rather than `_MIM_LF {`.

**Section:** §12-1-headers  
**Confidence:** HIGH (patch line is exact; string is byte-verifiable)  
**Source:** https://github.com/Open-Cascade-SAS/OCCT/pull/448  
**Oracle verify needed?** No — the malformed string is present verbatim in the fixture and
detectable by byte assertion.

---

### DEF-CCC: OCCT #1318 — STEP writer infinite loop on oversized raw string with indentation prefix (E17)

STEP file WRITER-INTENT fixture: a STEP DATA-section entity whose text-content field is intentionally
long enough that the writer's 72-character line-wrap logic combined with the indentation prefix
produces zero remaining columns after indent. A synthetic fixture might use a `DESCRIPTION`
attribute of 512 chars or more on a nested entity so that the indent depth is nonzero and the
72-char buffer is exhausted by the prefix. Expected: pre-fix OCCT writer hangs infinitely; post-fix
(PR #1318) writer either drops the indent or splits the string cleanly. The fixture would demonstrate
the exact string-length and indent-depth combination that trips the loop. As this is writer-intent,
the fixture format is a JSON/Python spec of the shape to write, plus the oracle's expected byte
sequence in the output STEP.

**Section:** §12-1-headers or a new §12-14-writer-defects section  
**Confidence:** MEDIUM (mechanism is fully described but exact trip-string length depends on OCCT
writer's exact indent policy; needs oracle verify against pre-fix OCCT)  
**Source:** https://github.com/Open-Cascade-SAS/OCCT/pull/1318  
**Oracle verify needed?** YES — need to reproduce the infinite loop against pre-fix OCCT to confirm
the exact trip conditions.

---

### DEF-DDD: OCCT #1327 / FreeCAD #30266 — OCCT 8.0 STEP writer regression drops curved surface entities (E18)

STEP file exercising the OCCT 8.0 writer regression: a shape with mixed planar and curved
(B-spline, cylindrical) surfaces, written via the C++ `STEPControl_Writer` API path (as FreeCAD
uses) rather than DRAW (which does not reproduce). The written STEP output has correct planar
`ADVANCED_FACE`/PLANE entities but the B-spline and cylindrical faces' underlying surface entity
references are silently null or missing. Slicers produce completely wrong toolpaths. Regression is
version-specific: OCCT 7.x writes the same source shape correctly. Fixture takes writer-intent
form.

**Section:** §12-2b-nurbs (or §12-14-writer-defects)  
**Confidence:** MEDIUM (regression is confirmed but the exact writer-code path is not root-caused
in the tracker; needs oracle verify against OCCT 8.0 to reproduce)  
**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/1327, https://github.com/FreeCAD/FreeCAD/issues/30266  
**Oracle verify needed?** YES — verify OCCT 8.0 vs 7.x diff on the same input shape.

---

### DEF-EEE: Fusion 360 → Creo circular chamfer — single 360° `CONICAL_SURFACE` with internal seam edge (E21)

STEP file matching Fusion 360's output pattern for a circular chamfer: one `ADVANCED_FACE` on a
`CONICAL_SURFACE` covering the full 360° angular extent, with the seam represented as one internal
`EDGE_CURVE` on the periodic boundary between the two seam vertices. This is topologically valid
(the face wraps around) but breaks receivers that require periodic surfaces to be split at 180°.
Expected: SolidWorks, FreeCAD, Rhino, ZW3D accept the fixture; PTC Creo Parametric drops the
chamfer with `CONICAL_SURFACE not processed`. Fixture pattern: hole+chamfer joint on a plate.

**Section:** §12-2-surfaces  
**Confidence:** HIGH (entity structure is precisely describable per MartinHanak's PTC community
diagnosis)  
**Source:** https://community.ptc.com/t5/3D-Part-Assembly-Design/Circular-chamfer-import-faulty/td-p/27769  
**Oracle verify needed?** No — the defect is on the receiver side (Creo); OCCT will accept the
fixture and load it correctly, so the fixture demonstrates the producer-consumer convention
mismatch as a byte-level property of the file.

---

## Notes for B4.5d Fixture Synthesis

**High-confidence Ed.3 leader-line family (DEF-PP through DEF-TT):** all follow the Pmi144–Pmi147
accept-live-oracle pattern; each needs only a minimal cube carrier + the specific Ed.3 entity
chain + the AP242 Ed.3 file header `{1 0 10303 442 4 1 4}`. Synthesize as a batch.

**MEDIUM-confidence Ed.3 topology-length family (DEF-VV, DEF-WW, DEF-XX):** three related entity
classes (BOUNDED_CURVE_WITH_LENGTH, CONNECTED_EDGE_SUB_SET, SUBPATH) that all attach length or
sub-region metadata to existing topology; each needs the underlying topology (loop/path/curve) plus
the metadata entity referencing it. Confirm entity attribute lists against Ed.3 EXPRESS.

**HIGH-confidence OCCT-tracker fixtures (DEF-AAA, DEF-BBB):** DEF-AAA is precisely described in
issue #383 (indices vs values in `SetCoord()` calls). DEF-BBB is byte-verifiable — the string
`_MIM_LF. {` with the dot is the exact defect.

**MEDIUM-confidence writer fixtures (DEF-CCC, DEF-DDD):** both are writer-intent regressions
requiring oracle verify against OCCT ≤ 7.9 (DEF-CCC) or OCCT 8.0 (DEF-DDD).

**HIGH-confidence receiver-convention fixture (DEF-EEE):** the Creo circular-chamfer pattern is
precisely encodable as one `ADVANCED_FACE` + one `CONICAL_SURFACE` + one internal seam `EDGE_CURVE`
on a periodic boundary.

Batches (roughly grouped by section for parallel synthesis):
- **§12-7-pmi batch (7 fixtures):** DEF-PP, DEF-QQ, DEF-RR, DEF-SS, DEF-TT, DEF-UU, DEF-YY, DEF-AAA
- **§12-3-curves / §12-2b-nurbs batch (2 fixtures):** DEF-VV, DEF-DDD (writer-intent)
- **§12-2-surfaces batch (1 fixture):** DEF-EEE
- **§12-4-topology batch (2 fixtures):** DEF-WW, DEF-XX
- **§12-13 or new §12-14 (2 fixtures):** DEF-ZZ (data-equivalence), DEF-BBB (header dot), DEF-CCC (writer loop)

Total: 15–16 new fixtures depending on E07/E09/E10 and E13/E14 merges.

---

## Appendix: Source URLs

1. AP242 Edition 3 change notes:
   - https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (21 new entities, listed above)

2. OCCT GitHub Issues & PRs 2024–2026:
   - https://github.com/Open-Cascade-SAS/OCCT/issues/383 (NIST AP242 Ed.3 datum axis exception)
   - https://github.com/Open-Cascade-SAS/OCCT/pull/407 (fix for #383)
   - https://github.com/Open-Cascade-SAS/OCCT/pull/448 (AP242 SchemaName remove dot)
   - https://github.com/Open-Cascade-SAS/OCCT/pull/1318 (STEP writer infinite loop fix)
   - https://github.com/Open-Cascade-SAS/OCCT/issues/1327 (OCCT 8 STEP writer regression)
   - https://github.com/Open-Cascade-SAS/OCCT/issues/1283 (COMPOUND_REPRESENTATION_ITEM — HIT via Pmi137)
   - https://github.com/Open-Cascade-SAS/OCCT/issues/382 (single CYLINDRICAL_SURFACE wrong — HIT)
   - https://github.com/Open-Cascade-SAS/OCCT/issues/349 (bldc_driver missing faces — HIT)
   - https://github.com/Open-Cascade-SAS/OCCT/issues/512 (cascade.unit=M infinite — HIT via N015)
   - https://github.com/Open-Cascade-SAS/OCCT/issues/541 (KiCad round-trip origin+colors — HIT via Xp025)
   - https://github.com/Open-Cascade-SAS/OCCT/issues/1081 (AP242→GLB balloon — HIT via Pmi062)

3. FreeCAD companion issues:
   - https://github.com/FreeCAD/FreeCAD/issues/30266 (LibPack OCCT 8 broken STEP export — companion to OCCT #1327)
   - https://github.com/FreeCAD/FreeCAD/issues/24361 (Desktop export Access Violation — out of scope)

4. Fusion 360 → Creo circular chamfer diagnosis:
   - https://community.ptc.com/t5/3D-Part-Assembly-Design/Circular-chamfer-import-faulty/td-p/27769

5. Onshape 2024 color regression:
   - https://forum.onshape.com/discussion/23763/step-import-missing-colors-has-the-step-file-import-process-been-changed (HIT via A068 / Xp025)

---

## Wave-8 Summary

- **Sampled:** 25 defects across AP242 Ed.3 remaining entities + OCCT GitHub 2024–2026 + Fusion→Creo
  circular chamfer + Onshape color regression + FreeCAD 2025 regressions.
- **Novel:** 19 (raw) / 16 (with plausible merges) — highest novelty rate to date (76.0% / 72.7%).
- **Dominant novel source:** AP242 Ed.3 remaining 16 entities (14 of the 19 novel defects come from
  this seam). Wave-7 opened it; wave-8 covers most of the remainder.
- **Complementary novel source (5 defects):** OCCT GitHub tracker 2024–2026 — datum-axis
  indices-vs-values (DEF-AAA), FILE_SCHEMA extra dot (DEF-BBB), writer infinite loop (DEF-CCC),
  OCCT 8 curved-surface writer regression (DEF-DDD), Fusion→Creo circular chamfer (DEF-EEE).
- **Remaining Ed.3 headroom:** roughly 2 Ed.3 entities untouched after wave-8 — the wave has largely
  exhausted the Ed.3 entity seam. Wave-9 will need a new seam (candidates: ISO 10303 Part 1
  metadata additions in AP242 Ed.3, kinematic-module Ed.3 additions not on the steptools change
  notes page, or CAx-IF Round 55/56 test-suite content).
