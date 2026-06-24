"""Baseline B3.6 oracle-disagreement analysis.

Walks /tmp/cad-v2-out/, classifies each fixture by its
(occt_heal_on, gmsh_autofix_on, ifcopenshell, manifold, ocaf) signature,
and surfaces the clusters with the most-divergent kernel responses.

Without solvespace and brlcad installed, these 5 are the active
independent signals (treating OCCT-on/off as one signal because they
agree on virtually everything; same for gmsh).
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


CACHE = Path("/tmp/cad-v2-out")


def normalize(s: str) -> str:
    """Bucket noisy outputs to coarse categories for clustering."""
    if not s:
        return "empty"
    if s.startswith("shape("):
        return "shape(N)"
    if s.startswith("loaded"):
        return "loaded"
    if s.startswith("root_labels="):
        return "ocaf_loaded"
    if s in ("empty", "reject", "accept", "schema_n/a", "failed",
            "process_signal", "subprocess_error", "timeout", "not_installed",
            "no_shapes_loaded"):
        return s
    if s.startswith("warn("):
        return "warn"
    if s.startswith("accept("):
        return "accept"
    if s.startswith("signal("):
        return "signal"
    return s[:30]


def main() -> None:
    fixtures = []
    for jf in sorted(CACHE.glob("12-*/[!_]*.json")):
        try:
            d = json.loads(jf.read_text())
        except Exception:
            continue
        s = d.get("summary", {})
        if not s:
            continue
        sig = (
            normalize(s.get("occt_heal_on", "")),
            normalize(s.get("gmsh_autofix_on", "")),
            normalize(s.get("ifcopenshell", "")),
            normalize(s.get("manifold", "")),
            normalize(s.get("ocaf", "")),
        )
        fixtures.append((jf.stem, sig))

    print(f"Analyzed {len(fixtures)} fixtures from {CACHE}")
    print()

    # Cluster by signature
    by_sig: dict[tuple, list[str]] = defaultdict(list)
    for fid, sig in fixtures:
        by_sig[sig].append(fid)

    print(f"=== {len(by_sig)} distinct oracle-signatures ===\n")

    # Print top signatures
    sigs_sorted = sorted(by_sig.items(), key=lambda kv: -len(kv[1]))
    print("Top 15 most common signatures (occt, gmsh, ifc, manifold, ocaf):")
    print(f"{'count':>6}  {'occt':12} {'gmsh':12} {'ifc':12} {'manifold':14} {'ocaf':14}  example")
    for sig, fids in sigs_sorted[:15]:
        print(f"{len(fids):>6}  "
              f"{sig[0]:12} {sig[1]:12} {sig[2]:12} {sig[3]:14} {sig[4]:14}  "
              f"{fids[0]}")
    print()

    # Surface "interesting" signatures: low-frequency = high-information
    print(f"=== Rare-signature audit candidates (count == 1) ===\n")
    rare = [(fids[0], sig) for sig, fids in sigs_sorted if len(fids) == 1]
    print(f"Total fixtures with unique oracle-signature: {len(rare)}\n")
    if rare:
        print("First 20 (each is a singleton kernel-disagreement pattern):")
        for fid, sig in rare[:20]:
            print(f"  {fid:<14}  occt={sig[0]:<12} gmsh={sig[1]:<12} ifc={sig[2]:<12} manifold={sig[3]:<14} ocaf={sig[4]}")
    print()

    # Kernel-divergence count: how often does each pair of oracles disagree?
    print("=== Kernel-pair disagreement rates ===\n")
    # Convert to "loaded"/"rejected"/"silent" buckets for cleaner comparison
    def coarsen(b: str) -> str:
        if b in ("shape(N)", "loaded", "ocaf_loaded", "accept"):
            return "loaded"
        if b in ("reject", "failed", "step_read_failed", "no_shapes_loaded", "signal"):
            return "rejected"
        if b in ("empty",):
            return "silent"
        if b in ("schema_n/a", "not_installed", "subprocess_error"):
            return "n/a"
        return "other"

    names = ["occt", "gmsh", "ifc", "manifold", "ocaf"]
    pairs = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4),
             (2, 3), (2, 4), (3, 4)]
    pair_disagree = Counter()
    pair_compare = Counter()
    for fid, sig in fixtures:
        coarse = [coarsen(b) for b in sig]
        for i, j in pairs:
            if coarse[i] == "n/a" or coarse[j] == "n/a":
                continue
            pair_compare[(names[i], names[j])] += 1
            if coarse[i] != coarse[j]:
                pair_disagree[(names[i], names[j])] += 1

    print(f"{'pair':16}  {'compared':>9}  {'disagree':>9}  {'%':>5}")
    for pair, total in sorted(pair_compare.items(), key=lambda kv: -kv[1]):
        d = pair_disagree.get(pair, 0)
        pct = 100.0 * d / total if total else 0
        print(f"{pair[0]:>6}-{pair[1]:<9}  {total:>9}  {d:>9}  {pct:>4.1f}%")


if __name__ == "__main__":
    main()
