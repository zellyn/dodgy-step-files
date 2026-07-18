# B4 Mining Wave-9 Audit — 2026-07-02

## Background

Wave-8 (76.0% novelty) exhausted the AP242 Ed.3 non-kinematics seam by mining the remaining ~16
Ed.3 entities. All wave-7/wave-8 Ed.3 catalog additions are shipped as `Pmi144`–`Pmi147` and the
wave-8 DEFERRED items. The task brief pointed at "AP242 Ed.3 kinematics module" as the top wave-9
candidate, but the steptools.com Ed.3 change notes and cross-checked ISO status make it clear:

**Ed.3 (2022) added NO new kinematics entities** — it is a corrective maintenance edition. The
kinematics module lives in the AP242 Ed.1 Domain Model (retired 53 AP214/AP203 entities and
introduced 533 new definitions for kinematics/assembly/PMI). The Ed.1 kinematic module is
already DEFERRED as **DEF-MM** in BACKLOG.md, blocked on an oracle. **The genuinely new
kinematics seam is AP242 Ed.4** (ISO 10303-242:2025 Ed.4, published 2025-08), which extends
kinematics with structural joints and fasteners linked to xMCF, and which is being actively
tested by the CAx-IF/JT-IF in Round 56J (August 2025).

Wave-9 pivots to:

- **AP242 Ed.2 MR Domain Model XML Kinematics Rec. Practices v1.0** (CAx-IF/JT-IF, 26-Nov-2021):
  22 documented kinematic-pair kinds, ~20 unit-test models, four open Bugzilla maintenance
  issues in Annex B, and **explicit "not supported by NX/CATIA" markers on 8 pair kinds**.
  This is the richest single-document interoperability seam surfaced in any wave so far.
- **CAx-IF Round 56J Test Suite** (August 2025) — 22 KM4 kinematic-pair test suffixes, plus
  Persistent-ID/UUID_SET_ITEM defect classes (`num_kin_pair_place`, `valid_kin_pair`,
  `kin_limits`, `kin_mech_valprops` statistics for pass/fail categorisation).
- **OCCT GitHub tracker 2025 H1** — issues #349, #382, #384, #417, #430, #484, #507, #512, #572,
  #682, #688, #1200 (post-wave-8 sample), particularly the NIST-PMI GT-magnitude polymorphism
  gap (#384), the OBJ-export sphere-seam class (#430), the `guage.zip` "Nothing to transfer"
  class (#484), and #349 `bldc_driver` (wave-8 E20 revisited).
- **AP242 Ed.4** (ISO 10303-242:2025 Ed.4, Aug 2025) — kinematics extended with **STRUCTURAL_JOINT**
  and fastener linkage to xMCF (external Mechanical Connection Format). The new-entity family
  in Ed.4 mirrors the Ed.3 leader-line family class already mined in wave-8 (new-entity-dropped-
  by-older-reader).

Sources evaluated but not primary:

- AP242 Ed.3 change notes — confirmed exhausted (wave-7 + wave-8 covered all 21 new Ed.3
  entities; no kinematics in Ed.3).
- STEP-NC additive-manufacturing 2025 paper (Springer *Int J Adv Manuf Technol* — DOI
  10.1007/s00170-025-15290-8) — no entity-level defects; taxonomic recommendations only.
- Onshape/SolidWorks/Fusion 360 forum threads 2025 — surfaced but the patterns already have
  matches in catalog (E22 wave-8 hit; also Xp025, A068, Ps015 etc.).
- ZIP/UTF-8 compressed STEP (Ed.3) — `Ad110`/`Ad111`/`Ad112`/`Ad113` already exhaustively cover
  the compression-bomb class.
- STEP-XML `.stpx` — `P012` covers the "receiver rejects .stpx" class. Ed.3 XML alternative
  encoding conversion-loss classes were spot-checked below (F16) but the mechanism reduces to
  the AP242 XML Kinematics Rec. Practices Bugzilla issues, which are much richer.

---

## Sources Chosen

| # | Source | Why chosen |
|---|--------|-----------|
| 1 | **CAx-IF/JT-IF AP242 Ed.2 MR Domain Model XML Kinematics Rec. Practices v1.0** (26-Nov-2021, 81pp) | Documents 22 kinematic-pair kinds with 8 explicit "not supported by NX/CATIA" markers + 4 open Bugzilla issues (#6271, #7908, #8578, #9073) + 3 explicit "not supported by NX/CATIA" post-processor rewrite recipes. Corresponds one-to-one to CAx-IF Round 56J suffixes. |
| 2 | **CAx-IF Round 56J Test Suite** (v1.0, 1-Aug-2025, 1884 lines text) | Names 22 KM4 suffixes; encodes AP242 Ed.4 Release Candidate schema; defines pass/fail predicates that will show up in vendor reports across 2025-2026. |
| 3 | **AP242 Ed.4 (ISO 10303-242:2025 Ed.4, published 2025-08)** — kinematics + structural-joint + xMCF fastener extensions | Post-wave-8 seam; STRUCTURAL_JOINT and xMCF link entities are the direct analogue of the wave-8 Ed.3 leader-line entity family. |
| 4 | **OCCT GitHub tracker 2025 H1** — issues surfaced post-wave-8 sampling | #384, #430, #484, #349, #1200 + ancillary; recent enough to be untouched by prior waves. |
| 5 | **Hubert Hautmann (AUDI AG) STEPDay2024 presentation** "STEP AP242 XML Kinematic" (13-Nov-2024, PDF) | Vendor-side status: KM2 (2020) → KM3 → KM4 (2024) test model progression; identifies "Multiple occurrences of kinematic mechanism and structure" as an open challenge. |
| 6 | **PTC Community — "Kinematic information exchange via STEP AP242 XML format"** (idea 807709) | Creo has not implemented AP242 XML Kinematics import as of 2024; user requests the capability. Confirms vendor gap in receiver-side implementation. |

---

## Defect Catalog (25 defects sampled)

Format per entry: pattern, entities, source, novelty judgment.

---

### F01 — AP242 XML Kinematics: `spherical_pair_with_pin` neither exported by CATIA nor imported by NX

**Pattern:** STEP AP242 Domain Model XML file containing a `KinematicPair` whose `Kind` is
`spherical_pair_with_pin` (2-DOF elbow-style pair — yaw + pitch rotation about intersecting axes).
The Rec. Practices explicitly note: "not supported by CATIA nor NX." A file authored by (e.g.)
Siemens JT that carries this pair kind, when imported into CATIA V6 or NX, silently drops the
pair from the mechanism graph — the mechanism topology is missing one edge and the receiving
CAD system's mechanism-solver reports a degrees-of-freedom mismatch. The rec-practice does not
prescribe a downgrade path (unlike `universal_pair`, which has an explicit "map as two cylindrical
pairs" downgrade recipe).

**Entities:** `KINEMATIC_PAIR` / `LOW_ORDER_KINEMATIC_PAIR` (Kind='spherical_pair_with_pin'),
`KINEMATIC_LINK`, `AXIS_PLACEMENT_3D` (PairFrame1/2), `MECHANISM_STATE`

**Source:** https://www.mbx-if.org/home/wp-content/uploads/2024/05/rec_prac_ap242xml_kinematics_v1.0.pdf §4.3.1 (p.32)

**Confidence:** HIGH — receiver-side implementation gap documented verbatim.
**Oracle verify needed?** YES — same blocker as DEF-MM (need HOOPS Exchange / ST-Developer).

**Novel?** YES — DEF-MM covers a single generic `REVOLUTE_PAIR`/`KINEMATIC_JOINT` two-link
mechanism; there is no catalog entry for the "pair-kind unsupported by receiver, no documented
downgrade recipe" defect class. Distinct from Pmi075 (self-loop joint referencing the same link
twice — a graph-topology defect, not a pair-kind gap). **NOVEL**.

---

### F02 — AP242 XML Kinematics: `unconstrained_pair` (6-DOF) not supported by NX or CATIA

**Pattern:** STEP AP242 Domain Model XML file with a `KinematicPair` whose `Kind` is
`unconstrained_pair` — a 6-DOF pair (rare; used to model a floating base or a temporarily
unconstrained connector). The Rec. Practices flag: "not supported by NX and CATIA." Neither
receiver has an established downgrade path. Import silently drops the pair. Distinct from F01
because `unconstrained_pair` semantically permits limits on **all six** axes (three rotation +
three translation), so the downstream information loss is strictly greater than F01's 2-DOF
gap.

**Entities:** `KINEMATIC_PAIR` (Kind='unconstrained_pair'), `KINEMATIC_LINK`,
`LowerLimitActualRotation{X,Y,Z}` + `LowerLimitActualTranslation{X,Y,Z}` attribute pairs

**Source:** https://www.mbx-if.org/home/wp-content/uploads/2024/05/rec_prac_ap242xml_kinematics_v1.0.pdf §4.3.1 (p.32)

**Confidence:** HIGH.
**Oracle verify needed?** YES.

**Novel?** YES — 6-DOF unconstrained joint is distinct from any joint kind in DEF-MM or the
Pmi075 catalog entry. **NOVEL**.

---

### F03 — AP242 XML Kinematics: `universal_pair` in target NX must be re-expressed as two cylindrical pairs (post-processor rewrite lossy)

**Pattern:** STEP AP242 Domain Model XML file with a `KinematicPair` of Kind `universal_pair`
(2-DOF Cardan joint). NX does not support `universal_pair` directly; the Rec. Practices
prescribe: "If the universal pair is not supported by the target CAD system (for example NX),
it shall be imported as the combination of two cylindrical pairs (between the cross and both
brackets of the universal pair)." The rewrite loses the identity of the original pair — the
receiver's mechanism graph now has one extra intermediate link (the notional "cross"), so any
downstream tool referring to the original pair by name (motion-coupling, drive-actuation,
FMU/URDF export) breaks.

**Entities:** `KINEMATIC_PAIR` (Kind='universal_pair'), rewritten to two `CYLINDRICAL_PAIR` with
an inserted intermediate `KINEMATIC_LINK`

**Source:** Kinematics Rec. Practices v1.0 §4.3.1 (p.34); NX symbol table

**Confidence:** HIGH.
**Oracle verify needed?** YES.

**Novel?** YES — "receiver-side pair-kind rewrite loses pair identity + inserts phantom
intermediate link" is a distinct data-loss class. No existing catalog entry captures it.
**NOVEL**.

---

### F04 — AP242 XML Kinematics: CATIA CV joint maps as two universal pairs — sender-side pair-kind bifurcation

**Pattern:** STEP AP242 Domain Model XML file exported from CATIA V6 containing what the user
authored as a single "CV joint" (constant-velocity joint). Per Rec. Practices §4.3.1: "The
CATIA CV joint shall be mapped as the combination of two universal pairs (as mapped internally
by CATIA)." Instead of a single `homokinetic_pair`, the CATIA writer emits **two** consecutive
`universal_pair` instances joined by a phantom intermediate `KinematicLink` with an
"internal-implementation-detail" name. A downstream consumer that expected a single homokinetic
pair (per the ISO Part 105 catalogue) sees a heavier mechanism graph and cannot round-trip back
to a CATIA CV joint if editing the graph.

**Entities:** two `KINEMATIC_PAIR` (Kind='universal_pair') joined by a phantom `KINEMATIC_LINK`

**Source:** Kinematics Rec. Practices v1.0 §4.3.1 (p.34) preprocessor recommendation

**Confidence:** HIGH.
**Oracle verify needed?** YES.

**Novel?** YES — CATIA-specific sender bifurcation is a distinct writer-behaviour class. Not the
same as F03 (which is receiver-side rewrite). **NOVEL**.

---

### F05 — AP242 XML Kinematics: `rolling_curve_pair` (high-order) not supported by NX

**Pattern:** STEP AP242 Domain Model XML with a `HighOrderKinematicPair` whose Kind is
`rolling_curve_pair` (two curves rolling without slipping — cam-follower archetype). Per Rec.
Practices §4.3.2 (p.39): "not supported by NX." No downgrade path; NX drops the pair on import.
Distinct from `sliding_curve_pair` (NX symbol '"curve on curve"' *is* supported). Distinct also
from `planar_curve_pair` (which is a supertype, but does not carry the rolling constraint —
importing rolling as planar loses the no-slip constraint).

**Entities:** `HIGH_ORDER_KINEMATIC_PAIR` (Kind='rolling_curve_pair'), `CurveOrSurface1/2`
references to `ADVANCED_FACE.EDGE_CURVE`, `Orientation` (x-axis-agreement flag)

**Source:** Kinematics Rec. Practices v1.0 §4.3.2 (p.39)

**Confidence:** HIGH.
**Oracle verify needed?** YES.

**Novel?** YES — high-order pair kind, distinct from all low-order pair defects in F01–F04.
**NOVEL**.

---

### F06 — AP242 XML Kinematics: `rolling_surface_pair` / `sliding_surface_pair` (high-order) not supported by NX nor CATIA

**Pattern:** STEP AP242 Domain Model XML with a `HighOrderKinematicPair` whose Kind is
`rolling_surface_pair` or `sliding_surface_pair` (two-surface rolling or sliding contact —
ball-bearing / gear-mesh archetypes). Rec. Practices §4.3.2 (p.40) explicitly: "not supported
in NX and CATIA." Both receivers silently drop the pair. Distinct from F05 (curve-curve) —
these are surface-surface. Distinct from `sliding_curve_pair` which IS supported (as "curve on
curve" in NX).

**Entities:** `HIGH_ORDER_KINEMATIC_PAIR` (Kind='rolling_surface_pair' or 'sliding_surface_pair'),
`CurveOrSurface1/2` referencing `ADVANCED_FACE.face_geometry`, `Orientation` (z-direction-agreement
flag between the two surfaces)

**Source:** Kinematics Rec. Practices v1.0 §4.3.2 (p.40)

**Confidence:** HIGH.
**Oracle verify needed?** YES.

**Novel?** YES — surface-surface high-order pair, distinct from F05's curve-curve. **NOVEL**.

---

### F07 — AP242 XML Kinematics: Bugzilla #6271 — `KinematicLinkToOccurrenceAssociation` cardinality constraint unenforceable

**Pattern:** STEP AP242 Domain Model XML file that violates the "each Part Occurrence
referenced by at most one KinematicLink per Mechanism" cardinality rule — a single occurrence
is referenced by two distinct `KinematicLink`s within the same `Mechanism`. The rule is
prescribed in Rec. Practices §4.2 (p.21) but is NOT expressible in the XSD (Bugzilla #6271
"under discussion" as of Nov 2021, target AP242 Ed.3 — still unresolved through Ed.4). Receiver
implementations diverge: some silently pick one link, others error, some raise a duplicate-link
warning. Any downstream mechanism solver sees an ambiguous graph.

**Entities:** `KINEMATIC_LINK` (multiple, one occurrence),
`KINEMATIC_LINK_TO_OCCURRENCE_ASSOCIATION`, `NEXT_ASSEMBLY_USAGE_OCCURRENCE`

**Source:** Kinematics Rec. Practices v1.0 §4.2 (p.21), Bugzilla #6271, Annex B

**Confidence:** HIGH — documented open ISO maintenance issue.
**Oracle verify needed?** YES.

**Novel?** YES — cardinality-unenforceable-in-XSD is a distinct schema-hole class. Pmi075
(self-loop joint) is a validity violation at DATA level, not an XSD-level unenforceable
constraint. **NOVEL**.

---

### F08 — AP242 XML Kinematics: Bugzilla #7908 — `LowOrderKinematicPairWithMotionCoupling` supports only 2 links (Link1/Link2), not 4

**Pattern:** STEP AP242 Domain Model XML file where a gear train with an idler gear or a
compound rack-pinion mechanism needs 3-4 links coupled by motion (input shaft, idler, output
shaft). The `LowOrderKinematicPairWithMotionCoupling` entity has only `Link1`/`Link2` fields —
Bugzilla #7908 (still "under discussion" as of Rec. Practices v1.0) requests adding `Link3`/
`Link4`. Producers work around by cascading two separate `LowOrderKinematicPairWithMotionCoupling`
instances with a shared intermediate link; the intended atomic coupling is lost.

**Entities:** `LOW_ORDER_KINEMATIC_PAIR_WITH_MOTION_COUPLING` (Kind='gear_pair' or
'rack_and_pinion_pair'), two chained instances with a phantom idler link

**Source:** Kinematics Rec. Practices v1.0 §4.3.3, Bugzilla #7908, Annex B

**Confidence:** HIGH.
**Oracle verify needed?** YES.

**Novel?** YES — distinct from F04 (CATIA-side workaround for a low-order pair): F08 is
schema-level insufficient-arity for a specific pair-kind class. **NOVEL**.

---

### F09 — AP242 XML Kinematics: Bugzilla #9073 — `ProductStructureKinematicPathAssociation` cannot carry a property value

**Pattern:** STEP AP242 Domain Model XML file where a designer wants to attach a design
property (e.g., a lubrication interval, a fatigue rating, a certification annotation) to a
kinematic path — the graph-walk sequence of pairs from base link to end-effector. The entity
`ProductStructureKinematicPathAssociation` is NOT in the `PropertyAssignmentSelect` union
(Bugzilla #9073, "new" as of Nov 2021). Downstream downstream-consumption tools cannot attach
the property; it must be attached to individual pairs, which loses the path-scoped semantics.

**Entities:** `PRODUCT_STRUCTURE_KINEMATIC_PATH_ASSOCIATION`, `PROPERTY_VALUE_ASSIGNMENT` (not
allowed by AP242 Ed.2 schema on this target)

**Source:** Kinematics Rec. Practices v1.0 §4.9, §4.13, Bugzilla #9073, Annex B

**Confidence:** HIGH.
**Oracle verify needed?** YES.

**Novel?** YES — property-attachment-not-in-schema is a distinct class. **NOVEL**.

---

### F10 — AP242 XML Kinematics: Bugzilla #8758 — `KinematicLinkToOccurrenceAssociation` cannot carry a `Substructure` reference

**Pattern:** STEP AP242 Domain Model XML file where a moving assembly node (not an atomic part)
is the target of a `KinematicLink`, and the sender wants to specify which specific occurrence
inside the assembly holds the pair frame's `AxisPlacement`. Per Rec. Practices §4.2 remark:
"the occurrence path from the occurrence of the single part where the AxisPlacement has been
computed is currently lost" — no `Substructure` field exists on
`KinematicLinkToOccurrenceAssociation`. Bugzilla #8758 requests it be added. On import, "any"
part under the moving assembly ends up holding the AxisPlacement, producing wrong-part-tagged
pair frames on round-trip.

**Entities:** `KINEMATIC_LINK`, `KINEMATIC_LINK_TO_OCCURRENCE_ASSOCIATION` (missing
`Substructure` attribute), `AXIS_PLACEMENT_3D`

**Source:** Kinematics Rec. Practices v1.0 §4.2 remark (p.21), Bugzilla #8758

**Confidence:** HIGH.
**Oracle verify needed?** YES.

**Novel?** YES — sub-structure-path-loss is a distinct schema-gap class. **NOVEL**.

---

### F11 — AP242 XML Kinematics: `spherical_pair` 3-axis limits not supported by NX (only single Z-axis actuation retained)

**Pattern:** STEP AP242 Domain Model XML with a `spherical_pair` (3-DOF pair — yaw + pitch +
roll about a common point). Per Rec. Practices §4.3.1 (p.31) remark: "Rotation Lower/UpperLimits
may be specified around all 3 axis (not supported by NX)." A sender that specifies
`LowerLimitActualRotationX/Y` in addition to Z will have the X/Y limits silently dropped on NX
import; the imported joint has only the Z-axis limit. Distinct from F01 (which is the
`spherical_pair_with_pin` 2-DOF pair kind — a completely different pair kind).

**Entities:** `KINEMATIC_PAIR` (Kind='spherical_pair'),
`LowerLimit/UpperLimitActualRotation{X,Y,Z}` (X and Y silently dropped by NX)

**Source:** Kinematics Rec. Practices v1.0 §4.3.1 (p.31)

**Confidence:** HIGH.
**Oracle verify needed?** YES.

**Novel?** YES — receiver-side attribute-subset silent-drop is a distinct class from F01/F03
(which are entire-pair-kind drops). **NOVEL**.

---

### F12 — AP242 XML Kinematics: `planar_pair` 3-attribute limits not supported by NX (Z-rotation + X/Y-translation)

**Pattern:** STEP AP242 Domain Model XML with a `planar_pair` (3-DOF pair — Z-rotation +
X/Y-translation in a plane, e.g., a coin sliding on a table). Per Rec. Practices §4.3.1 (p.29)
remark: "According to Part 105, both rotation and Translation Lower/UpperLimits may be
specified: around the Z axis (Rotation) and along the X and Y axis (Translation) (not
supported by NX)." NX imports the pair with all three limits silently dropped, leaving the
plane pair effectively unconstrained.

**Entities:** `KINEMATIC_PAIR` (Kind='planar_pair'), `LowerLimitActualRotationZ`,
`LowerLimitActualTranslationX`, `LowerLimitActualTranslationY`

**Source:** Kinematics Rec. Practices v1.0 §4.3.1 (p.29)

**Confidence:** HIGH.
**Oracle verify needed?** YES.

**Novel?** YES — planar pair with three-way limit silent-drop; distinct from F11 (spherical) by
pair kind and by attribute set. **NOVEL**.

---

### F13 — CAx-IF Round 56J: `kin_mech_valprops` validation-property partial-match failure mode (`all/partial/none`)

**Pattern:** STEP AP242 Domain Model XML file where the sender declares validation properties
for a `Mechanism` (per Rec. Practices §4.13.2 — attributes like num-links, num-pairs, joint-type
histogram). On import to a receiver, some properties match and some do not — the receiver's
mechanism graph has been rewritten (e.g., per F03 or F04). Round 56J's `kin_mech_valprops`
statistic is `all/partial/none` — a `partial` outcome signals silent degradation between
sender's intended graph and receiver's actual graph. The catalog currently has no fixture
demonstrating "sender's validation-property count disagrees with receiver's post-import
mechanism count."

**Entities:** `MECHANISM_REPRESENTATION`, `PROPERTY_DEFINITION_REPRESENTATION` with
`num_kin_pair_place` / `num_kin_pair` / `num_kin_mech_valprops` counts

**Source:** CAx-IF Round 56J Test Suite v1.0 §2.5 (p.25)

**Confidence:** MEDIUM — the defect exists in principle but the specific miscount depends on
which downgrade recipe (F03/F04) was triggered.
**Oracle verify needed?** YES.

**Novel?** YES — validation-property partial-match is a distinct outcome class from
whole-mechanism-drop or whole-pair-drop. **NOVEL**.

---

### F14 — CAx-IF Round 56J: `chain` / `groups` / `multiple_occurrences` structure-tests exercise flat-vs-hierarchical mechanism structure

**Pattern:** STEP AP242 Domain Model XML with a `Mechanism` whose kinematic-pair chain crosses
assembly-hierarchy boundaries — a `KinematicLink` references an occurrence at level-3 of the
assembly, and a `KinematicPair` connects it to a `KinematicLink` referencing an occurrence at
level-5 of a different sub-assembly branch. Per Rec. Practices §4.5, most CAD systems require
assembly nodes involved in `KinematicPair` to have no further `KinematicPair`s between their
components ("rigidity rule"). Round 56J's `KM4_chain`, `KM4_grps`, `KM4_multi`, `KM4_spec`
suffixes stress the "flatten vs preserve" hierarchy decision. Receivers silently pick one
strategy; sender's original hierarchy is lost.

**Entities:** `MECHANISM_REPRESENTATION`, `KINEMATIC_LINK`,
`NEXT_ASSEMBLY_USAGE_OCCURRENCE` (chain of ≥3 levels)

**Source:** CAx-IF Round 56J Test Suite v1.0 §2.5.4 (p.24); Kinematics Rec. Practices v1.0
§4.5 (p.53)

**Confidence:** MEDIUM.
**Oracle verify needed?** YES.

**Novel?** YES — cross-hierarchy pair-link is a distinct class from F13's property-partial-match.
**NOVEL**.

---

### F15 — AP242 Ed.4 (Aug 2025) `STRUCTURAL_JOINT` linked to xMCF fastener: entity dropped by Ed.3 and earlier readers

**Pattern:** STEP AP242 Ed.4 file with a `STRUCTURAL_JOINT` entity linking two parts through a
mechanical fastener (bolt, rivet, weld) with an accompanying reference to an xMCF (Mechanical
Connection Format) external artifact carrying the joint's mechanical properties (pre-load,
torque, spring constants). Ed.3 / Ed.2 / AP214 readers do not recognise `STRUCTURAL_JOINT`;
the entity is silently dropped. The B-rep geometry loads and the parts appear as two rigid
bodies; the joint linkage — and any pre-tension or FEA hand-off it enables — vanishes.
Analogous to wave-8's E01–E14 pattern (Ed.3 new entity silently dropped by Ed.2 reader), but
targeting the Ed.4 fastener seam.

**Entities:** `STRUCTURAL_JOINT` (Ed.4 new), `MECHANICAL_FASTENER_LINK`, `xMCF_EXTERNAL_REFERENCE`

**Source:** https://www.ap242.org/edition-4.html; ISO 10303-242:2025 Ed.4

**Confidence:** MEDIUM — Ed.4 is a fresh publication (Aug 2025); the exact entity names above
are inferred by analogy to Ed.3 leader-line naming; entity spelling in the actual EXPRESS
schema may differ, but the "new Ed.4 entity silently dropped by Ed.3 reader" defect class is
robust.
**Oracle verify needed?** YES — requires access to Ed.4 EXPRESS schema (not free).

**Novel?** YES — the entire Ed.4 STRUCTURAL_JOINT + xMCF family is post-Ed.3, so wave-7/wave-8
Ed.3-focused mining did not touch it. **NOVEL**.

---

### F16 — AP242 XML alternative encoding: EXPRESS `SELECT` types cannot round-trip through XSD "combined" restriction

**Pattern:** STEP AP242 Domain Model XML file with an EXPRESS-level `SELECT` type that the
Kinematics Rec. Practices §1.1.9 legend explicitly flags: "SelectType1 combined (not supported
by XML)." Certain SELECT-type instances that are valid in the P21 encoding cannot be expressed
in the XML alternative encoding at all — the round-trip P21 → XML → P21 loses SELECT variance,
collapsing to a single arbitrary branch. The Kinematics doc calls out this class explicitly in
its XSD notation legend (p.9); it is not a per-entity gap but a structural encoding limitation.

**Entities:** any EXPRESS `SELECT` union type instantiated in P21 (e.g.,
`ComposedOrExternalGeometricModelSelect`, `RepresentedDefinition`, `Curve/Surface.External`)

**Source:** Kinematics Rec. Practices v1.0 §1.1.9 (p.9) XSD-notation legend

**Confidence:** HIGH — this is documented in the XSD-notation legend directly.
**Oracle verify needed?** YES — requires an XML-to-P21 converter (e.g., stp2bom).

**Novel?** YES — no catalog entry covers "SELECT variance lost via XML round-trip." The nearest
is `P012` (`.stpx` / `.stpz` unsupported) which is about the entire file variant being
rejected, not about SELECT-variance loss inside a supported XML variant. **NOVEL**.

---

### F17 — OCCT #384: `geometric_tolerance.magnitude` polymorphism gap — `StepRepr_ReprItemAndLengthMeasureWithUnitAndQRI` not recognised as `MEASURE_WITH_UNIT` by 21 tolerance-reader classes

**Pattern:** STEP AP242 file (e.g., `nist_ctc_01_asme1_ap242-e1.stp`, `nist_stc_10_asme1_ap242-e2.stp`)
where a `GEOMETRIC_TOLERANCE` (any of Angularity, CircularRunout, Coaxiality, Concentricity,
Cylindricity, Flatness, LineProfile, Parallelism, Perpendicularity, Position, Roundness,
Straightness, SurfaceProfile, Symmetry, TotalRunout, or Unequally-Disposed variants) has its
`magnitude` attribute encoded as a complex entity of type
`StepRepr_ReprItemAndLengthMeasureWithUnitAndQRI` or `StepRepr_ReprItemAndPlaneAngleMeasureWithUnitAndQRI`.
Twenty-one OCCT reader classes hard-code the type check as `IsKind("StepBasic_MeasureWithUnit")`,
which fails on these complex parent types — the tolerance magnitude reads as null across all
21 tolerance kinds.

**Entities:** `GEOMETRIC_TOLERANCE` (and 20 subtypes), `MEASURE_REPRESENTATION_ITEM`,
complex-form `(LENGTH_MEASURE_WITH_UNIT() MEASURE_REPRESENTATION_ITEM() MEASURE_WITH_UNIT(…)
REPRESENTATION_ITEM(''))`

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/384

**Confidence:** HIGH — closed issue with detailed reproducer + fix in Release 8.0.
**Oracle verify needed?** NO — OCCT 8.0 fixes; older OCCT returns null.

**Novel?** NO — `Pmi068` (line 44155) already covers "GEOMETRIC_TOLERANCE magnitude returns
null via indirect chain," and the wider MEASURE_WITH_UNIT polymorphism defect is at
`STEP_PROBLEM_CATALOG.md:4908`. The 21-reader class extent of the defect is a scope-widening
signal but the pattern-signature is already in the catalog. **HIT**.

---

### F18 — OCCT #430: BRepMesh seam-vertex duplication on small-radius sphere OBJ export

**Pattern:** STEP file containing a `SPHERICAL_SURFACE` face (e.g., an atomic sphere) that,
when tessellated by `BRepMesh_IncrementalMesh` and exported to Wavefront OBJ via manual
`BRep_Tool::Triangulation` + vertex/face dump, exhibits a visible seam defect at the periodic
seam of the sphere — vertices near the seam are duplicated at slightly-different UV
coordinates, and the OBJ face indices reference these duplicates asymmetrically. Effect is
strongly radius-dependent (defect at R=0.5, gone at R=13.5). Not a triangulation quality issue
(the raw `Poly_Triangulation` is consistent) but a UV-seam-vertex-index-numbering issue at the
OBJ-export boundary.

**Entities:** `SPHERICAL_SURFACE`, `ADVANCED_FACE` with seam edge on the sphere equator,
downstream OBJ face-index generation

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/430

**Confidence:** MEDIUM — the defect reproduces per the issue tracker, but the mechanism is
downstream of `Poly_Triangulation` — it is in the OBJ writer's vertex-index generation.
**Oracle verify needed?** NO — OCCT ships the defective writer.

**Novel?** YES — no catalog entry covers "OBJ-export vertex-duplication at periodic surface
seam." Pmi062 is glTF-writer inflation (different mechanism, different output format). Gs187
is null triangulation (different symptom class — zero triangles vs seam mis-index).
**NOVEL** (small-radius sphere OBJ export).

---

### F19 — OCCT #484: `guage.zip` — "Nothing to transfer" on file that FreeCAD + CAD Assistant also cannot import but "some other CAD software" can

**Pattern:** STEP file where `STEPControl_Reader::NbRootsForTransfer` returns 0 (or all root
transfers succeed but `NbShapes == 0`), causing `RetVoid` return. The file loads and parses
(no read error) but produces no shape roots. The user reports that FreeCAD and CAD Assistant
also fail, but "some other CAD software" (unspecified) succeeds — implying the root-entity
discovery heuristic differs across kernels. Distinct from `P015` / `A102` (kernel silently
drops file body — those are cases where roots ARE found but the transfer downstream drops the
geometry).

**Entities:** valid `PRODUCT_DEFINITION_SHAPE`, `SHAPE_DEFINITION_REPRESENTATION` chain but
without the specific `ADVANCED_BREP_SHAPE_REPRESENTATION` or `MANIFOLD_SURFACE_SHAPE_REPRESENTATION`
that OCCT's root-selection filter looks for; alternative shape-representation forms (e.g.,
`GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION`) that OCCT does not treat as a
`transferable` root.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/484

**Confidence:** MEDIUM — reproducer exists but the mechanism is not root-caused.
**Oracle verify needed?** NO — OCCT reports the outcome directly.

**Novel?** YES — "Nothing to transfer with 0 roots" is a distinct failure mode from
silent-empty-body. Some catalog entries treat "silent empty" as the outcome but do not
specifically address "no roots detected." **NOVEL**.

---

### F20 — OCCT #349 (revisited): `bldc_driver.STEP` — no root-cause, but the class deserves a specific fixture-pattern label

**Pattern:** STEP file rendering with missing/incorrect faces in OCCT DRAW while FreeCAD
renders correctly. Wave-8's E20 dismissed this as "no mechanism identified" and marked HIT.
Revisiting: the specific class here is "silently loads with an OCCT-side face-visibility gap
that the SEND-side does not exhibit" — the file is valid, the DRAW harness completes without
error, but some faces are missing from the display AIS. Comment thread reveals the file uses
a specific ordering of `FACE_OUTER_BOUND` / `FACE_BOUND` that OCCT-Draw filters differently
than FreeCAD's XCAF display.

**Entities:** `ADVANCED_FACE`, `FACE_BOUND` vs `FACE_OUTER_BOUND` (mixed usage)

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/349

**Confidence:** LOW — mechanism still not root-caused after 12 comments on the issue.
**Oracle verify needed?** N/A — kernel-specific display defect.

**Novel?** NO — same verdict as wave-8 E20; without a specific entity-level mechanism, the
pattern reduces to the generic "OCCT importer drops faces on well-formed input" class already
covered by A102, P015, and family. **HIT** (repeat of wave-8 E20 verdict).

---

### F21 — OCCT #1279 (Mantis 32819): `VrmlAPI_Writer` does not honour hierarchical XCAFDoc color inheritance

**Pattern:** STEP file with per-assembly-branch color inheritance — a top-level assembly node
has a `STYLED_ITEM` + `COLOUR_RGB` chain applied at the assembly level; child parts inherit
via XCAF's `XCAFDoc_ColorTool::GetColor(label, XCAFDoc_ColorGen)`. When re-exported through
`VrmlAPI_Writer`, only the leaf-level appearance directly attached to `MESH` nodes is retained
— assembly-level inherited color is silently lost. `XCAFPrs_DocumentExplorer` traversal finds
the shapes-with-colors correctly, but `VrmlAPI_Writer` does not use that explorer.

**Entities:** `STYLED_ITEM` + `PRESENTATION_STYLE_ASSIGNMENT` + `COLOUR_RGB` chain at
assembly level; XCAF `XCAFDoc_ColorTool` hierarchical color lookup path

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/1279 (migrated from MANTIS 32819)

**Confidence:** HIGH — reproducer + comment thread + prior MANTIS ticket cross-reference.
**Oracle verify needed?** NO.

**Novel?** YES — VRML-writer-side color-inheritance-loss is a distinct output-format class
from A068 (XCAF root-label color not exported) and Xp025 (OCCT re-export drops colors). The
new signature is "STEP loads with colors correct, VRML writer drops inherited colors while
XCAF explorer sees them." **NOVEL**.

---

### F22 — OCCT #1200: `XCAFDoc_ShapeTool::FindSubShape` crash on `propeller.stp` in 8.0.0-rc5

**Pattern:** STEP file (`propeller.stp`) crashing `XCAFDoc_ShapeTool::FindSubShape` during
XCAF tree construction. Wave-8 did not sample this; but the catalog has **Ad084** which
directly references this issue (`OCCT #1200, propeller.zip`).

**Entities:** unspecified (propeller.stp)

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/1200

**Confidence:** covered.
**Oracle verify needed?** N/A.

**Novel?** NO — `Ad084` (line 16210) covers this exact issue by name. **HIT**.

---

### F23 — OCCT #1041: `BRepAlgoAPI_Fuse` on N-fold rotationally-arrayed copies of a STEP shape fails as N varies

**Pattern:** STEP file loaded into OCCT, then rotated by 360°/N and fused with the original
across N=1..7 occurrences. `BRepAlgoAPI_Fuse` produces a shape whose surface area is smaller
than N-1 times the source area — some faces are lost in the fuse across specific N values.
FreeCAD issue #27252 reports this from the user side; OCCT #1041 confirms the kernel-side
mechanism. Distinct from Boolean fuse defects on translated copies (line 4186 co-planar co-conical
merge). This is on rotational-symmetry axes; the fuse-tolerance interaction with rotation angles
of 360°/N for small N is the mechanism.

**Entities:** `MANIFOLD_SOLID_BREP` (any shape), `AXIS2_PLACEMENT_3D` rotation transform,
downstream `BRepAlgoAPI_Fuse`

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/1041 + FreeCAD/FreeCAD#27252

**Confidence:** MEDIUM.
**Oracle verify needed?** NO.

**Novel?** YES — rotational-fuse-tolerance interaction is a distinct class from translational-
overlap-fuse. **NOVEL** (Boolean modelling, not I/O; still within §12.12 or §12.8 scope).

---

### F24 — OCCT #507: address-sanitizer container-overflow during `BRepMesh_IncrementalMesh` on `file1.step` — deflection-dependent, WASM-affected

**Pattern:** STEP file that meshes cleanly in release builds (no crash) but triggers Clang
`AddressSanitizer` `container-overflow` when compiled with `-fsanitize=address` and meshed
with linear deflection 0.1 + angular deflection 1. The crash is deflection-parameter dependent
(other settings do not always trigger). WASM builds crash regardless of sanitizer settings.
Present in 7.7+, 7.9.0, master; absent in 7.6.3. Distinct from Pf008/Pf009 (stack overflow
under TBB): this is a heap-container overflow, and it is deflection-parameter-triggered.

**Entities:** unspecified — the file loads, the shape passes checkshape; the defect is at
`BRepMesh_IncrementalMesh` internal container extension

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/507

**Confidence:** MEDIUM.
**Oracle verify needed?** NO — sanitizer catches on OCCT 7.7+.

**Novel?** YES — Pf008/Pf009 are stack-overflow classes; this is a distinct heap-container
overflow that is deflection-parameter-sensitive. **NOVEL** (adversarial parameter combination).

---

### F25 — OCCT #1238: `XCAFDoc_DimTolTool::GetGDTPresentations` returns N-1 of N `DRAUGHTING_CALLOUT` entries when one callout name matches "Datum10@Plane4(A)" pattern

**Pattern:** STEP file containing four `DRAUGHTING_CALLOUT` entries where the fourth has a name
of the form `'Datum10@Plane4(A)'` (contains `@` and parentheses — a NIST-derived datum
callout). `GetGDTPresentations` returns three entries; the fourth is silently omitted. The
same file imported into SolidWorks 2025 with "Include PMI" imports all four correctly. The
mechanism is in OCCT's callout-name pattern filter — non-alphanumeric characters in the name
cause the callout to be skipped from the presentations map.

**Entities:** `DRAUGHTING_CALLOUT('Datum10@Plane4(A)', ...)`, `PROPERTY_DEFINITION_REPRESENTATION`,
XCAF `XCAFDoc_DimTolTool` presentation index

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/1238

**Confidence:** MEDIUM — reproducer file provided but the exact filter regex is not confirmed
in the issue thread.
**Oracle verify needed?** NO.

**Novel?** YES — callout-name-with-special-character silent-drop is a distinct class from the
existing DRAUGHTING_CALLOUT entries (which are about coplanarity, semantic-vs-graphic, or
count-based defects). **NOVEL**.

---

## Sources Exhausted

- **AP242 Ed.3 change notes**: no new kinematics entities in Ed.3 — kinematics lives in Ed.1
  (DEF-MM deferred) and now Ed.4 (F15). Ed.3 non-kinematics entities exhausted by wave-7 + wave-8.
- **ZIP / UTF-8 compressed STEP variants**: Ad110/Ad111/Ad112/Ad113 exhaustively cover
  compression-bomb classes; no new production-tool-side defects surfaced in searches.
- **STEP-NC additive-manufacturing**: 2025 Springer paper is taxonomic, not defect-specific;
  the STEP-NC seam is already covered by catalog entries around line 10500-10700 (`MACHINING_*`
  family).
- **Onshape/SolidWorks/Fusion 360 2025 forum threads**: patterns match existing catalog entries
  (Xp025, A068, Ps015, Tsh036, wave-8 E22).

---

## Unique Novel Count

Sampled: **25 defects**.
Novel: **F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13, F14, F15, F16, F18,
F19, F21, F23, F24, F25 = 22**.
HIT / dupe / out-of-scope: **F17 (Pmi068), F20 (repeat of wave-8 E20 verdict), F22 (Ad084) = 3**.

**Novelty: 22 / 25 = 88.0%**.

Caveats:

- F05 (`rolling_curve_pair`) and F06 (`rolling_surface_pair` / `sliding_surface_pair`) could
  plausibly be merged into ONE "high-order kinematic pair not supported by NX/CATIA" fixture;
  if merged, novel drops to 21 → 21/24 = 87.5%.
- F01/F02 (both "receiver-side unsupported pair kind") could be merged; if further merged,
  novel drops to 20 → 20/23 = 86.9%.
- F07/F08/F09/F10 are four distinct Bugzilla issues each on a distinct schema hole; they should
  NOT be merged — each is a separate ISO maintenance item.
- Conservative merged count: **20 novel / 23 unique = 87.0%**.

The 88% raw and 87% merged rate is the highest of any wave and reflects: (a) the AP242 XML
Kinematics Rec. Practices document contains ~40 pages of explicit "not supported by NX/CATIA"
markers and 4 open Bugzilla issues, and (b) none of the CAx-IF/JT-IF interoperability-forum
material has been previously mined.

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
| Wave 8 | AP242 Ed.3 remaining 16 entities + OCCT GitHub 2024-2026 + Fusion→Creo chamfer | 25 | 19 (16 after merges) | 76.0% (72.7% merged) |
| **Wave 9** | **AP242 XML Kinematics Rec.Practices + CAx-IF Round 56J + AP242 Ed.4 + OCCT 2025-H1** | **25** | **22 (20 after merges)** | **88.0% (87.0% merged)** |

Trend: 24.6% → 10.5% → 9.3% → 34.3% → 28.0% → 46.7% → 34.8% → 76.0% → **88.0%**

---

## Deferred List (novel entries requiring oracle verification or Ed.4 schema access)

Continuing from wave-8's DEF-EE last identifier. Wave-9 tags are **DEF-FFF through DEF-ZZZ**
(then rolls forward if needed).

| Tag | Wave-9 ID | Section | Description | Confidence | Oracle needed? |
|-----|-----------|---------|-------------|------------|----------------|
| DEF-FFF | F01 | §12-7-pmi / §12-7-kinematics | `spherical_pair_with_pin` neither exported by CATIA nor imported by NX; no documented downgrade recipe | HIGH | YES (HOOPS Exchange / ST-Developer) |
| DEF-GGG | F02 | §12-7-kinematics | `unconstrained_pair` (6-DOF) unsupported by NX and CATIA | HIGH | YES |
| DEF-HHH | F03 | §12-7-kinematics | `universal_pair` receiver rewrite to two cylindrical pairs loses identity, inserts phantom link | HIGH | YES |
| DEF-III | F04 | §12-7-kinematics | CATIA-side CV joint bifurcates into two `universal_pair` on export | HIGH | YES |
| DEF-JJJ | F05 | §12-7-kinematics | `rolling_curve_pair` (high-order) unsupported by NX | HIGH | YES |
| DEF-KKK | F06 | §12-7-kinematics | `rolling_surface_pair` / `sliding_surface_pair` (high-order) unsupported by NX and CATIA | HIGH | YES |
| DEF-LLL | F07 | §12-7-kinematics | Bugzilla #6271 — `KinematicLinkToOccurrenceAssociation` cardinality unenforceable in XSD | HIGH | YES |
| DEF-MMM (rename to avoid clash with existing DEF-MM) | F08 | §12-7-kinematics | Bugzilla #7908 — `LowOrderKinematicPairWithMotionCoupling` supports only 2 links | HIGH | YES |
| DEF-NNN | F09 | §12-7-kinematics | Bugzilla #9073 — `ProductStructureKinematicPathAssociation` not in `PropertyAssignmentSelect` | HIGH | YES |
| DEF-OOO | F10 | §12-7-kinematics | Bugzilla #8758 — `KinematicLinkToOccurrenceAssociation` missing `Substructure` field | HIGH | YES |
| DEF-PPP | F11 | §12-7-kinematics | `spherical_pair` X/Y-axis rotation limits silently dropped by NX | HIGH | YES |
| DEF-QQQ | F12 | §12-7-kinematics | `planar_pair` three-axis limits silently dropped by NX | HIGH | YES |
| DEF-RRR | F13 | §12-7-kinematics / §12-8-mixed | CAx-IF `kin_mech_valprops` partial-match after receiver rewrite (F03/F04) | MEDIUM | YES |
| DEF-SSS | F14 | §12-7-kinematics / §12-6-assembly | Mechanism graph crossing ≥3 assembly-hierarchy levels (rigidity-rule violation) | MEDIUM | YES |
| DEF-TTT | F15 | §12-7-pmi / §12-8-mixed | AP242 Ed.4 `STRUCTURAL_JOINT` + xMCF fastener link entity dropped by Ed.3 readers | MEDIUM | YES (Ed.4 EXPRESS schema) |
| DEF-UUU | F16 | §12-1a-encoding / §12-8-mixed | XML alternative encoding cannot round-trip EXPRESS `SELECT` variance | HIGH | YES (XML→P21 converter) |
| DEF-VVV | F18 | §12-14-mesh / §12-8-mixed | BRepMesh OBJ-export vertex-index duplication on small-radius sphere periodic seam | MEDIUM | NO |
| DEF-WWW | F19 | §12-1c-transfer | STEPControl_Reader "Nothing to transfer" (0 roots detected) on file that other kernels read | MEDIUM | NO |
| DEF-XXX | F21 | §12-6-assembly / §12-1c-transfer | `VrmlAPI_Writer` drops hierarchical XCAFDoc color inheritance (leaf-only) | HIGH | NO |
| DEF-YYY | F23 | §12-12-boolean / §12-8-mixed | `BRepAlgoAPI_Fuse` on N-fold rotationally-arrayed copies loses faces for specific N | MEDIUM | NO |
| DEF-ZZZ | F24 | §12-11-adversarial / §12-14-mesh | BRepMesh AddressSanitizer container-overflow deflection-parameter-dependent | MEDIUM | NO |
| DEF-AAAA | F25 | §12-7-pmi | `DRAUGHTING_CALLOUT` name with `@` or `()` characters silently dropped from `GetGDTPresentations` | MEDIUM | NO |

**Renaming note:** DEF-MM (existing) is AP242 Ed.1 kinematics — reused ID prefix for wave-9's
F08 was inadvertent; renamed to DEF-MMM. Wave-9 uses triple-letter IDs to avoid all collision
with wave-8's double-letter IDs (DEF-AA..DEF-EE).

---

## Strongest new seam

**The AP242 Ed.2 MR Domain Model XML Kinematics Rec. Practices document is the richest single
defect source encountered in any wave.** It contains 22 pair kinds, 8 explicit "not supported
by NX/CATIA" markers, 4 open Bugzilla issues (documented ISO-level schema holes), and 3 explicit
receiver-side rewrite recipes that lose pair identity. This drives F01–F14, i.e., 14 of the 25
sampled defects in a single well-defined source. Combined with the CAx-IF Round 56J test suite
that names each pair kind as a testable suffix (KM4_rev, KM4_gr90, KM4_pocs, etc.), each of
these defects has an immediate reference-implementation validation path via the interoperability
forum's semi-annual reporting cycle.

**Runner-up seam:** AP242 Ed.4 (published Aug 2025) STRUCTURAL_JOINT + xMCF fastener extensions
— the direct 2025 successor to wave-8's Ed.3 leader-line family, but requires Ed.4 schema
access to enumerate all new entities (currently gated behind ISO paywall). One entity sampled
(F15); expect ~10-20 more once Ed.4 change notes are published in HTML analogous to
`notes_ap242e3.html`.

---

## Interference-safe notes

- No sub-agents dispatched.
- Catalog not modified.
- Audit file at `/Users/zellyn/gh/dodgy-step-files/audit/b4_mining_wave_9_2026-07-02.md`
  (local only, not committed, not pushed).
- The two other parallel workstreams (DRIFT audit agent, mutation-test regen at PID 918
  writing `/tmp/qmut_full_v2.json`) were not touched. The bash calls in this task read GitHub
  issues, PDF converts to text, and grep — none write to `/tmp/qmut_full_v2.json` or the
  DRIFT-audit paths.
