# §12.1a — Encoding & string-literal defects (Le-prefix)

UTF-8 BOM, raw multi-byte UTF-8, `\X\` / `\X2\` / `\X4\` / `\S\` / `\P\` directive defects, doubled-apostrophe escape, unterminated strings, embedded backslashes / control characters, locale-specific encodings (GB18030, Shift-JIS, cp1251, DOS850), edition-default encoding mismatches, and BOM/escape interactions.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.1a) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Le001](Le001.stp) | UTF-8 BOM at start of `ISO-10303-21;` |
| [Le002](Le002.stp) | Edition-default encoding mismatch (Ed.2 ISO-8859-1 vs Ed.3 UTF-8) |
| [Le004](Le004.stp) | `\X\` (single-byte ISO-8859) escape with bad hex digit count or non-hex input |
| [Le005](Le005.stp) | `\X2\…\X0\` (UCS-2) escape: missing terminator, bad digit count, or nesting |
| [Le006](Le006.stp) | `\X4\…\X0\` (UCS-4) escape with hex run not divisible by 8 or containing surrogate code points |
| [Le007](Le007.stp) | `\X2\` endianness confusion / lone-surrogate handling |
| [Le008](Le008.stp) | `\S\X` (8-bit shift) directive: misuse, chaining, or apostrophe-after-`\S\` |
| [Le009](Le009.stp) | `\P{X}\` page-shift directive: bad selector / state-machine omission |
| [Le010](Le010.stp) | `\F\` font-shift directive consumed wrongly |
| [Le011](Le011.stp) | `\N\` notation directive misused as C-style newline escape |
| [Le012](Le012.stp) | Unrecognised backslash control directive in a string |
| [Le013](Le013.stp) | Apostrophe-doubling escape `''` confused with string terminator |
| [Le014](Le014.stp) | Apostrophe inside a `\X2\…\X0\` block decoded as string close |
| [Le015](Le015.stp) | Unterminated string literal |
| [Le016](Le016.stp) | Single backslash inside a string literal (Windows path) |
| [Le017](Le017.stp) | Raw control character (U+0000..U+001F) in string body |
| [Le018](Le018.stp) | Inline newline inside an unterminated literal silently concatenated |
| [Le020](Le020.stp) | String literal exceeds Ed.3 32 769-octet limit |
| [Le021](Le021.stp) | Component name in non-UTF-8 locale encoding (GB18030 / Shift-JIS / cp1251 / DOS850) |
| [Le022](Le022.stp) | Non-ASCII / Japanese / Greek Unicode in PRODUCT.name via `\X2\…\X0\` |
| [Le023](Le023.stp) | Locale-dependent decimal separator inside numeric attribute |
| [Le025](Le025.stp) | Empty / blank / single-space NAME silently emptied |
| [Le026](Le026.stp) | `\X0\` end-marker missing — remainder treated as encoded content |
| [Le027](Le027.stp) | 8-bit characters and case-insensitive keyword tolerance in lexer |
| [Le028](Le028.stp) | Stray NUL bytes / DOS `\r\n` line endings inside the file |
| [Le029](Le029.stp) | Header `FILE_DESCRIPTION` strings containing commas or parentheses (regex-split bug) |
| [Le030](Le030.stp) | `\PE\` selector and `\Q\x` directive support |
| [Le031](Le031.stp) | UTF-16 / UTF-32 BOM mistaken for an ASCII file |
| [Le032](Le032.stp) | `\X2\…\X0\` or `\N\` escape spanning a physical line break |
| [Le035](Le035.stp) | Encoding directives emitted in Ed.3 UTF-8 file unnecessarily |
| [Le036](Le036.stp) | Round-trip loss of `\X2\` content through XML / DB layer |
| [Le037](Le037.stp) | `\PE\` alphabet-extension directive switching to a non-Latin code page mid-string |
| [Le038](Le038.stp) | Bare `\PE\` directive at end-of-string with no operand letter |
| [Le039](Le039.stp) | `\PE\` selector letter outside the legal A..I range |
| [Le040](Le040.stp) | `\Q\` numeric-character-reference at the upper Unicode boundary (U+10FFFF) |
| [Le041](Le041.stp) | `\Q\` encoding a code point in the UTF-16 surrogate range (U+D800..U+DFFF) |
| [Le042](Le042.stp) | `\Q\` payload contains non-decimal characters |
| [Le043](Le043.stp) | `\X4\` with a valid supplementary-plane code point followed by a short trailing hex run |
| [Le044](Le044.stp) | `\X2\` payload containing UTF-16 surrogate halves |
| [Le045](Le045.stp) | String literal at the Edition-3 length limit (32768 characters) |
| [Le046](Le046.stp) | String literal containing every legal printable ASCII character |
| [Le047](Le047.stp) | REAL literal at IEEE-754 subnormal / minimum-normal / maximum boundaries |
| [Le048](Le048.stp) | REAL literal exceeding double range (overflow → +Inf / underflow → 0) |
| [Le049](Le049.stp) | Carriage-return stripping during STEP file write |
| [Le050](Le050.stp) | Unicode characters in STEP export silently dropped |
