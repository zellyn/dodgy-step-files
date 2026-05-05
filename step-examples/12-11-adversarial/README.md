# §12.11 — Adversarial / parser-robustness defects (Ad-prefix)

Adversarial / parser-robustness defects: deep entity-graph cycles, integer-overflow IDs, hostile escape sequences, billion-laughs-style expansions, and other inputs designed to expose parser pathologies.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.11) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Ad001](Ad001.stp) | Heap buffer overflow on overlong `'…'` string literal |
| [Ad002](Ad002.stp) | Stack overflow via deeply nested aggregate parentheses |
| [Ad003](Ad003.stp) | Negative / zero `B_SPLINE` degree or empty knot/multiplicity lists drive `malloc` size confusion |
| [Ad004](Ad004.stp) | Cyclic complex-entity reference graph causes infinite recursion |
| [Ad005](Ad005.stp) | Dangling forward reference to undefined `#NNN` |
| [Ad014](Ad014.stp) | Float literal with extreme exponent (`1E999999`) propagates as inf/NaN |
| [Ad015](Ad015.stp) | Empty aggregate where schema requires at least one element |
| [Ad026](Ad026.stp) | Self-referencing complex-entity instance during construction |
| [Ad027](Ad027.stp) | STEP "zip bomb": 10⁷ tiny instances exhaust memory |
| [Ad030](Ad030.stp) | Type-confusion via mis-typed reference (CARTESIAN_POINT used as DIRECTION) |
| [Ad031](Ad031.stp) | Malformed `FILE_DESCRIPTION` (missing `implementation_level` argument) triggers use-after-free in deferred header diagnostic |
| [Ad032](Ad032.stp) | Schema-EXPRESS rule recursion bomb |
| [Ad033](Ad033.stp) | Translator OOB write copying parsed string into packed C struct |
| [Ad035](Ad035.stp) | IGES-style 80-column padding sensitivity (shared translator code paths) |
| [Ad038](Ad038.stp) | File concatenation produces conflicting IDs and dual end-markers |
| [Ad042](Ad042.stp) | Reference to entity-of-wrong-type in attribute slot |
| [Ad043](Ad043.stp) | STEP read raises uncaught exception on null / invalid entity reference |
| [Ad044](Ad044.stp) | `EDGE_CURVE.same_sense` boolean read uninitialised |
| [Ad045](Ad045.stp) | Healing pipeline raises exception on real input with `EDGE_CURVE` vertices off the `LINE` by sub-confusion offset ("must not throw") |
| [Ad046](Ad046.stp) | STEP writer crashes on `ADVANCED_FACE` `EDGE_CURVE` with no `SURFACE_CURVE` / pcurve plus empty `APPLIED_GROUP_ASSIGNMENT` |
| [Ad047](Ad047.stp) | `ADVANCED_FACE` `same_sense=.F.` inverts surface normal: negative or invalid face area after orientation fix |
| [Ad049](Ad049.stp) | Real literal lacks decimal point or has Fortran `D` exponent |
| [Ad050](Ad050.stp) | Empty `EDGE_LOOP` / empty wire / empty entity iterator crashes reader |
| [Ad051](Ad051.stp) | Reference to non-existent entity number (negative or out-of-range) |
| [Ad052](Ad052.stp) | STEP file referencing itself as external file (infinite loop) |
| [Ad053](Ad053.stp) | Cyclic / reference-to-reference chain of `SHAPE_REPRESENTATION_RELATIONSHIP` |
| [Ad054](Ad054.stp) | Mutual-cycle `NEXT_ASSEMBLY_USAGE_OCCURRENCE` chain hangs reader's `Transfer` phase forever |
| [Ad055](Ad055.stp) | Stack overflow when meshing TBB pool from STEP import |
| [Ad056](Ad056.stp) | General-transform constructor throws on extreme non-uniform face stretch |
| [Ad057](Ad057.stp) | Memory leak / unbounded RSS after STEP assembly read (typed-value / BOOLEAN-enum table allocations not freed) |
| [Ad059](Ad059.stp) | Mismatched weight / pole counts in BSpline (writer-emitted) |
| [Ad064](Ad064.stp) | Underscore inside string truncated by name-parsing consumer |
| [Ad077](Ad077.stp) | Zero-length aggregates trigger `count-1` underflow / 4 GB loop walk (signed-integer attribute used as unsigned) |
| [Ad078](Ad078.stp) | `NEXT_ASSEMBLY_USAGE_OCCURRENCE` child as PRODUCT_DEFINITION_SHAPE (mis-typed select) |
| [Ad080](Ad080.stp) | Two `DATA` sections with colliding `#NNN` id space in one file (token-boundary attack) |
| [Ad081](Ad081.stp) | Empty `SHAPE_REPRESENTATION.items` plus dangling `PRODUCT_DEFINITION_SHAPE` triggers out-of-range abort in root-transfer (Rhino-6 emit) |
| [Ad082](Ad082.stp) | Late-bound forward reference (`FACE_OUTER_BOUND` → `EDGE_LOOP` → `ORIENTED_EDGE` defined later) trips binary BREP indexed-map lookup |
| [Ad083](Ad083.stp) | Multiple `PRODUCT`s share the same name; only `NEXT_ASSEMBLY_USAGE_OCCURRENCE` id disambiguates (assembly reader flat-load label collision) |
| [Ad084](Ad084.stp) | `XCAFDoc_ShapeTool::FindSubShape` crash building XCAF tree |
| [Ad085](Ad085.stp) | Composite-curve-segment self-cyclic reference |
| [Ad086](Ad086.stp) | Translator silently masks segfault-class faults as "transfer failed" on type-confused / overflow attribute references |
| [Ad087](Ad087.stp) | STEP reader crashes on file with unresolved entity reference |
| [Ad088](Ad088.stp) | Crash on reading STEP with malformed parameter values |
| [Ad089](Ad089.stp) | Reader broken parsing on missing last parameter |
| [Ad090](Ad090.stp) | Lower-case `End-ISO-10303-21` token rejected |
| [Ad091](Ad091.stp) | Crash on STEP file from non-C locale (decimal separator) |
| [Ad092](Ad092.stp) | Crash reading large STEP file: exception during transfer |
| [Ad093](Ad093.stp) | Empty / null input file path causes crash |
| [Ad094](Ad094.stp) | Shell translator dereferences null on empty face list |
| [Ad095](Ad095.stp) | STEP file from Pro/Engineer crashes (vendor-attribution) |
| [Ad096](Ad096.stp) | Crash on AP242 file: access violation reading entity |
| [Ad097](Ad097.stp) | Comment string inside STEP file breaks parser |
| [Ad098](Ad098.stp) | Infinite recursion during ShapeFix after Boolean cut |
| [Ad099](Ad099.stp) | Self-intersection healing of a wire with self-tangent loop pcurve never terminates |
| [Ad100](Ad100.stp) | Memory leak reading STEP file into TDocStd_Document |
| [Ad101](Ad101.stp) | Wire edge-curve healing reads past end of edge list after edge removal (open EDGE_LOOP / non-closed 3-edge wire) |
| [Ad102](Ad102.stp) | Crash transferring HLR-created shapes via STEP writer |
| [Ad103](Ad103.stp) | Coincident VERTEX_POINTs at identical CARTESIAN_POINT coordinates trigger vertex-merge healing throws on already-absorbed vertex |
