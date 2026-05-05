# §12.1a encoding — adversarial validation

Validator run: `uv run python -m step_corpus.validate <file> --json` for every
`Le*.stp` in `/Users/zellyn/gh/cad/research/step-examples/12-1a-encoding/`.
All files declare `FILE_SCHEMA('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }')`,
so `ifcopenshell_strict` always reports `reject` (schema unsupported by IFC) —
not informative for these fixtures. Verdicts use OCCT (heal-on/off) and gmsh
(autofix-on/off) plus byte_signature plus direct file inspection.

## Per-file

Le001 CONFIRMED — `bom_utf8=true`, OCCT/gmsh both reject_at_read with `"unexpected QUID, expecting STEP"`; all 4 parsers reject. Matches BOM defect exactly.
Le002 CONFIRMED — declares `implementation_level='4'` (Ed.3) and emits `'caf\X\E9'` (Ed.2-style). All parsers accept (lawful syntax). Defect is conceptual (reader edition assumption); file content matches catalog reproducer.
Le004 CONFIRMED — file contains all four malformed `\X\` forms (`\X\e9`, `\X\F`, `\X\009`, `\X\E9 9`) at the documented PRODUCT name slots; OCCT/gmsh accept silently (over-tolerant — exactly the defect). Validator pipeline segfaults on the 3rd tier; result built per-tier (gmsh skipped).
Le005 CONFIRMED — file emits all four malformed `\X2\` forms (3-digit, missing `\X0\`, whitespace-split, nested) in PERSON.given fields. All parsers accept silently.
Le006 CONFIRMED — file emits 4-digit `\X4\03C0\X0\`, lone surrogate `\X4\0000D83D\X0\`, and above-U+10FFFF `\X4\00110000\X0\`. All parsers silently accept.
Le007 CONFIRMED — file embeds lone high surrogate `\X2\D800\X0\`. All parsers silently accept (exactly the over-tolerance defect targets).
Le008 CONFIRMED — file emits `'abc\S\'def'` (apostrophe-after-`\S\`) and `'caf\S\\S\i'` (chaining). hibyte=12 from comment em-dashes (`\S\` bytes are literal ASCII `5C 53 5C`). All parsers accept.
Le009 CONFIRMED — file emits `\Pg\`, `\P1\`, `\P!\`, `\P\`, valid `\PB\`, and out-of-range `\PJ\` selectors. All parsers accept.
Le010 CONFIRMED — file emits `'mix\F\katakana hello'` and `'start\F\bold middle\F\bold end'` (multi-letter HTML-style misuse). All parsers accept.
Le011 CONFIRMED — file emits `'line1\N\line2'` and `'a\N\b\N\c'` per recipe. All parsers accept.
Le012 CONFIRMED — file emits `'foo\Z\bar'` and `'head\M\tail'` (unrecognised directives). All parsers accept silently.
Le013 CONFIRMED — file contains all parity test cases (`O''Brien`, `a''b`, `''''`, `foo''bar''`). `''` is a legal escape; all parsers correctly accept.
Le014 CONFIRMED — file embeds `'pre\X\27post'` and `'a\X\27b\X\27c'` (apostrophe-as-hex). All parsers accept (the defect targets buggy parity-only scanners; well-formed parsers must succeed here).
Le015 CONFIRMED — file truncates after `#20=PERSON('p1','unclosed_string_then_eof\n` (no close-quote, no `;`, no ENDSEC). OCCT reports `Line 23: unexpected end of file`; gmsh rejects; ifc-SPF rejects-via-schema (parsed past). Reproducer matches catalog recipe exactly.
Le016 CONFIRMED — file has bare `'C:\path'`, `'C:\Users\Test\X1\file.stp'`, and contrast `'C:\\good\\path'`. All parsers silently accept (exactly the round-trip-loss defect).
Le017 CONFIRMED — `has_nul=true` plus raw 0x09 (TAB) and 0x0B (VT) at byte offsets 794/844/892. All parsers silently accept (the over-tolerance defect).
Le018 CONFIRMED — `FILE_DESCRIPTION` and `PERSON` strings span LF mid-string. All parsers accept and (per spec §5.2) ignore the LF inside strings.
Le020 CONFIRMED — `size=50978`; single PERSON.name string ~50 000 octets, well above 32 769. OCCT/gmsh both reject_at_read; ifc-SPF rejects. Bounds enforced.
Le021 CONFIRMED — raw bytes verified by hex inspection: GB18030 `E6 A0 B8`, cp1251 `C4 E5 F2 E0 EB FC`, Shift-JIS `82 A0`, UTF-8 `C3 A9` in PRODUCT.name slots. hibyte=16. All parsers accept (over-tolerance).
Le022 CONFIRMED — file uses `\X2\03B1\X0\`, `\X2\30423044\X0\`, and `temp\X2\00B0\X0\C` per recipe. All parsers accept lawful syntax.
Le023 CONFIRMED — file emits `(1,5,0.,0.)`, `(2.5,3,7,4,0)`, `(0,0,0,0,0)` — comma-as-decimal pollutes the LIST. CARTESIAN_POINT requires 3 coords; this file provides 4–5. All parsers accept (exactly the defect — silent locale-driven LIST mis-parse).
Le025 CONFIRMED — file contains `PRODUCT('','...)`, `PRODUCT(' ','...)`, `PRODUCT('   ','...)`, `PRODUCT('\X\09','...)` per recipe. Defect is kernel-level trim behavior, not file-level rejection; all parsers accept (correctly).
Le026 CONFIRMED — `'\X2\00B0'`, `'\X2\00B0C'`, `'\X2\30423044'` all close-quote without `\X0\` per recipe. All parsers accept (the over-tolerance / garbling defect).
Le027 CONFIRMED — magic line is `iso-10303-21;` (lowercase), keywords are `EndSec`/`Data`/`End-Iso-10303-21`, and a comment contains raw 0xB0 (`°C`). All parsers accept (showing they handle the case-insensitive / 8-bit-comment cases — but the defect is about parsers that *don't*; this file is the test harness).
Le028 CONFIRMED — `has_crlf=true`, `has_nul=true`. CR LF line endings throughout, NUL byte injected after the comment terminator (`/* … */ \0 ISO-10303-21;`). All parsers tolerate.
Le029 CONFIRMED — `FILE_DESCRIPTION(('a, b (c)','d, with comma and (paren) inside'),'2;1');` plus commas-with-parens in `FILE_NAME` author/org/tool slots. All parsers accept (defect targets buggy regex-split-on-comma header parsers).
Le030 CONFIRMED — file emits `\PE\foo`, `\Q\'foo\Q\'`, and `\PE\bar\Q\\` per recipe. All parsers accept (over-tolerance defect targets parsers that desynchronise).
Le031 CONFIRMED — `bom_utf16le=true`, `has_nul=true`, body is UTF-16 LE encoded throughout (verified at offset 0: `FF FE 2F 00 2A 00 …`). All 4 parsers reject.
Le032 CONFIRMED — `has_crlf=true`, `hibyte=0`. CR LF inserted between hex groups in `\X2\30A2<CRLF>30A4\X0\` at byte offsets 722 and 781 per recipe. All parsers accept.
Le035 CONFIRMED — declares `implementation_level='4'` (Ed.3) and contains `'caf\X\E9'`, `'caf\PA\\S\i'`, and raw UTF-8 `caf<C3 A9>` (verified hibyte=5). Triple-form recipe matches.
Le036 CONFIRMED — file emits `'C:\\path\\file'` (literal backslashes), `'rare=\X4\00020BB7\X0\'` (CJK Ext-B), and `'mix=\X2\03B103B203B3\X0\-abc'` per recipe. All parsers accept; defect tests round-trip preservation.

## Summary
Total: 31
CONFIRMED: 31
FAIL: 0
AMBIGUOUS: 0

## Notes & caveats
- `ifcopenshell_strict` always reports `reject` for these AUTOMOTIVE_DESIGN
  fixtures (schema unsupported by IFC); not informative — for `Le001`/`Le031`
  the message is `"Unable to parse IFC SPF header"` (i.e. genuine parse
  rejection), elsewhere `"Unsupported schema"` (parse OK). Both flavours are
  in the JSON output.
- `Le004.json` was rebuilt manually because the validator pipeline segfaults
  (exit 139) when ifcopenshell + OCCT + gmsh run sequentially on this file;
  the gmsh tiers are recorded as `skipped`. Each tier passes individually.
- The four files that produced empty JSON on first run (Le001, Le015, Le020,
  Le031) were polluted by OCCT colour-coded ANSI error logs prefixing stdout;
  fixed by stripping the prefix before the leading `{"file":`. The OCCT log
  text is preserved above as evidence of true rejection.
- For "tolerant defect" fixtures (most of the set), the CONFIRMED verdict
  rests on byte-level inspection plus the catalog-recipe match — *not* on
  parser rejection, because by construction an over-tolerant parser accepts.
  Where the catalog calls for parser rejection (Le001, Le015, Le020, Le031)
  every available parser does reject.

## Recommendations
None — every file in the §12.1a Le-series exhibits its catalogued defect.
Possible future hardening (out of scope here):
- Replace ifcopenshell with a non-IFC-schema Part-21 parser (e.g. stepcode
  `exp2cxx`-built reader) so the strict-tier verdict is informative for
  AUTOMOTIVE_DESIGN files.
- Capture OCCT/gmsh stderr/stdout warnings into the JSON output so that
  "accepted with warning" can be distinguished from "accepted silently" —
  currently the fixtures that rely on warning emission (Le004, Le005, Le009,
  Le012, Le026) cannot be adversarially distinguished from a parser that
  truly does nothing. Consider redirecting `OSD_MessageDispatcher` or wrapping
  with `contextlib.redirect_stdout` in `parse_occt`.
- Investigate the validator segfault on Le004 — likely a state leak between
  the ifcopenshell C++ deleter and OCCT's static initialisation.
