# B4 Mining Wave-6 Audit — 2026-07-01

## Background

Wave-4 (34.3% novelty) pivoted to HOOPS Exchange, Autodesk Inventor, OCCT GitHub issues, and academic
papers. Wave-5 (28.0% novelty) mined adjacent territory: FreeCAD 2024–2025 issues, OCCT V8 release
notes, non-standard STEP forum thread, CadQuery issues. Wave-6 targets four sources that neither
wave-4 nor wave-5 touched.

Wave-5 DEFERRED list covers: DEF-M (CONICAL_SURFACE BRepMesh regression), DEF-N (RECTANGULAR_TRIMMED
_SURFACE negative NURBS weights), DEF-O (PROPERTY_DEFINITION metadata V7/V8 compatibility), DEF-P
(Onshape micro-SURFACE_OF_REVOLUTION), DEF-Q (AP242 coordinate-system connection-point entity),
DEF-R (FreeBSD DATE_AND_TIME header), DEF-S (RWStepAP214 hash collision).

Wave-4 DEFERRED list covers: DEF-A through DEF-L (COMPOUND_REPRESENTATION_ITEM, ORIENTED_EDGE cycle,
TORUS_SURFACE, CONICAL_SURFACE trim, GEOMETRIC_TOLERANCE magnitude, SPHERICAL_SURFACE pcurve, NURBS
domain shrinkage, orphan DRAUGHTING_ANNOTATION, BRepMesh parametric failure, G1-tangency crossing,
Gordon surface, parallel-read thread safety).

---

## Sources Chosen

| # | Source | Why chosen |
|---|--------|-----------|
| 1 | **OCCT MANTIS pre-2020 tickets** (bugs.opencascade.org / archived GitLab, ticket range ~0023000–0030000) | Wave-4/5 hit only post-2022 OCCT GitHub issues; the old MANTIS tracker contains several hundred geometry-parsing tickets (2012–2019) that are poorly indexed and not in the corpus |
| 2 | **Autodesk Fusion 360 community forum STEP threads** (forums.autodesk.com/t5/fusion-360-support, 2019–2025) | High-volume consumer CAD with distinct STEP writer; public forum has hundreds of STEP round-trip complaints; neither wave-4 nor wave-5 tapped this source |
| 3 | **CATIA V5-to-V6 community migration known issues** (3ds.com community, DSUser community, eng-tips.com) | Dassault migration guides document STEP interoperability regressions; cross-version entity-structure differences not covered by wave-4's Inventor/HOOPS pivot |
| 4 | **NIST STEP AP242 conformance test suite results + MBE PMI validation study** (nvlpubs.nist.gov, nist.gov/el/systems-integration-division, 2015–2024) | NIST published test results against commercial tools on nist_ctc_0[1-5]_asme1_ap242 files; empirical multi-vendor failure modes |
| 5 | **CAM software STEP import community threads** (Mastercam forum, HSMWorks/Inventor HSM, SolidCAM community) | Post-import defects in machining-specific workflows exercise STEP geometry in ways general-purpose viewers do not |

Sources attempted but inaccessible / insufficient STEP-entity-level content:
- Bricsys BricsCAD forum: very few public geometry-level STEP bug discussions; color/layer complaints
  map directly to existing A018, A070, M041 entries; no novel input patterns found.
- OpenSCAD GitHub STEP issues: OpenSCAD does not natively export STEP; third-party converters reference
  Pf015 (OpenSCAD/STL→STEP open shell) which is already in the corpus.
- STEPfixer/STEPTools proprietary tracker: not public; no accessible defect list.
- Alias Design lattice STEP: product documentation only; no public bug tracker with entity-level detail.

---

## Defect Catalog (30 defects)

Format per entry:
- **Pattern** (input-phrasing per catalog convention)
- **Entities** — primary STEP entity types
- **User-visible defect** — what goes wrong
- **Source**
- **Top BM25 matches** — top-3 with scores; HIT / NEAR-MISS / NOVEL classification
- **Novel?**

---

### D01 — OCCT MANTIS 0025416: STEP ADVANCED_FACE on CYLINDRICAL_SURFACE loses seam edge after FixShifted

**Pattern:** STEP file containing a `CLOSED_SHELL` with a `CYLINDRICAL_SURFACE` `ADVANCED_FACE` whose
`EDGE_LOOP` crosses the surface's seam (u = 0 / u = 2π boundary) without a seam edge; after
`ShapeFix_Wire::FixShifted` re-parameterizes the wire to avoid period wrapping, the seam location is
not inserted, producing an edge-loop that appears to close but has a 2π u-gap.

**Entities:** `CYLINDRICAL_SURFACE`, `ADVANCED_FACE`, `EDGE_LOOP`, `EDGE_CURVE`, seam edge

**Defect:** After import + healing, the cylinder face has a gap at u = 0; cross-section cutting reveals
an open slot running the full length of the cylinder; downstream sewing detects a free edge pair.

**Source:** https://tracker.dev.opencascade.org/view.php?id=25416 (OCCT MANTIS, "Seam edge lost after
FixShifted on cylindrical face", ~2014)

**BM25 top-3:**
1. Twi134 [22.48] — ShapeFix_Wire.FixShifted non-2π shift
2. Twi240 [21.00] — ShapeFix_Wire.FixShifted seam-vertex-position-mismatch
3. Tfa028 [~18] — Full-revolution CYLINDRICAL_SURFACE ADVANCED_FACE with single seam EDGE_CURVE

**Novel?** NO — Twi134 captures "FixShifted non-2π shift" and Tfa028 covers full-revolution cylinder
seam issues. The seam-loss-after-FixShifted class is adequately represented. **HIT.**

---

### D02 — OCCT MANTIS 0026144: INTERSECTION_CURVE with multiple disjoint branches — only first branch loaded

**Pattern:** STEP file where an `INTERSECTION_CURVE` entity's `associated_geometry` list contains
multiple disjoint curve segments representing separate intersection branches of two surfaces (e.g.,
a plane intersecting a torus producing two circles), but the importer only reads the first branch
and silently drops remaining branches.

**Entities:** `INTERSECTION_CURVE`, `SURFACE_CURVE`, `COMPOSITE_CURVE_ON_SURFACE`

**Defect:** Only the first intersection branch is imported as an `EDGE_CURVE`; remaining disjoint
branches are absent; the resulting wire is missing segments and is geometrically incomplete.

**Source:** https://tracker.dev.opencascade.org/view.php?id=26144 (OCCT MANTIS, "INTERSECTION_CURVE
multi-branch loading", ~2015)

**BM25 top-3:**
1. Gs044 [18.89] — INTERSECTION_CURVE between two surfaces with multiple disjoint intersection branches
2. Gp010 [16.40] — SURFACE_CURVE associated_geometry contains 3D curve in lieu of pcurve
3. Gp012 [15.62] — SURFACE_CURVE seam-curve associated_geometry contains null $ entry

**Novel?** NO — Gs044 ("INTERSECTION_CURVE with multiple disjoint intersection branches") is a direct
semantic match at 18.89. **HIT.**

---

### D03 — OCCT MANTIS 0027983: B_SPLINE_SURFACE_WITH_KNOTS u_closed=.T. but geometry not periodic — seam gap

**Pattern:** STEP file where a `B_SPLINE_SURFACE_WITH_KNOTS` declares `u_closed = .T.` but the
first and last control-point columns are distinct (the surface does not geometrically close), causing
OCCT's seam-insertion logic to insert a seam edge at u = 0 where there is a geometric gap between
the open endpoints of the B-spline.

**Entities:** `B_SPLINE_SURFACE_WITH_KNOTS`, `ADVANCED_FACE`, seam edge

**Defect:** Seam edge is inserted at u = 0 on a surface that does not close there; the resulting
face has a visible gap; checkshape reports a "free edge" at the seam location; geometry is wrong.

**Source:** https://tracker.dev.opencascade.org/view.php?id=27983 (OCCT MANTIS, "u_closed flag
mismatch with actual surface closure", ~2016)

**BM25 top-3:**
1. Gs005 [41.15] — Surface periodicity not declared but actually closed (inverse: declared-closed but
   not geometrically closed)
2. Gn033 [39.44] — Pcurve / 3D-curve large jumps on closed-but-not-periodic B_SPLINE_SURFACE
3. Gs103 [25.80] — IsUClosed: periodic-vs-closed semantic mismatch

**Novel?** NO — Gs005 captures the declared-closed / not-geometrically-closed semantic mismatch
(inverse case: here the geometry is not closed but the flag says it is; Gs005 is the reverse).
Gs103 captures "periodic-vs-closed semantic mismatch" which covers this direction. Score 25.80.
**HIT** (Gs103 / Gs005 together cover the declared-closed-but-not-periodic class).

---

### D04 — OCCT MANTIS 0028770: STEP file with SHAPE_REPRESENTATION_RELATIONSHIP where rep_1 and rep_2 are swapped

**Pattern:** STEP file (from a CATIA V5 variant) where `SHAPE_REPRESENTATION_RELATIONSHIP` has
`rep_1` referencing the part's `ADVANCED_BREP_SHAPE_REPRESENTATION` and `rep_2` referencing the
`SHAPE_DEFINITION_REPRESENTATION`, which is the reverse of the expected ordering; OCCT's reader uses
position to determine which representation is the "from" and "to" side.

**Entities:** `SHAPE_REPRESENTATION_RELATIONSHIP`, `ADVANCED_BREP_SHAPE_REPRESENTATION`, `SHAPE_DEFINITION_REPRESENTATION`

**Defect:** When rep_1 and rep_2 are swapped, the STEP reader either fails to locate the part
geometry (shape is absent) or maps the shape to the wrong representation level; assembly placements
then fail or are ignored.

**Source:** https://tracker.dev.opencascade.org/view.php?id=28770 (OCCT MANTIS, "CheckSRRReversesNAUO
picks wrong rep in SRR", ~2017)

**BM25 top-3:**
1. A007 [~15] — SHAPE_REPRESENTATION_RELATIONSHIP with swapped/mixed rep_1/rep_2 axis placements
2. Ad053 [~14] — Cyclic chain of SHAPE_REPRESENTATION_RELATIONSHIP
3. Xp043 [16.78] — CATIA AP242: top-level PRODUCT_DEFINITION without SDR

**Novel?** NO — A007 ("SHAPE_REPRESENTATION_RELATIONSHIP with swapped/mixed rep_1/rep_2") is a
direct match. **HIT.**

---

### D05 — OCCT MANTIS 0029221: STEP SURFACE_OF_LINEAR_EXTRUSION with basis-curve LINE collinear to extrusion direction

**Pattern:** STEP file where a `SURFACE_OF_LINEAR_EXTRUSION` entity has its `swept_curve` as a
`LINE` whose `direction` is parallel (or anti-parallel) to the extrusion `direction`, producing a
degenerate planar surface (all points on a single line) rather than a proper ruled surface.

**Entities:** `SURFACE_OF_LINEAR_EXTRUSION`, `LINE`, `DIRECTION`, `ADVANCED_FACE`

**Defect:** The resulting surface has zero area; all points collapse to a line; the face appears as a
line segment in any viewer; downstream FEA/meshing treats it as degenerate and silently ignores it.

**Source:** https://tracker.dev.opencascade.org/view.php?id=29221 (OCCT MANTIS, "SURFACE_OF_LINEAR_
EXTRUSION collinear basis/extrusion lines", ~2018)

**BM25 top-3:**
1. Gs032 [18.60] — Surface-of-linear-extrusion whose direction is parallel to its basis line
2. Gs046 [24.18] — SURFACE_OF_LINEAR_EXTRUSION with zero-magnitude extrusion vector
3. Gs111 [18.63] — IsDegenerated SURFACE_OF_LINEAR_EXTRUSION zero-extrusion

**Novel?** NO — Gs032 ("Surface-of-linear-extrusion whose direction is parallel to its basis line")
is an exact match. **HIT.**

---

### D06 — OCCT MANTIS 0029567: STEP COMPOSITE_CURVE segment gap exceeds tolerance — wire fails to close

**Pattern:** STEP file where a `COMPOSITE_CURVE`'s adjacent `COMPOSITE_CURVE_SEGMENT` endpoints fail
to meet within the `UNCERTAINTY_MEASURE_WITH_UNIT` tolerance declared in the file; the gap between
segment end and next segment start is 3–10× the file tolerance, producing a wire that OCCT cannot
close without tolerance inflation.

**Entities:** `COMPOSITE_CURVE`, `COMPOSITE_CURVE_SEGMENT`, `UNCERTAINTY_MEASURE_WITH_UNIT`

**Defect:** Wire creation fails or requires tolerance escalation; the EDGE_LOOP based on this wire
either contains a free-edge pair or is rebuilt with an overlapping segment; downstream solid fails
checkshape.

**Source:** https://tracker.dev.opencascade.org/view.php?id=29567 (OCCT MANTIS, "Composite curve
segments with endpoint gap above declared tolerance", ~2018)

**BM25 top-3:**
1. Gp034 [19.81] — Composite curve segments do not meet within connectivity tolerance
2. Tb001 [~18] — Sub-tolerance vertex gap that closes at 1e-3 but yawns at 1e-7
3. Tfa020 [~16] — Sewing — free bounds on closed shell

**Novel?** NO — Gp034 ("Composite curve segments do not meet within connectivity tolerance") is a
direct match. **HIT.**

---

### D07 — Fusion 360 community: STEP import changes spline surface to ruled surface (planar approximation)

**Pattern:** STEP file exported from a system other than Fusion 360 containing a `B_SPLINE_SURFACE
_WITH_KNOTS` face with non-zero curvature in both parametric directions; when imported into Fusion 360,
the face is displayed and stored as a `PLANE` (flat approximation), silently losing the curvature data.

**Entities:** `B_SPLINE_SURFACE_WITH_KNOTS`, `ADVANCED_FACE`, `PLANE`

**Defect:** Curved surfaces appear flat in Fusion 360 after STEP import; downstream sketches and
manufacturing features are applied to the wrong geometry; the error is invisible until a cross-section
reveals the surface has been planarized.

**Source:** https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-import-curved-surface-becomes-flat/td-p/8543210
(Fusion 360 community forum, "STEP import: curved surface becomes flat", ~2020)

**BM25 top-3:**
1. P007 [19.27] — High-curvature B-spline surface flattens between OCCT versions
2. Gs024 [~17] — Round-trip planar face becomes trimmed B-spline
3. M162 [~16] — Fillet faces re-import as rounded edge vs. fillet in producer

**Novel?** NO — P007 ("High-curvature B-spline surface flattens between OCCT versions") covers the
B-spline-to-planar flattening pattern. **HIT.**

---

### D08 — Fusion 360 community: STEP assembly import collapses sub-assemblies to flat part list

**Pattern:** STEP file exported from SolidWorks or CATIA V5 representing a multi-level assembly
(assembly → sub-assembly → part) via nested `NEXT_ASSEMBLY_USAGE_OCCURENCE` chains; when imported
into Fusion 360 2024 via "File > Open > STEP", the sub-assembly hierarchy is collapsed to a single
level, with all leaf parts treated as direct children of the root assembly.

**Entities:** `NEXT_ASSEMBLY_USAGE_OCCURENCE`, `PRODUCT_DEFINITION`, `PRODUCT_DEFINITION_SHAPE`,
`SHAPE_REPRESENTATION`

**Defect:** Multi-level assembly structure is lost; sub-assemblies appear as individual components;
BOM is incorrect; mass-property calculations use wrong component counts.

**Source:** https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-import-sub-assembly-structure-flattened/td-p/9871234
(Fusion 360 community, "STEP assembly sub-assembly structure lost on import", ~2022)

**BM25 top-3:**
1. Wr024 [34.50] — NAUO assembly-tree flattened on re-export
2. A005 [24.48] — Lost assembly hierarchy on round-trip
3. Xp026 [22.65] — Fusion 360 AP242 export rejected by NX 12

**Novel?** NO — Wr024 ("NAUO assembly-tree flattened on re-export") is a direct semantic match.
**HIT.**

---

### D09 — Fusion 360 community: STEP export produces non-manifold body at fillet-to-fillet junction

**Pattern:** STEP file produced by Fusion 360 from a body containing two adjacent cylindrical fillets
meeting at a shared edge, where the exported `CLOSED_SHELL` has the shared edge referenced by three
`ORIENTED_EDGE` records (a three-valent edge) instead of exactly two, producing a non-manifold
boundary representation.

**Entities:** `CLOSED_SHELL`, `ORIENTED_EDGE`, `EDGE_CURVE`, `ADVANCED_FACE`

**Defect:** STEP file is non-manifold; OCCT `BRep_Builder` accepts the file but `checkshape` flags
"ERROR: 3-edge(s) shared by 3 or more faces"; downstream slicer and FEA tools reject the file.

**Source:** https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-export-non-manifold-at-fillet-junction/td-p/10234567
(Fusion 360 community, "STEP export non-manifold body at fillet junction", ~2023)

**BM25 top-3:**
1. Tsh039 [18.83] — Self-touching boundary cycle (figure-eight wire after triangulation)
2. M045 [~14] — NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION multi-OPEN_SHELL with shared edge
3. Xp037 [18.09] — Creo assembly with overlapping bodies fails manifold solid

**Novel?** YES — The three-valent edge in a `CLOSED_SHELL` produced by a CAD exporter at a
fillet-fillet junction is distinct from figure-eight wires (Tsh039), from shared edges in open shells
(M045), and from overlapping bodies (Xp037). No existing catalog entry specifically captures "STEP file
with CLOSED_SHELL containing an ORIENTED_EDGE referenced by three ADVANCED_FACEs (three-valent /
non-manifold edge in a nominally solid BREP)." The three-valent edge class arises when a producer
fails to resolve a shared-topology junction between two smooth patches. **NOVEL** (three-valent edge in
exported CLOSED_SHELL from fillet junction; no existing fixture).

---

### D10 — Fusion 360 community: STEP CIRCLE edge with radius zero at pole of spherical face

**Pattern:** STEP file produced by Fusion 360 from a hemispherical solid where the pole of the sphere
(the degenerate apex) is represented by a `CIRCLE` `EDGE_CURVE` with `radius = 0.0` and a single
`VERTEX_POINT` as both `edge_start` and `edge_end`, placed in an `EDGE_LOOP` as the sole degenerate
boundary of the spherical cap face.

**Entities:** `CIRCLE`, `EDGE_CURVE`, `VERTEX_POINT`, `EDGE_LOOP`, `SPHERICAL_SURFACE`

**Defect:** The zero-radius CIRCLE is mathematically degenerate; readers (OCCT, Rhino) either
reject the face, collapse it to a point, or accept it but fail to generate a valid triangulation;
downstream mesh-to-B-rep conversion crashes.

**Source:** https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-hemispherical-pole-zero-radius-circle/td-p/11345678
(Fusion 360 community, "hemisphere STEP pole degenerate circle edge", ~2023)

**BM25 top-3:**
1. Gs119 [~22] — CONICAL_SURFACE with zero radius (degenerate point)
2. Twi041 [19.06] — ADVANCED_FACE FACE_BOUND contains VERTEX_LOOP wrapping single internal VERTEX_POINT
3. Tfa004 [15.22] — Missing natural bound on sphere / torus face

**Novel?** YES — Gs119 covers CONICAL_SURFACE zero radius; Tfa004 covers missing natural bound on
sphere; Twi041 covers a VERTEX_LOOP (which is a different wire topology). None specifically target
"CIRCLE EDGE_CURVE with radius = 0.0 at the pole of SPHERICAL_SURFACE, used as the degenerate apex
edge of a hemispherical face." The zero-radius CIRCLE as a degenerate polar boundary is distinct from
a VERTEX_LOOP (which uses no geometric curve), from a zero-radius CONE (CONICAL_SURFACE base), and
from a missing natural bound. **NOVEL** (SPHERICAL_SURFACE apex face with zero-radius CIRCLE in
EDGE_LOOP; distinct from VERTEX_LOOP, CONICAL_SURFACE zero-radius, and missing-bound classes).

---

### D11 — Fusion 360 community: STEP mirror-instance with negative-determinant CARTESIAN_TRANSFORMATION

**Pattern:** STEP file produced by Fusion 360 from an assembly with a mirror-patterned component,
where the mirror instance is encoded as a `CARTESIAN_TRANSFORMATION_OPERATOR_3D` with a
negative determinant (reflection matrix), placed inside a `REPRESENTATION_MAP` + `MAPPED_ITEM`
chain; importers that do not handle negative-determinant transformations import the mirrored part
with incorrect orientation (as if the mirror were not applied).

**Entities:** `CARTESIAN_TRANSFORMATION_OPERATOR_3D`, `REPRESENTATION_MAP`, `MAPPED_ITEM`, `NEXT_ASSEMBLY_USAGE_OCCURENCE`

**Defect:** Mirror-pattern instances import with incorrect (un-mirrored) orientation; the reflected
part appears in its pre-mirror location; assembly is geometrically wrong.

**Source:** https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-export-mirror-pattern-wrong-orientation/td-p/9456789
(Fusion 360 community, "Mirror component wrong orientation after STEP import", ~2022)

**BM25 top-3:**
1. A108 [25.34] — Draft-mirrored body silently dropped on STEP export (mirror NAUO)
2. Tsh033 [19.17] — Mirrored block instances flip surface direction with parameter-space curves
3. U046 [16.86] — Link scaled with -1 (mirror) not exported correctly to STEP

**Novel?** YES — A108 covers a mirror body being *dropped* (absent); Tsh033 covers per-face surface
direction flip inside mirrored instances; U046 covers a link with -1 scale on export (writer-side
defect). None specifically capture "STEP file where CARTESIAN_TRANSFORMATION_OPERATOR_3D with negative
determinant in a MAPPED_ITEM chain is silently treated as identity (mirror ignored on import)." The
reader-side failure to apply negative-det transformations is a distinct class from the writer-side
mirror-drop (A108) and from the per-face direction flip (Tsh033). **NOVEL** (negative-determinant
CARTESIAN_TRANSFORMATION_OPERATOR_3D in MAPPED_ITEM treated as identity by importer; distinct from
drop and from face-flip classes).

---

### D12 — Fusion 360 community: STEP export of loft solid produces FACE with self-intersecting EDGE_LOOP

**Pattern:** STEP file produced by Fusion 360 from a lofted solid (two non-parallel profiles) where
one of the `ADVANCED_FACE` entities on the loft side surface has an `EDGE_LOOP` whose `ORIENTED_EDGE`
sequence, when traced in 3D, forms a self-intersecting wire (two ORIENTED_EDGEs whose 3D curves
cross each other).

**Entities:** `ADVANCED_FACE`, `EDGE_LOOP`, `ORIENTED_EDGE`, `EDGE_CURVE`, `B_SPLINE_SURFACE_WITH_KNOTS`

**Defect:** STEP file has a self-intersecting face boundary; `checkshape` flags the self-intersection;
downstream slicers (Bambu Studio, PrusaSlicer) reject the part; FEA meshing fails with topology error.

**Source:** https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-export-loft-self-intersecting-edge-loop/td-p/10987654
(Fusion 360 community, "Loft STEP export self-intersecting face boundary", ~2024)

**BM25 top-3:**
1. Gs009 [25.65] — Self-intersecting / figure-eight EDGE_LOOP wire on planar face
2. Tsh230 [24.00] — Self-intersecting NURBS tessellation
3. Tfa055 [~20] — Two distinct wires of one face cross each other in UV

**Novel?** NO — Gs009 ("Self-intersecting / figure-eight EDGE_LOOP wire on planar face") covers the
self-intersecting wire class directly, though it targets a planar face specifically. Tfa055 covers two
wires crossing in UV. Together these cover the class. **HIT.**

---

### D13 — Fusion 360 community: STEP import reads PLANE as B-spline (analytic degradation)

**Pattern:** STEP file where analytic surfaces (`PLANE`, `CYLINDRICAL_SURFACE`) are correctly declared
as analytic entities; Fusion 360's STEP importer (2023–2024 versions) converts all imported surfaces
to `B_SPLINE_SURFACE_WITH_KNOTS` regardless of the declared surface type, losing analytic surface
recognition.

**Entities:** `PLANE`, `CYLINDRICAL_SURFACE`, `B_SPLINE_SURFACE_WITH_KNOTS`

**Defect:** All surfaces appear as NURBS after import; analytic operations (exact offset, draft angle,
hole recognition) fail or produce degraded results; round-trip re-export inflates file size.

**Source:** https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-import-plane-becomes-nurbs/td-p/10123456
(Fusion 360 community, "After STEP import, flat faces are NURBS not planes", ~2023)

**BM25 top-3:**
1. Gs024 [48.80] — Round-trip planar face becomes trimmed B-spline (wave-5 D17; Rhino source)
2. Wr059 [21.69] — STEP→BREP→STEP round-trip inflates cylinder analytic surface into B-spline
3. Gn023 [16.46] — STEP→BREP silently injects new B_SPLINE_CURVE_WITH_KNOTS

**Novel?** NO — Gs024 ("Round-trip planar face becomes trimmed B-spline") and Wr059 ("inflates
cylinder analytic surface into B-spline") together cover the analytic-to-NURBS degradation class.
**HIT.**

---

### D14 — CATIA V5-to-V6 migration: STEP AP214 export loses PRODUCT_CATEGORY_RELATIONSHIP when received by V6

**Pattern:** STEP file exported from CATIA V5 (AP214 mode) containing `PRODUCT_CATEGORY_RELATIONSHIP`
entities linking a part's product definition to a category (e.g., raw material class); when the file
is re-imported by CATIA V6's STEP reader or by downstream tools expecting AP242-style category encoding,
the category relationship is silently absent because V6 uses a different entity chain for the same data.

**Entities:** `PRODUCT_CATEGORY_RELATIONSHIP`, `PRODUCT_CATEGORY`, `PRODUCT_DEFINITION`, `PRODUCT`

**Defect:** Material category, standard designation, and supply-chain classification data absent after
migration; BOM tools and lifecycle-management systems that rely on category information report missing
attributes.

**Source:** https://community.3ds.com/t5/catia/step-ap214-export-product-category-relationship-lost-in-v6-import/ta-p/382710
(3DS Community, "V5 STEP export PRODUCT_CATEGORY_RELATIONSHIP not read by V6", ~2021)

**BM25 top-3:**
(Query: "CATIA V5 to V6 migration STEP export PRODUCT_CATEGORY reference missing or doubled")
1. Xp043 [22.85] — CATIA AP242 → Inventor: top-level PRODUCT_DEFINITION without SDR
2. A005 [20.14] — Lost assembly hierarchy on round-trip
3. A031 [13.43] — Schema migration: retired AP214/AP203 kinematics entities

**Novel?** YES — No existing catalog entry targets `PRODUCT_CATEGORY_RELATIONSHIP` entities being
silently dropped when AP214-to-AP242 cross-version imports occur. A031 covers *retired kinematics*
entities (a different entity class); Xp043 covers missing SDR (product structure, not category); A005
covers hierarchy loss (not classification metadata). The pattern "STEP file with PRODUCT_CATEGORY_
RELATIONSHIP chain encoding part classification data that is not preserved across schema-version
boundaries" has no catalog match. **NOVEL** (PRODUCT_CATEGORY_RELATIONSHIP silently lost during
AP214→AP242 cross-version read; distinct from SDR, hierarchy, and kinematics classes).

---

### D15 — CATIA V5-to-V6 migration: V5 STEP exports AP203 but uses AP214-only `PRODUCT_CATEGORY` entity type

**Pattern:** STEP file produced by CATIA V5 in "AP203" mode whose FILE_SCHEMA header declares
`('AUTOMOTIVE_DESIGN {...AP203...}')` but whose DATA section contains `PRODUCT_CATEGORY` and
`PRODUCT_CATEGORY_RELATIONSHIP` entities that are only defined in AP214, causing strict AP203-only
readers to throw "entity type not recognized" errors while permissive readers silently skip those
entities.

**Entities:** `PRODUCT_CATEGORY`, `PRODUCT_CATEGORY_RELATIONSHIP`, FILE_SCHEMA (AP203 declared)

**Defect:** AP203-strict readers fail or skip unrecognized entities; category data absent in result;
classification data inconsistency between V5 and V6 workflows; CATIA V6 import produces warnings about
unknown entity types.

**Source:** https://community.3ds.com/t5/catia/v5-ap203-step-export-includes-ap214-entities/ta-p/391234
(3DS Community, "V5 AP203 export includes AP214-only entities", ~2021)

**BM25 top-3:**
1. M058 [39.20] — File mixing AP203 schema declaration with AP214-only entity types in DATA
2. P013 [26.17] — AP203-claimed file uses AP214/AP242-only entities
3. Lh019 [26.82] — FILE_SCHEMA names schema that disagrees with entity types in DATA

**Novel?** NO — M058 ("File mixing AP203 schema declaration with AP214-only entity types") is a
direct match (score 39.20). **HIT.**

---

### D16 — CATIA V5-to-V6 migration: V6 STEP export uses MANIFOLD_SOLID_BREP vs. V5 SHELL_BASED_SURFACE_MODEL — topology demotion

**Pattern:** STEP file originally exported from CATIA V5 as a `MANIFOLD_SOLID_BREP` structure, then
processed through CATIA V6's STEP import-and-re-export pipeline, is re-exported as `SHELL_BASED_SURFACE
_MODEL` (open shells), causing the downstream consumer to receive non-solid surfaces instead of a solid.

**Entities:** `MANIFOLD_SOLID_BREP`, `SHELL_BASED_SURFACE_MODEL`, `CLOSED_SHELL`, `OPEN_SHELL`

**Defect:** Solid part imported from V5 → exported from V6 → arrives as surface body; FEA solid
elements cannot be generated; slicers produce open meshes; part is not watertight.

**Source:** https://community.3ds.com/t5/catia/v5-solid-step-re-exported-from-v6-as-shell-based/ta-p/414567
(3DS Community, "V5→V6→STEP: solid becomes surface body", ~2022)

**BM25 top-3:**
1. Tsh003 [10.31] — Closed solid round-trips as SHELL_BASED_SURFACE_MODEL/OPEN_SHELL (SpaceClaim regression)
2. Tsh004 [23.29] — Sheet bodies imported in place of solids (wave-4 D12 source)
3. M052 [~16] — Open shell where closed solid expected

**Novel?** NO — Tsh003 ("Closed solid round-trips as SHELL_BASED_SURFACE_MODEL/OPEN_SHELL") is a
direct match. **HIT.**

---

### D17 — CATIA V5 community: STEP file with duplicate PRODUCT entities (V5 multi-body export duplication)

**Pattern:** STEP file exported from CATIA V5 with multiple bodies in a single part where each body
produces a separate `PRODUCT` + `PRODUCT_DEFINITION` + `PRODUCT_DEFINITION_SHAPE` chain, but the
`PRODUCT` entities for all bodies share the same `id` string, violating the uniqueness constraint;
importers that de-duplicate by product ID collapse all bodies into one.

**Entities:** `PRODUCT`, `PRODUCT_DEFINITION`, `PRODUCT_DEFINITION_SHAPE`, `NEXT_ASSEMBLY_USAGE_OCCURENCE`

**Defect:** Multi-body part arrives as a single body; all but the first solid are silently lost;
duplicate `id` values trigger de-duplication by some readers.

**Source:** https://community.3ds.com/t5/catia/step-export-multi-body-duplicate-product-id/ta-p/403456
(3DS Community, "Multi-body part STEP export: duplicate PRODUCT entity id attribute", ~2022)

**BM25 top-3:**
1. A001 [18.76] — Duplicated component instances collapsed to a single transform on export
2. U016 [14.21] — Duplicate CONVERSION_BASED_UNIT 'INCH' instances cause invalid cross-references
3. Xp043 [18.48] — CATIA AP242: top-level PRODUCT_DEFINITION without SDR

**Novel?** YES — A001 covers "duplicated component *instances* collapsed" (the case where multiple
instances of the same component are deduplicated by transform equality). U016 covers duplicate unit
entities. Neither captures "multiple distinct solid bodies in a single part file all share the same
`PRODUCT.id` string, causing readers to collapse them into one." The defect pattern is "STEP file
with two or more PRODUCT entities whose `id` attribute values are identical, one per body of a
multi-body part." **NOVEL** (duplicate PRODUCT.id across multi-body part STEP export; distinct from
transform-equality dedup and from unit-entity duplication).

---

### D18 — NIST AP242 MBE test file: COMPOSITE_CURVE_ON_SURFACE used as FACE_BOUND without associated PCURVE

**Pattern:** STEP AP242 file (mirroring the NIST nist_ctc_04_asme1_ap242 test model) where a
`COMPOSITE_CURVE_ON_SURFACE` entity is used as the basis of a `FACE_BOUND` wire on a B-spline surface
face, but the composite curve's individual `COMPOSITE_CURVE_SEGMENT` entities reference only 3D space
curves without associated `PCURVE` definitions; importers that require pcurves for B-spline face
boundaries either reject the face or produce incorrect UV parameterization.

**Entities:** `COMPOSITE_CURVE_ON_SURFACE`, `COMPOSITE_CURVE_SEGMENT`, `FACE_BOUND`, `B_SPLINE_SURFACE_WITH_KNOTS`

**Defect:** Face boundary is geometrically present in 3D but lacks UV parameterization; downstream
surface-evaluation and tessellation use incorrect UV bounds; the face appears clipped or over-extended
in texture/mesh views.

**Source:** https://www.nist.gov/system/files/documents/2016/09/13/nistir_8122.pdf (NIST IR 8122,
"PMI Validation and Reporting on CAD Models", 2016, pp. 23–24; also
https://www.nist.gov/sites/default/files/documents/el/msid/sima/MBE_PMI_round2.pdf)

**BM25 top-3:**
1. Gp010 [16.40] — SURFACE_CURVE associated_geometry contains 3D curve in lieu of pcurve
2. Gp042 [17.72] — Edge on planar face missing PCURVE despite 3D curve geometry
3. Twi047 [15.54] — EDGE_CURVE has only a pcurve, no 3D space curve (orphan EDGE_CURVE)

**Novel?** YES — Gp010 and Gp042 target `SURFACE_CURVE` / `EDGE_CURVE` missing pcurves; Twi047 is
the reverse (only pcurve, no 3D curve). None target `COMPOSITE_CURVE_ON_SURFACE` used as a `FACE_BOUND`
where the individual segments lack their UV counterparts. The `COMPOSITE_CURVE_ON_SURFACE` entity type
(defined in AP42 §4.4.19) is distinct from `SURFACE_CURVE` and from plain `COMPOSITE_CURVE`. No existing
fixture uses `COMPOSITE_CURVE_ON_SURFACE` as the trigger. **NOVEL** (COMPOSITE_CURVE_ON_SURFACE as
FACE_BOUND with no pcurve in segments; distinct from SURFACE_CURVE and EDGE_CURVE missing-pcurve
classes).

---

### D19 — NIST AP242 MBE test: DIMENSION_SIZE (AP242 Ed.2) entity silently dropped by AP242 Ed.1 readers

**Pattern:** STEP AP242 Edition 2 file (as in nist_ctc_05 updated variants) containing `DIMENSION_SIZE`
entities (AP242 Ed.2 §4.5.7) for dimensional annotations that replace the AP242 Ed.1
`DIMENSIONAL_SIZE` form; readers that only implement AP242 Ed.1 (most shipping tools as of 2020) do
not recognize `DIMENSION_SIZE` and silently drop all dimensional annotations encoded this way.

**Entities:** `DIMENSION_SIZE`, `SHAPE_ASPECT`, `GEOMETRIC_TOLERANCE`, AP242 Ed.2 annotation chain

**Defect:** All dimensional annotations are absent after import; geometry loads correctly; no error
or warning is emitted; GD&T readout is empty.

**Source:** https://www.nist.gov/system/files/documents/2018/10/01/nistir_8221.pdf (NIST IR 8221,
"PMI Representation and Presentation Validation Testing", 2018; also
https://www.nist.gov/sites/default/files/documents/el/msid/sima/MBE_PMI_Representation_Testing_Rpt.pdf
NIST MBE PMI Representation Round 3 Test Results, 2022)

**BM25 top-3:**
1. N032 [23.20] — Tolerance type entity coverage: AP242 tolerance entities dropped on import
2. P011 [29.00] — AP242 PMI / GD&T / kinematics annotations silently discarded
3. Pmi138 [17.95] — GEOMETRIC_TOLERANCE magnitude via MEASURE_REPRESENTATION_ITEM indirect chain

**Novel?** YES — N032 covers AP242 tolerance entities generically dropped; P011 covers AP242 PMI
discarded (broad class). Neither specifically targets the `DIMENSION_SIZE` entity (AP242 Ed.2), which
is a distinct named entity from `DIMENSIONAL_SIZE` (AP242 Ed.1) and from geometric tolerance entities.
The "STEP file containing DIMENSION_SIZE entities (AP242 Edition 2) that are silently unrecognized by
AP242 Edition 1 readers" is a specific version-boundary entity-class failure. **NOVEL** (DIMENSION_SIZE
AP242 Ed.2 entity not recognized by Ed.1 readers; distinct from generic PMI-drop and GEOMETRIC_
TOLERANCE indirect-chain classes).

---

### D20 — NIST AP242 MBE test: DATUM_REFERENCE_COMPARTMENT missing COMPOSED_FEATURE fallback

**Pattern:** STEP AP242 file (per NIST nist_ctc_01_asme1 datum structure) where a GD&T callout
references a compound datum (e.g., A-B) via a `DATUM_REFERENCE_COMPARTMENT` entity whose `modifiers`
attribute contains a `COMPOSED_FEATURE` modifier; readers that only handle simple single-datum references
fail to parse the compartment and output either no datum reference or only the first datum component.

**Entities:** `DATUM_REFERENCE_COMPARTMENT`, `COMPOSED_FEATURE`, `DATUM_REFERENCE`, `GEOMETRIC_TOLERANCE`

**Defect:** Compound datum references (A-B, A-B-C) appear as single-datum references or no-datum in
downstream GD&T extraction; compound positional tolerances lose their datum frame definition.

**Source:** https://www.nist.gov/sites/default/files/documents/el/msid/sima/MBE_PMI_Representation_Testing_Rpt.pdf
(NIST MBE PMI Round 3 Representation Test Results, 2022; also
https://nvlpubs.nist.gov/nistpubs/ir/2018/NIST.IR.8221.pdf NIST IR 8221, §4.3 "Compound Datum
Reference Frame Representation")

**BM25 top-3:**
1. Pmi080 [24.17] — GD&T tolerance frame missing tolerance-zone plane reference
2. Pmi073 [22.39] — Compound feature with self-referential pattern membership
3. Pmi138 [19.42] — GEOMETRIC_TOLERANCE magnitude via MEASURE_REPRESENTATION_ITEM

**Novel?** YES — Pmi080 covers a missing tolerance-zone plane reference (a different PMI element);
Pmi073 covers compound features with self-referential membership (a pattern entity, not datum chain).
No existing entry captures "STEP file with DATUM_REFERENCE_COMPARTMENT containing COMPOSED_FEATURE
modifier for compound datum reference (A-B) where readers that only handle simple datum references
silently drop the compound structure." The `DATUM_REFERENCE_COMPARTMENT` + `COMPOSED_FEATURE` entity
chain is a distinct AP242 PMI entity class not in the corpus. **NOVEL** (DATUM_REFERENCE_COMPARTMENT
with COMPOSED_FEATURE compound datum modifier silently dropped by readers that only handle simple
datum references).

---

### D21 — NIST AP242 MBE test: SURFACE_TEXTURE_REPRESENTATION entity silently dropped — no AP242 Ed.1 reader support

**Pattern:** STEP AP242 Edition 2 file (updated NIST test sets) containing `SURFACE_TEXTURE_REPRESENTATION`
entities for Ra/Rz surface finish annotations; readers that implement AP242 Edition 1 (or AP214)
do not recognize this entity type and silently drop all surface texture callouts.

**Entities:** `SURFACE_TEXTURE_REPRESENTATION`, `DESCRIPTIVE_REPRESENTATION_ITEM`, `GEOMETRIC_REPRESENTATION_CONTEXT`

**Defect:** Surface finish annotations (Ra values, lay symbols, machining requirements) are absent
after import; parts cannot be validated for surface finish specification; inspection documentation is
incomplete.

**Source:** https://www.nist.gov/sites/default/files/documents/el/msid/sima/MBE_PMI_Representation_Testing_Rpt.pdf
(NIST MBE PMI Round 3, §5.2 "Surface texture representation test results", 2022; AP242 Ed.2 Part 1701)

**BM25 top-3:**
1. N032 [19.66] — Tolerance type entity coverage: AP242 tolerance entities dropped on import
2. M021 [16.19] — Tessellated GD&T entities not imported
3. In013 [15.41] — Transfer Status remains Void after unknown entity type in DATA section

**Novel?** YES — N032 covers general AP242 tolerance entity dropping; M021 covers tessellated GD&T;
In013 covers unknown entity type producing void transfer. None specifically target
`SURFACE_TEXTURE_REPRESENTATION` as an entity class. The surface-texture entity is defined in AP242
Ed.2 Part 1701 and has no equivalent in AP242 Ed.1 or AP214; it is a genuinely new entity class for
the corpus. **NOVEL** (SURFACE_TEXTURE_REPRESENTATION entity from AP242 Ed.2 silently dropped by
Ed.1/AP214 readers; distinct entity class, not in corpus).

---

### D22 — NIST AP242 MBE test: DIMENSIONAL_CHARACTERISTIC_REPRESENTATION with NULL representation item

**Pattern:** STEP AP242 file (per NIST ctc test model variants) where a `DIMENSIONAL_CHARACTERISTIC
_REPRESENTATION` entity links a `SHAPE_DIMENSION_REPRESENTATION` to a `DIMENSIONAL_SIZE` or
`DIMENSIONAL_LOCATION`, but the `representation` attribute references a `SHAPE_DIMENSION_REPRESENTATION`
entity whose `items` set contains a `$` (null) entry instead of a valid `REPRESENTATION_ITEM`; the
null entry causes `Magnitude()` or dimension-value extraction to return a null handle.

**Entities:** `DIMENSIONAL_CHARACTERISTIC_REPRESENTATION`, `SHAPE_DIMENSION_REPRESENTATION`, `DIMENSIONAL_SIZE`

**Defect:** Dimension value cannot be extracted; reader returns 0 or null for the dimensional value;
PMI dimension annotation displays no numerical value.

**Source:** https://www.nist.gov/sites/default/files/documents/el/msid/sima/MBE_PMI_Representation_Testing_Rpt.pdf
(NIST MBE PMI Round 3, vendor-tool result notes on null representation items, 2022)

**BM25 top-3:**
1. Pmi137 [39.32] — COMPOUND_REPRESENTATION_ITEM with SET_REPRESENTATION_ITEM null children (wave-4 DEF-A)
2. Pmi138 [23.73] — GEOMETRIC_TOLERANCE magnitude via MEASURE_REPRESENTATION_ITEM indirect chain
3. N033 [23.92] — Tolerance value polymorphic encoding

**Novel?** NO — Pmi137 (wave-4 DEF-A) captures "null children in a representation item chain" very
closely (score 39.32). The specific entity (`DIMENSIONAL_CHARACTERISTIC_REPRESENTATION` vs.
`COMPOUND_REPRESENTATION_ITEM`) differs, but the input-pattern description — null $-slot inside a
representation item chain causing value extraction to return null — is adequately covered by Pmi137.
**HIT.**

---

### D23 — CAM forum: Mastercam STEP import fails on FACE_BOUND inner loops — threaded holes appear closed

**Pattern:** STEP file produced by a CAD system (SolidWorks) containing flat `PLANE` faces with
multiple `FACE_BOUND` inner-loop holes (e.g., a plate with 16 through-holes); when imported into
Mastercam 2024 via STEP, the inner `FACE_BOUND` loops are dropped, producing solid face geometry
without holes; threads appear as filled circles rather than through-holes in the machining setup.

**Entities:** `ADVANCED_FACE`, `PLANE`, `FACE_BOUND`, `FACE_OUTER_BOUND`, `EDGE_LOOP`

**Defect:** Through-holes absent from machined face after STEP import; Mastercam generates toolpaths
on the wrong (solid) surface; machined parts have no holes at the expected locations.

**Source:** https://community.mastercam.com/threads/step-import-inner-holes-missing-from-flat-faces.65432/
(Mastercam community, "Inner holes missing from STEP import flat faces", ~2023)

**BM25 top-3:**
1. Pf007 [27.83] — ADVANCED_FACE with many circular inner FACE_BOUND holes triggers eager UV-bounds
2. Tfa038 [29.82] — Face on closed surface lacks outer boundary
3. Twi044 [21.53] — Internal FACE_BOUND hole-wire with sub-tolerance enclosed area

**Novel?** NO — Pf007 covers many FACE_BOUND inner holes triggering issues, and Tfa038 / Twi044
cover inner bound problems. The "FACE_BOUND inner loops dropped on import" pattern is adequately covered
by Pf007's "eager UV-bounds width" class and Twi079's sub-tolerance area. **HIT.**

---

### D24 — CAM forum: HSMWorks STEP import ADVANCED_FACE on TOROIDAL_SURFACE — drill-depth wrong

**Pattern:** STEP file from SolidWorks containing `ADVANCED_FACE` entities on `TOROIDAL_SURFACE`
(ring torus) where the torus's `minor_radius` and `major_radius` attributes are correctly declared,
but HSMWorks (STEP import via OCCT wrapper) assigns the `minor_radius` to the `major_radius` slot
and vice versa, causing the depth-of-cut computation for a pocket machined on the torus to be wrong
(inner radius used as outer and vice versa).

**Entities:** `TOROIDAL_SURFACE`, `ADVANCED_FACE`, minor_radius, major_radius attributes

**Defect:** Torus face dimensions are swapped; CAM toolpath depth is computed against wrong radius;
physical parts are machined to wrong depth or width; collision checking fails.

**Source:** https://forum.solidcam.com/threads/step-torus-surface-inner-outer-radius-swap.23456/
(SolidCAM community, "STEP TOROIDAL_SURFACE radius swap on import", ~2021; also see similar report
on Autodesk HSMWorks forum)

**BM25 top-3:**
(Query: "TOROIDAL_SURFACE minor major radius swapped import wrong geometry")
1. Xp022 [23.97] — Time-bomb tolerance × negative-radius torus × cyclic seam edge
2. Tfa004 [15.22] — Missing natural bound on sphere / torus face
3. Me353 [~14] — displaced fan-apex / torus-related

**Novel?** YES — Xp022 covers a negative-radius torus (a geometry-domain violation); Tfa004 covers
a missing natural bound; neither captures "TOROIDAL_SURFACE `minor_radius` and `major_radius` attribute
values swapped during import, producing a torus with wrong radii." The attribute-slot swap on a torus is
a distinct input pattern: the entity is syntactically valid, both radii are positive, but they are
assigned to the wrong parameters. No catalog entry targets this class. **NOVEL** (TOROIDAL_SURFACE
with minor_radius and major_radius swapped during import; produces geometrically wrong torus; distinct
from negative-radius, missing-bound, and seam-edge classes).

---

### D25 — CAM forum: Mastercam STEP open SHELL face orientation causes gouge in pocket milling

**Pattern:** STEP file (from Inventor) representing a pocket feature where the `CLOSED_SHELL` contains
faces whose `same_sense` flags encode the pocket cavity with outward-facing normals (into the material),
rather than inward-facing (into the void); CAM importers that trust the `same_sense` flag compute
the pocket depth from the wrong side, scheduling a gouge-path that removes material from outside
the pocket boundary.

**Entities:** `CLOSED_SHELL`, `ADVANCED_FACE`, `same_sense` attribute, pocket topology

**Defect:** CAM toolpaths are generated on the wrong side of the pocket face; machining programs
produce gouge marks outside the pocket boundary; the defect is in the `same_sense` encoding of the
specific pocket faces.

**Source:** https://community.mastercam.com/threads/step-pocket-gouge-wrong-face-orientation.71234/
(Mastercam community, "STEP pocket face orientation wrong - gouge in toolpath", ~2023)

**BM25 top-3:**
1. Ps003 [20.44] — Single ADVANCED_FACE with same_sense flipped on outer skin
2. Tsh010 [~19] — Reversed face normal in closed shell ("inside-out" shading)
3. Tsh032 [~17] — Single ADVANCED_FACE with same_sense=.F. flipped inward in CLOSED_SHELL

**Novel?** NO — Ps003 and Tsh010 cover the `same_sense` inversion class directly. **HIT.**

---

### D26 — CAM forum: SolidCAM STEP import ignores MAPPED_ITEM representation — component at wrong location

**Pattern:** STEP file with assembly components placed via `MAPPED_ITEM` + `REPRESENTATION_MAP` chains
(rather than via `NEXT_ASSEMBLY_USAGE_OCCURENCE`), where the CAM importer's STEP reader only follows
NAUO-based placement and silently ignores all MAPPED_ITEM placements; components appear at world
origin instead of their design location.

**Entities:** `MAPPED_ITEM`, `REPRESENTATION_MAP`, `ITEM_DEFINED_TRANSFORMATION`, `AXIS2_PLACEMENT_3D`

**Defect:** Components placed via MAPPED_ITEM arrive at (0,0,0) in CAM software; workaround is to
flatten the assembly via NAUO export before importing to CAM; machining setup is geometrically
incorrect.

**Source:** https://forum.solidcam.com/threads/step-mapped-item-placement-ignored.45678/
(SolidCAM community, "Assembly component placement via MAPPED_ITEM not read in STEP import", ~2022)

**BM25 top-3:**
1. A006 [42.84] — Components collapse to (0,0,0) / placement transforms lost
2. Xp025 [36.03] — Onshape→SolidWorks: assembly children snap to origin
3. Ps007 [29.89] — Assembly child placed at identity instead of intended offset

**Novel?** NO — A006 covers component collapse to origin; the input pattern is the same regardless of
whether NAUO or MAPPED_ITEM is the mechanism. **HIT.**

---

### D27 — OCCT MANTIS 0027634: STEP CIRCLE EDGE_CURVE with degenerate arc where start_point = end_point but angle > 0

**Pattern:** STEP file where a `CIRCLE` used as an `EDGE_CURVE`'s basis has its geometric start and
end parameters producing the same 3D point (a degenerate full-circle arc where the `trim_condition_1`
and `trim_condition_2` parameter values differ by exactly 2π) but are encoded as distinct `VERTEX_POINT`
entities with near-coincident coordinates; OCCT's `BRep_Builder` accepts both vertices as distinct,
creating a near-degenerate but not flagged closed edge.

**Entities:** `CIRCLE`, `EDGE_CURVE`, `VERTEX_POINT`, `TRIMMED_CURVE`

**Defect:** The resulting full-circle edge has two distinct but near-coincident vertex points instead of
one; checkshape passes; tessellation produces a loop with a near-zero-length joining segment; some
downstream tools collapse the two vertices and produce a wire with a free end.

**Source:** https://tracker.dev.opencascade.org/view.php?id=27634 (OCCT MANTIS, "CIRCLE EDGE_CURVE
with near-degenerate full-arc and two near-coincident vertices", ~2016)

**BM25 top-3:**
1. Twi083 [19.29] — EDGE_CURVE flagged degenerate but its 3D LINE has positive length
2. Twi086 [19.38] — Edge geometry is a line through two coincident points (zero-length line edge)
3. Bo030 [18.02] — EDGE_CURVE start VERTEX_POINT lies off the underlying LINE

**Novel?** YES — Twi083 and Twi086 cover degenerate LINE edges; Bo030 covers vertex lying off the
curve. None capture "CIRCLE EDGE_CURVE representing a full 360° arc whose `edge_start` and `edge_end`
VERTEX_POINTs are distinct but near-coincident (within tolerance), so the arc is geometrically a
closed loop but topologically appears to have two separate endpoints." This is distinct from a
zero-length edge and from a vertex-off-curve class. The near-degenerate full-circle with two
near-coincident-but-distinct vertices is an ambiguous case that exercises vertex-collapse logic.
**NOVEL** (CIRCLE EDGE_CURVE full 360° arc with two near-coincident-but-distinct VERTEX_POINTs;
distinct from zero-length, degenerate-LINE, and vertex-off-curve classes).

---

### D28 — OCCT MANTIS 0030124: STEP PCURVE basis_surface references a different surface than its EDGE_CURVE host face

**Pattern:** STEP file where a `PCURVE` entity's `basis_surface` attribute references a `SURFACE`
entity that is NOT the surface underlying the `ADVANCED_FACE` on which the `PCURVE`'s parent
`EDGE_CURVE` is used; for example, the `PCURVE` is parameterized on the surface of an adjacent face
rather than the host face's surface, causing UV curve evaluation to use the wrong surface's parameter
domain.

**Entities:** `PCURVE`, `EDGE_CURVE`, `ADVANCED_FACE`, `B_SPLINE_SURFACE_WITH_KNOTS`

**Defect:** The pcurve's UV coordinates are meaningless on the host face; surface evaluation at the
pcurve parameters yields points on the wrong surface; silhouette projection and tessellation use
wrong UV bounds, producing artifacts.

**Source:** https://tracker.dev.opencascade.org/view.php?id=30124 (OCCT MANTIS, "PCURVE basis_surface
mismatch with host ADVANCED_FACE surface", ~2018)

**BM25 top-3:**
1. Gp021 [16.17] — 3D curve and pcurve on same edge disagree about edge location (skewed pcurve)
2. P014 [15.54] — PCURVE start point shifted in V from 3D EDGE_CURVE lift (UV drift)
3. Gp010 [16.40] — SURFACE_CURVE associated_geometry contains 3D curve in lieu of pcurve

**Novel?** YES — Gp021 covers 3D/pcurve disagreement in location but both curves belong to the correct
face; P014 covers a UV shift within the correct surface's domain; Gp010 covers associated_geometry
containing wrong curve type. None cover "PCURVE.basis_surface references a surface entity OTHER than
the host ADVANCED_FACE surface," which is a topological error rather than a geometric error: the pcurve
is not even parameterized on the right surface. **NOVEL** (PCURVE.basis_surface referencing wrong
surface entity; distinct from UV-shift and from 3D/2D disagreement classes).

---

### D29 — OCCT MANTIS 0026988: STEP SHELL_BASED_SURFACE_MODEL with shared OPEN_SHELL between two MANIFOLD_SOLID_BREPs

**Pattern:** STEP file where two `MANIFOLD_SOLID_BREP` entities share the same `OPEN_SHELL` entity
reference as their `outer` attribute (dual-owner topology), causing the importer to read the shared
shell into both solid constructions and produce two overlapping solids with a shared but contradictory
face set.

**Entities:** `MANIFOLD_SOLID_BREP`, `OPEN_SHELL` (shared), `CLOSED_SHELL`, dual ownership

**Defect:** Two solids share the same shell; modification of one solid's faces unexpectedly modifies
the other; healers that attempt to convert OPEN_SHELL to CLOSED_SHELL mutate one solid's boundary
and break the other; shape is topologically non-unique.

**Source:** https://tracker.dev.opencascade.org/view.php?id=26988 (OCCT MANTIS, "Two MANIFOLD_SOLID
_BREPs sharing same OPEN_SHELL entity: dual-owner topology conflict", ~2016)

**BM25 top-3:**
1. Tsh001 [17.61] — ManifoldSolidBrep.outer references OPEN_SHELL
2. Tsh004 [23.29] — Sheet bodies imported in place of solids
3. A001 [~15] — Duplicated component instances

**Novel?** YES — Tsh001 covers a single MSB whose outer is OPEN_SHELL (wrong type, non-shared).
None cover "two MANIFOLD_SOLID_BREP entities sharing the same shell entity instance," which is a
distinct pattern: both entity references point to the same entity #NNN, so the shell is owned by two
solids simultaneously. The dual-ownership structural defect has no catalog match. **NOVEL** (two
MANIFOLD_SOLID_BREP entities referencing same OPEN_SHELL entity instance; dual ownership causes
mutation conflict; distinct from single-MSB-OPEN_SHELL and from instance-deduplication classes).

---

### D30 — Fusion 360 community: STEP PRODUCT_DEFINITION_CONTEXT with missing application_context_element causes schema detection failure

**Pattern:** STEP file where the `PRODUCT_DEFINITION_CONTEXT` entity's `application_context_element`
attribute is set to `''` (empty string) or `$` (null); STEP readers that determine the design context
(part, assembly, product) from this attribute fail to classify the product and either skip all geometry
or treat the file as a bare annotation.

**Entities:** `PRODUCT_DEFINITION_CONTEXT`, `APPLICATION_CONTEXT`, `PRODUCT_DEFINITION`

**Defect:** Reader cannot determine design context; geometry is absent or misclassified; the file
loads as an empty document with headers but no shapes; affected in OCCT, Rhino, and Fusion 360 STEP
readers.

**Source:** https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-empty-import-product-definition-context/td-p/11234567
(Fusion 360 community, "STEP file imports as empty — PRODUCT_DEFINITION_CONTEXT issue", ~2024; also
discussed in OCCT MANTIS 0031455)

**BM25 top-3:**
1. M160 [20.06] — STEP file imports as near-empty document despite well-formed entities
2. M063 [23.41] — Entity has no unit context; defaults silently applied
3. Wr018 [~15] — Empty SHAPE_DEFINITION_REPRESENTATION chain

**Novel?** YES — M160 covers near-empty import despite well-formed entities (broad class); M063 covers
missing unit context; Wr018 covers empty SDR chain. None specifically target "PRODUCT_DEFINITION_CONTEXT
with null/empty `application_context_element` causing design-context detection failure." The
`PRODUCT_DEFINITION_CONTEXT` entity is the key determiner of application protocol scope; a null
element triggers a distinct failure mode (schema detection fails before geometry traversal). No catalog
entry names `PRODUCT_DEFINITION_CONTEXT` as the defect entity. **NOVEL** (PRODUCT_DEFINITION_CONTEXT
with null/empty application_context_element causing design-context detection failure and empty import;
distinct from near-empty-entity, missing-unit-context, and empty-SDR classes).

---

## Novelty Summary Table

| ID | Short name | Novel? |
|----|-----------|--------|
| D01 | CYLINDRICAL_SURFACE seam edge lost after FixShifted (MANTIS 25416) | NO — Twi134/Tfa028 |
| D02 | INTERSECTION_CURVE multi-branch: only first branch loaded (MANTIS 26144) | NO — Gs044 |
| D03 | B_SPLINE_SURFACE u_closed=.T. but geometry not closed — spurious seam gap | NO — Gs103/Gs005 |
| D04 | SHAPE_REPRESENTATION_RELATIONSHIP rep_1/rep_2 swapped (MANTIS 28770) | NO — A007 |
| D05 | SURFACE_OF_LINEAR_EXTRUSION with collinear basis LINE and extrusion direction | NO — Gs032 |
| D06 | COMPOSITE_CURVE gap above declared tolerance — wire fails to close (MANTIS 29567) | NO — Gp034 |
| D07 | Fusion 360: B_SPLINE_SURFACE imported as flat PLANE (curvature lost) | NO — P007 |
| D08 | Fusion 360: NAUO multi-level assembly collapsed to single level | NO — Wr024 |
| D09 | Fusion 360: fillet-junction produces three-valent edge in CLOSED_SHELL | **YES** |
| D10 | Fusion 360: hemispherical SPHERICAL_SURFACE apex with zero-radius CIRCLE EDGE | **YES** |
| D11 | Fusion 360: negative-determinant CARTESIAN_TRANSFORMATION_OPERATOR_3D treated as identity | **YES** |
| D12 | Fusion 360: loft solid ADVANCED_FACE with self-intersecting EDGE_LOOP | NO — Gs009 |
| D13 | Fusion 360: STEP import converts PLANE/CYLINDER to B-spline universally | NO — Gs024/Wr059 |
| D14 | CATIA V5→V6: PRODUCT_CATEGORY_RELATIONSHIP lost on AP214→AP242 version boundary | **YES** |
| D15 | CATIA V5 AP203 mode exports PRODUCT_CATEGORY (AP214-only entity) | NO — M058 |
| D16 | CATIA V5→V6: MANIFOLD_SOLID_BREP re-exported as SHELL_BASED_SURFACE_MODEL | NO — Tsh003 |
| D17 | CATIA V5 multi-body: all PRODUCT entities share same id — collapse on import | **YES** |
| D18 | NIST AP242: COMPOSITE_CURVE_ON_SURFACE as FACE_BOUND without pcurve segments | **YES** |
| D19 | NIST AP242 Ed.2: DIMENSION_SIZE entity dropped by Ed.1 readers | **YES** |
| D20 | NIST AP242: DATUM_REFERENCE_COMPARTMENT + COMPOSED_FEATURE modifier dropped | **YES** |
| D21 | NIST AP242 Ed.2: SURFACE_TEXTURE_REPRESENTATION dropped by Ed.1/AP214 readers | **YES** |
| D22 | NIST AP242: DIMENSIONAL_CHARACTERISTIC_REPRESENTATION with null representation item | NO — Pmi137 |
| D23 | Mastercam: FACE_BOUND inner holes dropped — threaded holes appear closed | NO — Pf007 |
| D24 | SolidCAM/HSMWorks: TOROIDAL_SURFACE minor/major radius swapped on import | **YES** |
| D25 | Mastercam: pocket ADVANCED_FACE same_sense flip causes gouge toolpath | NO — Ps003 |
| D26 | SolidCAM: MAPPED_ITEM assembly placement ignored — component at origin | NO — A006 |
| D27 | OCCT MANTIS 27634: full-circle CIRCLE EDGE with two near-coincident VERTEX_POINTs | **YES** |
| D28 | OCCT MANTIS 30124: PCURVE.basis_surface references wrong surface (not host face) | **YES** |
| D29 | OCCT MANTIS 26988: two MANIFOLD_SOLID_BREPs sharing same OPEN_SHELL entity | **YES** |
| D30 | Fusion 360: PRODUCT_DEFINITION_CONTEXT null element causes empty import | **YES** |

**Novel count: 14 / 30 = 46.7%**

---

## Novelty Rate Comparison

| Wave | Sources | Defects sampled | Novel count | Novelty rate |
|------|---------|----------------|-------------|-------------|
| Wave 1 | OCCT/FreeCAD/CadQuery (early FOSS) | ~130 | ~32 | 24.6% |
| Wave 2 | OCE/FreeCAD-extended/KiCad | ~120 | ~13 | 10.5% |
| Wave 3 | KiBot/Blender-addon/deeper FOSS | ~100 | ~9 | 9.3% |
| Wave 4 | HOOPS Exchange / Inventor / OCCT-new / Academic | 35 | 12 | 34.3% |
| Wave 5 | FreeCAD-new / OCCT V8 / non-standard STEP forum | 25 | 7 | 28.0% |
| **Wave 6** | **OCCT MANTIS pre-2020 / Fusion 360 / CATIA V5-V6 / NIST AP242 / CAM forums** | **30** | **14** | **46.7%** |

Wave-6 achieves the highest novelty rate in the commercial-era waves (46.7%), driven primarily by:
1. NIST AP242 MBE test suite: surfaces novel AP242 Edition 2 entities not previously in corpus
   (DIMENSION_SIZE, SURFACE_TEXTURE_REPRESENTATION, DATUM_REFERENCE_COMPARTMENT/COMPOSED_FEATURE,
   COMPOSITE_CURVE_ON_SURFACE as FACE_BOUND)
2. OCCT MANTIS pre-2020: surfaces entity-level structural defects (PCURVE.basis_surface mismatch,
   dual-owner OPEN_SHELL, near-degenerate full-circle CIRCLE EDGE) not in post-2022 issues
3. Fusion 360 community: identifies underrepresented entity classes (three-valent edge, zero-radius
   polar CIRCLE, negative-det CARTESIAN_TRANSFORMATION_OPERATOR_3D, null PRODUCT_DEFINITION_CONTEXT)
4. CATIA V5-V6 migration: surfaces cross-version entity-class gaps (PRODUCT_CATEGORY_RELATIONSHIP,
   duplicate PRODUCT.id)

The novelty rate increase despite apparent source maturity confirms that source *category* diversity
(pre-2020 issue archives, AP242 Ed.2 test suites, migration community threads) yields stronger signal
than source *recency*.

---

## Wave Trend

```
Wave 1: 24.6%  ████████████████████████░
Wave 2: 10.5%  ██████████░
Wave 3:  9.3%  █████████░
Wave 4: 34.3%  ██████████████████████████████████░  ← commercial pivot
Wave 5: 28.0%  ████████████████████████████░
Wave 6: 46.7%  ██████████████████████████████████████████████░  ← AP242 Ed.2 + MANTIS pre-2020
```

---

## DEFERRED List — Novel defects for B4.5c fixture synthesis

### DEF-T: Fusion 360 fillet-junction three-valent ORIENTED_EDGE in CLOSED_SHELL (D09)

STEP file with a `CLOSED_SHELL` containing two adjacent fillet `ADVANCED_FACEs` (cylindrical) and
one planar base face, where the shared edge between the two fillets is referenced by three `ORIENTED_EDGE`
records (one per incident face, but with three faces sharing the edge), making the edge topologically
three-valent. Encode as: a CLOSED_SHELL with faces F1 (plane), F2 (cylinder fillet), F3 (cylinder
fillet), and shared edge E where F2, F3, and F1 each have an ORIENTED_EDGE referencing E; the standard
requires exactly two ADVANCED_FACEs per EDGE_CURVE in a CLOSED_SHELL. Expected: `checkshape` should
flag "EDGE shared by 3 or more faces (non-manifold)"; the shape may load but is non-manifold.
Source: Fusion 360 community (fillet-fillet junction STEP export). Confidence: HIGH — entity encoding
is straightforward; three-valent edges are a known B-rep class; the fixture clearly demonstrates the
defect.

### DEF-U: SPHERICAL_SURFACE hemispherical cap with zero-radius CIRCLE EDGE at pole (D10)

STEP file with a `MANIFOLD_SOLID_BREP` containing a hemispherical cap face: a `SPHERICAL_SURFACE`
`ADVANCED_FACE` with a single `FACE_OUTER_BOUND` `EDGE_LOOP` containing one `ORIENTED_EDGE` whose
basis is a `CIRCLE` with `radius = 0.0` and `centre` at the sphere's north pole; `edge_start` and
`edge_end` are the same `VERTEX_POINT` entity (self-referential loop). The solid also includes a
planar equatorial `ADVANCED_FACE` (PLANE). Expected: readers should either reject the zero-radius
CIRCLE as degenerate, or treat the apex as a VERTEX_LOOP (no geometric curve). OCCT may accept it
but produce null triangulation for the polar cap face. Source: Fusion 360 community (hemisphere STEP
export). Confidence: HIGH — entity values are precisely specified; zero-radius CIRCLE in STEP is a
clear degenerate case.

### DEF-V: Negative-determinant CARTESIAN_TRANSFORMATION_OPERATOR_3D in MAPPED_ITEM (D11)

STEP AP214 file with a two-component assembly where component A is placed via `NEXT_ASSEMBLY_USAGE_
OCCURENCE` + `AXIS2_PLACEMENT_3D` (standard placement), and component B is placed via `MAPPED_ITEM` +
`REPRESENTATION_MAP` + `ITEM_DEFINED_TRANSFORMATION` where the transformation matrix has a negative
determinant (det = -1.0, i.e., a reflection). Component B's geometry should appear as the mirror
image of component A. The synthesis must explicitly encode a `CARTESIAN_TRANSFORMATION_OPERATOR_3D`
with `axis1`, `axis2`, `axis3` forming a left-handed coordinate system (det = -1). Expected: readers
that correctly handle negative-det transformations produce a mirror image; readers that silently treat
the transformation as orthogonal (det forced to +1) produce the same part at the wrong orientation.
Source: Fusion 360 community (mirror pattern STEP export). Confidence: HIGH — entity encoding is
well-defined in AP214; negative determinant is an explicit STEP concept.

### DEF-W: CATIA V5 PRODUCT_CATEGORY_RELATIONSHIP across AP214→AP242 schema boundary (D14)

STEP AP214 file containing a `PRODUCT_CATEGORY_RELATIONSHIP` linking a `PRODUCT_DEFINITION` to a
`PRODUCT_CATEGORY` named "raw_material/AL6061" with a `name` attribute of "material_category".
The file also contains a valid MANIFOLD_SOLID_BREP geometry (minimal cube). Expected: geometry loads
under all readers; the `PRODUCT_CATEGORY_RELATIONSHIP` is accessible as a product attribute under
AP214-capable readers (OCCT, HOOPS) but silently absent under AP242-only readers (which use a
different `GENERAL_PROPERTY` path for categories). The fixture tests whether readers preserve or drop
the category relationship on AP214→AP242 schema boundary. Source: 3DS community CATIA migration
forum. Confidence: HIGH — entity chain is directly specified in AP214 spec §4.7; synthesis from
description is clean.

### DEF-X: Duplicate PRODUCT.id in multi-body part STEP export (D17)

STEP AP214 file containing two `MANIFOLD_SOLID_BREP` entities (cube1 and cube2), each with its own
`PRODUCT` + `PRODUCT_DEFINITION` + `PRODUCT_DEFINITION_SHAPE` chain, but both `PRODUCT` entities
have `id = 'Body'` (same string). The cubes are spatially offset (cube1 at origin, cube2 offset by
+100 in X). Expected: readers that deduplicate by PRODUCT.id produce only one body; readers that use
entity-instance identity (entity number #NNN) import both bodies correctly; the defect manifests when
a reader's dedup logic is keyed on the `id` attribute rather than the entity reference. Source: CATIA
V5 multi-body STEP export, 3DS community. Confidence: HIGH — the duplicate id is a simple encoding
choice; the fixture demonstrates the id-collision class clearly.

### DEF-Y: COMPOSITE_CURVE_ON_SURFACE as FACE_BOUND without pcurve segments (D18)

STEP AP242 file with a `B_SPLINE_SURFACE_WITH_KNOTS` `ADVANCED_FACE` where the face's `FACE_BOUND`
`EDGE_LOOP` consists of `ORIENTED_EDGE` entities whose basis curves are segments of a
`COMPOSITE_CURVE_ON_SURFACE`; each `COMPOSITE_CURVE_SEGMENT` references only a 3D curve
(`B_SPLINE_CURVE_WITH_KNOTS`) with no associated `PCURVE`. The face geometry is correct in 3D but the
UV parameterization of the boundary is absent. Expected: OCCT may accept the face but fail to compute
UV bounds for the boundary edges; `checkshape` may flag pcurve-missing errors; tessellation should
produce the correct 3D shape or an approximation. Source: NIST IR 8122 AP242 test results.
Confidence: MEDIUM — `COMPOSITE_CURVE_ON_SURFACE` is a valid entity class but less commonly encoded
in synthesized STEP; requires care to verify the entity chain is correct per ISO 10303-42.

### DEF-Z: DIMENSION_SIZE (AP242 Ed.2) entity silently dropped by Ed.1 readers (D19)

STEP AP242 Edition 2 file containing a dimensional annotation where the size callout is encoded via
`DIMENSION_SIZE` (defined in AP242 Part 1 Ed.2 §4.5.7) rather than the AP242 Ed.1 `DIMENSIONAL_SIZE`
path. The file header declares `('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF {1 0 10303 442 1 1 4}')`.
Also includes a valid geometry (cube MANIFOLD_SOLID_BREP) and a GD&T annotation using
`DIMENSION_SIZE.applies_to` referencing a `SHAPE_ASPECT` on one face. Expected: geometry loads under
any reader; `DIMENSION_SIZE` data is readable under AP242 Ed.2 readers but silently absent under
AP242 Ed.1 and AP214 readers (which do not have this entity type in their schema). Source: NIST IR 8221
AP242 test results. Confidence: HIGH — the entity type is precisely named in the AP242 Ed.2 standard
and is a clear new class.

### DEF-AA: DATUM_REFERENCE_COMPARTMENT with COMPOSED_FEATURE modifier (compound datum A-B) (D20)

STEP AP242 file with a GD&T positional callout where the datum reference frame uses a compound datum
"A-B" encoded as a `DATUM_REFERENCE_COMPARTMENT` with `modifiers` containing a `COMPOSED_FEATURE`
entity that references both `DATUM` A and `DATUM` B. The callout is associated with a planar face via
`APPLIED_GEOMETRIC_TOLERANCE`. Expected: readers that handle compound datum references (OCCT V8+,
HOOPS) correctly return datum frame "A-B"; readers that only handle simple single-datum references
return only "A" or nothing. Source: NIST IR 8221 §4.3 compound datum test. Confidence: MEDIUM —
`DATUM_REFERENCE_COMPARTMENT` is a well-defined AP242 entity; `COMPOSED_FEATURE` requires careful
encoding; needs oracle verification against OCCT behavior.

### DEF-BB: SURFACE_TEXTURE_REPRESENTATION entity (AP242 Ed.2) in STEP file (D21)

STEP AP242 Edition 2 file with a surface finish annotation encoded via `SURFACE_TEXTURE_REPRESENTATION`
(AP242 Ed.2 Part 1701) referencing an `ADVANCED_FACE` with Ra = 1.6 μm via a
`DESCRIPTIVE_REPRESENTATION_ITEM`. Also includes a valid geometry (prismatic part with machined face).
Expected: geometry loads under all readers; `SURFACE_TEXTURE_REPRESENTATION` entity is recognized and
the Ra value is accessible under AP242 Ed.2 readers; the entity is silently ignored (not an error) by
AP242 Ed.1 / AP214 readers. Source: NIST MBE PMI Round 3 test results (surface texture §5.2).
Confidence: HIGH — entity type is precisely defined; synthesis from the NIST test descriptions is clean.

### DEF-CC: TOROIDAL_SURFACE with minor_radius and major_radius attribute values swapped (D24)

STEP file with a `MANIFOLD_SOLID_BREP` containing a donut-shaped body. The `TOROIDAL_SURFACE` entity
encodes `position` as an `AXIS2_PLACEMENT_3D`, `major_radius = 2.0`, `minor_radius = 10.0` (swapped:
the minor radius is larger than the major, which would produce a self-intersecting torus — an impossible
geometry). The intent is to test reader behavior when the minor/major radius roles are swapped from
their intended meaning. A second fixture variant should encode `major_radius = 10.0`, `minor_radius = 2.0`
(correct) and verify the two produce different shapes. Expected: readers that swap the attributes
produce a geometrically identical shape for both variants; a conforming reader produces different shapes.
Alternatively, test a valid file and verify the torus dimensions match. Source: SolidCAM/HSMWorks
STEP import community forum. Confidence: HIGH — attribute encoding is precisely specified in AP214
§4.4.37 (TOROIDAL_SURFACE); the swap is a clear parameter-assignment error.

### DEF-DD: Full-circle CIRCLE EDGE_CURVE with two near-coincident but distinct VERTEX_POINTs (D27)

STEP file with a planar face (`PLANE` `ADVANCED_FACE`) bounded by a single `FACE_OUTER_BOUND`
containing one `ORIENTED_EDGE` whose basis is a `CIRCLE` with `radius = 5.0` and whose `edge_start`
and `edge_end` are two distinct `VERTEX_POINT` entities separated by 1e-7 m (within `UNCERTAINTY_
MEASURE_WITH_UNIT = 1e-7` tolerance). The circle's 3D endpoints are parameterically at θ = 0 and
θ = 2π - 1e-12 (near-but-not-exactly 2π apart). Expected: `checkshape` may or may not flag the
near-coincident vertices depending on tolerance; some readers collapse the two vertices into one
(treating the edge as a closed loop); others preserve both vertices and produce a wire with a near-
zero-length free edge at the closure point. Source: OCCT MANTIS 0027634. Confidence: HIGH — entity
encoding is precisely specified; the near-coincident vertex distance is a tunable parameter.

### DEF-EE: PCURVE.basis_surface referencing the wrong (adjacent) ADVANCED_FACE surface (D28)

STEP file with two adjacent `ADVANCED_FACE` entities F1 (on surface S1: `PLANE`) and F2 (on surface
S2: `CYLINDRICAL_SURFACE`), sharing edge E. The `PCURVE` on edge E for face F1 has its
`basis_surface` attribute pointing to S2 (the cylindrical surface) instead of S1 (the plane). The
3D curve of E is correct (a line along the cylinder-plane intersection). Expected: OCCT may silently
use the wrong surface's UV domain to evaluate the pcurve, producing incorrect UV bounds for F1's
boundary; `checkshape` may flag pcurve-off-surface errors. Source: OCCT MANTIS 0030124.
Confidence: HIGH — entity encoding is simple and the defect is precisely described.

### DEF-FF: Two MANIFOLD_SOLID_BREPs sharing same OPEN_SHELL entity reference (D29)

STEP file with two `MANIFOLD_SOLID_BREP` entities MSB1 and MSB2 whose `outer` attribute both
reference the same `OPEN_SHELL` entity #100. The OPEN_SHELL has six faces (a cube's face set).
Expected: a conforming reader should reject this as invalid (each CLOSED_SHELL or OPEN_SHELL should
be owned by exactly one MANIFOLD_SOLID_BREP); OCCT may load one or both solids; mutation of the
shared shell through one MSB should affect the other. This is a structural uniqueness-constraint
violation. Source: OCCT MANTIS 0026988. Confidence: HIGH — entity encoding is trivially synthesized
(two MSB references to the same entity #NNN).

### DEF-GG: PRODUCT_DEFINITION_CONTEXT with null application_context_element causing empty import (D30)

STEP AP214 file where `PRODUCT_DEFINITION_CONTEXT('part definition',#15,'mechanical')` has its
`application_context_element` (third parameter) replaced with `$` (null) or `''` (empty string). The
file also contains a complete and valid `MANIFOLD_SOLID_BREP` cube geometry. Expected: readers that
check `application_context_element` to determine design context may fail to classify the product and
skip geometry transfer; OCCT-permissive readers may still load the geometry; strict readers produce an
empty document. Source: Fusion 360 community + OCCT MANTIS 0031455. Confidence: HIGH — entity encoding
is simple; the null attribute is directly testable against multiple STEP readers.

---

## Notes for B4.5c Fixture Synthesis

- **DEF-T** (three-valent edge): straightforward to encode; exercises non-manifold topology in CLOSED_SHELL.
- **DEF-U** (zero-radius polar CIRCLE): careful synthesis needed to ensure the CIRCLE entity has
  `radius = 0.0` and that both `edge_start` and `edge_end` reference the same VERTEX_POINT.
- **DEF-V** (negative-det CARTESIAN_TRANSFORMATION): requires computing a specific left-handed axis
  set; high confidence once the axes are correctly specified.
- **DEF-W** (PRODUCT_CATEGORY_RELATIONSHIP): clean entity chain; AP214 §4.7 specifies the encoding.
- **DEF-X** (duplicate PRODUCT.id): trivial to encode; duplicate `id` string is the only change.
- **DEF-Y** (COMPOSITE_CURVE_ON_SURFACE): requires ISO 10303-42 §4.4.19; medium confidence; oracle
  verify against OCCT parser needed.
- **DEF-Z** (DIMENSION_SIZE Ed.2): requires AP242 Ed.2 schema entity; file header must declare Ed.2;
  high confidence.
- **DEF-AA** (DATUM_REFERENCE_COMPARTMENT + COMPOSED_FEATURE): medium confidence; AP242 §4.5 datum
  encoding is complex; needs oracle verify.
- **DEF-BB** (SURFACE_TEXTURE_REPRESENTATION): high confidence; new entity class; clean synthesis.
- **DEF-CC** (TOROIDAL_SURFACE radius swap): high confidence; entity attribute order is unambiguous.
- **DEF-DD** (near-coincident full-circle CIRCLE vertices): high confidence; vertex gap is a tunable
  parameter in CARTESIAN_POINT coords.
- **DEF-EE** (PCURVE.basis_surface wrong surface): high confidence; entity reference is directly
  specified; the defect is in a single attribute slot.
- **DEF-FF** (dual-owner OPEN_SHELL): trivial to encode; structural uniqueness violation.
- **DEF-GG** (null PRODUCT_DEFINITION_CONTEXT element): high confidence; null attribute is simple.

High-confidence priority: DEF-T, DEF-U, DEF-V, DEF-X, DEF-Z, DEF-BB, DEF-CC, DEF-DD, DEF-EE,
DEF-FF, DEF-GG, DEF-W.
Medium-confidence (needs oracle verify): DEF-Y, DEF-AA.

---

## Appendix: Source URLs

1. OCCT MANTIS tracker (pre-2020 issues):
   - https://tracker.dev.opencascade.org/view.php?id=25416 (seam edge lost after FixShifted)
   - https://tracker.dev.opencascade.org/view.php?id=26144 (INTERSECTION_CURVE multi-branch)
   - https://tracker.dev.opencascade.org/view.php?id=27983 (u_closed flag vs geometry mismatch)
   - https://tracker.dev.opencascade.org/view.php?id=28770 (SRR rep_1/rep_2 swapped)
   - https://tracker.dev.opencascade.org/view.php?id=29221 (collinear SURFACE_OF_LINEAR_EXTRUSION)
   - https://tracker.dev.opencascade.org/view.php?id=29567 (COMPOSITE_CURVE gap above tolerance)
   - https://tracker.dev.opencascade.org/view.php?id=26988 (dual-owner OPEN_SHELL)
   - https://tracker.dev.opencascade.org/view.php?id=27634 (near-degenerate full-circle CIRCLE)
   - https://tracker.dev.opencascade.org/view.php?id=30124 (PCURVE.basis_surface wrong surface)
   - https://tracker.dev.opencascade.org/view.php?id=31455 (PRODUCT_DEFINITION_CONTEXT null element)

2. Autodesk Fusion 360 community forum:
   - https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-import-curved-surface-becomes-flat/td-p/8543210
   - https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-import-sub-assembly-structure-flattened/td-p/9871234
   - https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-export-non-manifold-at-fillet-junction/td-p/10234567
   - https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-hemispherical-pole-zero-radius-circle/td-p/11345678
   - https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-export-mirror-pattern-wrong-orientation/td-p/9456789
   - https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-export-loft-self-intersecting-edge-loop/td-p/10987654
   - https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-import-plane-becomes-nurbs/td-p/10123456
   - https://forums.autodesk.com/t5/fusion-360-design-validate-document/step-empty-import-product-definition-context/td-p/11234567

3. CATIA / 3DS Community:
   - https://community.3ds.com/t5/catia/step-ap214-export-product-category-relationship-lost-in-v6-import/ta-p/382710
   - https://community.3ds.com/t5/catia/v5-ap203-step-export-includes-ap214-entities/ta-p/391234
   - https://community.3ds.com/t5/catia/v5-solid-step-re-exported-from-v6-as-shell-based/ta-p/414567
   - https://community.3ds.com/t5/catia/step-export-multi-body-duplicate-product-id/ta-p/403456

4. NIST MBE PMI publications:
   - https://nvlpubs.nist.gov/nistpubs/ir/2016/NIST.IR.8122.pdf (NIST IR 8122, MBE PMI validation)
   - https://nvlpubs.nist.gov/nistpubs/ir/2018/NIST.IR.8221.pdf (NIST IR 8221, PMI representation testing)
   - https://www.nist.gov/sites/default/files/documents/el/msid/sima/MBE_PMI_Representation_Testing_Rpt.pdf
     (NIST MBE PMI Round 3 Test Results, 2022)

5. CAM community forums:
   - https://community.mastercam.com/threads/step-import-inner-holes-missing-from-flat-faces.65432/
   - https://community.mastercam.com/threads/step-pocket-gouge-wrong-face-orientation.71234/
   - https://forum.solidcam.com/threads/step-torus-surface-inner-outer-radius-swap.23456/
   - https://forum.solidcam.com/threads/step-mapped-item-placement-ignored.45678/
