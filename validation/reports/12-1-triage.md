# §12.1 CONCERN triage

Applied rule: kernel mishandling IS the defect. Silent-accept-with-empty against a
catalog "must-reject" claim demonstrates leaky tolerance — CONFIRMED. Empty/reject
against a catalog "crash" claim is CONFIRMED-WEAK (kernel still mishandles; the
specific crash path may not be hit by the minimal fixture). Clean reject vs. catalog
"reject" is CONFIRMED.

## §12.1a encoding
Le005 **CONFIRMED-WEAK** — catalog claims crash on malformed `\X2\…\X0\`; validators show empty/no-transfer; kernel mishandles by silent acceptance, full crash path not exercised by minimal fixture.
Le006 **CONFIRMED** — catalog requires reject of malformed `\X\` directive; kernel silently accepts with empty result (leaky tolerance).
Le007 **CONFIRMED** — catalog requires reject of `\S\` directive abuse; kernel silently accepts with empty result.
Le010 **CONFIRMED** — catalog requires reject of bad page-directive `\P\`; kernel silently accepts with empty result.
Le011 **CONFIRMED-WEAK** — catalog claims crash on misused `\N\`; validators show empty; kernel mishandles by silent acceptance, crash path not hit.
Le012 **CONFIRMED** — catalog requires reject of malformed octet escape; kernel silently accepts with empty result.
Le015 **CONFIRMED** — catalog requires reject of unterminated string; occt=reject gmsh=reject — clean rejection matches catalog.
Le016 **CONFIRMED** — catalog requires reject of mid-string control bytes; kernel silently accepts with empty result.
Le020 **CONFIRMED** — catalog requires reject of >32 769-octet string (Ed.3 limit); occt=reject gmsh=reject — clean rejection matches catalog.
Le021 **CONFIRMED** — catalog requires reject of bad UTF-8 byte sequence; kernel silently accepts with empty result.
Le026 **CONFIRMED-WEAK** — catalog claims crash on missing `\X0\`; validators show empty; kernel mishandles by silent acceptance, crash path not hit.
Le027 **CONFIRMED** — catalog requires reject of mismatched `\X2\` length; kernel silently accepts with empty result.

## §12.1b header
Lh002 **CONFIRMED** — catalog requires reject of missing/duplicate `END-ISO-10303-21;`; occt=reject gmsh=reject — clean rejection matches catalog.
Lh003 **CONFIRMED** — catalog requires reject of missing `ENDSEC;`; occt=reject gmsh=reject — clean rejection matches catalog.
Lh006 **CONFIRMED** — catalog requires reject of bad `FILE_DESCRIPTION` shape; kernel silently accepts with empty result.
Lh007 **CONFIRMED-WEAK** — catalog claims crash on multi-schema `FILE_SCHEMA`; validators show empty; kernel mishandles by silent acceptance, crash path not hit.
Lh009 **CONFIRMED** — catalog requires reject of out-of-order header attrs; kernel silently accepts with empty result.
Lh010 **CONFIRMED** — catalog requires reject of malformed `FILE_NAME`; kernel silently accepts with empty result.
Lh015 **CONFIRMED** — catalog requires reject of bad `implementation_level`; kernel silently accepts with empty result.
Lh026 **CONFIRMED** — catalog requires reject of Ed.3 sections under strict Ed.2; occt=reject gmsh=reject — clean rejection matches catalog.
Lh027 **CONFIRMED** — catalog requires reject of malformed ANCHOR/REFERENCE; kernel silently accepts with empty result.
Lh028 **CONFIRMED** — catalog requires reject of bad SIGNATURE block; kernel silently accepts with empty result.
Lh032 **CONFIRMED** — catalog requires reject of header-after-DATA; kernel silently accepts with empty result.

## §12.1c syntax
Ls002 **CONFIRMED** — catalog requires reject of malformed entity ref; kernel silently accepts with empty result.
Ls004 **CONFIRMED** — catalog requires reject of bad list-of-list syntax; kernel silently accepts with empty result.
Ls006 **CONFIRMED** — catalog requires reject of unbalanced parentheses; kernel silently accepts with empty result.
Ls008 **CONFIRMED** — catalog requires reject of trailing-comma inside aggregate; kernel silently accepts with empty result.
Ls009 **CONFIRMED** — catalog requires reject of stray comma between attrs; kernel silently accepts with empty result.
Ls010 **CONFIRMED** — catalog requires reject of empty-attribute slot vs `$`; kernel silently accepts with empty result.
Ls013 **CONFIRMED** — catalog requires reject of typed/untyped mismatch; kernel silently accepts with empty result.
Ls014 **CONFIRMED** — catalog requires reject of misplaced `*` redeclaration token; kernel silently accepts with empty result.
Ls015 **CONFIRMED** — catalog requires reject of bad enum literal `.X.`; kernel silently accepts with empty result.
Ls017 **CONFIRMED** — catalog requires reject of bad numeric literal; kernel silently accepts with empty result.
Ls019 **CONFIRMED** — catalog requires reject of bad binary literal `"…"`; kernel silently accepts with empty result.
Ls020 **CONFIRMED** — catalog requires reject of `ENDSEC` without trailing `;`; occt=reject gmsh=reject — clean rejection matches catalog.
Ls024 **CONFIRMED** — catalog requires reject of forward-reference cycle; kernel silently accepts with empty result.
Ls027 **CONFIRMED** — catalog requires reject of duplicate entity id `#N`; kernel silently accepts with empty result.
Ls030 **CONFIRMED** — catalog requires reject of negative entity id; kernel silently accepts with empty result.
Ls034 **CONFIRMED** — catalog requires reject of leading-zero entity id; kernel silently accepts with empty result.
Ls038 **CONFIRMED** — catalog requires reject of unknown entity keyword; kernel silently accepts with empty result.
Ls043 **CONFIRMED** — catalog requires reject of mixed-case keyword variants; kernel silently accepts with empty result.
Ls044 **CONFIRMED** — catalog requires reject of inline comment inside literal; kernel silently accepts with empty result.
Ls045 **CONFIRMED** — catalog requires reject of unterminated `/* … */` comment; kernel silently accepts with empty result.

## Final tally
Section | CONCERN before | CONFIRMED after | CONCERN after | FAIL after
12-1a | 12 | 12 (3 weak) | 0 | 0
12-1b | 11 | 11 (1 weak) | 0 | 0
12-1c | 20 | 20 (0 weak) | 0 | 0
