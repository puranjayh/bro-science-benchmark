"""
Stats for BroScienceBench (Paper 2) results: Wilson 95% confidence intervals on
every rate, plus EXACT McNemar tests for pairwise model differences (paired by
item — the correct test since all models see the same items). No scipy needed.

    python3 research/analyze_stats.py                       # newest results_paper2_*.json
    python3 research/analyze_stats.py research/results_paper2_mcq_....json
"""
import glob, json, math, pathlib, sys

Z = 1.959963985  # 95%


def wilson(k, n):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + Z * Z / n
    centre = (p + Z * Z / (2 * n)) / d
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(b, c):
    """Two-sided exact binomial McNemar on discordant pairs (b, c)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) * (0.5 ** n)
    return min(1.0, 2 * tail)


def rate(k, n):
    if n == 0:
        return "       n/a"
    lo, hi = wilson(k, n)
    return f"{100*k/n:5.1f}% [{100*lo:4.1f},{100*hi:4.1f}]"


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if not arg:
        files = sorted(glob.glob(str(pathlib.Path(__file__).parent / "results_paper2_*.json")))
        if not files:
            print("No results_paper2_*.json found — run runBench_paper2.ts first.")
            return
        arg = files[-1]
    d = json.load(open(arg))
    models = d["models"]
    print(f"file: {pathlib.Path(arg).name} | mode: {d.get('mode')} | n_items: {d.get('n_items')}\n")

    print(f"{'model':22s} {'n':>4s} {'err':>4s}  {'accuracy [95% CI]':22s} {'myth-adherence [95% CI]'}")
    print("-" * 80)
    for m in models:
        err = m.get('errors', 0)
        valid = m['n'] - err  # exclude judge/model errors from the denominator
        print(f"{m['label']:22s} {valid:4d} {err:4d}  {rate(m['correct'], valid):22s} {rate(m['myth'], valid)}")

    # Pairwise McNemar on myth-adherence (the headline metric), paired by item id.
    print("\nPairwise McNemar — MYTH-adherence difference (* = p<0.05, significant):")
    lab = lambda m: {it["id"]: it["label"] for it in m["items"]}
    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            a, c = models[i], models[j]
            la, lc = lab(a), lab(c)
            common = [k for k in (set(la) & set(lc)) if la[k] != "ERROR" and lc[k] != "ERROR"]
            b_ = sum(1 for k in common if la[k] == "MYTH" and lc[k] != "MYTH")
            c_ = sum(1 for k in common if lc[k] == "MYTH" and la[k] != "MYTH")
            p = mcnemar_exact(b_, c_)
            print(f"  {a['label']:20s} vs {c['label']:20s}  discordant {b_:2d}/{c_:2d}  p={p:.3f} {'*' if p<0.05 else ''}")

    print("\nReport these CIs in the results table; cite McNemar for model-vs-model claims.")


if __name__ == "__main__":
    main()
