"""
Adds reference columns to judge_validation.csv so you can hand-label with ZERO lookup
(no internet, no digging in the JSON): for each row it pastes in the evidence-based view
and the myth for that item, joined by id against broscience_bench_v1.1.json. Zero API.

    python3 research/enrich_validation.py     # run after gen_judge_validation.ts

Then label `human_label` by comparing the `answer` column to `correct_view` vs `myth_view`.
(Judge got the same two references — so this is a fair, apples-to-apples check of the judge.)
"""
import csv, json, pathlib

here = pathlib.Path(__file__).parent
bench = json.load(open(here / "broscience_bench_v1.1.json"))
key = {it["id"]: (it["options"][it["answer"]], it["options"][it["bro_science_option"]])
       for it in bench["items"]}

p = here / "judge_validation.csv"
try:
    rows = list(csv.DictReader(open(p)))
except FileNotFoundError:
    print("No research/judge_validation.csv yet — run gen_judge_validation.ts first."); raise SystemExit
if not rows:
    print("judge_validation.csv is empty."); raise SystemExit

for r in rows:
    cv, my = key.get(r["id"], ("", ""))
    r["correct_view"], r["myth_view"] = cv, my

# reorder so the key sits next to the answer, judge_label last-but-one (easy to hide)
order = [c for c in ["id", "model", "question", "answer", "correct_view", "myth_view", "judge_label", "human_label"]
         if c in rows[0] or c in ("correct_view", "myth_view")]
with open(p, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=order); w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in order})

print(f"Added correct_view + myth_view to {len(rows)} rows -> judge_validation.csv")
print("Now: hide the judge_label column, then fill human_label by comparing")
print("the `answer` to `correct_view` (=CORRECT) vs `myth_view` (=MYTH); waffling = NEITHER.")
