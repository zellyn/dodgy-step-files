# Defect Class Definitions

Formal definitions for each defect class in the STEP-Defect Catalog.
Each definition is 1–3 lines describing the necessary-and-sufficient
mathematical, structural, or syntactic condition for a fixture to
exhibit that class.

These definitions enable: (a) mechanical detection of unflagged
instances in the wild; (b) fuzz-input generation that violates the
definition; (c) precise entry-class taxonomy bookkeeping.

For each class:

- **Definition**: the necessary-and-sufficient condition for the defect.
- **Mechanical witness**: how to detect it from a single STEP fixture
  (regex, byte assertion, oracle output, tier-3 measurement).
- **Spec reference**: when applicable, the ISO 10303 clause that the
  defect violates.

Conventions: byte-assertion regexes use Python `rb'…'` syntax; "oracle
output" refers to validate2's per-fixture summary fields
(`occt_heal_off`, `occt_heal_on`, `gmsh`, `ifc`, `diagnostics`).

---

## Top-level taxonomy (15 cross-cutting tags)

The 15 tags are defined in `validation/src/step_corpus/_taxonomy.py`.
Each catalog entry receives 1–3 tags.

### crash
**Definition**: A fixture causes the consuming kernel to terminate by
fault (signal-segfault, abort/runtime-error, infinite loop, runaway
memory) before producing either a parsed shape or a clean rejection
diagnostic.
**Mechanical witness**: validate2's `occt_heal_off` or `occt_heal_on`
field contains `signal(N)` (any N), `process_signal`, `runtime_error`,
or a `timeout` longer than the kernel's read budget.
**Spec reference**: not a spec violation per se; a kernel implementation
defect, but typically *triggered* by a fixture that violates Part-21
or Part-42.

### silent-loss
**Definition**: Loading the fixture produces a model missing one or
more data elements that exist in the producer's intent (faces, colors,
labels, transforms, sub-shapes, attribute values, PMI), with **no**
kernel diagnostic naming the loss.
**Mechanical witness**: validate2 reports a non-empty `shape_count` or
`face_count` strictly less than the catalog entry's
`expected_shape_count` / face count derivable from the fixture's
explicit entity list, **and** no `diagnostics` field captures the loss
(empty diagnostics with reduced shape).

### round-trip
**Definition**: The defect is invisible on the first load but appears
after a save → reload cycle through the same kernel; the second-pass
model differs from the first by added, dropped, or mutated entities.
**Mechanical witness**: `validate2 --save-reload` shows
`shape_count_first ≠ shape_count_reload` or any structural diff under
`diff_summary`. Catalog title contains "round-trip" / "re-export" /
"after save".

### spec-violation
**Definition**: The fixture, considered as bytes alone, contradicts a
normative clause of ISO 10303-21 (Part 21), -42 (geometry / topology),
-238 (machining), -242 (PMI / AP242 multidisciplinary), or another
referenced AP. Conformant kernels MUST reject (or heal-with-diagnostic).
**Mechanical witness**: catalog `expected_kernel_behavior` contains
"reject" and `sources` cites an ISO 10303 / AP203 / AP214 / AP238 /
AP242 / Part-21 clause; verifiable independently by running an EXPRESS
schema validator (e.g., stepcode `check_express`).

### interop
**Definition**: A fixture that two distinct conformant readers (across
vendor-A and vendor-B) handle differently (one accepts, one rejects;
or both accept but produce semantically different models) without the
fixture itself being unambiguously spec-illegal.
**Mechanical witness**: validate2 oracle disagreement, e.g.
`occt=accept` and `gmsh=reject`, or `occt.shape_count ≠
gmsh.shape_count`, on a fixture whose `expected_validation` line
encodes this disagreement.

### performance
**Definition**: The fixture, while semantically modest, drives the
reader/writer into super-linear (typically Θ(n²) or worse) wall-clock,
memory, or recursion-depth consumption against an attacker-controlled
input dimension.
**Mechanical witness**: validate2 wall-clock or RSS exceeds a
calibrated baseline (e.g., 10× the same fixture with a smaller `n`),
or catalog `expected_validation` declares a `slow=` / `oom=` measure.

### adversarial
**Definition**: The fixture is intentionally engineered to attack the
parser, lexer, allocator, or file-system surface rather than to
exercise legitimate CAD modelling (e.g. zip-bomb expansion,
out-of-bounds index, type confusion, lone surrogate, path traversal in
external file references).
**Mechanical witness**: catalog `section_dir == "12-11-adversarial"`,
or sub-class is one of `{cyclic-reference / dos, resource-exhaustion /
dos, type-confusion, null-deref, heap-overflow / fuzz-class}`.

### geometry
**Definition**: The defect lives in the parametric description of a
curve, surface, or B-rep face (wrong knot vector, ill-defined NURBS
basis, missing pcurve, surface-of-revolution with degenerate axis,
offset curve through a singularity, etc.) without necessarily
breaking topology.
**Mechanical witness**: catalog `section_dir ∈ {12-2a-pcurves,
12-2b-nurbs, 12-2c-surfaces}`, or entry references one of the
parametric-geometry entity types: `B_SPLINE_*`, `RATIONAL_B_SPLINE_*`,
`OFFSET_CURVE_*`, `SURFACE_OF_REVOLUTION`, `*_PCURVE`.

### topology
**Definition**: The defect lives in the incidence / orientation /
connectivity structure of shells, wires, faces, edges, or vertices
(empty edge loops, dangling edge curves, non-closed manifold solids,
mis-oriented shell normals, vertex-tolerance budget violations).
**Mechanical witness**: catalog `section_dir ∈ {12-3a-shells,
12-3b-wires, 12-3c-faces}`, or entry references `EDGE_LOOP`,
`ORIENTED_EDGE`, `FACE_BOUND`, `VERTEX_LOOP`, `OPEN_SHELL`,
`CLOSED_SHELL`, or `MANIFOLD_SOLID_BREP`.

### pmi
**Definition**: The defect lives in product manufacturing information
(GD&T tolerance frames, datum references, dimensions, annotations,
saved views, AP242 hole / profile / sheet-metal feature definitions)
and is distinct from the underlying B-rep correctness.
**Mechanical witness**: catalog `section_dir == "12-7-pmi"`, or entry
references `DIMENSIONAL_*`, `GEOMETRIC_TOLERANCE_*`, `DATUM*`,
`ANNOTATION_PLANE`, `*_FEATURE` (AP242 hole / counterbore / round /
slot / pocket), or PMI presentation entities.

### assembly
**Definition**: The defect lives in the product-assembly graph (the
NAUO / mapped-item / placement / hierarchy structure that arranges
sub-products) and would not surface on a single-part fixture.
**Mechanical witness**: catalog `section_dir == "12-6-assembly"`, or
entry references `NEXT_ASSEMBLY_USAGE_OCCURRENCE`,
`PRODUCT_DEFINITION`, `SHAPE_REPRESENTATION_RELATIONSHIP`,
`ITEM_DEFINED_TRANSFORMATION`, `CONTEXT_DEPENDENT_SHAPE_REPRESENTATION`,
`MAPPED_ITEM`.

### encoding
**Definition**: The defect lives in the byte-level character encoding,
BOM handling, character-set escape directive (`\X\`, `\X2\`, `\X4\`,
`\PE\`, `\Q\`), or string-literal lexeme, orthogonal to Part-21
grammar.
**Mechanical witness**: catalog `section_dir == "12-1a-encoding"`, or
fixture begins with a BOM byte (`EF BB BF`, `FE FF`, `FF FE`,
`00 00 FE FF`, `FF FE 00 00`), or contains an `\X*\` escape directive.

### syntax
**Definition**: The defect lives in Part-21 grammar / framing /
tokenisation / instance-numbering (broken `ISO-10303-21;` magic, malformed
`HEADER`/`DATA`/`ENDSEC` framing, non-monotonic `#NNN`, illegal lexemes
like `.TRUE.` instead of `.T.`).
**Mechanical witness**: catalog `section_dir ∈ {12-1b-header,
12-1c-syntax}`; or a Part-21 grammar parser (e.g., stepcode `lazy_step`)
reports a parse error not attributable to encoding.
**Spec reference**: ISO 10303-21 §6 (lexical), §7 (data exchange
structure).

### units
**Definition**: The defect lives in unit declaration, conversion, or
context (wrong `LENGTH_UNIT`, missing `CONVERSION_BASED_UNIT` mapping,
coordinate scale mismatch like mm vs inch, derived-unit composition
error, inconsistent `UNCERTAINTY_MEASURE_WITH_UNIT`).
**Mechanical witness**: catalog `section_dir == "12-5-units"`, or entry
references `*_UNIT`, `UNCERTAINTY_MEASURE_WITH_UNIT`,
`CONVERSION_BASED_UNIT`, `DIMENSIONAL_EXPONENTS`,
`GLOBAL_UNIT_ASSIGNED_CONTEXT`.

### writer
**Definition**: The defect originates on the producer side at export
time, independent of any input file: numeric-format inconsistency,
spurious `$`/`*`, schema downgrade on export, dropped colour on
re-export, instance-numbering chaos.
**Mechanical witness**: catalog `section_dir == "12-13-writer-pathology"`,
or catalog title begins with `Re-export …`, `Writer emits …`,
`Producer …`.

---

## Sub-classes

Sub-classes are declared in each entry's `category` field as
`§12.x.y (sub-class: <name>)`. The catalog has 562 distinct sub-class
strings across 1282 entries; what follows defines the most frequent
cross-prefix sub-classes plus one representative sub-class per
named-prefix group (Le, Lh, Ls, Gp, Gn, Gs, Tsh, Twi, Tfa, N, U, A,
Pmi, M, Pf, Ad, Hea, Bo, Sw, Fi, Os, In, Gb, Tb, Ps, Xp, Wr).

### sub-class: ap242 feature definition  (count: 31, prefix Pmi)
**Definition**: An AP242 feature-template entity (`ROUND_HOLE`,
`COUNTERBORE_HOLE`, `COUNTERSUNK_HOLE`, `SLOT`, `POCKET`, `RIB`, `BOSS`,
`CHAMFER`, `EDGE_ROUND`, `THREAD`, …) whose feature parameters are
absent, malformed, geometrically inconsistent with the host face/solid,
or contradict the underlying B-rep.
**Mechanical witness**: regex
`matches(rb'(?:ROUND_HOLE|COUNTERBORE_HOLE|COUNTERSUNK_HOLE|SLOT|POCKET|RIB|BOSS|CHAMFER|EDGE_ROUND|THREAD)\s*\(')`
plus a parameter-vs-geometry oracle (tier-3) that compares feature
diameter / depth / location to the host shell extents.
**Spec reference**: ISO 10303-242:2014 §6.

### sub-class: ap238 deep machining  (count: 23, prefix M)
**Definition**: An AP238 STEP-NC machining feature
(`MACHINING_OPERATION`, `MILLING_*`, `TURNING_*`, `DRILLING_*`,
toolpath, workpiece-setup) with missing or geometrically inconsistent
parameters (cut depth exceeding workpiece, inverted feed direction,
toolpath escaping the bounding workpiece, missing fixture/setup).
**Mechanical witness**: regex
`matches(rb'(?:MACHINING_OPERATION|MILLING_|TURNING_|DRILLING_|TOOLPATH)')`
plus tier-3 toolpath/workpiece consistency check.
**Spec reference**: ISO 10303-238.

### sub-class: semantic-vs-graphic  (count: 20, prefix Pmi)
**Definition**: PMI is exported in graphic-only form (just polylines or
tessellation) when AP242 mandates a *semantic* representation
(`DRAUGHTING_*` with backing `SHAPE_ASPECT` / `DIMENSIONAL_*`), or vice
versa, leaving the dimension or tolerance machine-unreadable.
**Mechanical witness**: presence of `ANNOTATION_OCCURRENCE` /
polyline-only PMI without a paired
`DIMENSIONAL_LOCATION`/`DIMENSIONAL_SIZE` linking
`SHAPE_ASPECT` to geometry.

### sub-class: shape-healing  (count: 13, prefix Hea)
**Definition**: A fixture intentionally exercising a healing pipeline
(ShapeFix tools: `Solid`, `Shell`, `Wire`, `Edge`, `Face`,
`SameParameter`, `FixSmallSolid`, …); the defect requires the healer to
converge on a multi-defect input or to refuse a degenerate one.
**Mechanical witness**: catalog `category` references `Hea*`; entry
title contains `healing` / `ShapeFix` / `heal-pipeline`.

### sub-class: round-trip data loss  (count: 9, prefix Wr)
**Definition**: On `save → reload` cycling through the same kernel,
specific data classes silently disappear: face/solid colours, feature
labels, product names, persistent ids, supplemental geometry, PMI.
**Mechanical witness**: validate2 reload-diff shows
`{colors,labels,names,…}` cardinality strictly decreasing across the
round-trip.

### sub-class: tessellation  (count: 9, prefix M)
**Definition**: An entity from the AP242 tessellation hierarchy
(`TESSELLATED_SOLID`, `TRIANGULATED_FACE`,
`TESSELLATED_SHAPE_REPRESENTATION`,
`TESSELLATED_CONNECTING_EDGE`) with structurally-illegal contents
(free-edge stand-alone tessellation, illegal `axis2_placement_3d` in
representation, wrong-edition entity use).
**Mechanical witness**: regex
`matches(rb'(?:TESSELLATED_|TRIANGULATED_|COMPLEX_TRIANGULATED_)')`
plus a tessellation-schema check.

### sub-class: header / vendor metadata  (count: 6, prefix Wr)
**Definition**: A `FILE_DESCRIPTION` / `FILE_NAME` / `FILE_SCHEMA` /
`HEADER` field carries vendor-private encoding, conflicts with
`DATA`-section content (e.g., schema declared in HEADER but used as
something else), or leaks producer-only metadata that downstream readers
special-case.
**Mechanical witness**: byte-region scan within `ISO-10303-21;`
header section (between `HEADER;` and `ENDSEC;`).

### sub-class: `\x2\` directive  (count: 6, prefix Le)
**Definition**: A string literal containing a malformed `\X2\…\X0\`
(UCS-2) escape (wrong number of hex digits per code point, lone
surrogate, endianness confusion, or missing terminator).
**Mechanical witness**: regex
`matches(rb"\\X2\\(?:(?![0-9A-F]{4}).{0,3}\\X0\\|[0-9A-F]{0,3}(?:\\X0\\|$)|[0-9A-F]+\\X0\\)")`
or a stricter check that each block between `\X2\` and `\X0\` has a
length divisible by 4.
**Spec reference**: ISO 10303-21 §6.4.4.

### sub-class: saved-view  (count: 6, prefix Pmi)
**Definition**: PMI entities whose visibility / locator (`MDGPR`,
`DRAUGHTING_MODEL`, `CAMERA_MODEL_D3`, `MODEL_GEOMETRIC_VIEW`,
supplemental-geometry split) is ambiguous, missing, or split across
multiple representations.
**Mechanical witness**: presence of `MDGPR`, `DRAUGHTING_MODEL`, or
`CAMERA_MODEL_D3` plus a multi-anchor scan.

### sub-class: persistent-id  (count: 6, prefix Pmi)
**Definition**: An `id_attribute` value (UUID-like) is shared across
mutually-exclusive `SHAPE_ASPECT` / `DIMENSIONAL_LOCATION` /
`DIMENSIONAL_SIZE` instances, or is duplicated across distinct
`identified_item`s, breaking the contract that a persistent id
uniquely names one logical artefact.
**Mechanical witness**: aggregate scan: count occurrences of each
distinct `id_attribute` string; any value with cardinality > 1 across
non-aliased entities is the witness.

### sub-class: datum-frame  (count: 6, prefix Pmi)
**Definition**: A datum-reference frame contains identical or
non-unique datum letters within a product, or references datums that do
not exist, breaking the GD&T datum-frame uniqueness invariant.
**Mechanical witness**: parse `DATUM_REFERENCE` chains; assert
distinct datum-letter set per `GEOMETRIC_TOLERANCE` instance.
**Spec reference**: ASME Y14.5 / ISO 1101.

### sub-class: validation-property  (count: 6, prefix M)
**Definition**: A `GEOMETRIC_VALIDATION_PROPERTY` (volume, surface
area, centroid) is declared but its claimed value disagrees with a
direct measurement of the underlying geometry (or is attached at the
wrong representation level, e.g. geometry-only, invisible to
PDM-readers).
**Mechanical witness**: tier-3 measure: compute volume / surface-area
on the loaded shape; compare to declared `volume_measure` /
`area_measure` to within ε.

### sub-class: appearance  (count: 6, prefix M)
**Definition**: A `STYLED_ITEM` entity is unparented under
`MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION` (MDGPR) or
`DRAUGHTING_MODEL`, its `item` slot is `$` / dangling, or the styling
chain (`SURFACE_STYLE_USAGE`, `FILL_AREA_STYLE_COLOUR`) is broken.
**Mechanical witness**: regex `matches(rb'STYLED_ITEM\(')` plus
parent-context check.

### sub-class: dependency-depth  (count: 5, prefix Pf)
**Definition**: A fixture whose entity-reference graph has worst-case
chain depth far exceeding typical production files (e.g., 200+
sequential entity hops for `ADVANCED_FACE → FACE_BOUND → EDGE_LOOP →
ORIENTED_EDGE → EDGE_CURVE → …`), driving recursive readers into
quadratic or stack-blowing behaviour.
**Mechanical witness**: tier-3 entity-graph: longest simple path from
top-level shape to a leaf (`CARTESIAN_POINT`, `DIRECTION`) exceeds
threshold (e.g., > 64).

### sub-class: whitespace/line-ending  (count: 5, prefix Wr)
**Definition**: Anomalous whitespace / line-ending in the file body
(trailing spaces on every record, mixed CRLF/LF, multiple consecutive
blank lines, missing final newline, or stray NUL bytes).
**Mechanical witness**: byte scan: `matches(rb'[ \t]+\r?\n')` for
trailing whitespace; `matches(rb'\r\n')` AND `matches(rb'(?<!\r)\n')`
within one file for mixed line endings.

### sub-class: instance numbering  (count: 5, prefix Wr)
**Definition**: `#NNN` instance numbers are non-monotonic, contain
gaps, are randomly shuffled, or use forward references where the
producer convention guarantees sequential definition before use.
**Mechanical witness**: parse all `#N=` definitions; assert N is
strictly increasing or that the first reference to `#N` does not
precede its `#N=` definition (where the section's convention demands
backward references).

### sub-class: ap242 feature definition / sheet-metal  (count: 5, prefix Pmi)
**Definition**: `FLAT_PATTERN`, `BEND`, `LOUVER`, sheet-metal feature
whose parameters violate physical constraints (bend angle ≥ 180°,
bend radius < material thickness, hem-fold inside-out).
**Mechanical witness**: parameter-vs-thickness consistency check.
**Spec reference**: ISO 10303-242 sheet-metal application objects.

### sub-class: ap242 feature definition / profile  (count: 5, prefix Pmi)
**Definition**: A `PROFILE_FEATURE` whose `PROFILE_FLOOR` is non-closed
(open polyline used as boundary), self-intersecting (figure-eight loop),
or has wrong-orientation outer-vs-inner profile.
**Mechanical witness**: `matches(rb'PROFILE_FEATURE\(')` plus
2D-loop closure & self-intersection check.

### sub-class: supplemental  (count: 5, prefix M)
**Definition**: Supplemental geometry (bound vs unbound planes / lines
for PMI anchors, saved-view supplemental sets) split across multiple
CGRs or attached at a level invisible to one class of reader.
**Mechanical witness**: scan `SUPPLEMENTAL_GEOMETRY_*` references;
verify all are anchored under a single CGR per saved view.

### sub-class: mesh-as-brep  (count: 5, prefix M)
**Definition**: An STL-derived `TESSELLATED_SOLID` /
`TRIANGULATED_FACE` is exported as if it were a B-rep, or a
mesh-to-NURBS face has an inner `FACE_BOUND` extending outside its
`FACE_OUTER_BOUND`.
**Mechanical witness**: regex `matches(rb'TESSELLATED_SOLID')` AND
`matches(rb'MANIFOLD_SOLID_BREP')` in the same file, OR inner-bound /
outer-bound containment failure.

### sub-class: schema-validation  (count: 4, prefix Ad)
**Definition**: An entity violates an EXPRESS schema constraint (wrong
attribute count, wrong attribute type, illegal enumeration value,
illegal `WHERE`-rule outcome) that an EXPRESS-aware reader should
catch.
**Mechanical witness**: stepcode `check_express` reports a non-zero
violation count.
**Spec reference**: ISO 10303-11 (EXPRESS).

### sub-class: numeric formatting  (count: 4, prefix Wr)
**Definition**: Floating-point literals within one file are formatted
inconsistently (mixing scientific and fixed, varying precision, `1.`
vs `1.0`, `+0.0` vs `0.0`) or lose precision after round-trip.
**Mechanical witness**: byte scan of all `[+-]?\d+\.\d*(?:[eE][+-]?\d+)?`
matches; assert single canonical formatting style.

### sub-class: lesser-known directives  (count: 4, prefix Le)
**Definition**: A string literal uses a rarely-supported escape
directive (`\PE\` page-shift, `\Q\x` quote, `\F\` font-shift,
`\N\` line-break, `\T\` tab, `\S\` capital, `\Pn\` ISO-8859-n) that many
readers pass through with no warning.
**Mechanical witness**: regex
`matches(rb"\\(?:PE|Pn|Q[A-F0-9]|F|N|T|S)\\")` (note: must
distinguish from in-string literal `\\`).
**Spec reference**: ISO 10303-21 §6.4.

### sub-class: multi-section  (count: 4, prefix Lh)
**Definition**: A multi-DATA-section Part-21 file with cross-section
references via `@section_name#NNN`, ambiguous local `#NNN` reuse, or a
section name that fails the lexical conformance rules.
**Mechanical witness**: `matches(rb'DATA;')` with cardinality > 1 plus
`matches(rb'@\w+#\d+')`.

### sub-class: gap-analysis  (count: 4, prefix Twi)
**Definition**: A wire / loop with multiple junction gaps that a
gap-analysis must enumerate exhaustively (3D between successive edges,
or 2D between successive pcurves).
**Mechanical witness**: tier-3 gap-enumeration over all consecutive
`ORIENTED_EDGE` pairs in each `EDGE_LOOP`; expected count > 1.

### sub-class: annotation-plane  (count: 4, prefix Pmi)
**Definition**: An `ANNOTATION_PLANE` is ambiguous (`plane` vs
`planar_box`), the annotation geometry sits non-parallel to the declared
plane (offset > ε), or the plane is misaligned to the annotated face.
**Mechanical witness**: tier-3 normal-vs-annotation-vector check.

### sub-class: multi-pass-healing  (count: 3, prefix Pf)
**Definition**: Iterative `ShapeFix` passes expose a new defect each
pass without converging (unbounded healing), or trigger an infinite
loop on self-intersection healing of a crossed `EDGE_LOOP`.
**Mechanical witness**: instrumented healer pass count exceeds
threshold (e.g., > 8) or the fix-defect count is non-decreasing across
two consecutive passes.

### sub-class: cyclic-reference / dos  (count: 3, prefix Ad)
**Definition**: Entity references form a cycle (`#A → #B → #A`,
direct or transitive) that drives a naive recursive reader into
infinite recursion; or a STEP file whose `EXTERNAL_FILE` reference
points back to itself.
**Mechanical witness**: build the entity-reference DAG; report any
strongly-connected component of size ≥ 2.

### sub-class: optional-parameter abuse  (count: 3, prefix Wr)
**Definition**: A spurious `$` (NULL) appears where the schema requires
a value (omitted required parameter) or `*` (overridden) appears where
the schema does not allow it.
**Mechanical witness**: per-entity: parse the parameter list and
compare against schema arity / OPTIONAL flags; flag any required slot
matching `\$` or any non-OPTIONAL slot matching `\*`.
**Spec reference**: ISO 10303-21 §11.2.

### sub-class: lexeme conformance  (count: 3, prefix Le/Wr)
**Definition**: A lexeme is in non-canonical form (`.TRUE.` / `.FALSE.`
instead of `.T.` / `.F.`, lowercase enumeration, leading-zero integer
where the spec mandates none).
**Mechanical witness**: byte-regex `matches(rb'\.TRUE\.|\.FALSE\.')`
or `matches(rb'\.[a-z][a-z_]*\.')`.
**Spec reference**: ISO 10303-21 §6.4.

### sub-class: units / coordinate scale  (count: 3, prefix Wr)
**Definition**: Inch unit is declared in `LENGTH_UNIT` context but
coordinates are emitted in millimetres (or vice versa); or the unit
name was changed without rescaling coordinate values.
**Mechanical witness**: tier-3 measure: compare bounding-box scale
against declared unit's nominal magnitude. Mismatch ≥ 25× is a strong
witness for inch-vs-mm.

### sub-class: numeric character reference  (count: 3, prefix Le)
**Definition**: A `\Q\` numeric-character-reference encodes a code
point outside U+0000–U+10FFFF, inside the UTF-16 surrogate range
(U+D800–U+DFFF), or with malformed hex (non-hex digits, missing
terminator).
**Mechanical witness**: regex `matches(rb"\\Q\\([0-9A-Fa-f]+)")`
followed by code-point-range check.
**Spec reference**: ISO 10303-21 §6.4.4.

### sub-class: continuity  (count: 3, prefixes Gp, Gs)
**Definition**: A composite curve / B-spline has a C0 internal break
that downstream tools cannot ingest, or composite-curve segments do
not meet within `connectivity_tolerance`.
**Mechanical witness**: tier-3 derivative-evaluation: compute left/right
tangent at every internal join; flag pairs with tangent angle > θ_C¹.

### sub-class: pipeline  (count: 3, prefixes Tsh, Twi, Tfa)
**Definition**: A multi-defect topology fixture that requires an
*ordered* sequence of healing operations (e.g.,
reorder → connect → close, or face-by-face heal → shell-wide heal); any
out-of-order pipeline produces a worse model.
**Mechanical witness**: catalog notes describe the required ordering;
permuting healer phases changes the result.

### sub-class: tolerance ballooning by healing  (count: 3, prefix N)
**Definition**: A wireframe gap-fix or face-merge inflates the
shared-vertex tolerance to the worst input value, in lieu of bridging
the actual geometric gap; the model is "valid" only by virtue of an
inflated tolerance.
**Mechanical witness**: post-heal `vertex_tolerance` strictly larger
than the pre-heal max input tolerance, on a fixture whose intent is to
force this.

### sub-class: sameparameter  (count: 3, prefix N)
**Definition**: An edge has its `same_parameter` flag asserted, yet its
3D curve and any of its pcurves disagree at sampled parameters by more
than ε; or splitting a closed periodic face leaves new edges with
reversed pcurve vs 3D-curve sense.
**Mechanical witness**: tier-3 sampling: at N parameter values, evaluate
3D curve and pcurve-on-surface; flag deviations > ε.

### sub-class: derived-unit composition  (count: 3, prefix U)
**Definition**: A derived unit (`Pa` = `kg·m⁻¹·s⁻²`, `Pa·s`,
`N·m`, …) is built from an explicit `DERIVED_UNIT` /
`DERIVED_UNIT_ELEMENT` chain that does not balance to the claimed
unit's `DIMENSIONAL_EXPONENTS`.
**Mechanical witness**: parse `DERIVED_UNIT_ELEMENT` exponent vector;
compare to declared unit's `DIMENSIONAL_EXPONENTS`.
**Spec reference**: ISO 10303-41.

### sub-class: hole-feature  (count: 3, prefix Pmi)
**Definition**: A hole feature (counterbore / countersink) is emitted
as separate uncombined dimensions with no compound-feature link, or an
AP242 `*_HOLE` feature is missing required attributes.
**Mechanical witness**: scan for `COUNTERBORE_HOLE` / `COUNTERSUNK_HOLE`
without backing `COMPOUND_FEATURE` / `*_HOLE` group.

### sub-class: datum-targets  (count: 3, prefix Pmi)
**Definition**: A `placed_datum_target_feature` has a target dimension
of zero, has a shape that mismatches the datum-target type (e.g., area
target with a point shape), or its placement falls outside the host
face.
**Mechanical witness**: parse `DATUM_TARGET` dimension/shape; assert
non-zero and type-consistent.

### sub-class: validation property  (count: 3, prefix Pmi)
**Definition**: A `GEOMETRIC_VALIDATION_PROPERTY` claims a volume,
surface area, or centroid that disagrees with a tier-3 measurement
of the loaded shape; the *self-check* validation property is wrong.
**Mechanical witness**: tier-3 measurement of volume/area/centroid;
compare against declared value to within ε.

### sub-class: file-size / oom  (count: 2, prefix Pf)
**Definition**: A multi-GB STEP file (or a small file with massive
entity-count amplification) drives the receiver into unbounded resident
memory.
**Mechanical witness**: validate2 RSS or wall-clock ≥ catalog-declared
threshold; or `entity_count : file_size` ratio > 10⁵.

### sub-class: schema-validation / null-deref  (count: 2, prefix Ad)
**Definition**: An empty aggregate appears where the schema requires
≥ 1 element (`EDGE_LOOP(())`, empty wire, empty entity-iterator) and a
naive reader dereferences the (non-existent) first element.
**Mechanical witness**: regex
`matches(rb'EDGE_LOOP\s*\(\s*\x27[^\x27]*\x27\s*,\s*\(\s*\)\s*\)')`,
or analogous for other aggregates.
**Spec reference**: ISO 10303-42 §EDGE_LOOP `WHERE` rule
(`SIZEOF(edge_list) > 0`).

### sub-class: resource-exhaustion / dos  (count: 2, prefix Ad)
**Definition**: A "STEP zip-bomb" style file: small bytes-on-disk but
10⁶+ tiny entities or schema-EXPRESS rule recursion that exhausts
memory or stack.
**Mechanical witness**: entity count divided by file-size byte-count
exceeds threshold (e.g., > 10⁴ entities/MB).

### sub-class: type-confusion  (count: 2, prefix Ad)
**Definition**: An entity reference has the right syntactic form but
the wrong dynamic type: a `CARTESIAN_POINT` reference used where a
`DIRECTION` is required, or a `NEXT_ASSEMBLY_USAGE_OCCURRENCE` slotted
where a `PRODUCT_DEFINITION_SHAPE` is required.
**Mechanical witness**: per-attribute: resolve target entity, compare
its keyword against the schema's declared type for that attribute slot.

### sub-class: null-deref  (count: 2+, prefix Ad)
**Definition**: A reference to a non-existent entity number (negative,
out-of-range, or unallocated) that a naive reader dereferences;
or a `$` slot in a position where the reader does not check before
dereferencing.
**Mechanical witness**: build the `#N` definition set; report any
reference whose target is not in the set.

### sub-class: construction-residue  (count: 2, prefix Wr)
**Definition**: Re-output of intermediate construction entities
(orphan geometry, `SHAPE_DEFINITION_REPRESENTATION` chains with no
backing geometry, scratch lines/points left over from CSG modelling).
**Mechanical witness**: graph reachability: count entities not
reachable from any top-level `*_REPRESENTATION`.

### sub-class: schema downgrade  (count: 2, prefix Wr)
**Definition**: An AP242 input is exported as AP203 (or similar
schema downgrade), losing entities not representable in the target
schema; or `FILE_SCHEMA` declares a non-existent schema version.
**Mechanical witness**: compare `FILE_SCHEMA` against producer's
declared origin schema; entity-loss diff against original.

### sub-class: unit / coordinate  (count: 2, prefix Wr)
**Definition**: Coordinate-system axis swap (Y-up vs Z-up) is applied
without notification, or a coordinate scale-factor is applied twice
(model 1000× larger or smaller than expected).
**Mechanical witness**: bounding-box / orientation comparison against
declared `axis2_placement_3d` triad.

### sub-class: bom  (count: 2, prefix Le)
**Definition**: A UTF-16 / UTF-32 BOM (`FE FF`, `FF FE`,
`00 00 FE FF`, `FF FE 00 00`) appears at file start, where a UTF-8 BOM
(`EF BB BF`) is occasionally tolerated but multi-byte BOMs are spec-illegal.
**Mechanical witness**: `bytes_starts_with` one of the listed BOM byte
sequences.
**Spec reference**: ISO 10303-21 §6.1, §6.4.4.

### sub-class: control characters / framing  (count: 2, prefix Le)
**Definition**: Inline control characters (newline inside an
unterminated literal, NUL bytes, DOS `\r\n` mixed with Unix `\n`) that
naïvely-tokenising parsers either silently concatenate across or fault on.
**Mechanical witness**: scan tokenised string-literal byte-spans for
`\x00`, `\n`, `\r` not at literal-end.

### sub-class: numeric literal  (count: 2, prefix Le)
**Definition**: A REAL literal lies at IEEE-754 subnormal /
minimum-normal / maximum boundaries, or exceeds the double range
(overflow → `+Inf` / underflow → `0.0`).
**Mechanical witness**: tokenize each REAL literal; flag values
≤ 2.2250738585072014e-308 (denormal boundary) or
≥ 1.7976931348623157e+308 (max normal).

### sub-class: reference  (count: 2, prefix Lh)
**Definition**: A `REFERENCE` section points at an unresolvable
external anchor, or contains URIs of mixed schemes including
unsupported ones (e.g., `gopher://`, `data:` with executable content).
**Mechanical witness**: parse `REFERENCE` section; resolve each URI;
flag failed resolutions or scheme not in `{file, http, https}`.

### sub-class: signature  (count: 2, prefix Lh)
**Definition**: The `SIGNATURE` section is positioned before any
`DATA;` (signature-over-empty-content), or names an unknown signature
algorithm, or fails verification.
**Mechanical witness**: section-order scan; algorithm whitelist check.

### sub-class: offset curve  (count: 2, prefix Gs)
**Definition**: An `OFFSET_CURVE_3D` / `OFFSET_CURVE_2D` has
`ref_distance` equal to the basis curve's local radius of curvature
(producing a singularity), or a sign of `ref_distance` flipping
mid-composite-curve chain.
**Mechanical witness**: tier-3: at sampled t, compute `1/κ(t)` and
compare to `ref_distance`; flag |1/κ - d| < ε.
**Spec reference**: ISO 10303-42 `OFFSET_CURVE_3D`.

### sub-class: shell completeness  (count: 2, prefix Bo)
**Definition**: The outer shell of a `MANIFOLD_SOLID_BREP` is empty
(zero faces), or the `outer` reference dangles to a non-existent
`*_SHELL` entity.
**Mechanical witness**: regex
`matches(rb'MANIFOLD_SOLID_BREP\s*\(\s*\x27[^\x27]*\x27\s*,\s*#\d+\s*\)')`
plus resolve target shell; assert face count > 0.
**Spec reference**: ISO 10303-42 `MANIFOLD_SOLID_BREP` `WHERE` rules.

### sub-class: fast-sewing prerequisite  (count: 2, prefix Sw)
**Definition**: A "fast-sewing" face has a NULL surface reference, or
its host surface has infinite extent; both prerequisites for the fast
sewing path must hold for the operation to be safe.
**Mechanical witness**: scan `ADVANCED_FACE.face_geometry`; flag `$` or
unbounded surface (e.g., `PLANE` without bounding curves).

### sub-class: edge consistency  (count: 2, prefix Twi)
**Definition**: An `EDGE_CURVE`'s 3D curve evaluation does not match
its declared end vertices (`edge_start` / `edge_end`) within ε, or it
has only a pcurve and no 3D space curve.
**Mechanical witness**: tier-3: evaluate `EDGE_CURVE.edge_geometry` at
its parameter endpoints, compare to `edge_start.vertex_geometry` and
`edge_end.vertex_geometry`.

### sub-class: tolerance budget  (count: 2, prefix Twi)
**Definition**: A vertex tolerance is smaller than the largest
endpoint-discrepancy among edges meeting at that vertex; the budget is
under-allocated and a tolerant kernel must inflate or refuse.
**Mechanical witness**: per-vertex: compute max distance from each
incident edge's endpoint to the shared vertex point; assert ≤ vertex
tolerance.

### sub-class: knot vector  (count: 1, prefix Gn)
**Definition**: A B-spline curve / surface has a knot vector violating
the non-decreasing rule, with the wrong cumulative multiplicity for the
declared degree, or with a clamping mismatch between knots and
multiplicities arrays.
**Mechanical witness**: parse `B_SPLINE_*.knots` and `knot_multiplicities`;
verify `len(knots) == len(multiplicities)`, `sum(mults) == n + degree + 1`,
and strict non-decrease.
**Spec reference**: ISO 10303-42 `B_SPLINE_CURVE`.

### sub-class: missing pcurve  (count: 1, prefix Gp)
**Definition**: A `SURFACE_CURVE` lacks an `associated_geometry`
pcurve on a face that requires it, or all listed pcurves disagree
with the 3D curve at sampled parameters.
**Mechanical witness**: scan `SURFACE_CURVE.associated_geometry`;
require `≥ 1` `PCURVE` per surface that the curve lies on.

### sub-class: pathological-success / signed-volume  (count: 1, prefix Ps)
**Definition**: A solid that passes structural validation but whose
signed volume (oriented integral of outward normal) is negative or
zero; the solid is inverted or void-collapsed but reports as valid.
**Mechanical witness**: tier-3: compute signed volume via divergence
theorem on the loaded shape; flag `≤ 0`.

### sub-class: interface state-unloaded  (count: 1, prefix In)
**Definition**: The OCCT `IFSelect` interface remains in its `unloaded`
state after a load attempt, indicating the kernel produced no model
and silently returned without surfacing the failure.
**Mechanical witness**: validate2 `interface_state == "unloaded"` field.

### sub-class: fillet contour concavity  (count: 1, prefix Fi)
**Definition**: A `BLENDED_EDGE` (fillet/round) walks a contour whose
curvature inverts mid-traversal; the fillet-walk algorithm fails to
produce a continuous blend surface.
**Mechanical witness**: tier-3: along the edge, compute signed
curvature; flag a sign change.

### sub-class: approximation failure  (count: 1, prefix Gb)
**Definition**: An entity that requires a numerical approximation
(parameter inversion, intersection, projection) cannot converge within
the kernel's iteration / residual budget on this fixture.
**Mechanical witness**: kernel-side: iteration count > threshold or
residual > ε at termination.

### sub-class: offset prerequisite  (count: 2, prefix Os)
**Definition**: An offset operation (offset shape / offset curve) is
applied to a base whose properties violate prerequisites: non-closed
shell offset, degenerate offset distance, reversed orientation.
**Mechanical witness**: pre-condition check on the base shape's
closedness / orientation / distance sign.

### sub-class: hierarchy × unit-scaling  (count: 2, prefix Tb)
**Definition**: A multi-level assembly hierarchy with per-level unit
scaling produces a tolerance-boundary corner case where rounding at
each level accumulates beyond the declared global tolerance.
**Mechanical witness**: tier-3: traverse the assembly tree; for each
nested `ITEM_DEFINED_TRANSFORMATION`, accumulate scale; compare final
coordinate magnitudes against declared `UNCERTAINTY_MEASURE_WITH_UNIT`.

### sub-class: composite-surface  (count: 2, prefix Tfa)
**Definition**: A face is hosted on a composite / curve-bounded /
intersection-defined surface, and the composition's seams or defining
curves are inconsistent with the face's declared `face_bounds`.
**Mechanical witness**: parse composite-surface segments; verify each
boundary curve lies on its segment within tolerance.

### sub-class: edge sharing  (count: 1, prefix Tsh)
**Definition**: A shell has edges that should be shared between
neighbouring faces but are duplicated as separate `EDGE_CURVE`
instances, breaking sewing's edge-table identification.
**Mechanical witness**: tier-3: cluster edges by 3D-curve geometry +
endpoint within ε; flag clusters where face-side incidences ≠ shared
edge multiplicity.

### sub-class: instance-multiplication / placement  (count: 1, prefix A)
**Definition**: An assembly's instance-multiplication mechanism
(`MAPPED_ITEM` or `NAUO` with multiple placements) produces a placement
graph that double-applies a transform or omits a transform on one
branch.
**Mechanical witness**: tier-3: enumerate all leaf placements; verify
unique transform-chain per leaf.

### sub-class: subtype unimplemented  (count: 1, prefix Gn)
**Definition**: An entity uses a complex-instance subtype combination
(`B_SPLINE_CURVE` + `BEZIER_CURVE`, etc.) that the consuming kernel
recognizes by keyword but lacks a code path for.
**Mechanical witness**: complex-instance `&SCOPE` chain enumerates a
combination not in the kernel's dispatch table.

### sub-class: cross-product (umbrella, prefix Xp; covers §12.12)
**Definition**: A fixture whose defect is the *combination* of two or
more single-feature defects from other sub-classes (e.g., malformed
`\X2\` PRODUCT.name × self-intersecting wire), exercising the
disagreement surface between vendor pipelines.
**Mechanical witness**: catalog `category` lists ≥ 2 single-feature
defect references joined by `×`.

### sub-class: out-of-range tolerance declaration  (count: 2, prefix Tb)
**Definition**: An `UNCERTAINTY_MEASURE_WITH_UNIT` declares a value
outside a sensible operating range for the unit (e.g., 1 m on an
mm-scale model, 1e-30 m on a dm-scale model).
**Mechanical witness**: compare declared uncertainty against bounding-box
dimension order of magnitude.
**Spec reference**: ISO 10303-41 `UNCERTAINTY_MEASURE_WITH_UNIT`.

### sub-class: dimensional-exponents  (count: 2, prefix U)
**Definition**: A `DIMENSIONAL_EXPONENTS` 7-tuple does not match the
unit it is attached to (e.g., declaring `(1, 0, 0, 0, 0, 0, 0)` for a
plane angle, where it should be `(0, 0, 0, 0, 0, 0, 0)`).
**Mechanical witness**: parse `*_UNIT.dimensions` reference; compare
exponent vector against unit-class table.
**Spec reference**: ISO 10303-41.

---

## Coverage notes

- 15 top-level tag definitions (one per `TAG_VOCABULARY` entry).
- 73 sub-class definitions covering:
  - The top ~50 cross-prefix sub-classes by frequency (every sub-class
    with count ≥ 2, plus several count-1 entries for prefix coverage).
  - One representative sub-class per named prefix from the catalog
    header legend (Le, Lh, Ls, Gp, Gn, Gs, Tsh, Twi, Tfa, N, U, A,
    Pmi, M, Pf, Ad, Hea, Bo, Sw, Fi, Os, In, Gb, Tb, Ps, Xp, Wr).
- The remaining ~489 long-tail sub-classes are catalog-local
  disambiguators within a prefix; they fall under the parent
  prefix's umbrella definition above. (562 distinct sub-class
  strings appear across 1282 entries.)

## How to use these definitions

1. **Mechanical detection**: each definition's *witness* is concrete
   enough to encode as a checker. Many witnesses are pure byte-regex
   assertions (already encoded in catalog `Byte assertion` lines);
   others are tier-3 measurements (see
   `validation/src/step_corpus/_tier3.py` for the existing tier-3
   harness).
2. **Fuzz-input generation**: invert the witness. Generate a fixture
   that *positively* matches the regex / structure / measurement, then
   verify validate2 surfaces the expected behaviour from the entry's
   `expected_validation` line.
3. **Entry-class taxonomy bookkeeping**: when adding a new catalog
   entry, choose its sub-class string from this document (or extend
   this document with a new sub-class definition before the catalog
   merge).
