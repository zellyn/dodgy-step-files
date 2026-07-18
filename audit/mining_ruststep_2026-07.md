# Mining ruststep for NEW file-level STEP defect classes (2026-07)

**Source.** `ricosjp/ruststep` — an independent (non-OCCT) Rust Part-21 / EXPRESS
parser built on `nom`, plus the `truck` CAD kernel that consumes it. High value
because it is a *fresh, strict* reader: its grammar (read directly from source) and
its issue tracker enumerate Part-21 lexical/structural cases it rejects that
OCCT-centric readers silently tolerate — exactly the independent-parser divergences
our corpus under-covers.

**Method.** Read `gh issue list` (all, 100) for `ricosjp/ruststep` + `ricosjp/truck`;
read the actual parser source (`ruststep/src/parser/{token,basic,combinator}.rs` and
`.../exchange/{header,data,parameter,anchor,reference,mod}.rs`) to extract the exact
accepted grammar; then grepped `STEP_PROBLEM_CATALOG.md` for novelty. We cite the
**pattern** only (Apache-2.0/MIT source; issue-attached files are user-uploaded and
proprietary — DESCRIBE-ONLY, never ingest bytes).

**Key grammar facts extracted from ruststep source (the mining substrate):**
- `entity_instance_name = '#' digit1`, parsed into **`u64`**; leading zeros ignored
  ("`#001` == `#1`", cited to ISO 10303-21 §6.4.4.3 NOTE 2); value > `u64::MAX` →
  hard `Failure(u64-overflow)`.
- `real() = [sign] ws digit1 '.' digit0 [exponent]` — **decimal point mandatory**;
  `exponent = 'E' ...` (upper-case only). `1E5` (no dot) is NOT a real → `integer`
  grabs `1`, leaving `E5`.
- `untyped_parameter` tries **`real` before `integer`** → `3.0` in an INTEGER slot
  becomes `Parameter::Real`.
- `string() = ' ( '' | none_of(') )* '` — accepts any non-apostrophe byte raw
  (incl. control chars, LF, and un-decoded `\X2\` runs); `''` → single `'`.
- `standard_keyword = upper {upper|digit}` — lower-case entity keyword rejected.
  Section tags (`HEADER;`,`DATA`,`ENDSEC;`,`END-ISO-10303-21;`) are exact & case-sensitive.
- `subsuper_record = '(' many0(simple_record) ')'` — accepts an **empty** complex
  instance `#1=();` and single-record "complex" instances.
- `exchange_file` opens with `tag("ISO-10303-21;")` with **no leading `ignorable`** →
  any BOM/whitespace before the magic line fails immediately.

---

## Candidate table

| # | Title / defect class | Source citation (pattern only) | Reproducer recipe (minimal Part-21) | Expected kernel behavior | Target section | Novelty | License |
|---|---|---|---|---|---|---|---|
| 1 | **Leading-zero instance-name aliasing collision** — `#1` and `#01` are the *same* name (ISO §6.4.4.3 NOTE 2); two definitions silently alias | ruststep `token.rs::entity_instance_name` doc (NOTE 2, normalizes to `u64`) | `DATA;#1=CARTESIAN_POINT('',(0.,0.,0.));#01=DIRECTION('',(1.,0.,0.));#2=VECTOR('',#01,1.);ENDSEC;` — `#2` resolves to whichever of `#1`/`#01` won | reject `E_DUPLICATE_INSTANCE_ID` after leading-zero normalization; never silently overwrite | Lh (§12.1b) | **NEW** — Lh022 is *byte-identical* dup; this is dup-after-normalization, which byte-diff and lax parsers miss | pattern-only |
| 2 | **Instance-name magnitude overflow (> `u64::MAX`)** — 20+ digit `#N` overflows fixed-width ID maps | ruststep `token.rs::u64_overflow` (explicit `Failure`) | `#18446744073709551616=CARTESIAN_POINT('',(0.,0.,0.));` (2^64) referenced by a second entity | reject with "instance id out of range"; must not overflow/wrap the id→pointer table | §12.1c / Ad (adversarial) | **NEW** — no huge-ID class; existing overflow entry is STRING-length only | pattern-only |
| 3 | **REAL with exponent but no mandatory decimal point** (`1E5`, `6E-4`) — dot is mandatory in Part-21 real grammar | ruststep `token.rs::real` (requires `digit1 '.'` before `exponent`) | `#1=CARTESIAN_POINT('',(1E5,0E0,6E-4));` | strict reject (missing dot); lenient promote+warn | §12.1c (Ls) | **BORDERLINE** — nearest Ls001 (integer-in-real, no exp) & Ls003 (e/ws/`+` exponent); the *uppercase-E, no-dot* form `1E5` is not explicitly a fixture | pattern-only |
| 4 | **REAL literal in an INTEGER slot** (`3.0` where INTEGER required) — inverse of Ls001; `real`-first tokenizer mis-types it | ruststep `parameter.rs::untyped_parameter` (tries `real` before `integer`); issue #56 "tokenize integer as float" | `#1=REPRESENTATION_ITEM('');#2=...B_SPLINE_CURVE(3.0,...)` — degree/count field carrying `3.0` | reject or warn on non-integral value in INTEGER slot; never truncate silently | §12.1c (Ls) | **NEW-ish** — Ls001 covers integer→real; the real→integer direction (fractional value in count/degree) is uncovered | pattern-only |
| 5 | **Empty complex (subsuper) entity instance** `#1=();` — zero constituent records | ruststep `data.rs::subsuper_record` (`many0` allows empty) | `#1=();#2=SHAPE_DEFINITION_REPRESENTATION(#1,#3);` | reject: a complex instance must combine ≥1 (really ≥2) simple records | §12.1c (Ls) | **NEW-ish** — Ls013 covers `PRODUCT()` (keyword present, no attrs); a keyword-less empty complex `()` is distinct | pattern-only |
| 6 | **Single-record "complex" instance** `#1=(NAMED_UNIT(*));` — parenthesized combined-entity form wrapping one record | ruststep `data.rs::subsuper_record` accepts len-1 list; issue #189 "Support complex entity" | `#1=(LENGTH_UNIT());` used where a simple `#1=LENGTH_UNIT();` was meant | accept but canonicalize, or warn; independent readers historically choke on the combined-entity form entirely | §12.1c (Ls) | **BORDERLINE** — complex-leaf-order is covered (Ls046-area); degenerate 1-leaf wrapper is not | pattern-only |
| 7 | **Well-formed AP203 (HOOPS/Plasticity) rejected at the `DATA` section boundary** — header comment + spaced `FILE_SCHEMA( ( ... ) )` + `T..+17:00` timestamp; independent tokenizer aborts at `DATA;` | ruststep issue #252 (HOOPS Exchange 24.2 AP203; `TokenizeFailed ... Tag: DATA;`) | `HEADER;/* File generated by HOOPS Exchange */FILE_DESCRIPTION(('x'),'2;1');FILE_NAME('p','2025-03-05T17:10:01+17:00',('a'),('b'),'c','d','e');FILE_SCHEMA( ('AP203_CONFIGURATION_CONTROLLED_3D_DESIGN_OF_MECHANICAL_PARTS_AND_ASSEMBLIES_MIM_LF') );ENDSEC;DATA;#1=CARTESIAN_POINT('',(0.,0.,0.));ENDSEC;END-ISO-10303-21;` | accept (conformant); this is a strict-reader leniency gap, OCCT/HOOPS accept | Lh (§12.1b, differential) | **BORDERLINE** — differential/leniency class; individual tokens (spaced schema list, header comment) are each tolerated but the *conformant-file-that-a-strict-parser-rejects* framing is under-covered | DESCRIBE-ONLY (attached file proprietary) |
| 8 | **Out-of-range but ISO-8601-shaped UTC offset in `FILE_NAME` timestamp** (`+17:00`; max real offset +14:00) | ruststep #252 attached file (`...+17:00`) | `FILE_NAME('p','2025-03-05T17:10:01+17:00',('a'),('b'),'c','d','e');` | warn (lexically valid STRING; semantically impossible offset); never reject import | §12.1b (Lh) | **BORDERLINE** — Lh011 covers non-ISO-8601 *shape*; a well-shaped but out-of-range offset is a distinct sub-case | pattern-only |
| 9 | **Un-decoded `\X2\…\X0\` control run passed through as literal string bytes** — independent parser stores the escape verbatim instead of decoding | ruststep `token.rs::string` (`none_of("'")` only; no control-directive decoding) | `#1=PRODUCT('\X2\00E9\X0\','id','',());` — name silently kept as literal backslash-X text | decode control directives to Unicode on read; do not surface raw `\X2\` to the model | §12.1a (Le) | **LIKELY-COVERED** — Le022/Le026 cover `\X2\` handling; documents the *independent-parser passthrough* variant | pattern-only |
| 10 | **Value-instance / constant references in DATA** (`@1`, `#CONST`) resolved by strict Ed.3 parsers | ruststep `token.rs::{value_instance_name,constant_entity_name}` (`@digit1`, `#UPPER…`) | `DATA;#1=CARTESIAN_POINT('',(@1,0.,0.));ENDSEC;` (value-ref in a coord slot) or a `#PI` constant reference | reject/heal per Ed.2 vs Ed.3; Ed.2 readers must not misread `@1`/`#PI` as geometry | Lh (§12.1b, Ed.3) | **BORDERLINE** — Lh026/Lh034 cover Ed.3 ANCHOR/REFERENCE; `@`-value & `#CONST` *inside DATA parameters* not explicitly covered | pattern-only |
| 11 | **Unterminated `/* comment` (no closing `*/`)** — consumes to EOF | ruststep `combinator.rs::comment` (`tag("/*") … tag("*/")`, fails if no closer) | `DATA;/* note #1=... ENDSEC;END-ISO-10303-21;` (comment swallows the rest) | reject "unterminated comment"; must not hang or silently drop the tail | §12.1c (Ls) | **NEW-ish** — confirm vs any existing comment-framing entry; the *unterminated* variant appears uncovered | pattern-only |
| 12 | **Nested-comment illusion / stray `*/`** — `/* a /* b */ c */` closes at first `*/`, leaving ` c */` as garbage | ruststep `combinator.rs::comment` (non-nesting; `*` only escaped when not before `/`) | `/* outer /* inner */ tail */\nISO-10303-21; …` | Part-21 comments do not nest — reject the trailing `*/`; document non-nesting clearly | §12.1c (Ls) | **NEW-ish** — non-nesting-comment / stray-`*/` not found in catalog | pattern-only |
| 13 | **Whitespace inside a numeric literal after the sign / in the exponent** (`-  5`, `1. E +3`) — ruststep's `integer`/`real`/`exponent` all allow `multispace0` after the sign and around `E` | ruststep `token.rs::{integer,real,exponent}` (each interleaves `multispace0`) | `#1=DIRECTION('',(- 1.,0.,0.));` and `#2=...(1. E -3)` | strict reject (no interior whitespace in a numeric token); this reader is *too* lenient | §12.1c (Ls) | **BORDERLINE** — Ls003 covers whitespace *in the exponent*; whitespace *after the sign* (`- 1.`) is not | pattern-only |
| 14 | **Empty nested aggregate `()` in a required parameter slot** (real NIST simplified files: `ANNOTATION_PLANE(...,#n,())`) | ruststep issue #256 (parser failed on `()` in NIST MBE-PMI files) | `#1=ANNOTATION_PLANE('name',(#2),#3,());` — trailing empty LIST param | lex-accept `()` as empty aggregate; semantic layer rejects if slot requires ≥1 | Ad / §12.1c | **LIKELY-COVERED** — Ad015 (empty aggregate) + Ls013; documents the real MBE-PMI provenance | pattern-only (NIST files are public, ingestible — verify) |

---

## Dropped (not file-level / not novel / EXPRESS-schema-only)
- **#256 "multiple coincident vertices" welding** — geometry class, already covered (vertex-weld / duplicate-vertex-at-seam entries).
- **#243 `TrueNorth`→`Logical True`+`North`** — greedy logical-literal tokenization in an EXPRESS **WHERE** clause; no DATA-section analog (STEP logicals are dotted `.T.`). EXPRESS-only.
- **#71 empty tail remark `--` swallows next line**, **#55 `ENTITY\n`**, **#173 `generic_xxx`**, **#189/#209 SUBTYPE/`TOTAL_OVER`** — all EXPRESS-schema-parser (`espr`) issues, not Part-21 data files.
- **#138 large `Tables` stack usage**, **#69 large `.exp` stack overflow**, **#4 streaming**, **#6 error recovery** — runtime/API/perf, not encodable as a static fixture.
- **BOM before `ISO-10303-21;`** (grammar has no leading `ignorable`) — already **Le001**.
- **Lower-case entity keyword** — already **Lh018**. **Missing/`;`-less ENDSEC** — already covered. **String > 32769 octets** — already covered. **Control char in string body (incl. raw LF)** — already **Le017**. **Trailing comma / `.5` / lowercase-`e` exponent / integer-in-real** — Ls017/Ls002/Ls003/Ls001.
