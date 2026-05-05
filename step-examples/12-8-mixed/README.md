# §12.8 — Mixed / auxiliary defects (M-prefix)

Tessellation, validation-property, supplemental geometry, FEA, and appearance defects that cross the boundaries of the other §12 sections.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.8) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Fi001](Fi001.stp) | Fillet on a contour where concavity flips along the spine |
| [Fi002](Fi002.stp) | Fillet contour walks into a high-valence vertex (> 3 incident edges) |
| [Fi003](Fi003.stp) | Fillet radius exceeds local curvature radius along the spine |
| [Fi004](Fi004.stp) | Fillet contour is geometrically inconsistent (disjoint or self-crossing) |
| [Fi005](Fi005.stp) | Fillet stops at a vertex where the rolling-ball can't trim cleanly |
| [Fi006](Fi006.stp) | Fillet at a 4-edge corner unsupported |
| [Fi007](Fi007.stp) | Fillet leaks off the boundary of its host face |
| [Fi008](Fi008.stp) | Fillet completes partially: HasResult but BadShape |
| [M002](M002.stp) | AP242 Edition 1 disallows axis2_placement_3d in tessellated_shape_representation |
| [M003](M003.stp) | Free-edge tessellated shell cannot use tessellated_connecting_edge |
| [M004](M004.stp) | Watertightness lost when each tessellated face has its own coordinates_list |
| [M005](M005.stp) | "Number of facets" validation property must include flat triangles dropped on import |
| [M006](M006.stp) | integer_representation_item serialized without trailing decimal point |
| [M008](M008.stp) | Validation properties only at geometry level, invisible to PDM-only readers |
| [M010](M010.stp) | Bound vs. unbound supplemental elements (planes, lines) |
| [M011](M011.stp) | Supplemental geometry inadvertently included in part-level GVP |
| [M012](M012.stp) | tessellated_constructive_geometry_representation requires AP242 Ed.4 |
| [M013](M013.stp) | Saved-view supplemental geometry split across multiple CGRs |
| [M014](M014.stp) | Anonymous constructive_geometry_representation_relationship breaks PMI link |
| [M015](M015.stp) | Tessellated PMI placement: third coordinate must be 0 in tessellated_geometric_set (repositioned form preferred) |
| [M016](M016.stp) | Tessellated curve set missing both coordinates and line_strips |
| [M017](M017.stp) | Tessellated geometry without a styled_item (no color) |
| [M018](M018.stp) | Crash on empty TESSELLATED_SHELL((), $) argument list |
| [M019](M019.stp) | TRIANGLE_STRIP / TRIANGLE_FAN in COMPLEX_TRIANGULATED_FACE mis-decoded |
| [M020](M020.stp) | Tessellated face style binding lost (no TransferBRep_ShapeBinder) |
| [M021](M021.stp) | Tessellated GD&T (annotation) entities not imported |
| [M022](M022.stp) | STL-derived tessellated_solid / triangulated_face ignored by importers |
| [M023](M023.stp) | Mesh-to-NURBS face has inner `FACE_BOUND` extending outside the `FACE_OUTER_BOUND` (self-intersecting STL→STEP face) |
| [M024](M024.stp) | Mesh-to-BRep gaps at trim curves (non-watertight result) |
| [M025](M025.stp) | Tessellated geometry preserved on round-trip vs always recomputed |
| [M026](M026.stp) | Validation Properties value mismatch (geometry self-check) |
| [M027](M027.stp) | Surface-sampling-point validation property failure |
| [M028](M028.stp) | Topology-count validation property failure |
| [M029](M029.stp) | PMI-count validation property failure |
| [M030](M030.stp) | Validation property naming: "geometric_validation_property" with underscores vs spaces |
| [M031](M031.stp) | Validation property: missing unit_component |
| [M032](M032.stp) | Validation property name not in CAx-IF list / mismatches associated general_property name |
| [M033](M033.stp) | Constructive geometry / supplemental geometry not allowed type |
| [M035](M035.stp) | Single-item Constructive_Geometry_Representation crashes translator |
| [M036](M036.stp) | Datum target axes nearly identical |
| [M037](M037.stp) | AP209 FEM element wrong node count |
| [M038](M038.stp) | AP209 freedom_and_coefficient `a` ≠ 1, or single_point_constraint `b` ≠ 0 |
| [M039](M039.stp) | STYLED_ITEM not parented under MDGPR/DRAUGHTING_MODEL (Inventor) |
| [M040](M040.stp) | STYLED_ITEM.item is NULL or unresolved |
| [M041](M041.stp) | Surface transparency (SURFACE_STYLE_TRANSPARENT) ignored on import |
| [M042](M042.stp) | Color override at root label not applied (regression) |
| [M043](M043.stp) | Layer with empty/duplicate name colliding with another |
| [M044](M044.stp) | Empty DRAUGHTING_MODEL / PRESENTATION_LAYER_ASSIGNMENT |
| [M045](M045.stp) | `NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION` (multiple `OPEN_SHELL`s with shared edge) loses XCAF colour / layer attributes on read |
| [M046](M046.stp) | PRESENTATION_LAYER_ASSIGNMENT carrying material/group names dropped |
| [M047](M047.stp) | Texture / bitmap (IMAGE_TEXTURE / TEXTURE_MAPPING) loss on translation |
| [M048](M048.stp) | Material / appearance / physical attributes silently dropped on STEP export |
| [M049](M049.stp) | Schema migration: 53 retired kinematics entities (AP242 Ed.1) |
| [M050](M050.stp) | Composite material LLAI (Limited Length / Area Indicator) gaps |
| [M051](M051.stp) | Bare GEOMETRIC_SET / GEOMETRIC_CURVE_SET with non-geometric children or mesh-as-surfaces |
| [M052](M052.stp) | Open shell where closed solid expected (sheet-vs-solid demotion) |
| [M053](M053.stp) | Mesh-derived non-manifold misclassification across receivers |
| [M054](M054.stp) | FACETED_BREP linked to OPEN_SHELL (schema-illegal) |
| [M055](M055.stp) | POLY_LOOP on non-planar surface inside FACETED_BREP |
| [M056](M056.stp) | Tessellation export missing or conflicting with B-rep representation |
| [M057](M057.stp) | File declaring AP203 schema but emitting AP242-arity entities |
| [M058](M058.stp) | File mixing AP203 schema declaration with AP214-only entity types in DATA |
| [M059](M059.stp) | File with AP242 ED1 schema string but ED2-only enumeration value |
| [M060](M060.stp) | External reference resolves to the same file as the main file |
| [M061](M061.stp) | Scaling-factor encoded as non-unit DIRECTION ratios in AXIS2_PLACEMENT_3D / ITEM_DEFINED_TRANSFORMATION skipped on write |
| [M062](M062.stp) | SRR reverses the relation defined by NAUO; conflict resolved silently |
| [M063](M063.stp) | Entity has no unit context; defaults silently applied |
| [M064](M064.stp) | GEOMETRIC_REPRESENTATION_CONTEXT lacks UNCERTAINTY_MEASURE_WITH_UNIT; reader-side default precision substituted |
| [M065](M065.stp) | Product has both sub-assemblies and a directly-assigned shape |
| [M066](M066.stp) | Non-manifold COMPSOLID translated as a set of independent SOLIDs |
| [M067](M067.stp) | Transformation relation creation failed (AXIS2_PLACEMENT_3D with zero-vector DIRECTION ratios in ITEM_DEFINED_TRANSFORMATION); placement falls back to identity |
| [M068](M068.stp) | Pretessellated geometry skipped on STEP write |
| [M069](M069.stp) | `TRIANGULATED_FACE` emitted without `pnval` indices |
| [M070](M070.stp) | `STL` writer does not respect existing triangulation |
| [M071](M071.stp) | AP238 machining_operation references nonexistent process_aspect |
| [M072](M072.stp) | AP238 toolpath_curve open chain claimed as closed contour |
| [M073](M073.stp) | AP238 part-coordinate vs machine-coordinate unit mismatch |
| [M074](M074.stp) | AP238 left-handed setup coordinate frame on multi-axis machine |
| [M075](M075.stp) | AP238 selective control-flow references unresolved branch executable |
| [M076](M076.stp) | AP238 cutting-tool feedrate stated in wrong dimensional unit |
| [M077](M077.stp) | AP238 fixture references different workpiece than the setup is machining |
| [M078](M078.stp) | AP209 quadratic_hexahedron with wrong node count (12 instead of 20) |
| [M079](M079.stp) | AP209 boundary condition with no nodes attached |
| [M080](M080.stp) | AP209 material property unit mismatch by 6 orders of magnitude |
| [M081](M081.stp) | AP209 integration_point_count not consistent with element_type |
| [M082](M082.stp) | AP209 surface element node order is clockwise (negative Jacobian) |
| [M083](M083.stp) | AP209 nodal load applied to a node not in the model node set |
| [M084](M084.stp) | AP209 composite laminate has empty ply stack |
| [M085](M085.stp) | AP210 ply with mismatched top/bottom material designations |
| [M086](M086.stp) | AP210 via drilled outside the conductor / board outline |
| [M087](M087.stp) | AP210 signal net node references unresolved terminal |
| [M088](M088.stp) | AP210 etherometric vs metric measurement context confusion |
| [M089](M089.stp) | AP210 stackup plies overlap in the Z direction |
| [M090](M090.stp) | AP210 BoM line item with no PRODUCT_DEFINITION chain |
| [M091](M091.stp) | AP210 conductor trace exits the board outline |
| [Os001](Os001.stp) | Offset of a surface whose normals flip sign |
| [Os002](Os002.stp) | Inward offset by a distance equal to a cylinder's radius (face collapses to axis) |
| [Os003](Os003.stp) | Inward offset by a distance greater than a cylinder's radius (face inverts) |
| [Os004](Os004.stp) | Offset request fails: source OPEN_SHELL contains spatially disconnected ADVANCED_FACEs (no shared edge between groups) |
| [Os005](Os005.stp) | Offset edge-trim step fails (edges don't trim cleanly against neighbours) |
| [Os006](Os006.stp) | Offset vertex-fuse step fails (corner vertices don't merge) |
| [Os007](Os007.stp) | Offset edge-extension step fails: clamped B_SPLINE_CURVE_WITH_KNOTS has no analytic extension past its trim domain |
| [Os008](Os008.stp) | Faces along a shared edge have mixed C0/G1 connectivity (offset cannot decide regularity) |
| [Os009](Os009.stp) | ThruSections loft profile is closed wire mixed with open wire |
| [Os010](Os010.stp) | ThruSections loft profiles have inconsistent edge counts |
| [Os011](Os011.stp) | ThruSections loft used outside its supported envelope |
| [Os012](Os012.stp) | ThruSections / loft produces an EDGE_CURVE with no 3D curve (edge_geometry slot is null '$' — pcurve-only edge) |
| [Os013](Os013.stp) | Pipe section plane does not intersect the guide curve |
| [Os014](Os014.stp) | Pipe section drifts beyond auxiliary spine reach (impossible contact) |
| [Os015](Os015.stp) | Draft modification fails to recompute a deformed face |
| [Os016](Os016.stp) | Draft modification fails to recompute an edge |
| [Os017](Os017.stp) | Draft modification fails to recompute a vertex |
| [Os018](Os018.stp) | N-sided fill: constraint set is geometrically incompatible |
| [Os019](Os019.stp) | Middle-path computation between two wires fails |
| [Os020](Os020.stp) | MakeEvolved: profile sweep along a non-planar spine self-intersects |
| [Os021](Os021.stp) | Normal projection: source curve has no projection on target surface |
| [Os022](Os022.stp) | FindContigousEdges: paired LINEs/VECTORs from sewing have unequal parameter lengths (unit vs non-unit DIRECTION) for the same 3D extent |
| [Os023](Os023.stp) | MakeThickSolid: thickening direction passes through a self-intersection |
