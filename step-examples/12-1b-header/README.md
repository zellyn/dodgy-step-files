# §12.1b — Header & instance-numbering defects (Lh-prefix)

Missing/wrong magic line, missing `END-ISO-10303-21;`, missing `ENDSEC;`, wrong order or arity of HEADER entities, malformed `FILE_DESCRIPTION` / `FILE_NAME` / `FILE_SCHEMA`, schema-name issues, timestamp formats, and instance-numbering anomalies (`#0`, duplicate `#N`, gaps, forward references).

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.1b) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Lh002](Lh002.stp) | Missing or malformed closing marker `END-ISO-10303-21;` |
| [Lh003](Lh003.stp) | Missing `ENDSEC;` between sections |
| [Lh004](Lh004.stp) | HEADER section missing one of the three required entities (FILE_DESCRIPTION / FILE_NAME / FILE_SCHEMA), wrong order, or duplicated |
| [Lh005](Lh005.stp) | FILE_DESCRIPTION/FILE_NAME/FILE_SCHEMA arity mismatch (extra or missing attributes) |
| [Lh006](Lh006.stp) | `FILE_SCHEMA` written without the required double parentheses (list of strings) |
| [Lh007](Lh007.stp) | Multiple schema names listed inside a single FILE_SCHEMA |
| [Lh008](Lh008.stp) | Duplicate `FILE_SCHEMA` records with conflicting schema names |
| [Lh009](Lh009.stp) | Blank, mis-cased, or unrecognized schema name |
| [Lh010](Lh010.stp) | `FileImplementationLevel` non-canonical value |
| [Lh011](Lh011.stp) | `FileTimeStamp` not in ISO-8601 form |
| [Lh012](Lh012.stp) | Unquoted timestamp in FILE_NAME (timestamp not a STRING) |
| [Lh013](Lh013.stp) | Non-deterministic / build-time timestamp pollution |
| [Lh015](Lh015.stp) | User-defined HEADER entity not prefixed with `!` |
| [Lh016](Lh016.stp) | Edition-3 extra header entities (`FILE_INFO`, `FILE_POPULATION`, `SECTION_LANGUAGE`, …) |
| [Lh017](Lh017.stp) | User-defined entity name with `!` prefix in DATA section |
| [Lh018](Lh018.stp) | Lower-case keyword (`ifcperson`, `cartesian_point`, `ENTITY` etc.) |
| [Lh019](Lh019.stp) | FILE_SCHEMA names a schema that disagrees with entity types in DATA |
| [Lh022](Lh022.stp) | Duplicate instance ID (`#N=..` defined twice within one DATA section) |
| [Lh023](Lh023.stp) | Whitespace, tab, or comment between `#` and digits of an instance ID |
| [Lh024](Lh024.stp) | Reuse of `#NNN` across different DATA sections (Ed.3 multi-section) |
| [Lh025](Lh025.stp) | Mixing `#NNN` (entity) and `@NNN` (value) namespaces (Ed.3) |
| [Lh026](Lh026.stp) | Edition-3 ANCHOR / REFERENCE / SIGNATURE sections present in Edition-2 readers |
| [Lh027](Lh027.stp) | Malformed entity ID inside an ANCHOR entry (non-numeric `#`) |
| [Lh028](Lh028.stp) | Forward reference inside ANCHOR section to undefined data instance |
| [Lh029](Lh029.stp) | Schema name in FILE_SCHEMA has whitespace, comments, or vendor extensions inside the list |
| [Lh030](Lh030.stp) | Lower-case `name` field values where Recommended-Practices keywords are defined |
| [Lh031](Lh031.stp) | Header recognition relies on FILE_NAME originating-system substring (I-DEAS auto-detect) |
| [Lh032](Lh032.stp) | Constant reference (`#NAME`/`@NAME`) used where instance reference required |
| [Lh033](Lh033.stp) | Multi-DATA-section file with cross-section reference via `@section_name#NNN` |
| [Lh034](Lh034.stp) | REFERENCE section pointing at unresolvable external anchor |
| [Lh035](Lh035.stp) | ANCHOR section publishing the same anchor name twice |
| [Lh036](Lh036.stp) | SIGNATURE section with unknown signature algorithm |
| [Lh037](Lh037.stp) | User-defined HEADER entity (`!FOO`) emitted before required HEADER records |
| [Lh038](Lh038.stp) | `FILE_POPULATION` header record naming an unterminated population set |
| [Lh039](Lh039.stp) | Multi-DATA-section file with `#NNN` reuse and ambiguous local reference |
| [Lh040](Lh040.stp) | `FILE_INFO` Edition-3 record contradicting `FILE_NAME` date |
| [Lh041](Lh041.stp) | REFERENCE section with mixed URI schemes including unsupported schemes |
| [Lh042](Lh042.stp) | SIGNATURE section appearing before DATA (signature-over-empty-content) |
| [Lh043](Lh043.stp) | Header `FILE_DESCRIPTION` with comments inside string |
| [Lh044](Lh044.stp) | Cross-section reference resolves through chain (`@s1#10` defined as `@s2#20`) |
| [Lh045](Lh045.stp) | Cross-section reference to undefined section name |
| [Lh046](Lh046.stp) | HEADER section contains only `/* */` comments and no required records |
| [Lh047](Lh047.stp) | Lower-case section keywords (`data;` instead of `DATA;`) |
| [Lh048](Lh048.stp) | STEP reader cannot consume a non-seekable stream (in-memory / pipe / network) |
| [Lh049](Lh049.stp) | Big-endian / s390x byte-order in OCCT wrapper drops shapes |
| [Lh050](Lh050.stp) | STEP header `DATE_AND_TIME` malformed — FreeBSD `timezone` variable declaration conflict |
| [Lh051](Lh051.stp) | Leading-zero instance-name aliasing collision (`#1` and `#01` are the same name) |
| [Lh052](Lh052.stp) | Conformant AP203 file rejected at the `DATA;` boundary (independent-parser differential) |
| [Lh053](Lh053.stp) | FILE_NAME preprocessor_version contains "I-DEAS", plus a real open shell with an adjacent, edge-sharing closing shell |
