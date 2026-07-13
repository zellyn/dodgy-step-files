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
| [Xp023](Xp023.stp) | Deeply nested aggregate × overlong string literal in one fixture (Pf × Ad cross-product) |
| [Xp024](Xp024.stp) | Tessellated topology × shared shell × void containment in one fixture |
| [Xp025](Xp025.stp) | Onshape→SolidWorks: assembly children snap to origin (placements lost) |
| [Xp026](Xp026.stp) | Fusion 360 AP242 export rejected by NX 12 (no AP242 import) |
| [Xp027](Xp027.stp) | Inventor STEP import "stuck at 95%" — long path in FILE_NAME author field |
| [Xp028](Xp028.stp) | Onshape "imports as one Surface" — missing face yields OPEN_SHELL |
| [Xp029](Xp029.stp) | Onshape STEP/SLDPRT export drops cosmetic thread metadata |
| [Xp030](Xp030.stp) | Inventor exports Asian (CJK) characters as raw legacy-codepage bytes |
| [Xp031](Xp031.stp) | KiCad STEP imports cleanly in FreeCAD but corrupts in SolidWorks (PRODUCT.name de-dup) |
| [Xp032](Xp032.stp) | CATIA V5 degenerate B-spline surface → Inventor "empty PartBody" |
| [Xp033](Xp033.stp) | NX-emitted cylinder split into two ADVANCED_FACE halves at the seam |
| [Xp034](Xp034.stp) | CadQuery RGB shifted by sRGB→linear conversion on STEP export |
| [Xp035](Xp035.stp) | CadQuery STEP writer emits redundant COLOUR_RGB entities for identical colours |
| [Xp036](Xp036.stp) | STYLED_ITEM colours dropped by bare STEPControl_Reader (vs XCAF reader) |
| [Xp037](Xp037.stp) | Creo Parametric assembly STEP with overlapping bodies fails manifold solid |
| [Xp038](Xp038.stp) | Onshape 2-56 UNC tap drill misclassified as M1.6 metric clearance hole |
| [Xp039](Xp039.stp) | Inventor "simplified part" loses appearance via empty SURFACE_SIDE_STYLE |
| [Xp040](Xp040.stp) | Solid Edge import of Creo Elements STEP: "stuck" sub-assemblies |
| [Xp041](Xp041.stp) | IfcOpenShell rejects valid IFC4X1 file due to lowercase 'x' in schema name |
| [Xp042](Xp042.stp) | NX → Onshape "translation error" via super-multiplicity B-spline knot |
| [Xp043](Xp043.stp) | CATIA AP242 → Inventor: top-level PRODUCT_DEFINITION without SDR |
| [Xp044](Xp044.stp) | KiCad PCB STEP export: missing components / wrong MAPPED_ITEM target |
| [Xp045](Xp045.stp) | Far-from-origin model collapses in a float32 viewer buffer while double-precision CAD renders it |
| [Xp046](Xp046.stp) | Valid conical `ADVANCED_FACE` dropped by OCCT 7.7.x `BRepMesh` but present in ≤7.6.1 / desktop CAD (kernel-version differential) |
