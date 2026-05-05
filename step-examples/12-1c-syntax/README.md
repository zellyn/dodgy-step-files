# §12.1c — Part-21 syntax / grammar defects (Ls-prefix)

Missing semicolons, malformed entity instances, comment-syntax pitfalls, list/array/tuple delimiter errors, omitted attributes, type-prefix misuse, untyped enums, real-number formatting issues, and other lexical/grammar violations within the DATA section.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.1c) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [In001](In001.stp) | Model marked Loaded without entities; load skipped silently |
| [In002](In002.stp) | Load-time warning vs data-content warning: severity confusion |
| [In003](In003.stp) | A "Mend" demotes a Fail to a Warning, hiding the original failure (e.g., B_SPLINE_CURVE_WITH_KNOTS with wrong knot count auto-fixed) |
| [In011](In011.stp) | Reader exception swallowed (entity bound to null) when B_SPLINE control points use extreme-magnitude or subnormal coordinates (1.0E+308 / 5.0E-324) |
| [In012](In012.stp) | Transfer watchdog fires: dependency cycle in entity references |
| [In013](In013.stp) | Transfer Status remains Void after Defined was expected: unknown entity type in DATA section silently skipped (e.g., made-up future-schema entity) |
| [Ls001](Ls001.stp) | REAL literal missing mandatory decimal point |
| [Ls002](Ls002.stp) | REAL literal with no digit before the decimal point |
| [Ls003](Ls003.stp) | Lower-case `e` exponent or whitespace around exponent |
| [Ls004](Ls004.stp) | Fortran-style `D` exponent (`1.0D5`) |
| [Ls005](Ls005.stp) | Explicit positive sign on numeric literal (`+1.0`) |
| [Ls006](Ls006.stp) | Numeric literal with embedded underscore digit-grouping |
| [Ls008](Ls008.stp) | Float literal with extreme exponent / non-finite real |
| [Ls009](Ls009.stp) | Integer literal with hex/octal forms |
| [Ls010](Ls010.stp) | Complex / multiple-inheritance entity record ordering and contents |
| [Ls013](Ls013.stp) | Empty parameter list `()` versus typed empty parameter |
| [Ls014](Ls014.stp) | Untyped (`*`) attribute used where derived not declared / `$` confused with `*` |
| [Ls015](Ls015.stp) | Missing comma between attribute values |
| [Ls016](Ls016.stp) | Double comma / empty parameter slot |
| [Ls017](Ls017.stp) | Trailing comma at end of aggregate |
| [Ls018](Ls018.stp) | Two consecutive semicolons (`;;`) after instance |
| [Ls019](Ls019.stp) | Missing closing `)` of an aggregate (paren imbalance) |
| [Ls020](Ls020.stp) | Trailing semicolon after `ENDSEC` missing |
| [Ls023](Ls023.stp) | Missing or malformed opening magic line `ISO-10303-21;` |
| [Ls024](Ls024.stp) | Tail garbage after end marker |
| [Ls027](Ls027.stp) | Legacy SCOPE/ENDSCOPE blocks (Edition 1) and EXPORT lists |
| [Ls029](Ls029.stp) | Comment terminator absent — runs through EOF |
| [Ls030](Ls030.stp) | Apostrophe inside `/* ... */` comment misread as string delimiter |
| [Ls031](Ls031.stp) | Forward-slash inside `/* ... */` comment treated as nested-comment open |
| [Ls032](Ls032.stp) | Comment longer than implementation buffer |
| [Ls033](Ls033.stp) | Whitespace handling: tab/CR/LF/FF as token separators or ignored chars |
| [Ls034](Ls034.stp) | Enumeration value missing dotted delimiters or with bad casing |
| [Ls035](Ls035.stp) | Boolean enum that is not `.T.`/`.F.` |
| [Ls036](Ls036.stp) | Binary literal `"…"` malformed (bit-count nibble or hex case) |
| [Ls038](Ls038.stp) | Instance ID `#0` or out-of-range / overflowing |
| [Ls043](Ls043.stp) | Excessively long entity name |
| [Ls044](Ls044.stp) | String concatenation across consecutive literals (not allowed) |
| [Ls045](Ls045.stp) | Print/control directives appearing outside string-literal context |
| [Ls046](Ls046.stp) | STEP parser syntax error messages inaccessible to caller (e.g., entities with unclosed parentheses and missing string quotes) |
