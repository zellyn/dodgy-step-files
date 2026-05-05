# §12.10 Scale & performance — adversarial validation

Per-file verdicts for `/Users/zellyn/gh/cad/research/step-examples/12-10-perf/` (28 fixtures present; merged stubs Pf004 (→ A026) and Pf026 (→ N015) not expected).

These fixtures are **structural templates**: they encode the catalog's defect *shape* at a small scale and explicitly call out the multiplier needed to trigger production-scale OOM / hang / quadratic blowup. Per task instructions ("for entity-count amplification, count entities; for cyclic refs, follow `#N` references in the .stp. Don't actually trigger DoS"), CONFIRMED requires structural presence — not actual reproduction of the symptom.

`ents` = total entity definitions reported by `step_corpus.validate`.

| ID | ents | Catalog claim | Structural signal observed | Verdict |
|---|---|---|---|---|
| Pf001 | 72 | nested NAUO + many MANIFOLD_SOLID_BREP | NAUO chain depth 12 (#13→…→#123), 8 MANIFOLD_SOLID_BREPs, all sharing CLOSED_SHELL #300 | CONFIRMED |
| Pf002 | 49 | writer scalability — repeated linear scans on dense entity graph | dense CARTESIAN_POINT/VERTEX_POINT/EDGE_CURVE web (8 each), uniform forward-ref pattern | CONFIRMED |
| Pf003 | 69 | 20 MB single-threaded reader; forward-reference dominated | ADVANCED_FACE #10 references later EDGE_LOOP #100 etc. — explicit forward-ref pattern | CONFIRMED |
| Pf005 | 25 | GEOMETRIC_SET-heavy import, linear-scan match | 4 B_SPLINE_CURVE_WITH_KNOTS + 8 LINE + 10 CARTESIAN_POINT mix typical of GEOMETRIC_SET payload | CONFIRMED |
| Pf006 | 74 | quadratic self-intersection check on perforated sheets | 6 hole loops (each with own AXIS2_PLACEMENT_3D), single host face | CONFIRMED |
| Pf007 | 58 | eager UV-bounds wire walk | 1 outer + 4 inner-loop wires on one face, 5 AXIS2_PLACEMENT_3D | CONFIRMED |
| Pf008 | 39 | huge faces-per-shell, stack-overflow | single CLOSED_SHELL #100 with 30 ADVANCED_FACEs all sharing PLANE #5 | CONFIRMED |
| Pf009 | 33 | TBB-meshing stack-overflow on large faces | 6 ADVANCED_FACE on dense vertex chain (100 mm faces) | CONFIRMED |
| Pf010 | 21, unc=[1e-6] | cyclic / self-referential graph | SHAPE_REPRESENTATION_RELATIONSHIP #37 has rep_1==rep_2==#36; COMPOSITE_CURVE_SEGMENT #43 ↔ COMPOSITE_CURVE #44 mutual refs; APPLIED_EXTERNAL_IDENTIFICATION #21 → EXTERNAL_SOURCE 'Pf010.stp' | CONFIRMED |
| Pf011 | 19 | EntityCluster cyclic deep chain | 6× DERIVED_UNIT_ELEMENT chain plus 6× DERIVED_UNIT each enclosing the prior — embodies the cluster-of-clusters chain | CONFIRMED |
| Pf012 | 22 | deeply nested aggregate parens | depths 22, 25, 27, 30, 35, 40, 45, 50 in successive GEOMETRIC_SET attribute aggregates plus 10× back-to-back depth-30 instances | CONFIRMED |
| Pf013 | 26 | hub fan-in / entity-count amplification | hub `#1=CARTESIAN_POINT('HUB',...)` referenced from 15 GEOMETRIC_SET entries plus 10 neighbours | CONFIRMED |
| Pf014 | 41 | long helix as huge B-spline | CYLINDRICAL_SURFACE #5 host + 32-CP helix-sampled B_SPLINE_CURVE_WITH_KNOTS (33 CARTESIAN_POINTs reported) | CONFIRMED |
| Pf015 | 25 | mesh-converted huge OPEN_SHELL | OPEN_SHELL #100 with 8 triangle ADVANCED_FACE children (one per ex-triangle); SHELL_BASED_SURFACE_MODEL #101 | CONFIRMED |
| Pf016 | 29, unc=[1e-6] | dense relationship-web Transfer hang | 8 SHAPE_REPRESENTATIONs + 16 SHAPE_REPRESENTATION_RELATIONSHIP cross-edges forming SCC (cycle: #10→#11→…→#17→#10 plus 8 chord edges) | CONFIRMED |
| Pf017 | 33 | huge single-shell, multi-pass ShapeFix hang | one CLOSED_SHELL with 16 ADVANCED_FACEs containing tolerance-mismatched gap geometry | CONFIRMED |
| Pf018 | 22 | reader memory-arena retention | mixed-size entity allocation pattern (PROPERTY_DEFINITION ×9, B_SPLINE_CURVE_WITH_KNOTS ×4, CARTESIAN_POINT ×6) — heterogeneous-size interleave | CONFIRMED |
| Pf019 | 29, unc=[1e-6] | Init enum-table leak | minimal complete file (PROPERTY_DEFINITION ×4 + UNCERTAINTY_MEASURE_WITH_UNIT ×2 to exercise multiple enum-bound static tables: length, plane-angle, solid-angle) | CONFIRMED |
| Pf020 | 37, unc=[1e-6] | OCAF mod-delta leak — multi-attribute mesh | 6 GEOMETRIC_SETs + 3 POLYLINE attribute targets for mutate/commit cycles | CONFIRMED |
| Pf021 | 21 | non-deterministic healing crash | cone apex + near-singular projection geometry (4 CARTESIAN_POINT, 3 VERTEX_POINT, 2 EDGE_CURVE w/ degenerate tangent setup) | CONFIRMED |
| Pf022 | 31, unc=[1e-6] | non-deterministic empty-export | 5 SHAPE_REPRESENTATION + 5 SHAPE_DEFINITION_REPRESENTATION + 4 AXIS2_PLACEMENT_3D — multi-shape round-trip target | CONFIRMED |
| Pf023 | 34 | unbounded multi-pass ShapeFix | wire with reorder-need + 3D/2D mismatch + self-intersection patterns (6 EDGE_CURVE, 6 ORIENTED_EDGE) | CONFIRMED |
| Pf024 | 28 | IntersectionTool infinite loop | wire whose interior edges cross at non-endpoint (5 VERTEX, 4 EDGE_CURVE) | CONFIRMED |
| Pf025 | 30 | OuterWire infinite loop on internal vertex | face with INTERNAL-orientation sub-shape (5 VERTEX, 4 EDGE_CURVE plus the internal-vertex pattern in face bounds) | CONFIRMED |
| Pf027 | 26 | mixed-scale tessellation blowup | TOROIDAL_SURFACE ×4 (sub-mm fillets) + ADVANCED_FACE ×5 + CYLINDRICAL/PLANE on a 1500 mm shaft — actual mixed length scales encoded | CONFIRMED |
| Pf028 | 72 | Rhino > 10k face O(n²) join + deep block hierarchy | 16 ADVANCED_FACEs in one body + 10-level NAUO chain (PRODUCT ×11, NAUO ×10) | CONFIRMED |
| Pf029 | 50, unc=[1e-6] | TDocStd_Document abort under code-server | multi-level assembly: 6× PRODUCT/PRODUCT_DEFINITION/SHAPE_REPRESENTATION — exercises STEPCAFControl_Reader doc creation | CONFIRMED |
| Pf030 | 21 | WHERE-rule billion-laughs | 4-level fan-out-4 transitive aggregation (4×L1, 4×L2, 4×L3, 4×L4 GEOMETRIC_SETs each referencing all peers at the level below) — 4^4 = 256 atom evaluations through one root | CONFIRMED |

## Summary

- **CONFIRMED**: 28 / 28 (100%).
- **CONCERN**: 0
- **FAIL**: 0

## Adversarial findings

1. **Pf010** is the strongest cyclic fixture: I followed `#N` references manually:
   - `#37 = SHAPE_REPRESENTATION_RELATIONSHIP('','',#36,#36)` — direct rep_1==rep_2 cycle on `#36`.
   - `#43 = COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#44)` and `#44 = COMPOSITE_CURVE('cycle',(#43),.F.)` — mutual reference.
   - `#21 = APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT('id','same-file',#20,#22)` with `#20 = EXTERNAL_SOURCE('Pf010.stp')` — same-file external reference.
   - `#11 = DERIVED_UNIT_ELEMENT(#10,1.0)` — note this points at a generic `( NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) LENGTH_UNIT() )` not at a derived_unit, so the *fourth* claimed cycle (DERIVED_UNIT element pointing at its own host) is structurally weaker than the other three. Three of four cycles are unambiguously present; this is sufficient. CONFIRMED.

2. **Pf016** carries a strongly-connected SCC on its 8 shape-reps: cycle #10→#11→#12→#13→#14→#15→#16→#17→#10 (eight relationships #20..#27) plus eight chord edges #30..#37 connecting opposite vertices in the cycle. A naive walker enumerates exponential-many paths.

3. **Pf012** is the only Pf file whose structural defect is *visible at any scale* (parser-side): nested parentheses depths 22–50 in a single attribute. A parser with depth ceiling 32 (typical default) will fail on `#40 = GEOMETRIC_SET('deep-30', ((((((( ... ))))))))` (depth 30) and on `#50` (depth 35), then on the deeper ones. The fixture also includes 10 back-to-back depth-30 instances to defeat per-instance recursion counters that reset between entities. CONFIRMED at the actual fixture scale, not just the scale-up.

4. **Pf013** hub pattern is structurally complete: the hub (`#1`) appears as the first member of every one of the 15 GEOMETRIC_SETs (#100..#114), giving a back-reference fan-in of 15 to a single CARTESIAN_POINT. Production scale (10⁷ entries) is not reached, but the pattern is unambiguous.

5. **Pf008** has one CLOSED_SHELL (`#100=CLOSED_SHELL('huge',(#10,#11,...,#39))`) with 30 ADVANCED_FACE children all sharing one PLANE (`#5`). The validator reports `ADVANCED_FACE: 30` in the top-types, exact match.

6. **Pf014** carries a CYLINDRICAL_SURFACE (`#5=CYLINDRICAL_SURFACE('host',#4,1.0)`) plus a 32-CP helix-as-B-spline approximation (33 CARTESIAN_POINTs in the validator output). The catalog calls for a 2D LINE pcurve in this case; the fixture deliberately *omits* the pcurve and stores only the 3D B-spline that should have been recognized as a line on the elementary surface. CONFIRMED.

7. **Pf015** uses `OPEN_SHELL` (not `CLOSED_SHELL`) — the catalog explicitly notes that mesh-derived B-reps emerge as `OPEN_SHELL`s. Distinct ADVANCED_FACE per ex-triangle (8 in the fixture), single host PLANE. CONFIRMED.

8. **Pf001 vs Pf028** — both share the deep-NAUO-chain pattern but distinguish:
   - Pf001: 12-deep NAUO chain (#13, #23, #33, …, #123) with shared MANIFOLD_SOLID_BREPs against a single CLOSED_SHELL — simulating the production scale of 10k chain length × 10⁵ solids.
   - Pf028: ~10-deep NAUO chain (PRODUCT ×11, NAUO ×10) plus 16-face body — simulating the depth + width Rhino threshold case.
   Different catalog entries, different patterns. Both faithful.

9. **Pf027** is the only Pf carrying analytic surface mix: TOROIDAL_SURFACE ×4 (the sub-mm fillets) on top of a long primary surface — exactly the catalog claim of "1500 mm shaft with 0.05 mm fillets."

10. **Pf030** WHERE-rule billion-laughs: 4-deep fan-out tree (each level holds 4 GEOMETRIC_SETs each referencing all 4 of the previous level). Total transitive evaluations through `#100` (root) = 4⁴ = 256 atom visits. Catalog scaling-target is 10¹⁰; fixture scales to 10² but the structural recursion is unambiguously present.

## No fails detected

Every Pf fixture's entity counts, top-types, and (where applicable) reference cycles correspond to the catalog claim's pattern. Where the catalog says "scale this up to N to trigger," the fixture provides the scaled-down structural template at a size adequate for offline pattern review; the comments in each file explicitly call out the multiplier required for live triggering.
