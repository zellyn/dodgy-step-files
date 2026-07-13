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
| [M092](M092.stp) | AP238 workplan workingsteps in non-executable order |
| [M093](M093.stp) | AP238 machining_tool referenced without cutting-edge geometry |
| [M094](M094.stp) | AP238 setup placement inconsistent with workpiece coordinate system |
| [M095](M095.stp) | AP238 machining_operation declares negative execution time |
| [M096](M096.stp) | AP238 trajectory missing connecting curves between adjacent segments |
| [M097](M097.stp) | AP238 workingstep references a feature not on the workpiece |
| [M098](M098.stp) | AP238 tool feedrate exceeds manufacturer rated maximum |
| [M099](M099.stp) | AP238 tool feedrate declared as zero |
| [M100](M100.stp) | AP238 spindle-on issued after first tool-workpiece contact |
| [M101](M101.stp) | AP238 two5d_milling_operation applied to a 3D-only feature |
| [M102](M102.stp) | AP238 drilling sequence with coincident hole positions |
| [M103](M103.stp) | AP238 tool trajectory passes through workpiece body before designated cut |
| [M104](M104.stp) | AP238 producer emits SETUP where WORKPIECE_SETUP is required |
| [M105](M105.stp) | AP238 ISO 8601 timestamps on operations going backwards |
| [M106](M106.stp) | AP238 workplan total execution time exceeds shift length |
| [M107](M107.stp) | AP238 cutting tool diameter declared as zero or negative |
| [M108](M108.stp) | AP238 freeform_milling_operation without surface-tolerance attribute |
| [M109](M109.stp) | AP209 linear_hexahedron with only 4 nodes (should be 8) |
| [M110](M110.stp) | AP209 ply orientation vector not normalized |
| [M111](M111.stp) | AP209 single_point_constraint applied to a node not in the mesh |
| [M112](M112.stp) | AP209 multi_point_constraint chain forms a dependency cycle |
| [M113](M113.stp) | AP209 element_representation with degenerate jacobian (collapsed corner) |
| [M114](M114.stp) | AP209 hex element with aspect ratio greater than 10000 |
| [M115](M115.stp) | AP209 nodal force distribution with negative weights |
| [M116](M116.stp) | AP209 modal extraction count exceeds DOF rank |
| [M117](M117.stp) | AP209 anisotropic material with missing tensor components |
| [M118](M118.stp) | AP209 non-conforming mesh: tet and hex sharing a face with mismatched node counts |
| [M119](M119.stp) | AP209 shell element with zero plate thickness |
| [M120](M120.stp) | AP209 symmetry plane not perpendicular to a coordinate axis |
| [M121](M121.stp) | AP209 time-history loadcase with non-monotonically increasing time vector |
| [M122](M122.stp) | AP209 ply orientation expressed in wrong reference frame |
| [M123](M123.stp) | AP209 element references the same node twice in its node list |
| [M124](M124.stp) | AP209 fea_model includes element referencing a node outside its node-set |
| [M125](M125.stp) | AP209 node_group declares the same node id twice |
| [M126](M126.stp) | AP203 effectivity periods overlap with conflicting product configurations |
| [M127](M127.stp) | AP203 DOCUMENT_FILE referenced with empty URI / path field |
| [M128](M128.stp) | AP203 design approved AFTER its effectivity start date |
| [M129](M129.stp) | AP203 new revision references parent not in change-history chain |
| [M130](M130.stp) | AP203 assembly classified at lower security level than its components |
| [M131](M131.stp) | AP203 PRODUCT_DEFINITION linked to wrong PRODUCT_CONTEXT frame_of_reference |
| [M132](M132.stp) | AP203 material-class APPLIED_GROUP_ASSIGNMENT without a material reference |
| [M133](M133.stp) | AP203 inconsistent ISO 8601 date formats within the same file |
| [M134](M134.stp) | AP203 two distinct PERSON entities share the same id |
| [M135](M135.stp) | AP203 declares CONFIG_CONTROL_DESIGN (CC1) but uses CC2-only entities |
| [M136](M136.stp) | AP203 APPROVED_ITEM points to a product not in the design pool |
| [M137](M137.stp) | AP203 APPLIED_ACTION_ASSIGNMENT applies to mixed-class object list |
| [M138](M138.stp) | AP203 APPROVAL_PERSON_ORGANIZATION with empty PERSON field |
| [M139](M139.stp) | AP203 effectivity start date is AFTER its end date |
| [M140](M140.stp) | AP203 make-or-buy declaration contradicts external supplier record |
| [M141](M141.stp) | AP203 PRODUCT_CATEGORY hierarchy contains a cycle |
| [M142](M142.stp) | AP203 CHANGE_REQUEST targets revision already superseded |
| [M143](M143.stp) | AP210 vias declared with stack-up positions out of board-layer order |
| [M144](M144.stp) | AP210 NETWORK_NODE chain forms a cycle (signal feedback path) |
| [M145](M145.stp) | AP210 fixed-side reference inverts top/bottom semantics |
| [M146](M146.stp) | AP210 drill diameter exceeds pad diameter (annular ring inverted) |
| [M147](M147.stp) | AP210 surface-mount component oriented on wrong board side |
| [M148](M148.stp) | AP210 same NETWORK identifier used for two unrelated nets |
| [M149](M149.stp) | AP210 component pin numbering doesn't match physical pin sequence |
| [M150](M150.stp) | AP210 differential-pair traces have > 5 % length mismatch |
| [M151](M151.stp) | AP210 declared trace impedance contradicts stackup geometry |
| [M152](M152.stp) | AP210 microvia depth exceeds substrate thickness |
| [M153](M153.stp) | AP210 buried via has only one terminating layer reference |
| [M154](M154.stp) | AP210 placement footprint pin count conflicts with library footprint |
| [M155](M155.stp) | AP210 net connectivity ends at a non-pin element |
| [M156](M156.stp) | AP210 power net carries only mechanical placement constraint |
| [M157](M157.stp) | AP210 solder mask covers a pad that should be exposed |
| [M158](M158.stp) | AP210 assembly footprint pitch conflicts with component-library footprint |
| [M159](M159.stp) | AP210 connector keying / polarization missing |
| [M160](M160.stp) | STEP file imports as a near-empty document despite well-formed entities |
| [M161](M161.stp) | Reader does not validate cross-references; dangling references silently accepted |
| [M162](M162.stp) | Fillet faces re-import as rounded edge (Onshape/Rhino) but as fillet in producer |
| [M163](M163.stp) | Imported STEP per-face colours scramble after any unrelated edit operation (style binding instability) |
| [M164](M164.stp) | Linear pattern of arc-shaped feature emits twisted/corrupted faces in STEP |
| [M165](M165.stp) | Knurled body exports STEP with holes in surface (slicer reports non-manifold) |
| [M166](M166.stp) | Heatsink-style fin array crashes export pipeline at faceted sub-shape boundary |
| [M167](M167.stp) | AP238 turning operation cut depth exceeds workpiece radius |
| [M168](M168.stp) | AP238 turning_finishing_face with feed direction inverted |
| [M169](M169.stp) | AP238 turning_roughing stepover exceeds tool nose radius |
| [M170](M170.stp) | AP238 turning feed-direction ambiguous (radial vs axial conflict) |
| [M171](M171.stp) | AP238 thread_turning pitch differs from thread-spec pitch |
| [M172](M172.stp) | AP238 turning_operation on workpiece without rotation axis |
| [M173](M173.stp) | AP238 milling_toolpath consecutive points spaced beyond tool diameter |
| [M174](M174.stp) | AP238 milling_feed_rate varies along path with no F-code transition |
| [M175](M175.stp) | AP238 drilling_operation tool axis not normal to feature face |
| [M176](M176.stp) | AP238 boring tool diameter exceeds start-hole diameter |
| [M177](M177.stp) | AP238 coolant_operation requests through-tool flow on tool with no internal cooling |
| [M178](M178.stp) | AP238 inspection_probing path passes through workpiece body |
| [M179](M179.stp) | AP238 touch_probing tolerance smaller than probe stylus radius |
| [M180](M180.stp) | AP238 inspection_result measurement uncertainty exceeds feature tolerance |
| [M181](M181.stp) | AP238 workpiece_complete_for_nc missing required clamping references |
| [M182](M182.stp) | AP238 setup_instruction sequence with non-monotonic time stamps |
| [M183](M183.stp) | AP238 workpiece_setup coordinate system not aligned with machine axes |
| [M184](M184.stp) | AP238 executable_relationship forms a cycle (A precedes B, B precedes A) |
| [M185](M185.stp) | AP238 machining_tool_feedspeed product exceeds tool envelope |
| [M186](M186.stp) | AP238 coolant type incompatible with workpiece material |
| [M187](M187.stp) | AP238 knurling_operation pitch finer than tool resolution |
| [M188](M188.stp) | AP238 deburring_operation references edge not present in workpiece |
| [M189](M189.stp) | AP238 boring tool diameter declared as negative |
| [M190](M190.stp) | Compound with free VERTEX_POINT silently dropped on STEP export |
| [M191](M191.stp) | Isolated wireframe: `GEOMETRIC_CURVE_SET` of a cube's 12 edges with no topology (no solid root) |
| [M192](M192.stp) | Point-set only: `GEOMETRIC_SET` of eight `CARTESIAN_POINT`s with no curves, surfaces, or topology |
| [M193](M193.stp) | Tessellated face's declared exact-geometry link points at a real but never-built face, reader substitutes a surfaceless mesh face |
| [M194](M194.stp) | Tessellated shell's declared topological-geometry link points at a real but never-built shell, reader substitutes a fresh shell |
| [M195](M195.stp) | Tessellated solid's declared exact-geometry link points at a real but never-built solid, reader substitutes a fresh shell-plus-solid |
| [M196](M196.stp) | Bare geometric set mixing a supported curve with an unsupported placement entity: the placement is silently skipped, the curve translates normally |
| [M197](M197.stp) | Faceted polygon boundary repeats the same point reference twice in a row; the reader skips the resulting zero-length segment instead of building a degenerate edge |
| [M198](M198.stp) | Triangle-strip index list repeats a vertex within one triple; the reader silently excludes the collapsed triangle instead of misreading or crashing on it |
| [M199](M199.stp) | Tessellated face's per-face normal row has the wrong number of components; the reader silently leaves every node's normal unset rather than misreading the row |
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
