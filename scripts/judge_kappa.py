"""
Judge validation: compute agreement between the LLM judge (qwen) and your human
labels, from a filled CSV (research/judge_validation.csv) with columns:
  id, question, answer, judge_label, human_label
Fill in human_label (CORRECT / MYTH / NEITHER) for each row, then run this.

    python3 research/judge_kappa.py
Reports raw agreement + Cohen's kappa. kappa > 0.6 substantial, > 0.8 strong.
"""
import csv, pathlib
from collections import Counter

p = pathlib.Path(__file__).parent.parent / "results" / "judge_validation.csv"
rows = [r for r in csv.DictReader(open(p)) if r.get("human_label", "").strip()]
if not rows:
    print("Fill in the human_label column in research/judge_validation.csv first.")
    raise SystemExit

j = [r["judge_label"].strip().upper() for r in rows]
h = [r["human_label"].strip().upper() for r in rows]
n = len(rows)
labels = sorted(set(j) | set(h))

agree = sum(a == b for a, b in zip(j, h))
po = agree / n
cj, ch = Counter(j), Counter(h)
pe = sum((cj[l] / n) * (ch[l] / n) for l in labels)
kappa = (po - pe) / (1 - pe) if pe != 1 else 1.0

print(f"n labeled: {n}")
print(f"raw agreement: {100*po:.1f}%")
print(f"Cohen's kappa: {kappa:.3f}  "
      f"({'strong' if kappa>0.8 else 'substantial' if kappa>0.6 else 'moderate' if kappa>0.4 else 'weak'})")

# Cohen's kappa collapses when one label dominates (Feinstein & Cicchetti 1990,
# 'the paradoxes of kappa'). Report prevalence-robust alternatives too.
pabak = 2 * po - 1
q = len(labels)
pi = {l: (cj[l] + ch[l]) / (2 * n) for l in labels}
pe_g = sum(pi[l] * (1 - pi[l]) for l in labels) / (q - 1) if q > 1 else 0.0
ac1 = (po - pe_g) / (1 - pe_g) if pe_g != 1 else 1.0
print(f"PABAK: {pabak:.3f}   Gwet's AC1: {ac1:.3f}   (robust to class imbalance)")
print(f"label prevalence: {dict(Counter(h))}  <- if one dominates, trust AC1 over Cohen's kappa")
print("\ndisagreements (review these):")
for r in rows:
    if r["judge_label"].strip().upper() != r["human_label"].strip().upper():
        m = f" [{r.get('model', '').split('/')[-1]}]" if r.get("model") else ""
        print(f"  {r['id']}{m}: judge={r['judge_label']} human={r['human_label']}")
