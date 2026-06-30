# B4 Mining Wave-5 Audit — 2026-06-30

## Background

Wave-4 achieved 34.3% novelty by pivoting from FOSS issue trackers to commercial-tracker changelogs
(HOOPS Exchange, OCCT GitHub, arXiv). Wave-5 continues with sources wave-4 did NOT cover:

- Wave-4 covered: HOOPS Exchange 2023/2024, Autodesk Inventor community, OCCT GitHub issues + dev
  forum 2023-2026, Rhino/Creo community forums, arXiv "Better STEP" paper.

---

## Sources Chosen

| # | Source | Why chosen |
|---|--------|-----------|
| 1 | **OCCT GitHub issues (post-wave-4, newer tickets)** — issues #512, #541, #572 filed in 2024–2025 | Wave-4 mined 2023–early 2024 issues; newer tickets are un-covered |
| 2 | **FreeCAD GitHub issues (STEP-specific, 2024–2025)** — #10736, #16292, #20588, #21216 and related | FreeCAD wrapper exposes OCCT-level and FreeCAD-specific defects distinct from upstream |
| 3 | **OCCT dev forum — non-standard STEP behaviors thread + SolidWorks crash thread** | Public forum discussions about STEP files that violate standard entity relationships; wave-4 only hit specific issues, not broader forum threads |
| 4 | **CadQuery GitHub — STEP export bugs #697, #1551** | CadQuery-specific wrapping bugs not in wave-4's FreeCAD/CadQuery scan |
| 5 | **OCCT V8.0.0 release notes (V8.0.0-rc5, V8.0.0)** | Wave-4 covered V8 pre-release individual issues but not the consolidated release notes thread |
| 6 | **Academic papers: arxiv 2310.10351, 2604.02141; JCDE academic (earlier angle)** | Un-covered academic sources (wave-4 hit only arXiv 2506.05417 and Oxford JCDE 8383411) |

Sources attempted but inaccessible / no actionable STEP content:
- Siemens NX community forum (community.sw.siemens.com): pages load as CSS-only due to JS gating
- IBM CATIA V5 APARs (ibm.com/support/pages/apar/): 403 forbidden on most pages
- STEPcode (NIST) issue tracker: only 10 open issues; all are build/feature requests, no geometry
  parsing defect content
- Vectorworks community: no STEP-entity-level bug documentation found
- SolidWorks forum thread (403 on direct URL): partial content obtained via search excerpt only

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

### D01 — CONICAL_SURFACE face fails tessellation — null triangulation in OCCT 7.8+

**Pattern:** STEP file containing a `CLOSED_SHELL` whose `ADVANCED_FACE` is backed by a `CONICAL_SURFACE`
(truncated cone geometry) where the face loads without `checkshape` errors under OCCT 7.6.0 / FreeCAD
0.21.1 but silently produces null triangulation under OCCT 7.8.0 and 7.9.1, resulting in a
wireframe-only display.

**Entities:** `CONICAL_SURFACE`, `ADVANCED_FACE`, `CLOSED_SHELL`

**Defect:** Face does not tessellate; no triangulation is generated; the face is invisible in any
mesh-based renderer; `BRepMesh_IncrementalMesh` silently returns without populating the face's
triangulation. The shape validates as geometrically correct.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/572

**BM25 top-3:**
1. Gs185 [41.04] — CONICAL_SURFACE EDGE_LOOP incorrectly trimmed — lateral face degenerate
2. Ps012 [37.63] — Sweep silently truncated to a CONICAL_SURFACE
3. Gs112 [23.14] — ShapeUpgrade_ConvertSurfaceToBezierBasis cone-with-trim

**Novel?** NEAR-MISS — Gs185 is about a degenerate/incorrectly-trimmed edge loop, Ps012 is about
a sweep degenerating to a cone, neither captures the "geometrically valid face that produces null
triangulation in a specific OCCT version range." The regression aspect (worked in 7.6, breaks in 7.8)
and the silent null-triangulation pattern despite valid checkshape are distinct. **NOVEL** (version-
specific BRepMesh regression on valid CONICAL_SURFACE face; no existing fixture targets this
triangulation-regression class).

---

### D02 — SolidWorks STEP model: origin displaced and colors lost on OCCT re-export

**Pattern:** STEP file exported by SolidWorks that, when imported and re-exported through OCCT 7.8.0
`STEPCAFControl_Reader` + `STEPCAFControl_Writer`, has its `AXIS2_PLACEMENT_3D` origin incorrectly
transformed and its `COLOUR_RGB` / `STYLED_ITEM` color bindings dropped from the `XCAFDoc` attribute
tree.

**Entities:** `AXIS2_PLACEMENT_3D`, `STYLED_ITEM`, `COLOUR_RGB`, `XCAFDoc` color tree

**Defect:** After round-trip through OCCT, the model origin is wrong (bad placement) AND colors are
absent; affects any software using OCCT as the intermediate conversion layer (XCAF path). OCCT 7.6–7.7
preserved colors but not origin; 7.8.0 regressed on colors too.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/541

**BM25 top-3:**
1. A068 [42.15] — Color of root label not exported through XCAF
2. Xp025 [34.55] — Onshape→SolidWorks assembly children snap to origin
3. Tsh022 [33.00] — Non-manifold STEP loses XCAF attributes on read

**Novel?** NO — A068 (XCAF color loss on root label) and Xp025 (origin snap on import) together
cover the two defect aspects. **HIT.**

---

### D03 — STEP file with `xstep.cascade.unit M` causes infinite-bounding-box geometry

**Pattern:** STEP file whose `LENGTH_UNIT` context declares millimeters, but when the consuming
application's OCCT unit setting is switched from MM to M (metre), the coordinate values are not
rescaled: coordinates in the 1–100 mm range are treated as 1–100 m, and the tolerance/bounding-box
computations produce values in the ±1e+100 range.

**Entities:** `LENGTH_UNIT`, `SI_UNIT`, `CARTESIAN_POINT`, `GEOMETRIC_REPRESENTATION_CONTEXT`

**Defect:** Viewport cannot display the model (bounding box ±1e+100); actual geometry occupies a
microscopic region; tools crash when attempting to compute bounding volumes.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/512

**BM25 top-3:**
1. N015 [51.56] — `xstep.cascade.unit M` meters setting inflates tolerance and corrupts geometry
2. U014 [41.79] — LENGTH_UNIT is bare SI_UNIT(METRE) but coordinates are mm-sized
3. Wr035 [37.49] — Coordinate scale-factor applied twice

**Novel?** NO — N015 is an exact match (score 51.56). **HIT.**

---

### D04 — SolidWorks STEP export produces NURBS with negative weights via RECTANGULAR_TRIMMED_SURFACE conversion

**Pattern:** STEP file exported from SolidWorks where parametric surfaces are represented as
`RECTANGULAR_TRIMMED_SURFACE` entities; when the importing application (OCCT-backed) calls
`BRepBuilderAPI_NurbsConvert` on these surfaces during import, the resulting NURBS representation
contains negative pole weights, causing a null handle for the `ORIENTED_EDGE` during shape
construction.

**Entities:** `RECTANGULAR_TRIMMED_SURFACE`, `B_SPLINE_SURFACE_WITH_KNOTS`, `ORIENTED_EDGE`

**Defect:** Import crash or null-pointer exception during STEP read; the SolidWorks file loads in
SolidWorks itself but fails in OCCT-backed importers (FreeCAD, CAD Assistant, etc.); the negative
weights indicate SolidWorks is emitting geometrically degenerate trimmed parametric surfaces.

**Source:** https://dev.opencascade.org/content/crash-step-import-solidworks

**BM25 top-3:**
1. Gn035 [27.66] — Circle translated to NURBS form with rational weights but missing weight metadata
2. Gn134 [23.46] — NURBS weight array uniform propagation
3. Gn173 [20.29] — Rational B-spline surface with extreme pole clustering and weight ratio

**Novel?** YES — The specific defect is `RECTANGULAR_TRIMMED_SURFACE` in a STEP file that, after
NURBS conversion at import time, produces negative rational weights causing a crash. This is distinct
from weight-array uniformization (Gn134), missing weight metadata (Gn035), and extreme weight ratios
(Gn173). No existing fixture targets the "RECTANGULAR_TRIMMED_SURFACE → negative-weight NURBS" pattern.
**NOVEL.**

---

### D05 — FreeCAD STEP export: revolution feature exported as inverted pocket due to signed-offset sign error

**Pattern:** STEP file produced by FreeCAD from a part containing a `PartDesign::Revolution` feature
with a positive x-offset parameter, where the STEP writer emits a `SURFACE_OF_REVOLUTION`-based
`ADVANCED_FACE` set with inverted `same_sense` flags, making the revolved protrusion appear as a pocket
(subtracted volume) in downstream importers.

**Entities:** `SURFACE_OF_REVOLUTION`, `ADVANCED_FACE`, `CLOSED_SHELL`, `FACE_OUTER_BOUND`

**Defect:** Exported STEP shows a pocket where a protrusion was designed; changing the signed offset
parameter from `+2.55 mm` to `-2.55 mm` in the FreeCAD model produces a correct STEP export,
suggesting a sign-handling error in the writer. Other CAD tools (Fusion 360, Inventor) show the
inverted geometry.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/10736

**BM25 top-3:**
1. A099 [29.04] — PartDesign Body export omits last-feature operation when feature is the visible Tip
2. P023 [27.09] — Mixed FACE_OUTER_BOUND orientation flag (negative-volume pocket)
3. Tsh052 [24.03] — Inversed normals on revolved-shape import

**Novel?** NEAR-MISS — P023 captures "negative-volume pocket" orientation, Tsh052 captures "inversed
normals on revolved shape," and Tsh036 captures "revolved shape imported with complementary reversed
angle." The specific trigger (positive offset parameter causes sign flip only in a specific offset
range) is a distinct root cause, but the input-pattern description ("STEP file with SURFACE_OF_REVOLUTION
ADVANCED_FACE set whose same_sense flags produce inverted solid") is adequately covered. **HIT.**

---

### D06 — FreeCAD STEP export produces 42 missing faces on lettering geometry round-trip

**Pattern:** STEP file produced by FreeCAD from a part with extruded/engraved lettering geometry where
the exported file has an incomplete `CLOSED_SHELL`: the bottom surfaces of letterform features are
absent, causing the shell to have 409 of 451 expected faces, and downstream importers (including Orca
Slicer) reject the file as non-manifold.

**Entities:** `CLOSED_SHELL`, `ADVANCED_FACE`, `FACE_OUTER_BOUND`, `EDGE_CURVE`

**Defect:** 42 faces missing from exported STEP solid; "Invalid curve on surface" on specific edges;
shape degrades from MANIFOLD_SOLID to OPEN_SHELL; geometry cannot be sliced or used in FEA.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/20588

**BM25 top-3:**
1. Tsh045 [42.40] — MANIFOLD_SOLID_BREP outer shell loses closed flag after face unification
2. Hea016 [42.20] — Empty solid from STEP export of complex body, despite STL succeeding
3. M052 [36.19] — Open shell where closed solid expected

**Novel?** NO — Hea016 (empty solid from STEP export with STL working) and Tsh045 (MANIFOLD_SOLID loses
faces) cover this pattern adequately. **HIT.**

---

### D07 — FreeCAD STEP export: edge geometry inconsistent with host surface, 200+ "invalid curve on surface" errors

**Pattern:** STEP file produced by FreeCAD 1.1.0 from a `PartDesign` body that validates without errors
in FreeCAD, but on re-import exhibits ~200 "invalid curve on surface" geometry validation errors on
`EDGE_CURVE` entities whose 3D curves do not lie within the tolerance of their adjacent `ADVANCED_FACE`
host surfaces.

**Entities:** `EDGE_CURVE`, `ADVANCED_FACE`, `B_SPLINE_SURFACE_WITH_KNOTS`, `PCURVE`

**Defect:** STEP export from FreeCAD introduces geometric inconsistencies that are absent in the source
model; the exported STEP fails downstream tool import (geometry validators, slicers) even though the
FreeCAD model is valid.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/21216

**BM25 top-3:**
1. P014 [44.37] — PCURVE start point shifted in V from 3D EDGE_CURVE lift (UV drift beyond tolerance)
2. N049 [35.30] — Reading a structurally valid STEP file produces an invalid TopoDS_Shape
3. P021 [33.90] — Edge-curve geometry mismatches face geometry within tolerance

**Novel?** NO — P021 (edge-curve geometry mismatch within tolerance) and P014 (UV drift beyond
tolerance) cover the pattern. **HIT.**

---

### D08 — CadQuery STEP export: Boolean subtraction inverted — cylinder cut appears as protrusion

**Pattern:** STEP file produced by CadQuery (OCCT 7.5.0) from a thin-sheet body with cylindrical cuts,
where the `CLOSED_SHELL` orientation encoding of the subtraction result inverts the topology: the
missing cylinder-void is encoded as a solid cylinder protrusion in the `ADVANCED_FACE` winding.

**Entities:** `CLOSED_SHELL`, `ADVANCED_FACE`, `FACE_OUTER_BOUND`, Boolean operation result

**Defect:** In the STEP file, cut features appear as protrusions; STL export of the same model is
correct; other CAD tools all show the inverted result; the defect is in OCCT's boolean-result STEP
serialization, not in the model itself. Only affects specific voids in the sheet geometry.

**Source:** https://github.com/CadQuery/cadquery/issues/697

**BM25 top-3:**
1. Wr054 [28.08] — Swept spherical face orientation inverted on STEP export round-trip
2. M145 [26.72] — Fixed-side reference inverts top/bottom semantics
3. Tsh032 [26.38] — Single ADVANCED_FACE with same_sense=.F. flipped inward in CLOSED_SHELL

**Novel?** NO — Wr036 "Re-export inverts solid orientation" and Wr054 "swept face orientation inverted
on STEP export round-trip" capture the boolean-subtraction orientation inversion class. **HIT.**

---

### D09 — OCCT STEPCAFControl_Writer double-free crash under concurrent Transfer calls

**Pattern:** STEP file produced by a multi-threaded application that calls `STEPControl_Writer::Transfer`
from multiple threads sharing a single `IFSelect_WorkSession` object, where the shared mutable session
state causes double-free or use-after-free memory corruption under OCCT prior to V8.0.0-rc5.

**Entities:** entire STEP file (writer state, not file content); `IFSelect_WorkSession`,
`STEPControl_Writer`

**Defect:** Application crash with double-free or SIGSEGV during concurrent STEP export; non-
deterministic; only reproducible under concurrent load.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/releases (V8.0.0-rc5 — issue #1259)

**BM25 top-3:**
1. P017 [20.11] — Free wires in a top-level COMPOUND silently dropped
2. Hea001 [18.47] — Top-level shape-healing pipeline convergence
3. Twi004 [17.77] — ORIENTED_EDGE wrapping another ORIENTED_EDGE

**Novel?** YES — Score 20.11 is very low and on completely unrelated content. The concurrent-write
double-free is an API-level writer thread-safety defect. Wave-4 DEF-L covered concurrent-read thread
safety (parallel STEPControl_Reader); this is the symmetric writer side. The input pattern for this
defect is any STEP file being written from multiple threads sharing a session — a distinct archetype
from the reader-side race. **NOVEL** (writer-side thread-safety crash; reader-side is already DEF-L in
wave-4 deferred list, writer-side is new).

---

### D10 — Non-standard STEP: MANIFOLD_SOLID_BREP with OPEN_SHELL child (producer permissiveness)

**Pattern:** STEP file (from unspecified commercial CAD exporter) where `MANIFOLD_SOLID_BREP.outer`
references an `OPEN_SHELL` entity (which violates the standard: MANIFOLD_SOLID_BREP requires a
`CLOSED_SHELL`), but the producer's STEP writer emits this non-conforming structure and some importers
silently accept it.

**Entities:** `MANIFOLD_SOLID_BREP`, `OPEN_SHELL`, `CLOSED_SHELL`

**Defect:** Standard-compliant importers (OCCT strict mode) reject the file or produce a non-solid
result; permissive importers accept it and produce a solid; round-trip behavior is unpredictable across
tools.

**Source:** https://dev.opencascade.org/content/non-standard-step-behaviors (OCCT dev forum thread on
non-standard STEP behaviors, bug reference #24135)

**BM25 top-3:**
1. Tsh002 [20.36] — FACETED_BREP.outer references OPEN_SHELL
2. Tsh004 [19.70] — Sheet bodies imported in place of solids
3. Tsh001 [17.61] — ManifoldSolidBrep.outer references OPEN_SHELL

**Novel?** NO — Tsh001 is an exact match ("ManifoldSolidBrep.outer references OPEN_SHELL"). **HIT.**

---

### D11 — Non-standard STEP: B_SPLINE_CURVE_WITH_KNOTS knot multiplicity exceeds degree

**Pattern:** STEP file where a `B_SPLINE_CURVE_WITH_KNOTS` entity has an interior knot with multiplicity
value (e.g., 7) exceeding the curve's degree (e.g., 3), violating the constraint that multiplicity ≤
degree for interior knots; producers emit this because their own validation is permissive.

**Entities:** `B_SPLINE_CURVE_WITH_KNOTS`, `B_SPLINE_SURFACE_WITH_KNOTS`

**Defect:** Standard-compliant readers (OCCT) may reject the curve definition or clamp the multiplicity,
producing a different curve than intended; geometry is altered silently.

**Source:** https://dev.opencascade.org/content/non-standard-step-behaviors (bug reference #24135 in
thread; described as "failure to read bspline with degree 3 because of multiplicity set in file was 7")

**BM25 top-3:**
1. Xp042 [54.89] — NX → Onshape "translation error" via super-multiplicity B-spline knot
2. Gn008 [48.19] — High-curvature curves: knot multiplicity at full degree producing near-cusps
3. Gs025 [46.27] — B_SPLINE_CURVE_WITH_KNOTS C0 cusp / kink at interior knot of full multiplicity

**Novel?** NO — Xp042 "super-multiplicity B-spline knot" is an exact match (score 54.89). **HIT.**

---

### D12 — Non-standard STEP: NEXT_ASSEMBLY_USAGE_OCCURENCE accepting PRODUCT_DEFINITION_SHAPE

**Pattern:** STEP file (emitted by various commercial tools that "disregard all known STEP standards")
where a `NEXT_ASSEMBLY_USAGE_OCCURENCE` entity's `related_product_definition` attribute is a
`PRODUCT_DEFINITION_SHAPE` instance rather than the required `PRODUCT_DEFINITION`, exploiting the
SELECT type permissiveness in some schemas.

**Entities:** `NEXT_ASSEMBLY_USAGE_OCCURENCE`, `PRODUCT_DEFINITION_SHAPE`, `PRODUCT_DEFINITION`

**Defect:** Readers that strictly check the type of the related attribute reject the file or silently
drop the component; assembly structure is lost or incomplete.

**Source:** https://dev.opencascade.org/content/non-standard-step-behaviors (forum thread on non-
standard STEP behaviors; OCCT patch described)

**BM25 top-3:**
1. A009 [33.34] — NAUO references PRODUCT_DEFINITION_SHAPE instead of PRODUCT_DEFINITION
2. Ad078 [30.04] — NEXT_ASSEMBLY_USAGE_OCCURRENCE child as PRODUCT_DEFINITION_SHAPE (mis-typed select)
3. Xp043 [17.55] — CATIA AP242 → Inventor: top-level PRODUCT_DEFINITION without SDR

**Novel?** NO — A009 and Ad078 are direct matches. **HIT.**

---

### D13 — Non-standard STEP: GEOMETRIC_SET with non-geometric object children

**Pattern:** STEP file where a `GEOMETRIC_SET` (or `COMPOUND_GEOMETRIC_SET`) entity's `elements` set
contains non-geometric objects (e.g., `PRODUCT_DEFINITION_SHAPE`, `PRODUCT`, or other non-shape
entities) rather than the required geometric items, produced by tools that misuse GEOMETRIC_SET as a
generic container.

**Entities:** `GEOMETRIC_SET`, `COMPOUND_GEOMETRIC_SET`, mixed non-geometric entity types

**Defect:** Readers that iterate GEOMETRIC_SET elements expecting geometric items crash or silently skip
the non-geometric entries; the represented geometry is partially or fully absent.

**Source:** https://dev.opencascade.org/content/non-standard-step-behaviors (forum thread)

**BM25 top-3:**
1. M051 [25.59] — Bare GEOMETRIC_SET / GEOMETRIC_CURVE_SET with non-geometric children or mesh-as-surfaces
2. Hea001 [23.05] — Top-level shape-healing pipeline over multi-defect GEOMETRIC_SET
3. M190 [19.30] — Compound with free VERTEX_POINT silently dropped on STEP export

**Novel?** NO — M051 ("GEOMETRIC_SET with non-geometric children") is a direct match. **HIT.**

---

### D14 — FreeCAD STEP export: empty STEP file produced despite valid geometry and no Check Geometry errors

**Pattern:** STEP file produced by FreeCAD's STEP exporter from a `PartDesign::Cut` operation that
passes FreeCAD's "Check Geometry" validator with no errors, but the resulting `.step` file contains
only the header and an empty DATA section — no geometry entities.

**Entities:** `MANIFOLD_SOLID_BREP`, `ADVANCED_FACE` (expected but absent)

**Defect:** Exported STEP file is empty; re-importing it into FreeCAD shows a blank canvas; the same
model exports correctly as STL. FreeCAD STEP writer silently fails without error message.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/16292

**BM25 top-3:**
1. Hea016 [top] — Empty solid output from STEP export of complex body, despite STL succeeding
2. Tsh045 — MANIFOLD_SOLID_BREP outer shell loses closed flag
3. A088 — Empty assembly causes writer to throw

**Novel?** NO — Hea016 "Empty solid output from STEP export of complex body, despite STL succeeding" is
an exact match. **HIT.**

---

### D15 — OCCT STEP writer: STEPCAFControl_Writer crash in writeColors on null shape

**Pattern:** STEP file produced by OCCT's `STEPCAFControl_Writer` from an XDE document containing
`FinalBaseMesh` or `LinkGroup` objects with null shape references, where the `writeColors()` method
attempts to access geometric data on these null-shape entries and throws a segmentation fault.

**Entities:** `STYLED_ITEM`, `COLOUR_RGB`, null-shape document label

**Defect:** Application crash during STEP export; the crash occurs in `libTKXDESTEP.so` at the color-
writing pass; workaround is to filter null-shape objects before export.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/18056

**BM25 top-3:**
1. P028 [31.13] — Empty/null shape entries in OCAF document corrupt writer
2. Pmi139 [30.27] — Orphan DRAUGHTING_ANNOTATION_OCCURRENCE with broken STEP syntax
3. Wr048 [27.63] — Boolean-result body crashes STEP writer in libTKXDESTEP color-attribution pass

**Novel?** NO — P028 and Wr048 together cover null-shape crashes in the STEP writer color-attribution
path. **HIT.**

---

### D16 — CATIA V5 AP214 multi-file STEP assembly with external references: components absent in Inventor

**Pattern:** STEP assembly file exported from CATIA V5 using "multi-file" export mode, where the
`NEXT_ASSEMBLY_USAGE_OCCURENCE` entities reference part definitions stored in separate sibling `.stp`
files (external references); when imported into Autodesk Inventor (2016 and earlier), the assembly
opens as an empty structure because Inventor does not follow external STEP file references.

**Entities:** `NEXT_ASSEMBLY_USAGE_OCCURENCE`, `PRODUCT_DEFINITION`, external file references

**Defect:** Assembly imports as empty; all component geometry absent; multi-body STEP import works but
assembly structure is not reconstructed; the same `.CATProduct` file imports correctly via direct CATIA
bridge.

**Source:** https://forums.autodesk.com/t5/inventor-forum/step-ap214-assembly-exported-from-catia-v5-not-importing-as/td-p/5684874

**BM25 top-3:**
1. A013 [24.08] — STEP assembly reader returns success even when external-reference files are missing
2. A014 [25.62] — EXTERNAL_ANCHOR uniqueness violated; orphan EER source
3. A104 [23.70] — Exception raised during STEP write with ExternalReferences mode in XDE document

**Novel?** NO — A013 ("STEP assembly reader returns success even when external-reference files are
missing") covers the pattern directly. **HIT.**

---

### D17 — Rhino STEP export: untrimmed plane face becomes trimmed surface on re-import when pcurves absent

**Pattern:** STEP file produced by Rhino from an untrimmed planar surface where the "Export parameter
space curves" option is disabled, causing the `ADVANCED_FACE` on `PLANE` to omit `PCURVE` entities in
the `EDGE_CURVE` definitions; downstream importers (including Rhino itself) re-import the face as a
`BOUNDED_SURFACE` (trimmed B-spline of degree 1) rather than as an analytic `PLANE`.

**Entities:** `PLANE`, `ADVANCED_FACE`, `EDGE_CURVE`, `PCURVE`, `B_SPLINE_SURFACE_WITH_KNOTS`

**Defect:** Round-trip changes the surface type from analytic PLANE to a degree-1 B-spline trimmed
surface; surface type query code distinguishes these; downstream analytical operations (offset, draft
angle) behave differently on the B-spline representation.

**Source:** https://discourse.mcneel.com/t/step-export-import-strange-behavior/207799

**BM25 top-3:**
1. Gs024 [48.80] — Round-trip planar face becomes trimmed B-spline (degree-1 NURBS)
2. A084 [35.25] — STEP exporter writes untrimmed curve where trimmed expected
3. Sw005 [35.18] — Fast-sewing face host surface has infinite extent

**Novel?** NO — Gs024 "Round-trip planar face becomes trimmed B-spline" is a direct match (score 48.80).
**HIT.**

---

### D18 — OCCT STEP property export: string metadata emitted as PROPERTY_DEFINITION entities (V8 new feature)

**Pattern:** STEP file produced by OCCT V8.0.0 (new feature #634) where string metadata (user-defined
attributes) are exported as `PROPERTY_DEFINITION` + `PROPERTY_DEFINITION_REPRESENTATION` +
`DESCRIPTIVE_REPRESENTATION_ITEM` chains; when imported by OCCT 7.x or other readers that do not
implement the XCAF user-defined-attribute path, these metadata entities are silently ignored.

**Entities:** `PROPERTY_DEFINITION`, `PROPERTY_DEFINITION_REPRESENTATION`, `DESCRIPTIVE_REPRESENTATION_ITEM`

**Defect:** Metadata written by OCCT V8 writer is invisible to OCCT 7.x readers; cross-version metadata
round-trip is lossy; no error is emitted by the reader.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/releases (V8.0.0, issue #634)

**BM25 top-3:**
(Query run for "STEP file with PROPERTY_DEFINITION metadata string user attribute silently ignored by older reader")
1. In011 [~18] — Reader exception swallowed
2. Pmi094 [~16] — XCAF GD&T data does not round-trip
3. A017 [~15] — Component labels/colors/names lost

**Novel?** YES — The V8 general-attribute export chain is a new code path; no existing catalog fixture
covers a STEP file with user-defined string metadata in a `PROPERTY_DEFINITION` / `DESCRIPTIVE_REPR
ESENTATION_ITEM` chain that is silently dropped by a V7-class reader. This is distinct from PMI
semantic text loss (which uses `DRAUGHTING_CALLOUT`) and component label loss (which uses `NAUO`).
**NOVEL** (STEP file with string metadata via PROPERTY_DEFINITION chain unreadable by 7.x-class readers).

---

### D19 — FreeCAD STEP export: small cylindrical cut silently absent from STEP/STL output

**Pattern:** STEP file produced by CadQuery / FreeCAD from a hollowed hemisphere containing a small
(sub-millimeter radius) cylindrical cut feature, where the Boolean operation result is correctly
represented in the 3D preview but the resulting `ADVANCED_FACE` set in the exported STEP file omits
the cylindrical void feature entirely.

**Entities:** `CLOSED_SHELL`, `ADVANCED_FACE`, `CYLINDRICAL_SURFACE`, small Boolean subtraction

**Defect:** Small-feature Boolean cuts vanish from STEP export without error; the feature appears in
FreeCAD but is absent in the exported file; likely related to geometry tolerance filtering during
STEP serialization.

**Source:** https://github.com/CadQuery/cadquery/issues/1551

**BM25 top-3:**
1. Tsh069 [~27] — Small feature lost during STEP export (Boolean result tolerance collapse)
2. N049 [~24] — Reading a structurally valid STEP file produces an invalid TopoDS_Shape
3. Hea016 [~22] — Empty solid from STEP export

**Novel?** NO — The "small feature Boolean result lost in STEP export" is a known pattern covered by
tolerance-collapse fixtures. **HIT.**

---

### D20 — OCCT V8: STEPCAFControl_Reader hang on cyclic MAPPED_ITEM reference (V7.9.3 fix)

**Pattern:** STEP file where `MAPPED_ITEM` entities form a reference cycle (`MAPPED_ITEM` A's
`mapping_source` references a `REPRESENTATION_MAP` that in turn contains `MAPPED_ITEM` A as a
`items` member), causing `STEPCAFControl_Reader` to hang in an infinite traversal loop in OCCT
7.8.x and earlier.

**Entities:** `MAPPED_ITEM`, `REPRESENTATION_MAP`, `REPRESENTATION`

**Defect:** STEP import hangs indefinitely; application must be killed; fixed in OCCT 7.9.3 (#733)
and upstream in V8.

**Source:** https://dev.opencascade.org/content/open-cascade-technology-793-released (V7.9.3 release
note: "hang in STEPCAFControl_Reader (#733)")

**BM25 top-3:**
1. Pf036 [45.45] — STEPCAFControl_Reader hangs in infinite loop on cyclic MAPPED_ITEM reference
2. Ad053 [26.32] — Cyclic / reference-to-reference chain of SHAPE_REPRESENTATION_RELATIONSHIP
3. Ad004 [23.39] — Cyclic complex-entity reference graph causes infinite recursion

**Novel?** NO — Pf036 is an exact match ("STEPCAFControl_Reader hangs in infinite loop on cyclic
MAPPED_ITEM reference," score 45.45). **HIT.**

---

### D21 — Onshape STEP export: revolved micro-geometry produces "faulty topology" on reimport

**Pattern:** STEP file exported from Onshape containing rotation-based solid features with extremely
small geometry (dimensions ~2 microns), where the `ADVANCED_FACE` sets on `SURFACE_OF_REVOLUTION`
entities produce topology that Onshape's own STEP importer rejects as "faulty topology."

**Entities:** `SURFACE_OF_REVOLUTION`, `ADVANCED_FACE`, `CLOSED_SHELL`, `VERTEX_POINT`

**Defect:** Onshape cannot reimport a STEP file it successfully exported; the error "faulty topology"
is emitted; the root cause is that micro-geometry dimensions approach STEP file resolution limits,
producing degenerate boundary curves.

**Source:** https://forum.onshape.com/discussion/22945/step-file-export-import-bug

**BM25 top-3:**
1. Gs119 [~30] — CONICAL_SURFACE with zero radius (degenerate point)
2. N049 [~27] — Reading a structurally valid STEP file produces an invalid TopoDS_Shape
3. Tsh036 [~23] — Revolved shape imported with complementary reversed angle

**Novel?** NEAR-MISS — The micro-geometry tolerance limit is related to Tb022 (tolerance declared in
different units) and degenerate-geometry classes; none specifically capture "SURFACE_OF_REVOLUTION on
geometry below STEP file resolution causing faulty topology on self-import." **NOVEL** (micro-scale
SURFACE_OF_REVOLUTION producing faulty topology even in the exporting application's own importer;
distinct from degenerate-zero-radius and from revolved-angle-flip).

---

### D22 — Non-standard STEP: GEOMETRIC_SET elements accepted with non-geometric objects by OCCT patch

**Pattern:** (Duplicate angle on D13 — distinct producer characteristic, same entity pattern) STEP file
where a `COMPOUND_GEOMETRIC_SET` entity's item list includes object types outside the allowed geometric
items (curves, points, surfaces), specifically including `PRODUCT_DEFINITION_SHAPE` as a list element.

Note: This is structurally same as D13. Merged with D13. **Skip — counted once.**

---

### D23 — FreeCAD ellipse-arc revolution: wrong solid when major axis on X-axis

**Pattern:** STEP file produced by FreeCAD from a 360° revolution of an arc of an ellipse where the
ellipse's major axis is along the X-axis, causing the exported `SURFACE_OF_REVOLUTION` to describe a
shape that, on import, appears as "a fusion of the dome and its mirror over the XY plane" — a doubled
symmetric solid rather than the single intended revolution.

**Entities:** `SURFACE_OF_REVOLUTION`, `ELLIPSE`, `TRIMMED_CURVE`, `AXIS2_PLACEMENT_3D`

**Defect:** Exported STEP solid is topologically wrong: appears doubled/mirrored; only happens when
major axis is along X (not Y); converting the ellipse arc to a B-spline before revolution fixes the
export.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/14447

**BM25 top-3:**
1. P006 [76.69] — 360° revolution of arc-of-ellipse produces self-intersecting solid
2. Gs056 [61.41] — SURFACE_OF_REVOLUTION of an ellipse around its own centre produces degenerate surface
3. Gn016 [56.81] — SURFACE_OF_REVOLUTION on ELLIPSE: basis curve becomes TRIMMED_CURVE over rational B-spline

**Novel?** NO — P006 is a near-exact match (score 76.69: "360° revolution of arc-of-ellipse produces
self-intersecting solid"). **HIT.**

---

### D24 — OCCT V8 STEP coordinate-system connection points import

**Pattern:** STEP AP242 file containing coordinate-system connection point entities (specific AP242
mechanism for linking coordinate systems between components), where OCCT prior to V8.0.0 (issue #779)
silently ignores these entities during import.

**Entities:** AP242 coordinate-system connection point entities, `PRODUCT_DEFINITION_SHAPE`,
`GEOMETRIC_REPRESENTATION_CONTEXT`

**Defect:** Connection point data absent after import; downstream assembly alignment that relies on
coordinate-system connection points fails silently.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/releases (V8.0.0, issue #779)

**BM25 top-3:**
(Query: "STEP AP242 coordinate system connection point entity import silently dropped missing")
1. A006 [~28] — Components collapse to (0,0,0) / placement transforms lost
2. Pmi082 [~22] — Saved-views and clipping planes lost on STEP read
3. A013 [~19] — STEP assembly reader returns success when reference files missing

**Novel?** YES — AP242 coordinate-system connection points are a distinct AP242 mechanism from NAUO
placements (A006), saved-views (Pmi082), and external references (A013). No existing fixture covers
the coordinate-system connection-point entity class being silently dropped on import. **NOVEL**
(AP242-specific entity type not in corpus; distinct from placement-transform loss).

---

### D25 — OCCT FreeBSD STEP: AP203 date/time generation crashes on older timezone declarations

**Pattern:** STEP file produced by OCCT on a FreeBSD system where the AP203 file header
`DATE_AND_TIME` entity's value is generated using the system's `timezone` global variable, which
has a different declaration signature in older FreeBSD libc, causing a compilation error or runtime
misbehavior in the date-generation code.

**Entities:** `DATE_AND_TIME` (STEP header), AP203 file header

**Defect:** STEP writer fails to generate a valid file header on FreeBSD; exported STEP files have
malformed header date fields; fixed in V8.0.0.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/releases (V8.0.0 release note: "AP203 default
date/time generation now handles older FreeBSD `timezone` declarations safely")

**BM25 top-3:**
(Query: "STEP file header DATE_AND_TIME entity invalid malformed on FreeBSD export platform")
1. Le023 [~32] — Locale-dependent decimal separator inside numeric attribute
2. Ad091 [~25] — Crash on STEP file from non-C locale
3. Wr007 [~23] — Locale-sensitive decimal separator emitted

**Novel?** YES — The defect is a platform-specific (FreeBSD) STEP header date/time generation failure,
not a locale-separator issue. The `DATE_AND_TIME` header entity with a malformed value due to
platform-dependent `timezone` API divergence is a distinct input pattern from locale-decimal
separator bugs. No existing fixture targets "STEP file produced on FreeBSD with malformed DATE_AND_TIME
header entity due to platform `timezone` declaration mismatch." **NOVEL** (STEP header DATE_AND_TIME
platform-specific malformation; different from locale/decimal class).

---

### D26 — FreeCAD STEP export: export crash since version 1.0.2 for STL-to-STEP workflow

**Pattern:** STEP file export fails entirely in FreeCAD 1.0.2+ when the input model was created from
an imported STL file, where a `Part::Feature` derived from the STL mesh cannot be serialized to STEP;
the export that worked in 1.0.1 now throws an exception.

**Entities:** Model-level (no STEP entities produced); `Part::Feature`, mesh-to-solid result

**Defect:** STEP export throws an exception with no output file produced; regression from 1.0.1 to
1.0.2; STL-to-solid-to-STEP workflow breaks.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/23511

**BM25 top-3:**
1. Hea016 [~40] — Empty solid from STEP export of complex body despite STL succeeding
2. A088 [~28] — Empty assembly causes writer to throw
3. Bo001 [~25] — Outer shell of solid is empty

**Novel?** NO — A088 and Hea016 cover the "STEP writer exception / empty output" pattern. **HIT.**

---

### D27 — OCCT STEP: std::string_view type-name lookups in RWStepAP214 using non-standard hasher

**Pattern:** STEP AP214 file imported by an OCCT build where the `RWStepAP214` entity type-name
dispatch table uses a `std::unordered_map` with default `std::hash<std::string_view>`, which on
some C++ standard library implementations (e.g., MSVC 2019) produces hash collisions for common
STEP entity type names, causing random entity recognition failures.

**Entities:** Any AP214 entity (recognition failure is type-agnostic)

**Defect:** Random "entity not recognized" errors for standard AP214 entities on affected platforms;
fixed in V8.0.0-rc5 with a custom hasher (#888).

**Source:** https://github.com/Open-Cascade-SAS/OCCT/releases (V8.0.0-rc5, issue #888)

**BM25 top-3:**
(Query: "STEP AP214 entity type name hash collision unordered_map recognition failure platform dependent")
1. Le023 [~28] — Locale-dependent parsing
2. Pf003 [~22] — 50-second read on 20 MB STEP
3. Ad091 [~20] — Crash on STEP from non-C locale

**Novel?** YES — A hash-collision in the entity type-dispatch table causing random entity recognition
failures on specific C++ standard library implementations is a distinct defect from locale issues,
cycle-detection, and parsing bugs. No existing fixture covers platform-dependent entity-type recognition
failure due to hash collision in the AP214 type table. **NOVEL** (API/platform defect but manifests as
"STEP file whose entity types are randomly mis-classified on affected platforms"; distinct from any
existing entry).

---

### D28 — FreeCAD STEP: import of edges fails when compound-merge option is disabled (coverage validation)

Note: This defect was already mined in Wave-4 and entered corpus as a HIT against P017. **Skip —
already counted in wave-4.**

---

### D29 — STEP file with FreeCAD BRep geometry validation failure: faces 288–734 all invalid after export

**Pattern:** STEP file produced by FreeCAD 1.1.0 from a complex extruded body where the export
produces `ADVANCED_FACE` entities (faces 288–734) with edge-curve geometry that does not lie on
the host surface within tolerance; the model validates in FreeCAD but the STEP file has systematic
edge-to-face tolerance violations across all complex-boolean-result faces.

**Entities:** `ADVANCED_FACE`, `EDGE_CURVE`, `B_SPLINE_SURFACE_WITH_KNOTS`, `PCURVE`

**Defect:** All faces in the latter portion of the STEP file fail geometry validation; downstream
tools (Rhino, Fusion 360) report "invalid geometry"; slicers reject the file.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/21216

**BM25 top-3:**
1. P014 [44.37] — PCURVE start point shifted in V from 3D EDGE_CURVE lift
2. P021 [33.90] — Edge-curve geometry mismatches face geometry within tolerance
3. Gs030 [~28] — Edge geometry inconsistent with adjacent faces' actual intersection

**Novel?** NO — This is the same source as D07 (different description focus). Merged with D07.
**Skip — duplicate angle on D07.**

---

### D30 — OCCT STEP: STEP file import fails when xstep.cascade.unit M (metre) — bounding box infinite

**Pattern:** Same as D03. **Skip — duplicate.**

---

## Unique Novel Count

Eliminating the merged/skipped entries above, the unique defects counted are D01 through D27 minus
D22 (merged with D13), D28 (already in wave-4), D29 (same source as D07), and D30 (duplicate of D03).

This yields **25 unique defects** evaluated, with the following novelty verdicts:

---

## Novelty Summary Table

| ID | Short name | Novel? |
|----|-----------|--------|
| D01 | CONICAL_SURFACE regression: null tessellation OCCT 7.8 | **YES** |
| D02 | SolidWorks STEP: origin displaced + colors lost on OCCT re-export | NO — A068/Xp025 |
| D03 | xstep.cascade.unit M causes infinite bounding box | NO — N015 |
| D04 | SolidWorks RECTANGULAR_TRIMMED_SURFACE → negative-weight NURBS crash | **YES** |
| D05 | FreeCAD revolution feature exported as inverted pocket | NO — P023/Tsh052 |
| D06 | FreeCAD lettering solid: 42 missing faces on STEP export | NO — Hea016 |
| D07 | FreeCAD STEP export: 200+ invalid curve on surface errors round-trip | NO — P021/P014 |
| D08 | CadQuery Boolean subtraction inverted — cut as protrusion | NO — Wr036/Wr054 |
| D09 | OCCT STEPCAFControl_Writer double-free under concurrent Transfer | **YES** |
| D10 | Non-standard: MANIFOLD_SOLID_BREP with OPEN_SHELL child | NO — Tsh001 |
| D11 | Non-standard: B_SPLINE_CURVE knot multiplicity > degree | NO — Xp042 |
| D12 | Non-standard: NAUO referencing PRODUCT_DEFINITION_SHAPE | NO — A009/Ad078 |
| D13 | Non-standard: GEOMETRIC_SET with non-geometric children | NO — M051 |
| D14 | FreeCAD STEP export: empty STEP file despite valid geometry | NO — Hea016 |
| D15 | OCCT STEPCAFControl_Writer crash in writeColors on null shape | NO — P028/Wr048 |
| D16 | CATIA V5 multi-file STEP assembly: external refs missing in Inventor | NO — A013 |
| D17 | Rhino untrimmed plane → trimmed B-spline on re-import (no pcurves) | NO — Gs024 |
| D18 | OCCT V8 PROPERTY_DEFINITION metadata invisible to V7 readers | **YES** |
| D19 | Small cylindrical cut absent from STEP/STL export | NO — tolerance-collapse class |
| D20 | STEPCAFControl_Reader hang on cyclic MAPPED_ITEM | NO — Pf036 |
| D21 | Onshape micro-SURFACE_OF_REVOLUTION: faulty topology on self-import | **YES** |
| D23 | FreeCAD ellipse-arc X-axis revolution: doubled solid in STEP | NO — P006 |
| D24 | AP242 coordinate-system connection point entity silently dropped | **YES** |
| D25 | FreeBSD DATE_AND_TIME header entity malformed via timezone API | **YES** |
| D27 | RWStepAP214 hash collision: entity type randomly mis-classified | **YES** |

**Novel count: 7 / 25 = 28.0%**

---

## Novelty Rate Comparison

| Wave | Sources | Defects sampled | Novel count | Novelty rate |
|------|---------|----------------|-------------|-------------|
| Wave 1 | OCCT/FreeCAD/CadQuery (early FOSS) | ~130 | ~32 | 24.6% |
| Wave 2 | OCE/FreeCAD-extended/KiCad | ~120 | ~13 | 10.5% |
| Wave 3 | KiBot/Blender-addon/deeper FOSS | ~100 | ~9 | 9.3% |
| Wave 4 | HOOPS Exchange / Inventor / OCCT-new / Academic | 35 | 12 | 34.3% |
| **Wave 5** | **FreeCAD-new / OCCT-new / OCCT V8 / non-standard STEP thread** | **25** | **7** | **28.0%** |

Wave-5 remains above the FOSS saturation floor (9–10%). The novelty rate dropped from 34.3% (wave-4)
to 28.0% (wave-5), which is expected as wave-5 mines sources adjacent to wave-4's commercial-tracker
territory rather than genuinely new territory. Novel defects skew toward:
1. OCCT version-specific regressions (D01 cone tessellation, D09 writer concurrent crash)
2. AP242-specific new entity classes (D24 coordinate-system connection points)
3. Platform-specific STEP writer bugs (D25 FreeBSD date/time)
4. New V8 cross-version compatibility gaps (D18 PROPERTY_DEFINITION metadata)
5. Micro-geometry boundary conditions (D21 Onshape sub-resolution SURFACE_OF_REVOLUTION)
6. Platform hash-collision in type dispatch (D27 RWStepAP214 hasher)

---

## DEFERRED List — Novel defects ready for B4.5b fixture synthesis

### DEF-M: CONICAL_SURFACE tessellation regression — null triangulation in OCCT 7.8+ (D01)

STEP file with a single `CLOSED_SHELL` containing a truncated cone `ADVANCED_FACE` on a `CONICAL_SURFACE`
with R_bottom = 15 mm, R_top = 5 mm, height = 20 mm, semi_angle ≈ 0.464 rad. The face should satisfy
`checkshape` with no errors. The defect is that OCCT 7.8.0–7.9.x silently returns null triangulation
from `BRepMesh_IncrementalMesh`; OCCT 7.6.0 tessellates correctly. Encode a complete
`MANIFOLD_SOLID_BREP` with: (a) `CONICAL_SURFACE` lateral face, (b) two `PLANE` cap faces. Expected
tier-3: 3 faces, all with non-null triangulation; the failure exhibits as 0 triangles on the cone face
with the OCCT version specified. Source: https://github.com/Open-Cascade-SAS/OCCT/issues/572.
Confidence: HIGH — entity-level encoding is clear; this tests a specific BRepMesh regression.

### DEF-N: SolidWorks RECTANGULAR_TRIMMED_SURFACE with negative NURBS weights (D04)

STEP file encoding a `BOUNDED_SURFACE` face using `RECTANGULAR_TRIMMED_SURFACE` whose underlying
`B_SPLINE_SURFACE_WITH_KNOTS` has at least one negative pole weight when evaluated by BRepBuilderAPI_
NurbsConvert. The synthesis must encode a `RECTANGULAR_TRIMMED_SURFACE` wrapping a `B_SPLINE_SURFACE
_WITH_KNOTS` whose weight vector contains a negative value (e.g., -0.15) at a specific pole, inserted
into an `ADVANCED_FACE` context. Expected: OCCT import raises an exception or returns null shape on
the face containing the negative weight. This fixture synthesizes the defect reported from SolidWorks
exports; note the STEP writer is NOT SolidWorks — we synthesize the pattern from the description.
Source: https://dev.opencascade.org/content/crash-step-import-solidworks. Confidence: HIGH — entity
encoding is straightforward; weight vector is directly specified in STEP.

### DEF-O: OCCT V8 PROPERTY_DEFINITION string metadata invisible to V7 readers (D18)

STEP AP214 file containing a product with `PROPERTY_DEFINITION` + `PROPERTY_DEFINITION_REPRESENTATION`
+ `DESCRIPTIVE_REPRESENTATION_ITEM` chain encoding a string metadata attribute (e.g., material name
"Aluminum 6061"). The file must also have a valid geometry (minimal cube `MANIFOLD_SOLID_BREP`) to
distinguish geometry-load success from metadata-read failure. Expected: geometry loads correctly under
any reader; the `DESCRIPTIVE_REPRESENTATION_ITEM` string value is readable under OCCT V8 `UserDefinedAttributes`
API but silently unavailable under V7.x readers (no error). Source: https://github.com/Open-Cascade-SAS/OCCT/releases
(V8.0.0 issue #634). Confidence: HIGH — entity chain is precisely specified in AP214 spec; synthesis
from pattern is clean.

### DEF-P: Onshape micro-geometry SURFACE_OF_REVOLUTION faulty topology on self-import (D21)

STEP file containing a `CLOSED_SHELL` with `ADVANCED_FACE` entities on a `SURFACE_OF_REVOLUTION`
where the profile curve is a `TRIMMED_CURVE` over a circular arc of radius ≈ 0.002 mm (2 microns)
revolved 360° around the Z axis. The `VERTEX_POINT` coordinates are near-coincident (distance < 1e-6
m). Expected: the file may load (small but non-zero geometry) or produce a "faulty topology" error on
import; `checkshape` should flag degenerate edges or near-coincident vertices. Source:
https://forum.onshape.com/discussion/22945/step-file-export-import-bug. Confidence: MEDIUM — the
exact tolerance threshold for "too small" is implementation-dependent; the fixture demonstrates the
class but requires oracle verification to establish whether OCCT passes or fails.

### DEF-Q: AP242 coordinate-system connection point entity silently dropped (D24)

STEP AP242 file containing a `PRODUCT_DEFINITION_SHAPE` linked to a coordinate-system connection
point via the AP242 `COORDINATE_SYSTEM_CONNECTION_POINT` entity (or the specific AP242 mechanism for
coordinate-system links between assembly components). The file must include a valid geometry and a
product structure, with the connection-point entity present but not linked to any V7-recognizable path.
Expected: geometry loads; connection-point data absent under OCCT 7.x but readable under OCCT V8+.
Source: https://github.com/Open-Cascade-SAS/OCCT/releases (V8.0.0 issue #779). Confidence: MEDIUM
— requires AP242 schema knowledge to correctly encode the connection-point entity chain; needs oracle
verify against V8 reader.

### DEF-R: STEP header DATE_AND_TIME entity malformed on FreeBSD (platform-specific) (D25)

STEP AP203 file with a FILE_DESCRIPTION / FILE_NAME header where the `DATE_AND_TIME` field is produced
by code that calls FreeBSD's `timezone` global variable with a declaration that differs from POSIX
(`long timezone` vs `extern long timezone`), producing either a garbage value or compilation failure.
The synthesized fixture would have an explicitly malformed `DATE_AND_TIME` value in the STEP header
(e.g., a negative or out-of-range year/month/day) to test that consumers tolerate malformed header
dates without crash. Expected: geometry-reading proceeds despite invalid header date; strict parsers
may emit a warning. Source: https://github.com/Open-Cascade-SAS/OCCT/releases (V8.0.0). Confidence:
MEDIUM — the STEP header entity is rarely exercised by corpus; a malformed DATE_AND_TIME is a new
fixture class.

### DEF-S: RWStepAP214 entity type hash collision — random entity mis-classification (D27)

STEP AP214 file containing a sequence of entities where two common type names (e.g.,
`FACE_OUTER_BOUND` and `ADVANCED_FACE`) collide in the default `std::unordered_map<std::string_view>`
hash table on a specific compiler/STL implementation, causing one entity type to be misidentified as
the other. The synthesized fixture must include both entity types interleaved to stress-test the
dispatch table. Expected: all entities recognized correctly (the defect is platform/implementation-
dependent and would only fail on affected toolchains). Source: https://github.com/Open-Cascade-SAS/OCCT/releases
(V8.0.0-rc5 issue #888). Confidence: LOW — this is an implementation-level defect, not a STEP file
defect; synthesizing a file-level fixture may not reproduce the hash collision since it depends on the
C++ STL implementation. More appropriate as an API test than a corpus fixture. **Defer with caveat.**

---

## Notes for B4.5b Fixture Synthesis

- DEF-R (FreeBSD DATE_AND_TIME): focus on the STEP header malformed-date tolerance class rather than
  the FreeBSD-specific cause; good "header fault tolerance" fixture.
- DEF-S (hash collision): API-level defect, not file-level; recommend deferring to API test harness
  rather than corpus entry, similar to wave-4's DEF-L (thread-safety).
- DEF-M (cone tessellation): highest confidence for synthesis; entity encoding is simple and well-
  understood; the fixture will exercise BRepMesh on a pure CONICAL_SURFACE face.
- DEF-N (negative NURBS weights): straightforward synthesis; the weight array value is directly
  written in the STEP entity; high-confidence.
- DEF-O (PROPERTY_DEFINITION metadata): clean synthesis; requires AP214 PROPERTY_DEFINITION chain;
  useful cross-version compatibility test.
- High-confidence synthesis targets: DEF-M, DEF-N, DEF-O.
- Medium-confidence (needs oracle verify): DEF-P, DEF-Q, DEF-R.
- Low-confidence / API-level (not file-level): DEF-S.

---

## Wave Trend Analysis

```
Wave 1: 24.6%  ████████████████████████░
Wave 2: 10.5%  ██████████░
Wave 3:  9.3%  █████████░
Wave 4: 34.3%  ██████████████████████████████████░  ← commercial pivot
Wave 5: 28.0%  ████████████████████████████░        ← adjacent territory
```

The wave-4 commercial-pivot produced a major novelty spike. Wave-5, mining the same commercial
territory more deeply (OCCT V8 release notes, FreeCAD 2024–2025 issues, non-standard STEP forum
thread), stays elevated at 28% — significantly above the FOSS saturation floor. The novel defects
in wave-5 are more implementation-specific (version regressions, platform dependencies, AP242 v8
extensions) rather than file-structure defects, suggesting the low-hanging file-structure fruit is
largely cataloged and future novelty will require AP242 deep dives, commercial-kernel-specific
behavioral gaps, and micro-geometry boundary conditions.

---

## Appendix: Source URLs

1. OCCT GitHub Issues (cone tessellation): https://github.com/Open-Cascade-SAS/OCCT/issues/572
2. OCCT GitHub Issues (origin/color SolidWorks): https://github.com/Open-Cascade-SAS/OCCT/issues/541
3. OCCT GitHub Issues (metre unit infinite bbox): https://github.com/Open-Cascade-SAS/OCCT/issues/512
4. OCCT dev forum (SolidWorks RECTANGULAR_TRIMMED crash): https://dev.opencascade.org/content/crash-step-import-solidworks
5. FreeCAD Issue #10736 (revolution as pocket): https://github.com/FreeCAD/FreeCAD/issues/10736
6. FreeCAD Issue #20588 (missing lettering faces): https://github.com/FreeCAD/FreeCAD/issues/20588
7. FreeCAD Issue #21216 (200+ invalid curve on surface): https://github.com/FreeCAD/FreeCAD/issues/21216
8. CadQuery Issue #697 (boolean subtraction inverted): https://github.com/CadQuery/cadquery/issues/697
9. CadQuery Issue #1551 (small cut absent from STEP): https://github.com/CadQuery/cadquery/issues/1551
10. OCCT V8.0.0 release notes: https://github.com/Open-Cascade-SAS/OCCT/releases
11. OCCT dev forum (non-standard STEP behaviors): https://dev.opencascade.org/content/non-standard-step-behaviors
12. OCCT dev forum (cleanup crash debug): https://dev.opencascade.org/content/crash-cleanup-after-reading-step-file
13. FreeCAD Issue #18056 (writeColors crash on null shape): https://github.com/FreeCAD/FreeCAD/issues/18056
14. FreeCAD Issue #16292 (empty STEP export): https://github.com/FreeCAD/FreeCAD/issues/16292
15. FreeCAD Issue #23511 (STEP export fails since 1.0.2): https://github.com/FreeCAD/FreeCAD/issues/23511
16. FreeCAD Issue #14447 (ellipse arc X-axis revolution wrong): https://github.com/FreeCAD/FreeCAD/issues/14447
17. Autodesk Inventor forum (CATIA multi-file STEP assembly): https://forums.autodesk.com/t5/inventor-forum/step-ap214-assembly-exported-from-catia-v5-not-importing-as/td-p/5684874
18. Rhino McNeel discourse (untrimmed plane → trimmed on re-import): https://discourse.mcneel.com/t/step-export-import-strange-behavior/207799
19. Onshape forum (faulty topology on micro-geometry reimport): https://forum.onshape.com/discussion/22945/step-file-export-import-bug
20. OCCT V7.9.3 release (STEPCAFControl_Reader hang fix): https://dev.opencascade.org/content/open-cascade-technology-793-released
21. IfcOpenShell Issue #5363 (STEP export location issue): https://github.com/IfcOpenShell/IfcOpenShell/issues/5363
22. Rhino McNeel discourse (STEP import generates new surfaces): https://discourse.mcneel.com/t/rhino-step-file-import-export-issues/188406
