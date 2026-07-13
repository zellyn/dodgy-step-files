# 12-13-writer-pathology

## Fixtures

| ID | Title |
|---|---|
| [Wr001](Wr001.stp) | Trailing whitespace on every record line |
| [Wr002](Wr002.stp) | Mixed CRLF and LF line endings within one file |
| [Wr003](Wr003.stp) | Final `END-ISO-10303-21;` without trailing newline |
| [Wr004](Wr004.stp) | Tab characters used for line continuation indentation inconsistently |
| [Wr005](Wr005.stp) | Floating-point format inconsistency within one file |
| [Wr006](Wr006.stp) | Floating-point precision degradation on round-trip |
| [Wr007](Wr007.stp) | Locale-sensitive decimal separator emitted (comma instead of period) |
| [Wr008](Wr008.stp) | Excessive trailing zeros in numeric output |
| [Wr009](Wr009.stp) | Spurious `$` for required parameter (writer omits required value) |
| [Wr010](Wr010.stp) | Re-emitted `*` (overridden) where schema does not allow it |
| [Wr011](Wr011.stp) | Empty parameter list `()` where the schema requires at least one element |
| [Wr012](Wr012.stp) | Random `#N` numbering with no monotonic structure |
| [Wr013](Wr013.stp) | Forward references where sequential numbering was expected |
| [Wr014](Wr014.stp) | Sparse instance numbering with huge gaps |
| [Wr015](Wr015.stp) | Duplicate `#N` instance numbers in the same DATA section |
| [Wr016](Wr016.stp) | Re-output of intermediate construction entities (orphan geometry) |
| [Wr017](Wr017.stp) | Tessellation re-emitted from B-rep input (silent precision loss) |
| [Wr018](Wr018.stp) | Empty `SHAPE_DEFINITION_REPRESENTATION` chain (placeholder structure with no geometry) |
| [Wr019](Wr019.stp) | Re-export drops face and solid colour assignments |
| [Wr020](Wr020.stp) | Re-export drops feature labels and product names |
| [Wr021](Wr021.stp) | PMI annotations dropped on re-export |
| [Wr022](Wr022.stp) | Saved-view / camera metadata lost on re-export |
| [Wr023](Wr023.stp) | Validation properties (volume/area/centroid) dropped on re-export |
| [Wr024](Wr024.stp) | NAUO assembly-tree flattened on re-export |
| [Wr025](Wr025.stp) | NAUO chain re-rooted incorrectly (component becomes top) |
| [Wr026](Wr026.stp) | Vendor-specific FILE_DESCRIPTION strings that downstream readers special-case |
| [Wr027](Wr027.stp) | Unit context emitted twice with different units (HEADER vs DATA mismatch) |
| [Wr028](Wr028.stp) | `FILE_NAME.author` and `originating_system` fields blank or auto-filled with placeholder |
| [Wr029](Wr029.stp) | `FILE_DESCRIPTION` strings containing newlines or unescaped control characters |
| [Wr030](Wr030.stp) | `FILE_SCHEMA` listing schemas the file does not actually use |
| [Wr031](Wr031.stp) | Schema downgrade on export (AP242 input emitted as AP203, entities lost) |
| [Wr032](Wr032.stp) | Schema upgrade on export (AP203 input emitted as AP242 with synthesised stubs) |
| [Wr033](Wr033.stp) | `FILE_SCHEMA` declares schema version that does not exist |
| [Wr034](Wr034.stp) | Coordinate-system axis swap without notification (Y-up vs Z-up) |
| [Wr035](Wr035.stp) | Coordinate scale-factor applied twice (model 1000× larger or smaller than expected) |
| [Wr036](Wr036.stp) | Re-export inverts solid orientation (inside becomes outside) |
| [Wr037](Wr037.stp) | Loss of seam-edge marking on closed surfaces (cylinder seam emitted as ordinary edge) |
| [Wr038](Wr038.stp) | Re-emitted file uses entity-numbering pattern that breaks round-trip equivalence |
| [Wr039](Wr039.stp) | Re-export re-orders attributes within complex (subtype-stack) records |
| [Wr040](Wr040.stp) | Empty `name` strings on every entity (writer pre-fills `''` instead of omitting) |
| [Wr041](Wr041.stp) | Writer emits `.TRUE.` / `.FALSE.` instead of canonical `.T.` / `.F.` |
| [Wr042](Wr042.stp) | Inconsistent end-of-record terminator: `;\n` and `;\r\n` mixed in same file |
| [Wr043](Wr043.stp) | Writer emits raw UTF-8 bytes in string literal where Ed.2 mandates `\X\` / `\X2\` escape |
| [Wr044](Wr044.stp) | Inch unit declared in `LENGTH_UNIT` context but coordinates emitted in millimetres (no conversion) |
| [Wr045](Wr045.stp) | Unit name in `LENGTH_UNIT` changed without rescaling coordinate values |
| [Wr046](Wr046.stp) | Body Placement (rotation/translation) not applied during STEP export of a single part |
| [Wr047](Wr047.stp) | STEP import regressed by `BOPAlog_AlertBadPositioning` warnings (writer emits CSG-residual positions) |
| [Wr048](Wr048.stp) | Boolean-result body crashes STEP writer in `libTKXDESTEP` color-attribution pass |
| [Wr049](Wr049.stp) | Subtractive pipe at right-angle joints emits hidden sphere of material in joint |
| [Wr050](Wr050.stp) | Geometry coordinate values doubled on export (writer applies scale and unit-conversion both) |
| [Wr051](Wr051.stp) | step-g imports cleanly but downstream `g-stl` tessellator silently writes zero triangles |
| [Wr052](Wr052.stp) | Writer emits EDGE_CURVE backed by untrimmed LINE entity |
| [Wr053](Wr053.stp) | Toroidal-surface portion of fused solid corrupted on STEP round-trip |
| [Wr054](Wr054.stp) | Swept spherical face orientation inverted on STEP export round-trip |
| [Wr055](Wr055.stp) | Writer regression flips half of ORIENTED_EDGE directions |
| [Wr056](Wr056.stp) | Writer aliases geometrically-identical entities (shared substructure) |
| [Wr057](Wr057.stp) | Big-endian (s390x) writer emits empty STEP without diagnostic |
| [Wr058](Wr058.stp) | XCAF → STEP export crashes on umlaut in label |
| [Wr059](Wr059.stp) | STEP→BREP→STEP round-trip inflates cylinder analytic surface into B-spline |
| [Wr060](Wr060.stp) | Solidworks AP214 → OCCT version upgrade mis-locates surfaces |
| [Wr061](Wr061.stp) | X11 'aliceblue' colour shifted by sRGB→linear conversion on emit |
| [Wr062](Wr062.stp) | STEP→mesh gateway round-trip loses COLOUR_RGB and assembly hierarchy |
