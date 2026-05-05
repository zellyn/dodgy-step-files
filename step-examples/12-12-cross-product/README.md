# §12.12 — Cross-product synthesized defects (`Xp*`-prefix)

Fixtures combining 2-3 single-defect classes per file (encoding × wire,
sliver × non-manifold, PMI × tess/BRep mix, etc.). They exercise
ordering and interaction hazards when multiple defect types co-occur
in the same file. Each entry's `**Builds on:**` field cites the single-
defect entries it composes.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.12)
for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Xp001](Xp001.stp) | Malformed `\X2\` escape in PRODUCT.name AND self-intersecting wire |
| [Xp002](Xp002.stp) | Periodic-surface seam gap × pcurve missing × unit-context mismatch |
| [Xp003](Xp003.stp) | Sliver face × non-manifold edge (3 faces share one edge) |
| [Xp004](Xp004.stp) | PMI annotation × tessellation-vs-BRep mix in a single AP242 file |
| [Xp005](Xp005.stp) | NURBS knot vector × control-point weight × tolerance-boundary cusp |
| [Xp006](Xp006.stp) | Schema-mismatch × forward-reference × unresolved entity |
| [Xp007](Xp007.stp) | Cyclic complex-entity reference × deeply-nested aggregate |
| [Xp008](Xp008.stp) | Empty EDGE_LOOP × empty FACE_OUTER_BOUND × otherwise-valid solid |
| [Xp009](Xp009.stp) | UTF-8 BOM × missing END marker × out-of-range surface knot vector |
| [Xp010](Xp010.stp) | Negative torus radius × pcurve disagreement × tiny edge |
| [Xp011](Xp011.stp) | REAL missing decimal × integer in DIRECTION × empty FILE_NAME author |
| [Xp012](Xp012.stp) | Reversed face normal × non-watertight shell × duplicate edge |
| [Xp013](Xp013.stp) | Cone apex pcurve × surface-folded × non-manifold vertex |
| [Xp014](Xp014.stp) | Open shell as MANIFOLD_SOLID_BREP.outer × tolerance-violation × unit mismatch |
| [Xp015](Xp015.stp) | Self-intersecting wire on cylindrical (periodic) face × seam-edge missing |
| [Xp016](Xp016.stp) | Forward reference × cyclic reference × invalid axis-placement |
| [Xp017](Xp017.stp) | Empty geometric-set × extreme coordinates × NaN component |
| [Xp018](Xp018.stp) | PMI without saved-view × unit-system mismatch × forward references |
| [Xp019](Xp019.stp) | Multiple DATA sections × duplicated entity ID × cross-section reference |
| [Xp020](Xp020.stp) | Tessellated face × BRep face sharing PMI × unit-system inch/mm collision |
| [Xp021](Xp021.stp) | Disconnected EDGE_LOOP × pcurve missing × wire bypassing seam |
| [Xp022](Xp022.stp) | Time-bomb tolerance × negative-radius torus × cyclic seam edge |
