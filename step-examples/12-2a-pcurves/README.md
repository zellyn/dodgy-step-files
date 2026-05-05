# §12.2a — P-curve / 2D parameter-space defects (Gp-prefix)

Pcurve definitional issues: missing pcurves on parametric surfaces, wrong UV domain, pcurve/edge-3D mismatch, periodic-shift defects, degenerate pcurves, missing `representation_item` wiring, and parametric-vs-3D inconsistencies.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.2a) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Gp001](Gp001.stp) | Missing pcurve on edge — only the 3D curve representation is present |
| [Gp002](Gp002.stp) | Pcurve endpoints disagree with edge vertex 3D positions |
| [Gp005](Gp005.stp) | Pcurve with single-pole apex on sphere/cone (singularity) |
| [Gp007](Gp007.stp) | Edge parameter range outside the pcurve's natural domain |
| [Gp008](Gp008.stp) | Pcurve oscillations producing wire-intersector corruption |
| [Gp010](Gp010.stp) | Surface_curve.associated_geometry contains a 3D curve in lieu of pcurve |
| [Gp011](Gp011.stp) | Seam curve with same pcurve referenced twice |
| [Gp012](Gp012.stp) | `SURFACE_CURVE` / seam-curve `associated_geometry` list contains a null `$` entry |
| [Gp013](Gp013.stp) | CATIA "like-seam": two pcurves on same near-closed `B_SPLINE_SURFACE_WITH_KNOTS` |
| [Gp014](Gp014.stp) | Shared pcurve across multiple edges (SYRKO) |
| [Gp015](Gp015.stp) | Pcurve/3D-curve trimming failure ("Trimming of 2D curve failed") |
| [Gp016](Gp016.stp) | Pcurve in shifted/transformed UV frame relative to host surface |
| [Gp018](Gp018.stp) | Pcurve gaps / nearly-duplicate pcurves near periodic boundary after `B_SPLINE_SURFACE` conversion |
| [Gp019](Gp019.stp) | Edge on a composite-surface face is missing per-patch pcurve |
| [Gp020](Gp020.stp) | 2D gap between adjacent edges in wire — pcurves disagree in UV |
| [Gp021](Gp021.stp) | 3D curve and pcurve on same edge disagree about edge location (skewed/off-unit pcurve `LINE`) |
| [Gp022](Gp022.stp) | `EDGE_CURVE` `SameParameter=.T.` asserted but 3D curve and pcurve use different parameterisations (degenerate B-spline pcurve) |
| [Gp023](Gp023.stp) | Point-projection onto trimmed periodic `CYLINDRICAL_SURFACE` returns UV outside trimmed band (pcurve start parameter shifted by period) |
| [Gp024](Gp024.stp) | Pcurve refit after non-uniform scale produces large errors |
| [Gp026](Gp026.stp) | `EDGE_LOOP` contour not closed in UV (Jordan-curve violation across periodic-surface seam) |
| [Gp027](Gp027.stp) | Closed-face splitter leaves new pcurves out of sync with 3D curves on `CYLINDRICAL_SURFACE` |
| [Gp028](Gp028.stp) | Wire crosses periodic-surface seam without an explicit seam edge (pcurve trim range vs vertex angular position mismatch) |
| [Gp029](Gp029.stp) | Period-shift fix on revolved face leaves wire in inconsistent UV band, blocks meshing |
| [Gp030](Gp030.stp) | Bent / polyline-form `B_SPLINE` pcurve from PRO/E IGES requires protective handling |
| [Gp031](Gp031.stp) | Cylinder represented twice as duplicate `CYLINDRICAL_SURFACE` instances loses analytic identity |
| [Gp033](Gp033.stp) | B-spline curve has C0 internal break that downstream tools cannot ingest |
| [Gp034](Gp034.stp) | Composite curve segments do not meet within connectivity tolerance |
| [Gp035](Gp035.stp) | Edge has 3D curve but no pcurve, requiring projection onto host surface |
| [Gp036](Gp036.stp) | Pcurve shifting on non-periodic surface produces wrong result |
| [Gp037](Gp037.stp) | Pcurve projection produces infinite line instead of bounded |
| [Gp038](Gp038.stp) | Vertex 3D point and pcurve do not match within tolerance |
| [Gp039](Gp039.stp) | Pcurve projection unstable on closed B-spline curve |
