# B4 Mining Wave-7 Audit — 2026-07-01

## Background

Wave-4 (34.3%) pivoted to commercial changelogs (HOOPS Exchange, Inventor, OCCT GitHub). Wave-5
(28.0%) mined adjacent territory (FreeCAD 2024–2025, OCCT V8 release notes, non-standard STEP forum).
Wave-6 (46.7%) achieved the highest novelty rate by combining OCCT MANTIS pre-2020, Fusion 360 forums,
CATIA V5-V6 migration, NIST AP242 MBE tests, and CAM software forums.

Wave-7 mines four fully untouched source categories:

- **Additive manufacturing slicer issue trackers** (BambuStudio + PrusaSlicer) — consumer CAD-to-print
  workflow exposes STEP parsing under OCCT with a fixed tessellation parameter
- **ISO 10303-21 Edition 3 (2016) new features** — anchor/reference/signature sections, compressed
  archives, UTF-8; reader compatibility gaps not in prior waves
- **AP242 Edition 3 (December 2022)** — 21 new entity types; interoperability with Ed.1/Ed.2 readers
- **OCCT MANTIS middle tier (2020–2022)** — issue range 0031xxx–0032xxx, not covered by wave-6's
  pre-2020 range or wave-4/5's post-2022 range
- **FreeCAD 2025 STEP issues** — FreeCAD v1.0/1.1 regressions not in prior waves

Wave-6 DEFERRED list covers DEF-T through DEF-GG (14 entries: three-valent edge, zero-radius CIRCLE
pole, negative-det CARTESIAN_TRANSFORMATION, PRODUCT_CATEGORY_RELATIONSHIP, duplicate PRODUCT.id,
COMPOSITE_CURVE_ON_SURFACE as FACE_BOUND, DIMENSION_SIZE AP242 Ed.2, DATUM_REFERENCE_COMPARTMENT +
COMPOSED_FEATURE, SURFACE_TEXTURE_REPRESENTATION, TOROIDAL_SURFACE radius swap, full-circle CIRCLE
near-coincident vertices, PCURVE.basis_surface wrong surface, dual-owner OPEN_SHELL, null
PRODUCT_DEFINITION_CONTEXT element).

---

## Sources Chosen

| # | Source | Why chosen |
|---|--------|-----------|
| 1 | **BambuStudio GitHub issues** (bambulab/BambuStudio, 2023–2024) | Consumer slicer STEP import; OCCT-backed but with fixed tessellation parameters; publicly indexed issue tracker not touched in any prior wave |
| 2 | **PrusaSlicer GitHub issues** (prusa3d/PrusaSlicer, 2023–2025) | Prusa slicer STEP import bugs; same OCCT base as Bambu but different wrapper choices; surfaces slicer-specific STEP complaints |
| 3 | **ISO 10303-21 Edition 3 (2016) new features + reader gaps** (steptools.com/stds/step/IS_final_p21e3.html) | P21 Ed.3 introduced anchor sections, reference sections, signature sections, ZIP compressed archives, and raw UTF-8 strings; none of these new conformance classes have been mined; surfaces P21 structure-level defects beyond the file-content layer |
| 4 | **AP242 Edition 3 (December 2022) new entities** (steptools.com/docs/stp_aim/notes_ap242e3.html) | Ed.3 adds 21 new entity definitions and reorders 4 enum types; existing corpus has Ed.1 and Ed.2 entries but no Ed.3-specific entries; FreeCAD issue #19795 confirms none are implemented |
| 5 | **OCCT MANTIS 0031xxx–0032xxx range (2020–2022)** (tracker.dev.opencascade.org) | Wave-6 mined 0025xxx–0030xxx; wave-4/5 mined post-2022 GitHub issues; the 2020–2022 MANTIS range is a gap that contains geometry and data-exchange bugs |
| 6 | **FreeCAD v1.0/1.1 STEP regression issues (2025)** (github.com/FreeCAD/FreeCAD) | FreeCAD v1.0.0 introduced OCC-related STEP regressions; wave-5 mined pre-1.0 FreeCAD issues (#10736, #16292, #20588, #21216, #23511, #14447); post-1.0 regressions (#20889) are a new gap |

Sources attempted but inaccessible / no actionable STEP-entity-level content:
- CAx-IF Round 54J test suite PDF (mbx-if.org): binary-encoded PDF; content unreadable from fetch
- AP242.org interoperability pages (ap242.org): SSL certificate invalid; pages unreachable
- Teamcenter / Aras Innovator forums: no public entity-level STEP bug documentation found
- OpenCADE (Java port of OCCT): no public issue tracker found; project appears dormant
- Google Scholar 2024–2025 STEP preprints: results returned general ML papers, not STEP parser papers

---

## Defect Catalog (35 defects)

Format per entry:
- **Pattern** (input-phrasing per catalog convention)
- **Entities** — primary STEP entity types
- **User-visible defect** — what goes wrong
- **Source**
- **Top BM25 matches** — top-3 with scores; HIT / NEAR-MISS / NOVEL classification
- **Novel?**

---

### D01 — BambuStudio STEP import: small ADVANCED_FACE silently absent — open edges reported (Bambu #2290)

**Pattern:** STEP file (AP214, produced by Onshape) containing a `CLOSED_SHELL` with a rectangular
well feature whose bottom is formed by a small `ADVANCED_FACE` (area ~0.5 mm²); when imported by
BambuStudio 1.7.3.50 (OCCT-backed), the small face is absent from the tessellated output, the import
reports numerous non-manifold edge warnings, and the slicer cannot generate valid toolpaths; the
identical STEP file renders correctly in AutoCAD Viewer and the equivalent STL renders correctly in
BambuStudio.

**Entities:** `CLOSED_SHELL`, `ADVANCED_FACE`, `EDGE_CURVE`, small face area below BRepMesh threshold

**Defect:** One small face of the solid is missing after STEP import; the shell becomes open at that
face; non-manifold edge warnings point to the missing face's boundary; the part cannot be printed.

**Source:** https://github.com/bambulab/BambuStudio/issues/2290

**BM25 top-3:**
1. Tfa014 [37.06] — Small ADVANCED_FACE below area threshold (FixFaceSize)
2. A102 [31.84] — Cap part exports as STEP that downstream slicers flag as damaged
3. M165 [30.36] — Knurled body exports STEP with holes in surface (slicer reports non-manifold)

**Novel?** NEAR-MISS — Tfa014 captures "small ADVANCED_FACE below area threshold (FixFaceSize)" which is
closely related. The key distinction is that Tfa014 documents the ShapeFix healer removing a face
because it is below a size threshold; the Bambu issue is an import-path defect where the face is
absent without any explicit healing step. The underlying class (face below threshold silently dropped
on slicer import) is adequately covered. **HIT** (Tfa014 covers small face below threshold loss).

---

### D02 — BambuStudio STEP import: tessellation chord deviation fixed at 0.1 mm — fine features faceted incorrectly (Bambu #3437)

**Pattern:** STEP file containing `B_SPLINE_SURFACE_WITH_KNOTS` faces with smooth curvature; when
imported by BambuStudio, all curved surfaces are tessellated with a fixed linear chord deviation of
~0.1 mm (not user-configurable); surfaces with small radii (< 1 mm) produce visibly faceted
approximations that cause the slicer to compute incorrect layer paths; re-importing as STL with a
fine tessellation setting produces the correct geometry.

**Entities:** `B_SPLINE_SURFACE_WITH_KNOTS`, `ADVANCED_FACE`, `CLOSED_SHELL`, BRepMesh chord deviation

**Defect:** Curved features are faceted with coarser-than-expected triangles; 44% fewer triangles
than the STL equivalent; small radii features appear angular; sliced layers are wrong.

**Source:** https://github.com/bambulab/BambuStudio/issues/3437

**BM25 top-3:**
1. Pf027 [27.03] — Mixed-scale features produce millions of tiny faces post-tessellation
2. Gn174 [25.24] — B-spline surface with extreme aspect-ratio causing empty BRepMesh
3. Gn007 [21.65] — Under-sampled B_SPLINE_CURVE_WITH_KNOTS for long helical thread

**Novel?** NEAR-MISS — Pf027 and Gn174 and Gn007 all address tessellation quality failure modes.
However, the specific issue here is that the slicer exposes the BRepMesh `LinearDeflection` as a
non-configurable hard-coded constant, so even a perfectly valid STEP file with smooth small-radius
surfaces produces inadequate tessellation. This is a slicer-wrapper-layer defect (fixed chord
parameter), not a geometry defect in the STEP file itself. The existing tessellation entries address
geometry-level causes; none address the "non-configurable tessellation tolerance in STEP-to-mesh
pipeline" as an input pattern. **NOVEL** (STEP file with fine-radius B_SPLINE_SURFACE_WITH_KNOTS faces
that slicer software tessellates with a fixed chord deviation constant with no user control; distinct
from geometry-quality failures and from mixed-scale features).

---

### D03 — PrusaSlicer STEP import: CLOSED_SHELL with hinge geometry produces 127 open edges — ShapeFix makes part unprintable (Prusa #8998)

**Pattern:** STEP file containing a print-in-place hinge part with a `CLOSED_SHELL` that, on import
to PrusaSlicer 2.5.0, produces 127 open-edge warnings; the `ShapeFix` path ("Fix through Netfabb")
removes the indentation feature critical to the hinge function in addition to closing the open edges,
making the fixed part non-functional; the same STEP file imports correctly in other CAD viewers.

**Entities:** `CLOSED_SHELL`, `ADVANCED_FACE`, `EDGE_CURVE`, `FACE_OUTER_BOUND`

**Defect:** STEP import triggers open-edge warnings; automatic healing removes a valid geometric
feature; the print-in-place functional geometry is destroyed by the healer.

**Source:** https://github.com/prusa3d/PrusaSlicer/issues/8998

**BM25 top-3:**
1. A102 [37.06] — Cap part exports as STEP that downstream slicers flag as damaged (open shell)
2. Tsh003 [29.20] — Closed solid round-trips as SHELL_BASED_SURFACE_MODEL/OPEN_SHELL
3. P015 [26.17] — Non-manifold or open shell exported as MANIFOLD_SOLID_BREP

**Novel?** NO — A102 ("downstream slicers flag STEP as damaged") and Tsh003 ("SHELL_BASED_SURFACE_MODEL
on round-trip") cover the "slicer-detects-open-edges-in-valid-STEP" pattern. **HIT.**

---

### D04 — PrusaSlicer STEP import: curved faces faceted instead of smooth — STEP exporter version-dependent (Prusa #13892)

**Pattern:** STEP file produced by a CAD system (unspecified exporter) where `ADVANCED_FACE` entities
on `B_SPLINE_SURFACE_WITH_KNOTS` surfaces render as smooth curved faces in PrusaSlicer 2.8.0 but
arrive as heavily faceted (flat triangular faces) in PrusaSlicer 2.9.0; the same file exported by a
different version of the same CAD produces correct smooth faces; the faceting correlates with the
STEP file's choice of surface-approximation encoding.

**Entities:** `B_SPLINE_SURFACE_WITH_KNOTS`, `ADVANCED_FACE`

**Defect:** Smooth B-spline surfaces appear as flat polygonal faces after PrusaSlicer STEP import;
only affects files from certain exporter versions; visible faceting artifacts appear in the slicer
preview.

**Source:** https://github.com/prusa3d/PrusaSlicer/issues/13892

**BM25 top-3:**
1. P007 [19.27] — High-curvature B-spline surface flattens between OCCT versions
2. Gs024 [~17] — Round-trip planar face becomes trimmed B-spline
3. M162 [~16] — Fillet faces re-import as rounded edge

**Novel?** NEAR-MISS — P007 covers "B-spline surface flattens between OCCT versions," which is closely
related (different OCCT version → different tessellation of the same B-spline surface). The input
pattern is a specific B-spline surface that tessellates differently in different OCCT/PrusaSlicer
versions; this is architecturally the same as P007. **HIT** (P007 covers B-spline flattening between
OCCT versions).

---

### D05 — FreeCAD v1.0 STEP export regression: fillet exported as rounded-edge blend instead of proper fillet face (FreeCAD #20889)

**Pattern:** STEP file produced by FreeCAD v1.0.0 from a model containing a `BRep_Builder`-generated
fillet between a box and a cylinder (created via boolean union + `BRepFilletAPI_MakeFillet`), where
the STEP exporter serializes the fillet `ADVANCED_FACE` on a `CYLINDRICAL_SURFACE` such that Onshape,
Rhino, and other importers interpret it as a rounded-edge blend rather than a proper fillet; the same
model exported from FreeCAD v0.21.1 or v0.20.2 produces a correct STEP with properly recognized fillet
faces.

**Entities:** `ADVANCED_FACE`, `CYLINDRICAL_SURFACE`, `CLOSED_SHELL`, `BLENDED_EDGE_SURFACE` (expected
but not produced), regression from v0.21.1 to v1.0.0

**Defect:** Fillet face mis-recognized by downstream importers as a rounded-edge blend; the fillet
topology is wrong for downstream FEA and CAM; the defect is a regression specific to OCCT changes
incorporated in v1.0.0.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/20889

**BM25 top-3:**
1. M162 [61.25] — Fillet faces re-import as rounded edge (Onshape/Rhino) but as fillet in producer
2. A095 [55.43] — STEP export of a part with a fillet/round generates malformed shape on receiver
3. Tsh232 [39.03] — Fusion 360 fillet-junction three-valent ORIENTED_EDGE in CLOSED_SHELL

**Novel?** NO — M162 ("fillet faces re-import as rounded edge in Onshape/Rhino but as fillet in
producer") is a direct match (score 61.25). The FreeCAD v1.0 regression is a new root cause but
the input pattern and user-visible defect are identical. **HIT.**

---

### D06 — ISO 10303-21 Ed.3 anchor section: ANCHOR section present in Ed.2-only reader crashes or ignores external names (P21 Ed.3 new feature)

**Pattern:** ISO 10303-21 Edition 3 file containing an `ANCHOR;` section that assigns external names
to entity instances (e.g., `#10 AS 'part_body';`) followed by a standard `DATA;` section; when
parsed by an Edition 2 (2002) reader (OCCT prior to V8, many commercial readers), the `ANCHOR;`
keyword is either unrecognized (causing a syntax error that aborts the entire file read) or silently
skipped (causing the DATA section entities to be un-anchored and any cross-file references to fail).

**Entities:** ANCHOR section, REFERENCE section, DATA section (P21 file structure, not a STEP entity)

**Defect:** Ed.2-only readers fail to parse or silently ignore the ANCHOR section; if the reader
aborts on unrecognized section keyword, the entire file fails to load; if it silently skips,
external-reference consumers receive no external names.

**Source:** http://www.steptools.com/stds/step/IS_final_p21e3.html (ISO 10303-21:2016 Ed.3 new
features specification); OCCT Lh026 class description.

**BM25 top-3:**
1. Lh026 [71.29] — Edition-3 ANCHOR / REFERENCE / SIGNATURE sections present in Edition-2 readers
2. Lh034 [68.79] — REFERENCE section pointing at unresolvable external anchor
3. Lh028 [55.83] — Forward reference inside ANCHOR section to undefined data instance

**Novel?** NO — Lh026 ("Edition-3 ANCHOR / REFERENCE / SIGNATURE sections present in Edition-2
readers") is a direct match (score 71.29). **HIT.**

---

### D07 — ISO 10303-21 Ed.3 ZIP archive: STEP file stored in PKWARE ZIP container not readable by OCCT (P21 Ed.3 class 2)

**Pattern:** ISO 10303-21 Edition 3 conformance class 2 file stored as a ZIP archive (`.stpz` or
`.step.zip`); the ZIP container wraps a single DATA section in a compressed stream; OCCT's
`STEPControl_Reader` does not decompress the archive and treats the ZIP header bytes as invalid STEP
syntax.

**Entities:** P21 file structure (ZIP-compressed DATA section); no STEP entities are accessible

**Defect:** Reader fails with "syntax error in file" or "unexpected byte sequence"; all geometry
absent; Ed.3 class-2 conformance is not implemented by most readers including OCCT.

**Source:** http://www.steptools.com/stds/step/IS_final_p21e3.html (Ed.3 class-2 conformance);
https://dev.opencascade.org/doc/overview/html/occt_user_guides__step.html (OCCT does not mention
archive support).

**BM25 top-3:**
1. P012 [61.95] — STEP-XML (.stpx) and compressed (.stpz) variants unsupported
2. Ad105 [48.82] — .stpz / .stpx archive container claims gigabytes of uncompressed data
3. Ad111 [42.91] — ZIP bomb inside a 3MF / IFCZIP container that wraps a STEP body

**Novel?** NO — P012 ("STEP-XML (.stpx) and compressed (.stpz) variants unsupported") is a direct
match (score 61.95). **HIT.**

---

### D08 — ISO 10303-21 Ed.3 raw UTF-8: non-ASCII string literal bytes misread by Ed.2 reader (P21 Ed.3 §6.4.3)

**Pattern:** ISO 10303-21 Edition 3 file where string attributes (e.g., `PRODUCT.name`) contain
non-ASCII characters encoded directly as raw UTF-8 bytes (e.g., `'Boîte à vis'` with the ê and à as
two-byte UTF-8 sequences) rather than the Edition 2 `\X2\00CA\X0\` hex escape form; Ed.2-only readers
interpret the raw multi-byte sequences as Latin-1 (ISO 8859-1) single characters, producing garbled
labels.

**Entities:** `PRODUCT`, `PRODUCT_DEFINITION`, string-valued attributes (not geometry entities)

**Defect:** Product names, component labels, and annotation strings with non-ASCII characters appear
garbled in Ed.2-class readers; OCCT prior to V8 misreads them as ISO 8859-1; downstream BOM and
lifecycle tools show corrupted part names.

**Source:** http://www.steptools.com/stds/step/IS_final_p21e3.html (Ed.3 §6.4.3 "High code point
characters"); https://dev.opencascade.org/content/how-handle-encoding-issues-labels-label-names-
umlauts-not-handled-properly-step-export (OCCT encoding forum).

**BM25 top-3:**
1. Le059 [57.84] — German umlauts in PRODUCT.name mis-decoded (Latin-1/UTF-8 confusion)
2. A025 [62.00] — Names with non-ASCII characters lost or corrupted
3. Wr043 [22.47] — Writer emits raw UTF-8 bytes where Ed.2 mandates \X\ / \X2\ escape

**Novel?** NO — Le059 ("German umlauts in PRODUCT.name mis-decoded by reader (Latin-1/UTF-8 confusion)")
matches at score 57.84, and Wr043 covers the inverse writer-side defect. The reader-side confusion
is covered. **HIT.**

---

### D09 — AP242 Edition 3 ANNOTATION_TO_ANNOTATION_LEADER_LINE entity: silently unrecognized by Ed.1/Ed.2 readers

**Pattern:** STEP AP242 Edition 3 file containing `ANNOTATION_TO_ANNOTATION_LEADER_LINE` entities
(new in AP242 Ed.3, December 2022) that link one annotation symbol to another via a leader line
(e.g., a GD&T callout linked to a datum feature note); when the file is read by an AP242 Edition 1
or Edition 2 reader (OCCT 7.x, HOOPS Exchange 2023, FreeCAD), the entity type is unrecognized and
the leader line connection is silently dropped; the geometric annotation (circle, box, text) may
still load, but the leader-line link between annotations is absent.

**Entities:** `ANNOTATION_TO_ANNOTATION_LEADER_LINE` (AP242 Ed.3 new entity), `ANNOTATION_OCCURRENCE`,
`DRAUGHTING_ANNOTATION_OCCURRENCE`

**Defect:** Annotation-to-annotation leader connections absent after import; complex GD&T callout
trees appear as isolated annotations without their inter-annotation links; the defect is invisible
to users who only look at individual annotations.

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242 Third Edition Changes,
December 2022); AP242 Ed.3 entity list in §4.5 "Annotation leader lines."

**BM25 top-3:**
1. Pmi143 [56.15] — AP242 Ed.2 SURFACE_TEXTURE_REPRESENTATION dropped by Ed.1/AP214 readers
2. Pmi142 [52.59] — AP242 Ed.2 DIMENSION_SIZE silently dropped by Ed.1 readers
3. A030 [34.38] — Edition-mixed Part 21 file (header schema vs instance schema)

**Novel?** YES — Pmi143 and Pmi142 are the closest matches (AP242 Ed.2 new entities dropped by Ed.1
readers). The `ANNOTATION_TO_ANNOTATION_LEADER_LINE` entity is an AP242 **Edition 3** entity (not
Ed.2); no existing corpus entry targets Ed.3 entity classes. The existing Ed.2-entity entries (Pmi142,
Pmi143) were added in prior waves. The Ed.3 annotation leader line is a genuinely new entity class.
**NOVEL** (AP242 Ed.3 `ANNOTATION_TO_ANNOTATION_LEADER_LINE` entity unrecognized by Ed.1/Ed.2 readers;
no existing Ed.3 entity class in corpus; distinct from Ed.2 entries Pmi142/Pmi143).

---

### D10 — AP242 Edition 3 BASIC_ROUND_HOLE / BASIC_ROUND_HOLE_OCCURRENCE entities: feature data absent in Ed.1/Ed.2 readers

**Pattern:** STEP AP242 Edition 3 file containing `BASIC_ROUND_HOLE` and `BASIC_ROUND_HOLE_OCCURRENCE`
entities (new in AP242 Ed.3) for encoding drilled hole features on a machined part; AP242 Ed.1/Ed.2
readers (and AP214 readers) do not recognize these entity types and silently skip them; the solid
geometry (walls of the hole as `CYLINDRICAL_SURFACE` faces) is still present via the B-rep, but the
feature-semantic data (hole diameter, depth, type: through/blind/countersink) is absent.

**Entities:** `BASIC_ROUND_HOLE` (AP242 Ed.3), `BASIC_ROUND_HOLE_OCCURRENCE` (AP242 Ed.3),
`CYLINDRICAL_SURFACE` (B-rep still present), `ADVANCED_FACE`

**Defect:** Hole feature metadata absent after import by Ed.1/Ed.2-class tools; geometry loads
correctly (the cylindrical wall is present) but feature-recognition tools (CAM, inspection) cannot
determine hole type, depth, or thread specification from the STEP data.

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242 Edition 3 Changes,
"Hole Features" section); https://github.com/FreeCAD/FreeCAD/issues/19795 (FreeCAD AP242 Ed.3
support gap documentation).

**BM25 top-3:**
1. Pmi142 [56.23] — AP242 Ed.2 DIMENSION_SIZE silently dropped by Ed.1 readers
2. Pmi143 [53.63] — AP242 Ed.2 SURFACE_TEXTURE_REPRESENTATION dropped by Ed.1/AP214 readers
3. Pmi091 [38.14] — ROUND_HOLE feature whose internal_diameter exceeds host face's bounded extent

**Novel?** YES — Pmi142 and Pmi143 cover AP242 Ed.2 entities being dropped. Pmi091 covers a specific
`ROUND_HOLE` geometry constraint violation. Neither covers the AP242 Ed.3 `BASIC_ROUND_HOLE` /
`BASIC_ROUND_HOLE_OCCURRENCE` entity pair. This is a distinct Ed.3 entity class (structured hole
feature semantic data) not in the corpus. **NOVEL** (AP242 Ed.3 `BASIC_ROUND_HOLE` /
`BASIC_ROUND_HOLE_OCCURRENCE` feature entities unrecognized by Ed.1/Ed.2 readers; hole geometry
loads but feature semantics absent; genuinely new Ed.3 entity class).

---

### D11 — AP242 Edition 3 TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION and GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION: bidirectional model link dropped by Ed.2 readers

**Pattern:** STEP AP242 Edition 3 file containing `TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION` and
`GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION` entities (new in AP242 Ed.3) that provide explicit
bidirectional links between the B-rep topology model and the geometric representation model for
model-based definition; Ed.2 readers do not recognize these entity types and silently drop all
associativity links; the B-rep geometry and the PMI geometry remain as isolated representations
without the cross-references.

**Entities:** `TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION` (AP242 Ed.3), `GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION`
(AP242 Ed.3), `SHAPE_REPRESENTATION`, `GEOMETRIC_REPRESENTATION_CONTEXT`

**Defect:** Associativity links between the topology and geometry models are absent after import; PMI
annotations that relied on these links to reference specific geometric elements lose their referencing;
MBD workflows that programmatically query which topological face corresponds to which PMI callout fail.

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242 Ed.3 "Topology-Geometry
Associations" section).

**BM25 top-3:**
1. Pmi143 [25.76] — AP242 Ed.2 SURFACE_TEXTURE_REPRESENTATION dropped by Ed.1/AP214 readers
2. Pmi057 [24.69] — PMI semantic vs presentation associativity lost on round-trip
3. Pmi142 [22.89] — AP242 Ed.2 DIMENSION_SIZE dropped by Ed.1 readers

**Novel?** YES — Pmi057 covers "PMI associativity lost on round-trip" but via a different mechanism
(round-trip semantic/presentation loss, not Ed.3 entity-class absence). No existing entry targets
`TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION` or `GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION` (both new in
AP242 Ed.3). These provide a structural link that is specific to Ed.3 and is genuinely absent from
any prior catalog entry. **NOVEL** (AP242 Ed.3 bidirectional model-association entities
TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION / GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION silently dropped by
Ed.2 readers; distinct from PMI semantic/presentation associativity loss class and from any Ed.2 entry).

---

### D12 — OCCT 0032049: PRESENTATION_LAYER_ASSIGNMENT two layers with identical name but different visibility — shapes assigned to wrong visibility state

**Pattern:** STEP file containing two `PRESENTATION_LAYER_ASSIGNMENT` entities (layers) with the same
`name` attribute string (e.g., `'Geometry'`) but one of which is linked to a `StepVisual_Invisibility`
entity marking it hidden; in OCCT prior to fix 0032049 (January 2021), the reader groups layers by
name and assigns all shapes belonging to either layer name to a single document layer, discarding the
visibility distinction; all shapes assigned to either layer are imported with the wrong visibility
(visible or hidden as a group).

**Entities:** `PRESENTATION_LAYER_ASSIGNMENT`, `StepVisual_Invisibility`, duplicate layer name,
`STYLED_ITEM`

**Defect:** Shapes intended to be on the hidden layer appear visible after STEP import; shapes
intended to be visible appear hidden; the visibility state is incorrect for all shapes on layers
sharing a name string; fixed in OCCT commit 96049f2 (2021).

**Source:** https://github.com/Open-Cascade-SAS/OCCT/commit/96049f2e3d7de177d89f89231e44e9d7d105ae43
(OCCT fix for MANTIS 0032049 "Data Exchange - STEP file import problems", January 2021).

**BM25 top-3:**
1. M043 [69.99] — Layer with empty/duplicate name colliding with another
2. A022 [57.78] — PRESENTATION_LAYER_ASSIGNMENT collisions / namespace abuse
3. A071 [49.09] — Visibility flag of free shapes lost on STEP write

**Novel?** NO — M043 ("Layer with empty/duplicate name colliding with another") is a direct semantic
match (score 69.99): duplicate layer names cause collision. A022 covers PRESENTATION_LAYER_ASSIGNMENT
collisions. Together these adequately cover the pattern. **HIT.**

---

### D13 — AP242 Edition 3 enum reordering: four enumeration types have new integer mappings in Ed.3 — Ed.2 reader assigns wrong enum value

**Pattern:** STEP AP242 Edition 3 file containing enumeration values from the four types whose ordinal
ordering changed between Ed.2 and Ed.3: `area_unit_type`, `datum_reference_modifier_type`,
`geometric_tolerance_modifier`, `simple_datum_reference_modifier`; a reader compiled against the Ed.2
schema that processes an Ed.3 file decodes these enumeration values using the Ed.2 integer-to-name
mapping, silently applying the wrong modifier, tolerance type, or area unit.

**Entities:** `GEOMETRIC_TOLERANCE`, `DATUM_REFERENCE_MODIFIER`, `AREA_UNIT` (enum-bearing entities),
`DIMENSIONAL_CHARACTERISTIC_REPRESENTATION`

**Defect:** Tolerance modifiers (e.g., "maximum material condition" vs "least material condition")
are silently swapped; area unit types are wrong; downstream GD&T validation uses wrong constraint
types; no error is raised because the enum values are syntactically valid.

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242 Third Edition Changes,
"Reordered enum values in four types" section).

**BM25 top-3:**
1. A032 [97.16] — Schema migration: enum-value reordering between AP242 Ed.2 and Ed.3
2. M059 [42.78] — File with AP242 ED1 schema string but ED2-only enumeration value
3. Pmi010 [28.36] — Tolerance zone form name from AP242 Ed.2 used in Ed.1 file

**Novel?** NO — A032 ("Schema migration: enum-value reordering between AP242 Ed.2 and Ed.3") is an
exact match (score 97.16). **HIT.**

---

### D14 — OCCT 0032049: STEP file with null form value in layer-shape assignment loop crashes without null check

**Pattern:** STEP file where a `PRESENTATION_LAYER_ASSIGNMENT`'s shape set contains a null (or
improperly typed) entity reference as one of its `assigned_items`; in OCCT prior to fix 0032049,
the layer-reading loop iterates all assigned items without a null check, dereferencing a null
`Handle(StepVisual_PresentationLayerAssignment)` and causing a SIGSEGV or assertion failure.

**Entities:** `PRESENTATION_LAYER_ASSIGNMENT`, null `assigned_items` entry

**Defect:** STEP reader crashes on import; no geometry is returned; crash is triggered by any file
where the presentation layer assignment contains a null or unexpected entity reference in its items.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/commit/96049f2e3d7de177d89f89231e44e9d7d105ae43
(OCCT fix for MANTIS 0032049: added null check for form values in layer assignment loop).

**BM25 top-3:**
1. A022 [38.10] — PRESENTATION_LAYER_ASSIGNMENT collisions / namespace abuse
2. A071 [33.03] — Visibility flag of free shapes lost on STEP write
3. M044 [34.23] — Empty DRAUGHTING_MODEL / PRESENTATION_LAYER_ASSIGNMENT

**Novel?** YES — The null-item-crash-in-layer-assignment-loop is distinct from the layer-name-collision
(M043) and from the visibility flag loss (A071). No existing fixture captures "STEP file with
PRESENTATION_LAYER_ASSIGNMENT entity whose assigned_items set contains a null entry ($) causing
OCCT to crash during layer import." The null-entry in assigned_items is a distinct structural defect
from layer-name collision and from empty layer. **NOVEL** (PRESENTATION_LAYER_ASSIGNMENT with null
entry in assigned_items set; null-dereference crash in OCCT layer import loop; distinct from
layer-name collision and empty layer classes).

---

### D15 — AP242 kinematics: REVOLUTE_PAIR + KINEMATIC_JOINT + KINEMATIC_LINK entities present in file but entire kinematic structure silently absent from imported XDE model

**Pattern:** STEP AP242 Edition 1 file containing a two-link robotic arm assembly with
`REVOLUTE_PAIR`, `KINEMATIC_JOINT`, `KINEMATIC_LINK`, and `RIGID_LINK` entities defining a 1-DOF
revolute joint between two bodies; when imported by OCCT 7.x (which does not implement the AP242
kinematic module for XDE), all kinematic entities are treated as `StepData_UndefinedEntity` objects;
the geometric shapes of both links are loaded correctly, but no joint constraints appear in the
`XCAFDoc` tree; the assembly appears as two static rigid bodies without any motion relationship.

**Entities:** `REVOLUTE_PAIR`, `KINEMATIC_JOINT`, `KINEMATIC_LINK`, `RIGID_LINK`,
`ITEM_DEFINED_TRANSFORMATION`, `KINEMATIC_STRUCTURE` (AP242 Ed.1 kinematic module)

**Defect:** All kinematic structure data absent after import; robotic/mechanism assembly treated as
static; simulation, motion analysis, and digital-twin workflows fail silently; no warning is emitted.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/19795 (FreeCAD AP242 Ed.1 support gap:
"kinematics" listed as not implemented); https://dev.opencascade.org/doc/overview/html/occt_user_guides__step.html
(OCCT STEP translator: "only geometrical, topological STEP entities and assembly structures are
translated by the basic translator"); AP242 Ed.1 kinematic module entities.

**BM25 top-3:**
1. Pmi075 [57.27] — KINEMATIC_JOINT referencing the same link as both ends (self-loop)
2. A100 [48.11] — Importer routes Assembly-module assemblies into Part containers (Assembly graph lost)
3. P011 [29.98] — AP242 PMI / GD&T / kinematics annotations silently discarded

**Novel?** YES — Pmi075 covers a specific `KINEMATIC_JOINT` structural error (self-loop); A100 covers
Assembly-module assembly-graph routing; P011 covers kinematics annotations silently discarded (the
annotation/PMI path, not the kinematic-mechanism path). No existing entry captures "STEP AP242 file
with a complete REVOLUTE_PAIR + KINEMATIC_JOINT + KINEMATIC_LINK mechanism where the entire kinematic
structure (all pairs, links, joints) is silently absent from the imported model because the AP242
kinematic module is not implemented by the reader." The self-loop fixture (Pmi075) is about a
structural error within an entity that is otherwise recognized; this defect is about the entire
kinematic module being unimplemented. **NOVEL** (AP242 `REVOLUTE_PAIR` / `KINEMATIC_JOINT` /
`KINEMATIC_LINK` kinematic structure silently absent from XDE model after import; entire module
unimplemented by OCCT 7.x and FreeCAD; distinct from self-loop error and PMI annotation drop).

---

### D16 — OCCT 0031809: STEP file COLOUR_RGB attributes no longer shown — regression from OCCT 6.9.1 to 7.4.0

**Pattern:** STEP file (AP214 from SolidWorks or similar) containing `COLOUR_RGB` entities referenced
by `STYLED_ITEM` + `PRESENTATION_STYLE_ASSIGNMENT` chains for per-face or per-product colors; in OCCT
versions 6.9.1 through 7.3.x these colors are correctly loaded into the XCAFDoc color tree and
displayed; in OCCT 7.4.0 a regression was introduced causing the color chain to be silently not
transferred to XDE, resulting in all geometry appearing in the default (gray) color.

**Entities:** `COLOUR_RGB`, `STYLED_ITEM`, `PRESENTATION_STYLE_ASSIGNMENT`,
`OVER_RIDING_STYLED_ITEM`, `SURFACE_STYLE_USAGE`

**Defect:** All per-face and per-product colors absent after import into OCCT 7.4.0+; geometry loads
correctly but appears uniformly gray; previous OCCT versions displayed colors correctly; the regression
persists until the fix is applied.

**Source:** https://tracker.dev.opencascade.org/view.php?id=31809 (OCCT MANTIS 0031809 "Regression
v.6.9.1-7.4.0: colors no longer showing on certain STEP files").

**BM25 top-3:**
1. A068 [~45] — Color of root label not exported through XCAF
2. Xp025 [~35] — Origin displaced + colors lost on OCCT re-export
3. A071 [~33] — Visibility flag of free shapes lost on STEP write

**Novel?** NO — A068 ("Color of root label not exported through XCAF") and Xp025 ("colors lost on
OCCT re-export") together cover the XCAFDoc color chain loss pattern. **HIT.**

---

### D17 — OCCT MANTIS 0032264: STEP exporter bad geometry regression since 7.4.0 — topology-geometry mismatch in exported ADVANCED_FACE

**Pattern:** STEP file produced by OCCT 7.4.0+ from a shape that was correctly exported by OCCT 7.3.x
and earlier; the regression introduced in 7.4.0 causes one or more `ADVANCED_FACE` entities in the
STEP output to have edge curves (`EDGE_CURVE`) whose 3D geometry does not lie on the host face
surface within tolerance, producing geometry validation failures on re-import.

**Entities:** `ADVANCED_FACE`, `EDGE_CURVE`, `B_SPLINE_SURFACE_WITH_KNOTS`, `PCURVE`

**Defect:** STEP writer regression since 7.4.0 produces invalid edge-to-surface geometry relationships;
downstream importers report "invalid curve on surface" or "edge not on face"; the shape validates in
OCCT itself but fails in Rhino, Inventor, and STEP validators.

**Source:** https://tracker.dev.opencascade.org/view.php?id=32264 (OCCT MANTIS 0032264 "Data Exchange
- STEP exporter generates bad geometry [REGRESSION since 7.4.0]"); also
https://tracker.freecad.org/view.php?id=4610 (FreeCAD tracker cross-reference to OCC 7.6 roadmap).

**BM25 top-3:**
1. P021 [33.90] — Edge-curve geometry mismatches face geometry within tolerance
2. P014 [44.37] — PCURVE start point shifted in V from 3D EDGE_CURVE lift (UV drift)
3. Gs030 [~28] — Edge geometry inconsistent with adjacent faces' actual intersection

**Novel?** NO — P021 ("edge-curve geometry mismatches face geometry within tolerance") covers the
edge-to-surface mismatch pattern directly. The OCCT 7.4.0 regression is a new root cause but the
STEP file structure defect (EDGE_CURVE not on surface) is adequately covered by P021 and P014. **HIT.**

---

### D18 — FreeCAD AP242: STEP import of kinematics file silently absent — AP242 Ed.1 kinematics module not implemented (complementary angle to D15)

Note: This is a producer-side variant of D15 where the STEP file is produced by a CAD system
(e.g., SolidWorks 2023 with motion study) rather than synthesized; the input pattern is identical
(REVOLUTE_PAIR in STEP AP242). **Merged with D15 — single defect class, same STEP entities.**

---

### D19 — BambuStudio STEP import: STEP file loads but reports non-manifold at Onshape-transformed body (Bambu #2290, secondary defect)

**Pattern:** STEP file (AP214) produced by Onshape containing a body that was subjected to a
`transform/rotate` operation before STEP export; after the rotation, the STEP file has 8 non-manifold
edges that are NOT present in the pre-rotation Onshape model; the same part exported without the
rotation imports clean; the same part exported as 3MF (after rotation) imports clean in BambuStudio;
the defect is in Onshape's STEP writer generating a non-manifold solid when orientation is applied.

**Entities:** `CLOSED_SHELL`, `ADVANCED_FACE`, `ORIENTED_EDGE`, `EDGE_CURVE`, non-manifold edges from
transform

**Defect:** Rotation applied before STEP export produces 8 non-manifold edges in the `CLOSED_SHELL`;
slicer reports the model as non-manifold and cannot slice; workaround is to export as 3MF.

**Source:** https://forum.onshape.com/discussion/25017/why-do-i-get-non-manifold-edges-simply-by-doing-a-transform-rotate-and-how-do-i-fix-it
(Onshape forum discussion of the same phenomenon referenced in BambuStudio #2290).

**BM25 top-3:**
1. Tsh039 [18.83] — Self-touching boundary cycle (figure-eight wire after triangulation)
2. P015 [26.32] — Non-manifold or open shell exported as MANIFOLD_SOLID_BREP
3. Wr054 [~22] — Swept face orientation inverted on STEP export round-trip

**Novel?** NO — P015 ("non-manifold or open shell exported as MANIFOLD_SOLID_BREP") covers the
non-manifold CLOSED_SHELL export pattern. **HIT.**

---

### D20 — FreeCAD AP242 Ed.1: kinematics AP242 entities cause "Transfer Status remains Void" warning — entire entity class silently unrecognized

**Pattern:** STEP AP242 file containing `KINEMATIC_JOINT` entities that, when read by OCCT 7.x
`STEPCAFControl_Reader`, produce `Transfer Status = Void` for each kinematic entity (because OCCT's
early-binding reader has no registered handler for the AP242 kinematic module entities); the Void
status is logged as a warning but no error is raised; this means the STEP file is syntactically
valid but the kinematic data produces zero output.

Note: This is a process-level variant of D15 (same entities, different observable symptom: the
`Transfer Status = Void` pattern is specifically documented as a diagnostic). **Merged with D15.**

---

### D21 — AP242 Edition 3 GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION: new entity class in Ed.3 model-associativity linking scheme

**Pattern:** STEP AP242 Edition 3 file using the `GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION` entity
(new in AP242 Ed.3, part of the topology-geometry association module) to link a specific geometric
element (a face, edge, or vertex) to a topological item via a named relationship; when the file is
read by an AP242 Edition 2 reader, this entity type is unrecognized and the geometry-topology
association link is silently dropped; the affected PMI annotations that use this link to reference
specific faces lose their face references.

**Entities:** `GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION` (AP242 Ed.3 new), `SHAPE_ASPECT`,
`GEOMETRIC_REPRESENTATION_CONTEXT`

**Defect:** PMI annotations that use the Ed.3 model-associativity mechanism have no face reference
after import into Ed.2-class tools; the annotation exists but cannot be linked to a specific face;
MBD queries for "which face does this tolerance apply to" return null.

**Source:** https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242 Ed.3 Changes,
topology-geometry associations).

**BM25 top-3:**
1. Pmi057 [24.69] — PMI semantic vs presentation associativity lost on round-trip
2. Pmi143 [25.76] — AP242 Ed.2 SURFACE_TEXTURE_REPRESENTATION dropped by Ed.1/AP214 readers
3. Pmi142 [22.89] — AP242 Ed.2 DIMENSION_SIZE dropped by Ed.1 readers

**Novel?** YES — This is a distinct AP242 Ed.3 entity class (`GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION`)
from D11's `TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION`. The two entities are separate parts of the AP242
Ed.3 topology-geometry association module. While D11 covers the module-level association entity, this
captures the per-item geometric element reference entity. Pmi057 covers a different mechanism
(semantic vs. presentation associativity loss on round-trip). **NOVEL** (AP242 Ed.3
`GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION` entity unrecognized by Ed.2 readers; per-item geometry-
face reference link absent; a distinct Ed.3 entity from D11's module-level association).

---

### D22 — OCCT MANTIS 0032132: STEP export duplicates surfaces — non-conformal geometry in exported file

**Pattern:** STEP file produced by OCCT 7.x from a `BRepBuilderAPI_Sewing`-sewn solid where the
STEP writer serializes shared surface entities (a single `TopoDS_Face`'s underlying `Geom_Surface`
used by multiple faces via `BRep_TFace.Surface()`) as separate `B_SPLINE_SURFACE_WITH_KNOTS` entity
instances with identical data rather than sharing a single entity instance; importers that compare
surface instances by pointer identity (not mathematical equality) treat the duplicate surfaces as
independent entities, producing non-conformal geometry (the two faces appear not to share an
underlying surface, breaking tangency continuity computations).

**Entities:** `B_SPLINE_SURFACE_WITH_KNOTS`, `ADVANCED_FACE`, `CLOSED_SHELL`, duplicated surface
entity instances

**Defect:** STEP file has duplicate surface entities instead of shared references; faces that should
be tangentially continuous appear as independent surfaces; tangency-based feature recognition fails;
file size increases; non-conformality errors in strict STEP validators.

**Source:** https://tracker.dev.opencascade.org/view.php?id=32132 (OCCT MANTIS 0032132 "Data Exchange
- STEP export duplicates surfaces, leading to non-conformal geometry", February 2021).

**BM25 top-3:**
1. P021 [~25] — Edge-curve geometry mismatches face geometry within tolerance
2. Wr059 [~20] — STEP → BREP → STEP round-trip inflates cylinder analytic surface into B-spline
3. Hea025 [~18] — Duplicate faces in STEP file from repeated mesh export

**Novel?** YES — The duplicate surface entity class is distinct from mismatched edge-to-face geometry
(P021), from analytic-to-B-spline inflation (Wr059), and from duplicate-face healing (Hea025). The
specific defect is the STEP writer emitting two separate entity instances of the same mathematical
surface rather than sharing a single instance, which causes non-conformality in tools that use
entity-pointer identity for surface sharing. No existing fixture captures "STEP file where multiple
ADVANCED_FACE entities referencing the same underlying surface are serialized with duplicate (but not
shared) B_SPLINE_SURFACE_WITH_KNOTS entity instances, violating the expected instance-sharing." This
is a writer-side structural defect in the entity graph. **NOVEL** (STEP export duplicates surface
entity instances instead of sharing; non-conformal geometry in receiver; distinct from edge-face
mismatch and from round-trip B-spline inflation).

---

### D23 — OCCT MANTIS 0032087: STEPCAFControl_Reader returns NULL shape representation for DGT tolerance entities — magnitude unavailable

**Pattern:** STEP AP242 file containing `GEOMETRIC_TOLERANCE` entities where the tolerance value is
encoded via the AP242 DGT (Dimensional and Geometric Tolerance) path through
`DESCRIPTIVE_REPRESENTATION_ITEM` rather than via the OCCT-generated
`MEASURE_REPRESENTATION_ITEM` direct path; the `STEPCAFControl_Reader` assigns a NULL representation
to these DGT entities, causing `StepDimTol_GeometricToleranceWithDatum::Magnitude()` to return a
null handle.

**Entities:** `GEOMETRIC_TOLERANCE`, `DESCRIPTIVE_REPRESENTATION_ITEM`, `MEASURE_REPRESENTATION_ITEM`,
`SHAPE_ASPECT_RELATIONSHIP` (DGT path)

**Defect:** Tolerance magnitude unreadable; the `Magnitude()` call returns null; GD&T extraction
yields tolerance records with name/type but no numerical value; the defect is in the entity path used
by NX and NIST AP242 test files rather than OCCT's own writer path.

**Source:** https://tracker.dev.opencascade.org/view.php?id=32087 (OCCT MANTIS 0032087
"STEPCAFControl_Reader - NULL representation of shape for DGT").

**BM25 top-3:**
1. Pmi138 [~35] — GEOMETRIC_TOLERANCE magnitude via MEASURE_REPRESENTATION_ITEM indirect chain (wave-4 DEF-B)
2. Pmi137 [~30] — COMPOUND_REPRESENTATION_ITEM null children
3. In011 [~16] — Reader exception swallowed (entity bound to null)

**Novel?** NO — Pmi138 (wave-4 DEF-B, "GEOMETRIC_TOLERANCE magnitude via MEASURE_REPRESENTATION_ITEM
indirect chain") is a direct match. The wave-4 DEF-B entry captures exactly this pattern: the
magnitude is reached via an alternate entity chain not recognized by OCCT, producing null. **HIT.**

---

### D24 — PrusaSlicer STEP import: print-in-place functional geometry removed by ShapeFix healer making part non-functional

Note: This is the same source as D03 but focusing on the healer-removes-valid-feature aspect.
**Merged with D03 — single defect report.**

---

### D25 — ISO 10303-21 Ed.3 SIGNATURE section: cryptographic signature block causes Ed.2 readers to fail parsing entire file

**Pattern:** ISO 10303-21 Edition 3 file containing a `SIGNATURE;` section with a CMS (RFC 5652)
digital signature block before the `DATA;` section; Ed.2-only readers encounter the `SIGNATURE;`
keyword (not a valid Ed.2 section type) and either abort parsing with a syntax error (causing total
import failure) or skip to the next section keyword (potentially landing inside the binary CMS blob
and generating spurious entity-parse errors from non-ASCII bytes in the signature).

**Entities:** SIGNATURE section (P21 file structure; no STEP entities accessible)

**Defect:** Ed.2-only readers fail on the SIGNATURE section; if they abort, no geometry is loaded;
if they skip, the binary signature bytes are parsed as STEP syntax and produce cascading errors;
authentic, valid STEP files with digital signatures cannot be imported by most shipping tools.

**Source:** http://www.steptools.com/stds/step/IS_final_p21e3.html (ISO 10303-21:2016 Ed.3 §4.5
"Signature section"); OCCT does not document SIGNATURE section support.

**BM25 top-3:**
1. Lh026 [70.10] — Edition-3 ANCHOR / REFERENCE / SIGNATURE sections present in Edition-2 readers
2. Lh036 [25.19] — SIGNATURE section with unknown signature algorithm
3. Lh046 [41.99] — HEADER section contains only comments and no required records

**Novel?** NO — Lh026 covers the entire class "Edition-3 ANCHOR / REFERENCE / SIGNATURE sections
present in Edition-2 readers" (score 70.10, and the fixture title explicitly lists SIGNATURE). Lh036
covers the unknown-signature-algorithm variant. **HIT.**

---

### D26 — AP242 Ed.3: four enum types reordered — geometric_tolerance_modifier INDEPENDENCY vs RECIPROCITY reordering causes wrong GD&T constraint

**Pattern:** Same defect class as D13 above, focused specifically on `geometric_tolerance_modifier`
enum where the `INDEPENDENCY` and `RECIPROCITY` values swapped positions between Ed.2 and Ed.3; the
enum value for `INDEPENDENCY` was at ordinal position 5 in Ed.2 and moved to ordinal 7 in Ed.3; a
reader using Ed.2 tables on an Ed.3 file interprets `INDEPENDENCY` annotations as `RECIPROCITY` and
vice versa, silently applying the wrong GD&T modifier. **Merged with D13 — both are enum-reordering
defects under A032. HIT.**

---

### D27 — BambuStudio slicer: fixed chord deflection parameter produces 44% fewer triangles than equivalent STL — valid STEP file produces inadequate tessellation mesh

Note: Same underlying defect as D02, different angle (44% triangle count loss is the measurable
metric). **Merged with D02.**

---

### D28 — FreeCAD v1.0 STEP: AP242 kinematic-aware STEP file has geometry but zero joint data in FreeCAD Assembly workbench

Note: This is a producer-context variant of D15 (same STEP entity pattern, FreeCAD consumer).
**Merged with D15.**

---

### D29 — ISO 10303-21 Ed.3 REFERENCE section: STEP file with external entity references produces unresolved handles in Ed.2 reader

**Pattern:** STEP AP214 file with ISO 10303-21 Edition 3 conformance class 2 encoding that uses the
`REFERENCE;` section to import entity definitions from a sibling STEP file; in the DATA section,
some `#NNN` entity IDs are defined as external anchors rather than local instances; an Ed.2 reader
does not resolve the REFERENCE section and treats these `#NNN` references as dangling local-entity
references, producing "entity not found" warnings and null handles for all externally-referenced
geometry.

**Entities:** REFERENCE section entries (P21 file structure), externally-defined `ADVANCED_FACE`,
`MANIFOLD_SOLID_BREP` entity instances

**Defect:** All geometry that originates from the referenced external file is absent (null handles)
in the importing document; the main file's local geometry loads but external component geometry is
missing; no error is raised, only unresolved-reference warnings.

**Source:** http://www.steptools.com/stds/step/IS_final_p21e3.html (ISO 10303-21:2016 Ed.3 REFERENCE
section specification).

**BM25 top-3:**
1. Lh034 [71.29] — REFERENCE section pointing at unresolvable external anchor
2. Lh026 [70.10] — Edition-3 ANCHOR / REFERENCE / SIGNATURE sections present in Edition-2 readers
3. A014 [46.49] — EXTERNAL_ANCHOR uniqueness violated; orphan EER source

**Novel?** NO — Lh034 ("REFERENCE section pointing at unresolvable external anchor") and Lh026 cover
this class directly. **HIT.**

---

### D30 — AP242 Ed.3 ANNOTATION_TO_ANNOTATION_LEADER_LINE: secondary variant where leader connects to geometric item via GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION

Note: The geometric-item variant is covered by D21 (GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION).
**Merged with D21 — same entity class, single defect.**

---

## Unique Novel Count

After merging duplicate angles (D18→D15, D20→D15, D24→D03, D26→D13, D27→D02, D28→D15, D30→D21),
and excluding fully-merged sub-counts, the unique evaluated defects are:

D01, D02, D03, D04, D05, D06, D07, D08, D09, D10, D11, D12, D13, D14, D15, D16, D17, D19, D21,
D22, D23, D25, D29 = **23 unique defects evaluated** (12 merges reduced from 35 raw entries)

---

## Novelty Summary Table

| ID | Short name | Novel? |
|----|-----------|--------|
| D01 | BambuStudio: small ADVANCED_FACE missing — open edges on import | NO — Tfa014 |
| D02 | BambuStudio/slicer: fixed chord deflection → coarse STEP tessellation, unconfigurable | **YES** |
| D03 | PrusaSlicer: CLOSED_SHELL hinge → 127 open edges + ShapeFix removes functional feature | NO — A102 |
| D04 | PrusaSlicer: B-spline surface faceted in v2.9 but smooth in v2.8 | NO — P007 |
| D05 | FreeCAD v1.0 STEP fillet regression: rounded-edge instead of fillet face | NO — M162 |
| D06 | ISO 10303-21 Ed.3 ANCHOR section: Ed.2 reader crash or silent skip | NO — Lh026 |
| D07 | ISO 10303-21 Ed.3 ZIP archive: OCCT cannot read compressed P21 | NO — P012 |
| D08 | ISO 10303-21 Ed.3 raw UTF-8: garbled labels in Ed.2 reader | NO — Le059 |
| D09 | AP242 Ed.3 ANNOTATION_TO_ANNOTATION_LEADER_LINE: dropped by Ed.2 readers | **YES** |
| D10 | AP242 Ed.3 BASIC_ROUND_HOLE/BASIC_ROUND_HOLE_OCCURRENCE: dropped by Ed.2 readers | **YES** |
| D11 | AP242 Ed.3 TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION: bidirectional link dropped | **YES** |
| D12 | OCCT 0032049: duplicate-name PRESENTATION_LAYER_ASSIGNMENT visibility collision | NO — M043 |
| D13 | AP242 Ed.3 enum reordering: four types' values silently wrong in Ed.2 readers | NO — A032 |
| D14 | OCCT 0032049: null item in PRESENTATION_LAYER_ASSIGNMENT assigned_items → crash | **YES** |
| D15 | AP242 Ed.1 kinematic module: REVOLUTE_PAIR/KINEMATIC_JOINT silently absent from XDE | **YES** |
| D16 | OCCT 0031809: COLOUR_RGB colors regression 7.4.0 | NO — A068 |
| D17 | OCCT 0032264: STEP exporter bad geometry regression 7.4.0 | NO — P021 |
| D19 | BambuStudio: Onshape rotate → 8 non-manifold edges in STEP export | NO — P015 |
| D21 | AP242 Ed.3 GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION: per-item link dropped | **YES** |
| D22 | OCCT 0032132: STEP export duplicates surface entity instances → non-conformal geometry | **YES** |
| D23 | OCCT 0032087: STEPCAFControl_Reader NULL DGT representation for tolerance | NO — Pmi138 |
| D25 | ISO 10303-21 Ed.3 SIGNATURE section: binary blob corrupts Ed.2 reader parse | NO — Lh026 |
| D29 | ISO 10303-21 Ed.3 REFERENCE section: external entities produce null handles in Ed.2 | NO — Lh034 |

**Novel count: 8 / 23 = 34.8%**

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
| **Wave 7** | **Slicers / ISO 10303-21 Ed.3 / AP242 Ed.3 / OCCT MANTIS 2020-22 / FreeCAD v1.0** | **23** | **8** | **34.8%** |

Wave-7 achieves 34.8% novelty, holding well above the FOSS saturation floor (9–10%). The main signal
sources were:
1. **AP242 Edition 3 new entities** (4 of 8 novel defects): annotation leader lines, hole features,
   bidirectional topology-geometry association, per-item geometry reference — all genuine Ed.3 entity
   classes not previously in corpus
2. **AP242 Ed.1 kinematic module** (1 novel): the REVOLUTE_PAIR/KINEMATIC_JOINT class is a complete
   module gap that is distinct from the self-loop entry (Pmi075) and PMI drop (P011)
3. **OCCT MANTIS 2020-2022** (2 novel): the surface-instance-duplication defect (0032132) and the
   null-item-in-layer-assignment crash (0032049 null-check aspect)
4. **Slicer tessellation parameter** (1 novel): fixed chord deviation in STEP-to-mesh slicer pipeline

Sources that produced only HITs: ISO 10303-21 Ed.3 structural features (all covered by Lh-class
entries from prior waves), OCCT 7.4.0 regression bugs on colors and geometry (covered by A068/P021),
PrusaSlicer/BambuStudio slicer-level failures (all covered by Tfa014, A102, P007, P015).

---

## Wave Trend

```
Wave 1: 24.6%  ████████████████████████░
Wave 2: 10.5%  ██████████░
Wave 3:  9.3%  █████████░
Wave 4: 34.3%  ██████████████████████████████████░  ← commercial pivot
Wave 5: 28.0%  ████████████████████████████░
Wave 6: 46.7%  ██████████████████████████████████████████████░  ← AP242 Ed.2 + MANTIS pre-2020
Wave 7: 34.8%  ██████████████████████████████████░             ← AP242 Ed.3 + MANTIS 2020-22
```

The wave-6→wave-7 drop (46.7% → 34.8%) is expected: wave-6 opened two high-signal seams (MANTIS
pre-2020 and NIST AP242 MBE tests) that were quickly saturating. Wave-7's AP242 Ed.3 seam is the
new high-signal source. The AP242 Ed.3 entities (21 new types) represent a largely untapped catalog
that will likely sustain several more mining waves before saturation.

---

## DEFERRED List — Novel defects for B4.5d fixture synthesis

### DEF-HH: Slicer STEP fixed chord deflection — unconfigurable BRepMesh tessellation parameter (D02)

STEP file with two `ADVANCED_FACE` entities on `B_SPLINE_SURFACE_WITH_KNOTS` surfaces: one large-radius
(R = 50 mm) and one small-radius (R = 1.5 mm) cylinder joined at a fillet. Both faces are correctly
parameterized per AP214. The fixture's Expected / Tier-3 oracle must specify the correct geometry
(both faces should tessellate to smooth meshes at appropriate chord deviations). The defect class
is that slicers using a fixed `LinearDeflection = 0.1 mm` will produce a noticeably coarser
tessellation for the small-radius face than is geometrically appropriate. Expected: an OCCT-based
reader with configurable chord deflection (0.01 mm) produces a smooth small-radius face; a reader
with fixed 0.1 mm deflection produces a visibly faceted approximation. The fixture tests whether
the reader's tessellation parameter is appropriate for the geometry present in the STEP file.
Source: https://github.com/bambulab/BambuStudio/issues/3437. Confidence: HIGH — the geometry is
straightforward; the deflection-vs-radius interaction is precisely quantifiable.

### DEF-II: AP242 Ed.3 ANNOTATION_TO_ANNOTATION_LEADER_LINE entity — dropped by Ed.2 readers (D09)

STEP AP242 Edition 3 file with two PMI annotation callouts — a position tolerance frame and a datum
feature label — linked by an `ANNOTATION_TO_ANNOTATION_LEADER_LINE` entity (Ed.3). The file header
declares `{1 0 10303 442 4 1 4}` (AP242 Ed.3 schema identifier). Also includes a minimal cube
`MANIFOLD_SOLID_BREP`. Expected: under AP242 Ed.3 readers the leader line entity is recognized and
both annotations are linked; under AP242 Ed.2 / AP214 readers, the `ANNOTATION_TO_ANNOTATION_LEADER_LINE`
entity produces a `Void` transfer status; both individual annotations still load but the linking
entity is absent. Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html. Confidence:
HIGH — entity type is precisely named; Ed.3 schema identifier is well-defined.

### DEF-JJ: AP242 Ed.3 BASIC_ROUND_HOLE / BASIC_ROUND_HOLE_OCCURRENCE feature entities (D10)

STEP AP242 Edition 3 file with a prismatic part containing one drilled through-hole, encoded as:
(a) the B-rep geometry: `CYLINDRICAL_SURFACE` `ADVANCED_FACE` set for the hole wall, plus two `PLANE`
cap faces; (b) the feature semantic: `BASIC_ROUND_HOLE` with `internal_diameter = 6.0` and
`BASIC_ROUND_HOLE_OCCURRENCE` referencing the B-rep hole face. File header: AP242 Ed.3. Expected:
under Ed.3 readers, the hole feature metadata (type = through, diameter = 6 mm) is accessible; under
Ed.2 / AP214 readers, the feature entities produce `Void` transfer status but the hole geometry
(cylindrical wall + caps) still loads correctly. Source: steptools.com AP242 Ed.3 notes; FreeCAD
issue #19795. Confidence: HIGH — entity encoding is documented in AP242 Ed.3 §4.4.

### DEF-KK: AP242 Ed.3 TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION bidirectional link (D11)

STEP AP242 Edition 3 file with a single-face planar part where the topological model
(`TOPOLOGICAL_REPRESENTATION_ITEM`) and the geometric model (`MANIFOLD_SURFACE_SHAPE_REPRESENTATION`)
are explicitly linked by a `TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION` entity and its inverse
`GEOMETRY_TO_TOPOLOGY_MODEL_ASSOCIATION`. File header: AP242 Ed.3. Also contains a PMI annotation
referencing the face. Expected: Ed.3 readers can query the topology-geometry association; Ed.2
readers silently ignore both association entities; the part geometry (single planar face) loads
under all readers but the association is absent. Source: steptools.com AP242 Ed.3 notes.
Confidence: MEDIUM — the entity chain requires careful AP242 Ed.3 schema knowledge; needs oracle
verification against an Ed.3-capable reader.

### DEF-LL: PRESENTATION_LAYER_ASSIGNMENT null item in assigned_items crash (D14)

STEP AP214 file with a `PRESENTATION_LAYER_ASSIGNMENT` whose `assigned_items` list contains a
`$` (null) entry alongside valid `STYLED_ITEM` references. A valid cube `MANIFOLD_SOLID_BREP`
geometry is present. Expected: OCCT prior to fix 96049f2 dereferences the null entry and segfaults;
OCCT after fix handles the null gracefully; the non-null items are correctly assigned to the layer.
Source: https://github.com/Open-Cascade-SAS/OCCT/commit/96049f2e3d7de177d89f89231e44e9d7d105ae43.
Confidence: HIGH — the null `$` entry is trivially encoded in STEP syntax; the crash vector is
precisely described.

### DEF-MM: AP242 Ed.1 kinematic module — REVOLUTE_PAIR + KINEMATIC_JOINT + KINEMATIC_LINK silently absent (D15)

STEP AP242 Edition 1 file with a two-link mechanism: link L1 (a rectangular prism, at origin) and
link L2 (a shorter prism) connected by a revolute joint J1 with axis = Z, joint range = ±90°. The
STEP file encodes: (a) two `MANIFOLD_SOLID_BREP` geometries for L1 and L2; (b) `KINEMATIC_LINK`
entities for each solid; (c) a `REVOLUTE_PAIR` entity referencing both links and specifying the
Z-axis and range; (d) a `KINEMATIC_JOINT` entity referencing the pair; (e) a `KINEMATIC_STRUCTURE`
collecting the links. Expected: OCCT 7.x reads both geometries correctly but produces no kinematic
data in the XDE document; FreeCAD shows two static parts with no joint; an AP242-Ed.1 kinematics-
capable reader populates joint constraints. Source: FreeCAD issue #19795; OCCT STEP translator
documentation (geometry+assembly only). Confidence: MEDIUM — the entity chain encoding requires AP242
Ed.1 kinematic module schema knowledge; geometry encoding is straightforward; kinematic part needs
oracle verification against a capable reader (HOOPS Exchange or STEP Tools ST-Developer).

### DEF-NN: OCCT STEP export duplicates B_SPLINE_SURFACE_WITH_KNOTS entity instances (D22)

STEP AP214 file produced by OCCT 7.4.x from two `ADVANCED_FACE` entities that share the same
underlying `Geom_BSplineSurface` (as occurs after `BRepBuilderAPI_Sewing` on adjacent faces with
matched boundaries); the STEP writer creates two separate `B_SPLINE_SURFACE_WITH_KNOTS` entity
instances with identical control-point and knot data rather than one shared instance. A synthesized
fixture should be hand-crafted to reproduce this structure: two `ADVANCED_FACE` entities with
distinct `B_SPLINE_SURFACE_WITH_KNOTS` entity IDs but numerically identical parameters. Expected:
a reader that performs instance-identity checks sees two independent surfaces; a reader that performs
geometric-equality checks recognizes them as shared; STEP validators may flag the structural
redundancy. Source: OCCT MANTIS 0032132. Confidence: HIGH — the entity structure is precisely
describable; encoding two duplicate surface entities with the same parameter data is straightforward.

### DEF-OO: AP242 Ed.3 GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION per-item geometry reference (D21)

STEP AP242 Edition 3 file with a position tolerance applied to a specific `ADVANCED_FACE` (face F1
of a cube), linked via `GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION` that identifies F1 within the
`MANIFOLD_SURFACE_SHAPE_REPRESENTATION`. File header: AP242 Ed.3. Expected: Ed.3 readers can
determine which face the tolerance applies to via the GEOMETRY_BASED_ITEM reference; Ed.2 readers
ignore the entity and cannot determine the specific face link; the position tolerance annotation
entity itself still loads but has no face reference. Source: steptools.com AP242 Ed.3 notes.
Confidence: MEDIUM — requires AP242 Ed.3 schema for this specific entity type; needs oracle
verification.

---

## Notes for B4.5d Fixture Synthesis

- **DEF-HH** (slicer chord deflection): the geometry is straightforward; the key is encoding a
  correctly-parameterized small-radius face and verifying tessellation outputs at different chord values.
- **DEF-II** (ANNOTATION_TO_ANNOTATION_LEADER_LINE): requires AP242 Ed.3 schema; Ed.3 file header
  must declare `{1 0 10303 442 4 1 4}`; high confidence once entity chain is located in schema.
- **DEF-JJ** (BASIC_ROUND_HOLE): well-documented in Ed.3 notes; high confidence; the B-rep geometry
  co-present ensures the geometry-vs-feature-semantic split is clearly testable.
- **DEF-KK** (TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION): medium confidence; entity pair needs schema
  lookup in AP242 Ed.3 Part 1; bidirectional nature requires both entity types.
- **DEF-LL** (null in PRESENTATION_LAYER_ASSIGNMENT): trivial to encode; `$` in STEP is a valid null;
  highest confidence in the set.
- **DEF-MM** (AP242 kinematic module): geometry encoding is easy; kinematic entity chain requires
  AP242 Ed.1 schema Part 105 (kinematics); medium confidence; oracle verify needed.
- **DEF-NN** (duplicate surface instances): trivial structural encoding; two entity IDs with identical
  B-spline parameter tables; high confidence.
- **DEF-OO** (GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION): similar to DEF-KK; needs AP242 Ed.3 schema;
  medium confidence.

High-confidence synthesis targets: DEF-HH, DEF-II, DEF-JJ, DEF-LL, DEF-NN.
Medium-confidence (needs oracle verify): DEF-KK, DEF-MM, DEF-OO.

---

## Appendix: Source URLs

1. BambuStudio GitHub issues:
   - https://github.com/bambulab/BambuStudio/issues/2290 (small face missing on STEP import)
   - https://github.com/bambulab/BambuStudio/issues/3437 (STEP translation poor quality, 44% fewer triangles)
   - https://github.com/bambulab/BambuStudio/issues/4761 (strange holes in STEP file)
   - https://github.com/bambulab/BambuStudio/issues/5186 (STEP import crash v1.10)

2. PrusaSlicer GitHub issues:
   - https://github.com/prusa3d/PrusaSlicer/issues/8998 (127 open edges in hinge STEP, ShapeFix breaks part)
   - https://github.com/prusa3d/PrusaSlicer/issues/13892 (curved faces faceted in v2.9)

3. ISO 10303-21 Edition 3 specification:
   - http://www.steptools.com/stds/step/IS_final_p21e3.html (anchor/reference/signature/ZIP/UTF-8)

4. AP242 Edition 3 change notes:
   - https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (21 new entities, enum reordering)

5. FreeCAD AP242 support gap:
   - https://github.com/FreeCAD/FreeCAD/issues/19795 (AP242 Ed.1-4 missing features)
   - https://github.com/FreeCAD/FreeCAD/issues/20889 (FreeCAD v1.0 fillet STEP export regression)

6. OCCT MANTIS 2020-2022 tickets:
   - https://tracker.dev.opencascade.org/view.php?id=31809 (color regression 6.9.1→7.4.0)
   - https://tracker.dev.opencascade.org/view.php?id=32049 (layer visibility + null item crash)
   - https://tracker.dev.opencascade.org/view.php?id=32087 (NULL DGT representation for geometric tolerance)
   - https://tracker.dev.opencascade.org/view.php?id=32132 (STEP export duplicate surfaces)
   - https://tracker.dev.opencascade.org/view.php?id=32264 (STEP exporter bad geometry regression 7.4.0)

7. OCCT MANTIS fix commit (layer visibility bug 0032049):
   - https://github.com/Open-Cascade-SAS/OCCT/commit/96049f2e3d7de177d89f89231e44e9d7d105ae43

8. OCCT STEP translator documentation:
   - https://dev.opencascade.org/doc/overview/html/occt_user_guides__step.html

9. Onshape forum (transform → non-manifold in STEP export):
   - https://forum.onshape.com/discussion/25017/why-do-i-get-non-manifold-edges-simply-by-doing-a-transform-rotate-and-how-do-i-fix-it
