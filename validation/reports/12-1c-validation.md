# §12.1c Syntax Corpus — Adversarial Validation

Corpus: `/Users/zellyn/gh/cad/research/step-examples/12-1c-syntax/Ls*.stp` (32 files).
Tooling: `uv run python -m step_corpus.validate <path> --json`.

## Methodology

Each file targets a §12.1c lexical / structural defect. The expected adversarial
outcome (per the task brief and the prose inside each fixture) is that at least
one of the bundled parsers (ifcopenshell strict, OCCT heal-on/off, gmsh
autofix-on/off) **rejects** the file or surfaces the defect.

**Key environmental finding.** Every fixture declares
`FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'))`, which causes
ifcopenshell-strict to reject with `Unsupported schema: AUTOMOTIVE_DESIGN ...`.
This is a *schema-class* rejection at the header layer, not a §12.1c
syntax-layer rejection — ifcopenshell never reaches the DATA section, so its
verdict carries **no signal** for this corpus. The verdicts below therefore
weight OCCT and gmsh as the meaningful detectors. (The two files that *don't*
fail ifcopenshell with the schema string — Ls023 and Ls032 — fail for
content reasons: malformed magic line, and a long comment whose body
displaces the SPF header parser respectively.)

**Second key finding.** OCCT and gmsh almost always return
`status=accept` with `n_roots=0`, `shape_null=true`, `total_entities=0`. They
are silently swallowing the defect, dropping the offending entity, and
producing an empty model rather than raising an error. So `accept-with-empty`
is functionally a **silent miss** for these defects. Verdicts treat it as
FAIL unless ifcopenshell strict (or another parser) would catch the defect
through a non-schema path.

**Verdict legend.**
- **CONFIRMED** — at least one parser rejected the file at the syntax/structural layer (not the AUTOMOTIVE_DESIGN schema reject).
- **FAIL** — every parser silently accepted (ifcopenshell strict's reject is the schema-class reject and so is discounted).
- **AMBIGUOUS** — partial signal (e.g. only schema-class reject, but defect is one ifcopenshell would catch on a recognized schema).

## Per-file verdicts

| File  | Defect class                                  | ifc strict      | OCCT        | gmsh        | Verdict     |
|-------|-----------------------------------------------|-----------------|-------------|-------------|-------------|
| Ls001 | bare INTEGER where REAL required              | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls002 | leading-dot REAL (.5)                         | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls003 | lower-case 'e' exponent                       | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls004 | Fortran 'D' exponent                          | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls005 | leading '+' on numeric                        | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls006 | underscore digit-grouping                     | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls008 | extreme exponent (1.0E+999999)                | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls009 | hex / octal integer literal                   | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls010 | complex-entity ordering & separators          | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls013 | zero-argument entity record                   | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls014 | `*` / `$` confusion                           | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls015 | missing comma between attributes              | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls016 | double comma (`,,`)                           | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls017 | trailing comma in aggregate                   | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls018 | double semicolon (`;;`)                       | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls019 | unbalanced `)` in aggregate                   | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls020 | missing `;` after ENDSEC                      | reject (schema) | reject_at_read | reject   | CONFIRMED   |
| Ls023 | malformed magic line `iso-10303-21` (no `;`)  | reject (header) | reject_at_read | reject   | CONFIRMED   |
| Ls024 | tail garbage after END-ISO-10303-21;          | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls027 | Edition-1 SCOPE / ENDSCOPE block              | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls029 | unterminated comment to EOF                   | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls030 | apostrophe inside comment                     | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls031 | slash inside comment / nested-comment trap    | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls032 | comment > 8 KiB                               | reject (header) | accept (0)  | accept (0)  | AMBIGUOUS   |
| Ls033 | whitespace defects (`FILE _SCHEMA`, `# 10`)   | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls034 | enum missing dots / bad case                  | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls035 | non-{.T.,.F.} boolean (.U., TRUE, .UNKNOWN.)  | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls036 | malformed binary literal forms                | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls038 | `#0` and 22-digit / wraparound IDs            | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls043 | hyphen-in-identifier / very long name         | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls044 | adjacent string literals                      | reject (schema) | accept (0)  | accept (0)  | FAIL        |
| Ls045 | control directives (\X\, \N\) outside string  | reject (schema) | accept (0)  | accept (0)  | FAIL        |

`accept (0)` = `status=accept`, `n_roots=0`, `shape_null=true`, `total_entities=0`.

## Diagnoses for non-CONFIRMED outcomes

- **Ls001-Ls009 (numeric literal defects).** OCCT and gmsh swallow integer-where-REAL, leading-dot, lower-case `e`, Fortran `D`, leading `+`, underscore grouping, extreme exponent, and hex/octal literals without producing any geometry or any error code. The brief predicted ifcopenshell-strict rejection; in this corpus that cannot fire because the schema header bounces the file before the literal lexer runs.
- **Ls010 (complex entity).** OCCT silently drops the multiple-inheritance records (alphabetic-order, comma-separated, missing-ancestor cases). No warning surfaced through the validator's status fields.
- **Ls013-Ls014 (parameter syntax).** Zero-argument entity records and `*`/`$` misuse are accepted with empty result.
- **Ls015-Ls019 (punctuation).** Missing comma, double comma, trailing comma, double semicolon, and the unbalanced-paren cases are accepted with empty result. The brief said "all parsers reject" — that's clearly false here for OCCT and gmsh, at least when wrapped through the validator's accept/reject mapping. The defects are real (verified by reading the file bodies).
- **Ls024 (tail garbage).** Stray `DATA;ENDSEC;` after `END-ISO-10303-21;` not flagged.
- **Ls027 (Edition-1 SCOPE).** Brief predicted reject by most parsers; OCCT/gmsh did not.
- **Ls029-Ls031 (comment defects).** Unterminated comment, embedded apostrophe, embedded `/*` all accepted silently.
- **Ls032 (long comment).** AMBIGUOUS: ifcopenshell rejects with `Unable to parse IFC SPF header` (positive signal: the 8 KiB+ comment knocks the SPF header parser off track), but OCCT/gmsh still report `accept` with empty content. So ifcopenshell hits a length-related failure mode the brief flagged, while the C++ kernels do not.
- **Ls033 (whitespace).** Split keyword `FILE _SCHEMA` and `# 10` reference still produce zero-shape accept.
- **Ls034-Ls036 (enum / binary literal).** All malformed enum and binary forms accepted silently.
- **Ls038 (instance-ID range).** `#0`, 22-digit IDs, and `#18446744073709551617` accepted silently.
- **Ls043 (identifier limits).** Hyphen-in-name `BS7752-1` and 200-char `AAA...` name accepted silently.
- **Ls044 (string concat).** Adjacent string literals accepted silently.
- **Ls045 (control directives).** `\X\09` inside a numeric literal and `\N\` between top-level tokens accepted silently.

## Confirmed signals

- **Ls020** — missing `;` after `ENDSEC` is detected by both OCCT (`IFSelect_RetFail`) and gmsh.
- **Ls023** — malformed magic line `iso-10303-21` (lower-case, no `;`) is rejected by every parser; even ifcopenshell breaks at the header (not at the schema lookup).

## Summary

- **CONFIRMED**: 2 / 32 (Ls020, Ls023).
- **AMBIGUOUS**: 1 / 32 (Ls032).
- **FAIL**: 29 / 32 — the remaining §12.1c defects pass through every bundled parser without producing a non-accept status. Defects are present in the file bodies (manually verified for Ls010, Ls015, Ls019, Ls027, Ls029, Ls032, Ls038, Ls044), so this is a detector gap, not a fixture gap.

## Recommendations

1. **The current validator setup is not adversarial enough for §12.1c.** OCCT and gmsh routinely return `status=accept` with `shape_null=true` / `total_entities=0`, which the validator currently maps to "accept" without escalation. Treating "accept-but-empty" as a soft-reject (or at least flagging it as `accept_empty`) would surface the silent-drop behavior that dominates this corpus.
2. **Capture stderr / IFC return-status warnings.** OCCT prints `**** ERR StepFile : Incorrect Syntax : Fails Count : N ****` to stderr (visible in raw output for Ls004 and others) — the validator should hoist these into the JSON `warnings`/`errors` field so the verdict reflects them.
3. **The AUTOMOTIVE_DESIGN schema string defeats ifcopenshell entirely.** Either (a) regenerate the corpus against an IFC schema, (b) add a stepcode/stepwise pure-syntax checker that ignores schema, or (c) add a custom Part-21 lexical validator (the intended primary detector for §12.1c). Without one, lexical-grammar fixtures cannot produce CONFIRMED verdicts other than via OCCT's coarse `IFSelect_RetFail`.
4. **Add a "schema-mismatch reject" demotion.** When ifcopenshell's only error is `Unsupported schema: ...`, that should not be counted as a positive defect detection in any §12.1c verdict.
5. **Per-file regression baseline.** The 2-CONFIRMED, 1-AMBIGUOUS, 29-FAIL split should be checked into the corpus as the current ground truth, so any future improvement (a Part-21-aware checker, a stricter OCCT mode) shows up as movement out of FAIL.
