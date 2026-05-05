# STEP Kernel Conformance Kit

A curated subset of the STEP-Defect Catalog (80 entries, ~6.2% of the full corpus) that any STEP-handling kernel should pass before being considered ready for production use. The Kit spans every defect class in the catalog's 15-tag taxonomy.

## How to use

For each entry, run your kernel against the fixture file (`step-examples/<section>/<id>.stp`). The expected outcome is given in `**Expected kernel behavior**:`. The catalog also documents what OCC actually does (`**OCC behavior**:`) and the model-level effect (`**Model impact**:`).

A kernel passes the Kit if:

- It produces an outcome in the entry's `allowed` set
- It does NOT produce any outcome in the `disallowed` set
- It does not crash, hang, or leak memory on adversarial entries

## Selection rationale

Entries in this Kit were chosen for:

1. Distinctness: each entry targets a different defect sub-class
2. Mechanical verifiability: every entry has byte-level or tier-3 (geometric/topological) assertions
3. Bytes-sufficient: defect lives in the `.stp` file alone, not in cross-file state, sibling pairs, or runtime-only behavior
4. Tag-coverage: at least 4 entries per taxonomy tag (mostly 5-7), spread across major catalog sections
5. Title brevity: sub-sub-class title-bloat (>120 chars) was excluded to keep canonical exemplars

## The Kit

### crash — kernel must not segfault, hang, or leak memory (5 entries)

- [A034](browse/12-6-assembly/A034.html): CheckSRRReversesNAUO segfault on SDR with SHAPE_ASPECT instead of PROPERTY_DEFINITION
- [Ad027](browse/12-11-adversarial/Ad027.html): STEP "zip bomb": 10⁷ tiny instances exhaust memory
- [Ad032](browse/12-11-adversarial/Ad032.html): Schema-EXPRESS rule recursion bomb
- [Gn002](browse/12-2b-nurbs/Gn002.html): RATIONAL_BSPLINE_CURVE / SURFACE with `NbWeights ≠ NbControlPoints`
- [Le040](browse/12-1a-encoding/Le040.html): `\Q\` numeric-character-reference at the upper Unicode boundary (U+10FFFF)

### silent-loss — entities or data dropped without diagnostic (6 entries)

- [Le054](browse/12-1a-encoding/Le054.html): High-bit byte ambiguous between Windows-1252 and ISO-8859-1
- [A001](browse/12-6-assembly/A001.html): Duplicated component instances collapsed to a single transform on export
- [A003](browse/12-6-assembly/A003.html): Empty / phantom assembly nodes (PRODUCT_DEFINITION with no shape)
- [Ad003](browse/12-11-adversarial/Ad003.html): Negative / zero `B_SPLINE` degree or empty knot/multiplicity lists drive `malloc` size confusion
- [Ad014](browse/12-11-adversarial/Ad014.html): Float literal with extreme exponent (`1E999999`) propagates as inf/NaN
- [Bo001](browse/12-3a-shells/Bo001.html): Outer shell of a solid is empty (zero faces)

### round-trip — re-export must preserve original structure (5 entries)

- [A005](browse/12-6-assembly/A005.html): Lost assembly hierarchy on round-trip (flatten to single CATPart / single solid)
- [A010](browse/12-6-assembly/A010.html): NAUO instance name lost on round-trip / re-export
- [Gs024](browse/12-2c-surfaces/Gs024.html): Round-trip planar face becomes trimmed B-spline (degree-1 NURBS)
- [Gs052](browse/12-2c-surfaces/Gs052.html): Surface of revolution with offset basis curve breaks on export
- [Le017](browse/12-1a-encoding/Le017.html): Raw control character (U+0000..U+001F) in string body

### spec-violation — file violates ISO 10303-21 / AP-242 syntax or schema rules (7 entries)

- [Ad042](browse/12-11-adversarial/Ad042.html): Reference to entity-of-wrong-type in attribute slot
- [A013](browse/12-6-assembly/A013.html): STEP assembly reader returns success even when external-reference files are missing
- [Ad038](browse/12-11-adversarial/Ad038.html): File concatenation produces conflicting IDs and dual end-markers
- [Gs043](browse/12-2c-surfaces/Gs043.html): `OFFSET_CURVE_3D` with `ref_distance` equal to the basis curve's radius of curvature (collapse)
- [Gs045](browse/12-2c-surfaces/Gs045.html): `SURFACE_OF_REVOLUTION` whose revolution axis crosses the basis curve at an interior point
- [Le004](browse/12-1a-encoding/Le004.html): `\X\` (single-byte ISO-8859) escape with bad hex digit count or non-hex input
- [Le009](browse/12-1a-encoding/Le009.html): `\P{X}\` page-shift directive: bad selector / state-machine omission

### interop — cross-vendor / cross-tool agreement (4 entries)

- [Xp023](browse/12-12-cross-product/Xp023.html): Deeply nested aggregate × overlong string literal in one fixture (Pf × Ad cross-product)
- [Xp024](browse/12-12-cross-product/Xp024.html): Tessellated topology × shared shell × void containment in one fixture
- [Xp025](browse/12-12-cross-product/Xp025.html): Onshape→SolidWorks: assembly children snap to origin (placements lost)
- [Xp036](browse/12-12-cross-product/Xp036.html): STYLED_ITEM colours dropped by bare STEPControl_Reader (vs XCAF reader)

### performance — bounded peak memory, no quadratic blow-ups (4 entries)

- [Pf011](browse/12-10-perf/Pf011.html): `EntityCluster` infinite recursion / leak on pathological deep chain
- [Pf001](browse/12-10-perf/Pf001.html): Multi-GB Creo AP242 assemblies trigger unbounded receiver memory
- [Pf008](browse/12-10-perf/Pf008.html): Stack overflow on huge faces-per-shell counts
- [Pf009](browse/12-10-perf/Pf009.html): Stack overflow when meshing with TBB pool from STEP import

### adversarial — hostile / fuzzed input must not corrupt kernel state (5 entries)

- [Ad084](browse/12-11-adversarial/Ad084.html): `XCAFDoc_ShapeTool::FindSubShape` crash building XCAF tree
- [Ad064](browse/12-11-adversarial/Ad064.html): Underscore inside string truncated by name-parsing consumer
- [Ad044](browse/12-11-adversarial/Ad044.html): `EDGE_CURVE.same_sense` boolean read uninitialised
- [Ad052](browse/12-11-adversarial/Ad052.html): STEP file referencing itself as external file (infinite loop)
- [Ad002](browse/12-11-adversarial/Ad002.html): Stack overflow via deeply nested aggregate parentheses

### geometry — surface / curve construction edge cases (6 entries)

- [Gs037](browse/12-2c-surfaces/Gs037.html): Offset of a surface-of-linear-extrusion fails iso-curve evaluation
- [Gp019](browse/12-2a-pcurves/Gp019.html): Edge on a composite-surface face is missing per-patch pcurve
- [Gn033](browse/12-2b-nurbs/Gn033.html): Pcurve / 3D-curve large jumps on closed-but-not-periodic `B_SPLINE_SURFACE_WITH_KNOTS` (undeclared `closed_u` seam)
- [Gp005](browse/12-2a-pcurves/Gp005.html): Pcurve with single-pole apex on sphere/cone (singularity)
- [Gs001](browse/12-2c-surfaces/Gs001.html): TOROIDAL_SURFACE with negative MajorRadius (SolidWorks/Pro-E orientation marker)
- [M020](browse/12-8-mixed/M020.html): Tessellated face style binding lost (no TransferBRep_ShapeBinder)

### topology — face / edge / shell connectivity (7 entries)

- [Twi005](browse/12-3b-wires/Twi005.html): ORIENTED_EDGE.edge_element references non-EDGE_CURVE
- [Tsh023](browse/12-3a-shells/Tsh023.html): Empty `EDGE_LOOP` / empty face list on shells
- [Twi004](browse/12-3b-wires/Twi004.html): ORIENTED_EDGE wrapping another ORIENTED_EDGE
- [Hea016](browse/12-3c-faces/Hea016.html): Empty solid output from STEP export of complex body, despite STL succeeding
- [M069](browse/12-8-mixed/M069.html): `TRIANGULATED_FACE` emitted without `pnval` indices
- [M078](browse/12-8-mixed/M078.html): AP209 quadratic_hexahedron with wrong node count (12 instead of 20)
- [N002](browse/12-4-tolerance/N002.html): Wireframe gap-fix inflates tolerance instead of bridging the gap

### pmi — Product Manufacturing Information / GD&T annotations (6 entries)

- [Pmi010](browse/12-7-pmi/Pmi010.html): Tolerance zone form name from AP242 Ed.2 used in Ed.1 file
- [Pmi049](browse/12-7-pmi/Pmi049.html): Tessellated geometry with no styled_item / color
- [M015](browse/12-8-mixed/M015.html): Tessellated PMI placement: third coordinate must be 0 in tessellated_geometric_set (repositioned form preferred)
- [N030](browse/12-4-tolerance/N030.html): Quarter `CYLINDRICAL_SURFACE` stored as `B_SPLINE_SURFACE_WITH_KNOTS` (canonical recognition tolerance budget)
- [N034](browse/12-4-tolerance/N034.html): `+/-` tolerance bounds inverted, equal, or wrong measure type
- [M011](browse/12-8-mixed/M011.html): Supplemental geometry inadvertently included in part-level GVP

### assembly — multi-part placement and hierarchy (5 entries)

- [A002](browse/12-6-assembly/A002.html): Hidden / suppressed bodies leak into export, or are dropped silently
- [A006](browse/12-6-assembly/A006.html): Components collapse to (0,0,0) / placement transforms lost
- [M060](browse/12-8-mixed/M060.html): External reference resolves to the same file as the main file
- [M160](browse/12-8-mixed/M160.html): STEP file imports as a near-empty document despite well-formed entities
- [N020](browse/12-4-tolerance/N020.html): Coordinate-system origin offset: hard-coded BOARD_OFFSET 0.05mm in PCB→MCAD pipeline

### encoding — string-literal escapes and code-page handling (5 entries)

- [Le005](browse/12-1a-encoding/Le005.html): `\X2\…\X0\` (UCS-2) escape: 3 hex digits in one group
- [Le026](browse/12-1a-encoding/Le026.html): `\X0\` end-marker missing — remainder treated as encoded content
- [Le011](browse/12-1a-encoding/Le011.html): `\N\` notation directive misused as C-style newline escape
- [Le013](browse/12-1a-encoding/Le013.html): Apostrophe-doubling escape `''` confused with string terminator
- [Le015](browse/12-1a-encoding/Le015.html): Unterminated string literal

### syntax — Part 21 token / structural rules (5 entries)

- [Lh007](browse/12-1b-header/Lh007.html): Multiple schema names listed inside a single FILE_SCHEMA
- [Ls010](browse/12-1c-syntax/Ls010.html): Complex / multiple-inheritance entity record: non-alphabetic leaf ordering
- [Lh002](browse/12-1b-header/Lh002.html): Missing or malformed closing marker `END-ISO-10303-21;`
- [Ls001](browse/12-1c-syntax/Ls001.html): REAL literal missing mandatory decimal point
- [M006](browse/12-8-mixed/M006.html): integer_representation_item serialized without trailing decimal point

### units — measure-unit conversion and tolerance scaling (5 entries)

- [N010](browse/12-4-tolerance/N010.html): `EDGE_CURVE` shorter than vertex tolerance (tiny edge covered by vertices, `distance_accuracy` exceeds edge length)
- [N015](browse/12-4-tolerance/N015.html): `xstep.cascade.unit M` meters setting inflates tolerance and corrupts geometry
- [U001](browse/12-5-units/U001.html): Solid Edge mm exported STEP read as meters by Inventor (imported part 1000 times bigger than expected)
- [U002](browse/12-5-units/U002.html): Onshape always emits METRE; NX rescales as if mm (1000× too small)
- [M023](browse/12-8-mixed/M023.html): Mesh-to-NURBS face has inner `FACE_BOUND` extending outside the `FACE_OUTER_BOUND` (self-intersecting STL→STEP face)

### writer — defects introduced by emitting kernels (5 entries)

- [Wr041](browse/12-13-writer-pathology/Wr041.html): Writer emits `.TRUE.` / `.FALSE.` instead of canonical `.T.` / `.F.`
- [Wr042](browse/12-13-writer-pathology/Wr042.html): Inconsistent end-of-record terminator: `;\n` and `;\r\n` mixed in same file
- [Wr044](browse/12-13-writer-pathology/Wr044.html): Inch unit declared in `LENGTH_UNIT` context but coordinates emitted in millimetres (no conversion)
- [Wr046](browse/12-13-writer-pathology/Wr046.html): Body Placement (rotation/translation) not applied during STEP export of a single part
- [Wr048](browse/12-13-writer-pathology/Wr048.html): Boolean-result body crashes STEP writer in `libTKXDESTEP` color-attribution pass

---

Generated from `STEP_PROBLEM_CATALOG.json` (1282 entries). Selection logic prioritises:

- entries with both byte-level and tier-3 assertions
- entries with documented synonyms / cross-references (better searchability)
- entries with explicit OCC-behavior annotations (good oracle alignment)
- diversity within each tag — at most ~2 entries from any one catalog section per tag
