"""
Integrity checker for the BroScienceBench dataset. Verifies schema, unique IDs,
option validity, answer != myth, and — critically — that within each myth cluster
the evidence-based text and the myth text are constant across all shuffled items
(i.e. the answer key was not scrambled). Exits non-zero on any error.

    python3 scripts/validate.py
"""
import json, pathlib
from collections import defaultdict

d = json.load(open(pathlib.Path(__file__).parent.parent / "data" / "broscience_bench_v1.1.json"))
items = d["items"]
errs, ids, clusters = [], set(), defaultdict(list)

for it in items:
    if it["id"] in ids:
        errs.append(f"duplicate id {it['id']}")
    ids.add(it["id"])
    for f in ("id", "category", "myth", "question", "options", "answer", "bro_science_option"):
        if f not in it or it[f] in ("", None):
            errs.append(f"{it['id']} missing {f}")
    o = it["options"]
    if set(o) != {"A", "B", "C"}:
        errs.append(f"{it['id']} bad option keys {set(o)}")
    if it["answer"] not in "ABC" or it["bro_science_option"] not in "ABC":
        errs.append(f"{it['id']} invalid answer/myth letter")
    if it["answer"] == it["bro_science_option"]:
        errs.append(f"{it['id']} answer == bro_science_option")
    if len(set(o.values())) != 3:
        errs.append(f"{it['id']} duplicate option text")
    clusters[it["myth"]].append(it)

# catastrophic check: correct text and myth text must be constant per cluster
for m, its in clusters.items():
    if len({i["options"][i["answer"]] for i in its}) != 1:
        errs.append(f"cluster {m}: inconsistent evidence-based text -> mapping broken")
    if len({i["options"][i["bro_science_option"]] for i in its}) != 1:
        errs.append(f"cluster {m}: inconsistent myth text -> mapping broken")

print(f"items {len(items)} | clusters {len(clusters)} | "
      f"held_out {sum(i['held_out'] for i in items)} | hard {sum(i['hard'] for i in items)}")
print(f"errors: {len(errs)}")
for e in errs[:25]:
    print("  -", e)
raise SystemExit(1 if errs else 0)
