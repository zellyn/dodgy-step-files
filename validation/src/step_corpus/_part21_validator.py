"""Pure-Python ISO 10303-21 syntactic validator.

Implements ISO 10303-21 Edition 3 Part-21 grammar checks **independent of
OCCT**. Used as the 4th oracle in validate2 to give cross-validation
signal: where this validator and OCCT disagree, the catalog has
something interesting to document.

Coverage:

- Magic line `ISO-10303-21;` at offset 0 (optionally preceded by UTF-8
  BOM).
- Required HEADER / DATA / ENDSEC framing.
- File closing `END-ISO-10303-21;`.
- Entity instance form `#N = TYPE(args);` lexes cleanly.
- All `#N` references resolve to a defined instance in the same file.
- REAL literals must contain a decimal point per §6.4.
- Balanced parens in lists / aggregates.
- Apostrophe-doubling escape inside string literals.
- Reasonable bound on overlong string literals (Edition-3 §11 limit:
  32_768 octets for type STRING).

Returns a structured verdict:

    {
        "status": "accept" | "reject" | "accept_with_warnings",
        "errors":   [list of structured error rows],
        "warnings": [list of structured warning rows],
        "n_entities": int,
        "n_unresolved_refs": int,
    }

Each error/warning row: ``{"code": "E_X", "line": N, "msg": "..."}``.

The validator is intentionally **conservative**: it errs on strict
spec-conformance, not on OCCT-style auto-healing. A file that OCCT
silently fixes will be REJECTED here. That's the point: divergence
between this validator and OCCT identifies "kernel auto-healed
malformed input" cases.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# 32768-octet limit on STRING values (Ed.3 §11; the limit applies to a
# single STRING, not an aggregate). We treat the value as a byte length.
STRING_OCTET_LIMIT = 32_768

# Regex pieces. Real numbers must contain a decimal point per §6.4.
# (We allow exponent notation; spec lets a digit follow the `.`.)
_RE_REAL = re.compile(rb"-?\d+\.\d*([eE][-+]?\d+)?|-?\.\d+([eE][-+]?\d+)?")
_RE_INT = re.compile(rb"-?\d+")
_RE_REF = re.compile(rb"#\d+")
# Entity defs at start-of-line OR right after a semicolon. Allow
# multi-line whitespace so the entity-name regex works.
_RE_INSTANCE_DEF = re.compile(rb"(?:^|;)\s*#(\d+)\s*=\s*[A-Za-z_(]", re.MULTILINE)


@dataclass
class Verdict:
    status: str = "accept"
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    n_entities: int = 0
    n_unresolved_refs: int = 0

    def _emit(self, target: list, code: str, msg: str, line: int = 0):
        target.append({"code": code, "line": line, "msg": msg[:300]})

    def err(self, code: str, msg: str, line: int = 0):
        self._emit(self.errors, code, msg, line)
        self.status = "reject"

    def warn(self, code: str, msg: str, line: int = 0):
        self._emit(self.warnings, code, msg, line)


def _line_of_offset(body: bytes, offset: int) -> int:
    """1-based line number of byte offset."""
    if offset >= len(body):
        return body.count(b"\n", 0, len(body)) + 1
    return body.count(b"\n", 0, offset) + 1


def _strip_bom(body: bytes, v: Verdict) -> bytes:
    if body.startswith(b"\xef\xbb\xbf"):
        v.warn("W_BOM", "UTF-8 BOM at file start (informational)", 1)
        return body[3:]
    if body.startswith(b"\xff\xfe") or body.startswith(b"\xfe\xff"):
        v.err("E_UTF16_BOM", "UTF-16 BOM at file start; Part-21 uses 7-bit ASCII", 1)
        return body
    return body


def _skip_leading_ws_and_comments(body: bytes) -> int:
    """Skip whitespace and `/* */` comments at the start of body.

    ISO 10303-21 §6.5 treats `/* */` comments as lexical whitespace, so
    they are permitted before the magic line.
    """
    i = 0
    n = len(body)
    while i < n:
        c = body[i]
        if c in (0x20, 0x09, 0x0a, 0x0d):
            i += 1
            continue
        if c == ord("/") and i + 1 < n and body[i+1] == ord("*"):
            j = body.find(b"*/", i + 2)
            if j < 0:
                return n
            i = j + 2
            continue
        break
    return i


def _check_magic(body: bytes, v: Verdict) -> int:
    """Return offset after the magic line, or -1 if missing."""
    start = _skip_leading_ws_and_comments(body)
    if body[start:].startswith(b"ISO-10303-21;"):
        return start + len(b"ISO-10303-21;")
    # Lowercase / mixed-case fallback
    if re.match(rb"[Ii][Ss][Oo]-10303-21;", body[start:]):
        v.err("E_MAGIC_CASE", "magic line not exactly 'ISO-10303-21;'",
              _line_of_offset(body, start))
        return start + len(b"iso-10303-21;")
    v.err("E_NO_MAGIC", "missing 'ISO-10303-21;' magic line", 1)
    return -1


def _check_close(body: bytes, v: Verdict) -> None:
    if not re.search(rb"END-ISO-10303-21;\s*\Z", body):
        # Try lowercase
        if re.search(rb"end-iso-10303-21;\s*\Z", body):
            v.err("E_CLOSE_CASE", "close marker not exactly 'END-ISO-10303-21;'",
                  body.count(b"\n") + 1)
        else:
            v.err("E_NO_CLOSE", "missing 'END-ISO-10303-21;' close marker",
                  body.count(b"\n") + 1)


def _strip_strings_and_comments(body: bytes, v: Verdict) -> bytes:
    """Mask out string literals and `/* */` comments so token analysis
    doesn't trip on them. Returns a body of the same length with
    masked content replaced by spaces.
    """
    out = bytearray(body)
    i = 0
    n = len(out)
    while i < n:
        c = out[i]
        if c == ord("/") and i + 1 < n and out[i+1] == ord("*"):
            # Comment block: /* ... */
            j = body.find(b"*/", i + 2)
            if j < 0:
                v.err("E_COMMENT_OPEN", "unterminated /* comment block",
                      _line_of_offset(body, i))
                # Mask to end
                for k in range(i, n):
                    if out[k] != ord("\n"):
                        out[k] = ord(" ")
                break
            for k in range(i, j + 2):
                if out[k] != ord("\n"):
                    out[k] = ord(" ")
            i = j + 2
        elif c == ord("'"):
            # String literal: 'foo''bar'  (doubled apostrophe escape)
            start = i
            i += 1
            byte_count = 0
            while i < n:
                if out[i] == ord("'"):
                    if i + 1 < n and out[i+1] == ord("'"):
                        # escaped
                        out[i] = ord(" ")
                        out[i+1] = ord(" ")
                        i += 2
                        byte_count += 1
                        continue
                    # End of string
                    break
                if out[i] != ord("\n"):
                    out[i] = ord(" ")
                i += 1
                byte_count += 1
            else:
                v.err("E_STRING_OPEN", "unterminated string literal",
                      _line_of_offset(body, start))
                break
            if byte_count > STRING_OCTET_LIMIT:
                v.err("E_STRING_TOO_LONG",
                      f"string literal of {byte_count} octets exceeds Ed.3 32 768 limit",
                      _line_of_offset(body, start))
            # Mask the closing apostrophe of the start
            out[start] = ord(" ")
            if i < n:
                out[i] = ord(" ")
                i += 1
        else:
            i += 1
    return bytes(out)


def _check_sections(body: bytes, masked: bytes, v: Verdict) -> tuple[int, int]:
    """Return (header_start, data_start) byte offsets, or (-1, -1) on
    error. Uses the masked body to avoid matching keywords inside
    strings."""
    # Section markers: use compiled patterns with pos for correctness.
    pat_endsec = re.compile(rb"\bENDSEC;")
    pat_data   = re.compile(rb"\bDATA;")
    h = re.search(rb"\bHEADER;", masked)
    e1 = pat_endsec.search(masked, h.end()) if h else None
    d = pat_data.search(masked, h.end() if h else 0)
    if d and e1 and d.start() < e1.start():
        d = pat_data.search(masked, e1.end())
    e2 = pat_endsec.search(masked, d.end()) if d else None
    if not h:
        v.err("E_NO_HEADER", "missing 'HEADER;' marker")
        return -1, -1
    if not e1:
        v.err("E_NO_HEADER_END", "missing first 'ENDSEC;' marker")
        return -1, -1
    if not d:
        v.err("E_NO_DATA", "missing 'DATA;' marker")
        return -1, -1
    if not e2:
        v.err("E_NO_DATA_END", "missing second 'ENDSEC;' marker")
        return h.start(), d.start()
    return h.start(), d.start()


def _scan_entities(body: bytes, masked: bytes, v: Verdict, data_start: int) -> tuple[set[int], set[int]]:
    """Return (defined_refs, used_refs)."""
    defined: set[int] = set()
    used: set[int] = set()
    # Entity definitions in DATA section
    for m in _RE_INSTANCE_DEF.finditer(masked, data_start):
        rid = int(m.group(1))
        if rid in defined:
            v.warn("W_DUP_REF", f"duplicate definition of #{rid}",
                   _line_of_offset(body, m.start()))
        defined.add(rid)
    # All references (anywhere in body, masked)
    for m in _RE_REF.finditer(masked):
        rid = int(m.group(0)[1:])
        used.add(rid)
    v.n_entities = len(defined)
    return defined, used


def _check_paren_balance(masked: bytes, v: Verdict) -> None:
    depth = 0
    line = 1
    for i, c in enumerate(masked):
        if c == ord("\n"):
            line += 1
        elif c == ord("("):
            depth += 1
        elif c == ord(")"):
            depth -= 1
            if depth < 0:
                v.err("E_PAREN_NEGATIVE", "unmatched closing paren", line)
                return
    if depth != 0:
        v.err("E_PAREN_UNBALANCED", f"paren imbalance: depth={depth}", line)


def _check_escapes(body: bytes, v: Verdict) -> None:
    """Validate Edition-3 escape directive forms inside string literals.

    The masked body has strings replaced with whitespace, so we have to
    scan the original body. We extract every string literal (between
    apostrophes, with `''` doubling) and check escapes within each.

    Catches:
    - `\X\` not followed by exactly 2 hex digits
    - `\X2\` without closing `\X0\`, or hex run not divisible by 4
    - `\X4\` without closing `\X0\`, or hex run not divisible by 8
    - `\PE\` directive only valid in alphabet-extension contexts
    - Bare `\` not followed by a recognized escape directive
    """
    i = 0
    n = len(body)
    while i < n:
        if body[i] != ord("'"):
            i += 1
            continue
        # Walk to end of string, tracking content
        i += 1
        start = i
        content = []
        while i < n:
            if body[i] == ord("'"):
                if i + 1 < n and body[i+1] == ord("'"):
                    content.append(ord("'"))
                    i += 2
                    continue
                break
            content.append(body[i])
            i += 1
        if i >= n:
            return  # unterminated; reported elsewhere
        i += 1  # skip closing apostrophe
        s = bytes(content)
        line = _line_of_offset(body, start)
        # Check escape directives
        j = 0
        while j < len(s):
            if s[j] != ord("\\"):
                j += 1
                continue
            # Found a backslash; classify
            rest = s[j+1:]
            # \X\HH (ISO-8859 single-byte)
            m = re.match(rb"X\\([0-9A-Fa-f]{2})", rest)
            if m:
                j += 1 + m.end()
                continue
            # \X2\HHHH...\X0\
            m = re.match(rb"X2\\", rest)
            if m:
                end_marker = rest.find(b"\\X0\\", m.end())
                if end_marker < 0:
                    v.err("E_X2_NO_TERM",
                          r"\X2\ escape missing closing \X0\\", line)
                    j += 1 + m.end()
                    continue
                hex_run = rest[m.end():end_marker]
                if not re.fullmatch(rb"[0-9A-Fa-f]*", hex_run):
                    v.err("E_X2_NON_HEX",
                          rf"\X2\\ contains non-hex bytes: {hex_run[:30]!r}", line)
                if len(hex_run) % 4 != 0:
                    v.err("E_X2_BAD_LEN",
                          rf"\X2\\ hex run length {len(hex_run)} not divisible by 4", line)
                j += 1 + end_marker + len(b"\\X0\\")
                continue
            # \X4\HHHHHHHH...\X0\
            m = re.match(rb"X4\\", rest)
            if m:
                end_marker = rest.find(b"\\X0\\", m.end())
                if end_marker < 0:
                    v.err("E_X4_NO_TERM",
                          r"\X4\ escape missing closing \X0\\", line)
                    j += 1 + m.end()
                    continue
                hex_run = rest[m.end():end_marker]
                if not re.fullmatch(rb"[0-9A-Fa-f]*", hex_run):
                    v.err("E_X4_NON_HEX",
                          rf"\X4\\ contains non-hex bytes", line)
                if len(hex_run) % 8 != 0:
                    v.err("E_X4_BAD_LEN",
                          rf"\X4\\ hex run length {len(hex_run)} not divisible by 8", line)
                j += 1 + end_marker + len(b"\\X0\\")
                continue
            # \S\X (8-bit shift, single char follows)
            m = re.match(rb"S\\.", rest, re.DOTALL)
            if m:
                j += 1 + m.end()
                continue
            # \P{X}\ (page shift)
            m = re.match(rb"P[A-Z]\\", rest)
            if m:
                j += 1 + m.end()
                continue
            # \PE\ alphabet-extension (Edition 3)
            m = re.match(rb"PE\\", rest)
            if m:
                j += 1 + m.end()
                continue
            # \F\ (font shift)
            m = re.match(rb"F\\", rest)
            if m:
                j += 1 + m.end()
                continue
            # \N\ (notation)
            m = re.match(rb"N\\", rest)
            if m:
                j += 1 + m.end()
                continue
            # \Q\<n> numeric char ref (Edition 3)
            m = re.match(rb"Q\\\d+\\", rest)
            if m:
                j += 1 + m.end()
                continue
            # Bare backslash
            v.warn("W_BARE_BACKSLASH",
                   f"unrecognized backslash escape: {rest[:6]!r}", line)
            j += 1


def _check_complex_instance_order(masked: bytes, v: Verdict) -> None:
    """Complex instances `(NAME1(...) NAME2(...) NAME3(...))` should list
    member subtypes in alphabetical order per ISO 10303-21 §11.

    Heuristic: find ``=\\s*\\(`` sequences (start of complex instance),
    extract the bare ``NAME(`` tokens, and verify ascending order.
    """
    pat = re.compile(rb"=\s*\(\s*([A-Z][A-Z0-9_]*\s*\([^()]*\)(?:\s*[A-Z][A-Z0-9_]*\s*\([^()]*\))+)\s*\)")
    for m in pat.finditer(masked):
        body_block = m.group(1)
        names = re.findall(rb"([A-Z][A-Z0-9_]*)\s*\(", body_block)
        if names != sorted(names):
            line = masked[:m.start()].count(b"\n") + 1
            v.warn("W_COMPLEX_ORDER",
                   f"complex-instance member names not alphabetical: {[n.decode() for n in names]}",
                   line)


def _check_real_literals(masked: bytes, v: Verdict) -> None:
    """Spot-check that REAL literals in argument positions have a decimal point.

    We look for tokens that look like numerics inside arg lists. A token
    like `5` inside `(5,5,5)` *might* be either INTEGER or REAL depending
    on the schema slot. Without a schema model we can't tell; so we only
    flag literals like `1e5` (no decimal point AND has exponent) as
    likely-malformed REALs. Conservative.
    """
    for m in re.finditer(rb"(?<![A-Za-z0-9_#.])(-?\d+[eE][-+]?\d+)(?![A-Za-z0-9_])", masked):
        v.err("E_REAL_NO_DOT",
              f"REAL literal {m.group(0)!r} has exponent but no decimal point",
              masked[:m.start()].count(b"\n") + 1)


def _check_file_description_arity(body: bytes, v: Verdict) -> None:
    """FILE_DESCRIPTION per ISO 10303-21 §10.2: takes exactly two args,
    `(description: LIST OF STRING, implementation_level: STRING)`.

    Surfaced by burn-down audits as a recurring synthesis-template bug.
    """
    m = re.search(rb"FILE_DESCRIPTION\s*\((.*?)\)\s*;", body, re.DOTALL)
    if not m:
        return
    args_text = m.group(1)
    # Count top-level commas (depth==0) to determine arity.
    depth = 0
    in_string = False
    commas = 0
    i = 0
    while i < len(args_text):
        c = args_text[i]
        if in_string:
            if c == ord("'"):
                if i + 1 < len(args_text) and args_text[i+1] == ord("'"):
                    i += 2
                    continue
                in_string = False
            i += 1
            continue
        if c == ord("'"):
            in_string = True
        elif c == ord("("):
            depth += 1
        elif c == ord(")"):
            depth -= 1
        elif c == ord(",") and depth == 0:
            commas += 1
        i += 1
    arity = commas + 1
    if arity != 2:
        v.err("E_FILE_DESC_ARITY",
              f"FILE_DESCRIPTION has {arity} top-level args; spec requires 2 "
              f"(description list, implementation_level)",
              _line_of_offset(body, m.start()))


def _check_forward_refs(body: bytes, masked: bytes, v: Verdict, data_start: int) -> None:
    """Walk DATA section in declaration order. Flag any `#N` reference
    inside an entity body where N > the entity's own id (forward reference).

    Per ISO 10303-21 §3.3.10, instances may be referenced in any order
    within DATA — forward refs are technically allowed. But many readers
    (and our own validators) work better when entities are topologically
    sorted, and forward refs are a common synthesis bug. Reported as a
    warning, not error.
    """
    # Iterate `#N=TYPE(...);` blocks
    pat = re.compile(rb"(?:^|;)\s*#(\d+)\s*=\s*[A-Za-z_(]")
    refs_pat = re.compile(rb"#(\d+)")
    matches = list(pat.finditer(masked, data_start))
    forward_count = 0
    first_example = None
    for i, m in enumerate(matches):
        eid = int(m.group(1))
        # Determine the end of this entity body (next entity def or section end)
        body_start = m.end()
        body_end = matches[i+1].start() if i + 1 < len(matches) else len(masked)
        # Find all references in this entity's body, skip the LHS we already matched.
        entity_body = masked[body_start:body_end]
        for r in refs_pat.finditer(entity_body):
            rid = int(r.group(1))
            if rid > eid:
                forward_count += 1
                if first_example is None:
                    first_example = (eid, rid, _line_of_offset(body, body_start + r.start()))
    if forward_count > 0:
        eid, rid, line = first_example
        v.warn("W_FORWARD_REF",
               f"{forward_count} forward references in DATA; first: #{eid} → #{rid}",
               line)


def _check_non_ascii_numerics(body: bytes, masked: bytes, v: Verdict) -> None:
    """Catch Unicode minus sign (U+2212, "−") and other non-ASCII chars in
    numeric contexts. Part-21 lexer accepts only ASCII 7-bit; non-ASCII
    in number tuples comes from copy-paste through Unicode-aware editors.
    """
    # U+2212 minus sign as UTF-8 = E2 88 92
    minus_u2212 = b"\xe2\x88\x92"
    line = 1
    for i, c in enumerate(body):
        if c == ord("\n"):
            line += 1
        if c > 127:
            # Only flag once per line and only for the minus sign
            # (other non-ASCII could be inside a string literal)
            if i + 2 < len(body) and body[i:i+3] == minus_u2212:
                v.err("E_NON_ASCII_MINUS",
                      f"Unicode U+2212 minus sign at byte {i}; use ASCII '-'",
                      line)
                # Only report first occurrence per file
                return


def validate(body: bytes) -> Verdict:
    v = Verdict()
    body = _strip_bom(body, v)
    end_magic = _check_magic(body, v)
    if end_magic < 0:
        return v
    _check_close(body, v)
    masked = _strip_strings_and_comments(body, v)
    _check_paren_balance(masked, v)
    h, d = _check_sections(body, masked, v)
    if h < 0:
        return v
    defined, used = _scan_entities(body, masked, v, d)
    unresolved = used - defined
    v.n_unresolved_refs = len(unresolved)
    if unresolved:
        v.err("E_UNRESOLVED_REFS",
              f"{len(unresolved)} unresolved #N references; first: #{min(unresolved)}")
    _check_real_literals(masked, v)
    _check_escapes(body, v)
    _check_complex_instance_order(masked, v)
    _check_file_description_arity(body, v)
    _check_forward_refs(body, masked, v, d)
    _check_non_ascii_numerics(body, masked, v)
    if v.status == "accept" and v.warnings:
        v.status = "accept_with_warnings"
    return v


def validate_file(path: Path) -> Verdict:
    return validate(path.read_bytes())


def _corpus_scan(argv: list[str]) -> int:
    """Scan all fixtures under step-examples (excluding _quarantine) and
    print a summary of rejects by section."""
    from step_corpus._build_catalog_json import RESEARCH_ROOT
    examples = RESEARCH_ROOT / "step-examples"
    framing = {"12-1a-encoding", "12-1b-header", "12-1c-syntax",
               "12-11-adversarial", "12-12-cross-product", "12-13-writer-pathology"}

    json_out = "--json" in argv
    sections: dict[str, dict[str, int]] = {}
    non_framing_rejects: list[tuple[str, str, list[str]]] = []
    error_codes: dict[str, int] = {}
    warning_codes: dict[str, int] = {}

    for f in examples.rglob("*.stp"):
        if "_quarantine" in str(f):
            continue
        section = f.parts[-2]
        v = validate_file(f)
        s = sections.setdefault(section, {"accept": 0, "accept_with_warnings": 0, "reject": 0})
        s[v.status] = s[v.status] + 1
        for e in v.errors:
            error_codes[e["code"]] = error_codes.get(e["code"], 0) + 1
        for w in v.warnings:
            warning_codes[w["code"]] = warning_codes.get(w["code"], 0) + 1
        if v.status == "reject" and section not in framing:
            codes = [e["code"] for e in v.errors]
            non_framing_rejects.append((section, f.name, codes))

    if json_out:
        json.dump({
            "sections": sections,
            "non_framing_rejects": [{"section": s, "name": n, "codes": c}
                                    for s, n, c in non_framing_rejects],
            "error_codes": error_codes,
            "warning_codes": warning_codes,
        }, sys.stdout, indent=2)
        return 1 if non_framing_rejects else 0

    total = {"accept": 0, "accept_with_warnings": 0, "reject": 0}
    for s in sections.values():
        for k, v in s.items():
            total[k] = total.get(k, 0) + v
    print(f"Corpus scan: {sum(total.values())} fixtures")
    print(f"  accept: {total['accept']}")
    print(f"  accept_with_warnings: {total['accept_with_warnings']}")
    print(f"  reject: {total['reject']}")
    print()
    print("By section (rejects in non-framing sections are real bugs):")
    for sec in sorted(sections):
        st = sections[sec]
        intentional = " [framing-defect section]" if sec in framing else ""
        print(f"  {sec}: a={st['accept']} w={st['accept_with_warnings']} r={st['reject']}{intentional}")
    print()
    print(f"Non-framing rejects: {len(non_framing_rejects)}")
    print("Top error codes:")
    for c, n in sorted(error_codes.items(), key=lambda x: -x[1])[:10]:
        print(f"  {c}: {n}")
    return 1 if non_framing_rejects else 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--corpus" in args:
        args.remove("--corpus")
        return _corpus_scan(args)
    if "--json" in args:
        json_out = True
        args.remove("--json")
    else:
        json_out = False
    if not args:
        print("usage: python -m step_corpus._part21_validator [--corpus] [--json] [<file.stp>]", file=sys.stderr)
        return 2
    p = Path(args[0])
    if not p.is_file():
        print(f"no such file: {p}", file=sys.stderr)
        return 2
    v = validate_file(p)
    if json_out:
        json.dump({
            "status": v.status,
            "n_entities": v.n_entities,
            "n_unresolved_refs": v.n_unresolved_refs,
            "errors": v.errors,
            "warnings": v.warnings,
        }, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"{v.status}  entities={v.n_entities}  unresolved={v.n_unresolved_refs}")
        for e in v.errors[:20]:
            print(f"  ERR  {e['code']}  line {e['line']}  {e['msg']}")
        for w in v.warnings[:10]:
            print(f"  WARN {w['code']}  line {w['line']}  {w['msg']}")
    return 0 if v.status == "accept" else (0 if v.status == "accept_with_warnings" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
