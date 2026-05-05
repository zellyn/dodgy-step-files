# §12.2c — Surface & curve degeneracy defects (Gs-prefix)

Surface/curve geometric degeneracies: zero-radius cylinders/cones/spheres, self-intersecting surfaces, degenerate elementary curves, sweep/extrusion direction issues, axis-placement defects, and other low-level geometric pathologies.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.2c) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Gb001](Gb001.stp) | Curve approximation cannot meet the requested tolerance |
| [Gb002](Gb002.stp) | Surface tangent / normal undefined at a parameter (LProp_Status.Undefined) |
| [Gb003](Gb003.stp) | Closed B-spline curve has reversed end-tangent |
| [Gb004](Gb004.stp) | Pcurve and 3D curve disagree by a measurable distance (CheckCurveOnSurface) |
| [Gs001](Gs001.stp) | TOROIDAL_SURFACE with negative MajorRadius (SolidWorks/Pro-E orientation marker) |
| [Gs002](Gs002.stp) | Degenerate (lemon/apple) torus where minor_radius >= major_radius |
| [Gs005](Gs005.stp) | Surface periodicity not declared but actually closed |
| [Gs006](Gs006.stp) | Surface singularities (degenerate poles) not in declared form |
| [Gs007](Gs007.stp) | Pcurve U coordinate outside canonical [0, 2π) seam range on `CYLINDRICAL_SURFACE` (whole wire off by period) |
| [Gs009](Gs009.stp) | Self-intersecting / figure-eight `EDGE_LOOP` wire on planar face (non-simple polygon) |
| [Gs010](Gs010.stp) | Self-intersecting / folded `B_SPLINE_SURFACE_WITH_KNOTS` (Jacobian sign change, transposed interior rows) |
| [Gs011](Gs011.stp) | Crossed-trim `EDGE_LOOP` with non-shared diagonals (mesh-derived BRep, STL→STEP) |
| [Gs012](Gs012.stp) | Non-simple `EDGE_LOOP` (face boundary self-crosses in UV: bow-tie quadrilateral) |
| [Gs014](Gs014.stp) | Zero-area / sliver / degenerate `ADVANCED_FACE` (sliver, spot, strip, pin; tiny aspect-ratio rectangle) |
| [Gs015](Gs015.stp) | Sliver face (high aspect ratio, two long edges within tolerance) |
| [Gs018](Gs018.stp) | Mismatched orientation of 3D curve and pcurve |
| [Gs019](Gs019.stp) | Pcurves shifted by integer period on closed surface |
| [Gs021](Gs021.stp) | Line displaced from true position (FPX Expert PCB) |
| [Gs024](Gs024.stp) | Round-trip planar face becomes trimmed B-spline (degree-1 NURBS) |
| [Gs025](Gs025.stp) | `B_SPLINE_CURVE_WITH_KNOTS` C0 cusp / kink at interior knot of full multiplicity (C1 expected) |
| [Gs026](Gs026.stp) | Helix on `CYLINDRICAL_SURFACE` mis-projected: pcurve missing or BSpline-approximated (analytic line lost) |
| [Gs028](Gs028.stp) | Pseudo-seam edge: `SURFACE_CURVE` claims `PCURVE_S1_AND_S2` but lists same pcurve twice |
| [Gs029](Gs029.stp) | Curve with last < first parameter range |
| [Gs030](Gs030.stp) | Edge geometry inconsistent with adjacent faces' actual intersection |
| [Gs031](Gs031.stp) | `ADVANCED_FACE` with two `FACE_OUTER_BOUND` entries (duplicated outer contour, overlapping pcurves) |
| [Gs032](Gs032.stp) | Surface-of-linear-extrusion whose direction is parallel to its basis line |
| [Gs033](Gs033.stp) | Trim curves on `TOROIDAL_SURFACE` / NURBS produce jagged tessellation borders (`TRIMMED_CURVE` on `ELLIPSE` pcurve) |
| [Gs034](Gs034.stp) | Twisted / pinched / vertex-split face: `EDGE_LOOP` revisits a shared vertex (Möbius-cell pathology) |
| [Gs035](Gs035.stp) | Composite curve segment with infinite parameters / null parent_curve |
| [Gs036](Gs036.stp) | Negative-radius / zero-magnitude direction or vector |
| [Gs037](Gs037.stp) | Offset of a surface-of-linear-extrusion fails iso-curve evaluation |
| [Gs038](Gs038.stp) | Pcurve U/V parameter has large jump near periodic boundary on BSpline |
| [Gs039](Gs039.stp) | Helical sweep / variable-radius blend silently emitted as incomplete shell (cap-only face on `SPHERICAL_SURFACE` with `VERTEX_LOOP` bound) |
| [Gs040](Gs040.stp) | High-curvature curve / cusp from NURBS knot insertion |
| [Gs041](Gs041.stp) | `RECTANGULAR_COMPOSITE_SURFACE` with non-uniform patch grid |
| [Gs042](Gs042.stp) | `CURVE_BOUNDED_SURFACE` with self-intersecting (bowtie) boundary |
| [Gs043](Gs043.stp) | `OFFSET_CURVE_3D` with `ref_distance` equal to the basis curve's radius of curvature (collapse) |
| [Gs044](Gs044.stp) | `INTERSECTION_CURVE` between two surfaces with multiple disjoint intersection branches, only one represented |
| [Gs045](Gs045.stp) | `SURFACE_OF_REVOLUTION` whose revolution axis crosses the basis curve at an interior point |
| [Gs046](Gs046.stp) | `SURFACE_OF_LINEAR_EXTRUSION` with zero-magnitude extrusion vector |
| [Gs047](Gs047.stp) | `BLENDED_EDGE_SURFACE` with mismatched fillet radii at a shared vertex |
| [Gs048](Gs048.stp) | `OFFSET_CURVE_2D` with sign of `ref_distance` flipping mid composite-curve chain |
| [Gs049](Gs049.stp) | B-spline surface has C0 isoparametric line that triggers split-on-import |
| [Gs050](Gs050.stp) | Toroidal surface stored incorrectly: major / minor swapped |
| [Gs051](Gs051.stp) | Sphere/cylinder cut produces wrong pcurves on second seam |
| [Gs052](Gs052.stp) | Surface of revolution with offset basis curve breaks on export |
| [Gs053](Gs053.stp) | Scaled sphere as B-spline approximation broken on export |
