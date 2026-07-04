# BroScienceBench

A 246-item benchmark for evaluating large language models on strength-training
misinformation - "bro-science": confident, popular, but evidence-contradicting
training and nutrition claims.

Each item pairs an evidence-based answer with a common gym myth. Models are
scored on **accuracy** (endorsing the evidence-based view) and **myth-adherence**
(endorsing the myth) under a free-text, open-ended protocol graded by a neutral
LLM judge that sits outside every evaluated model family.

## Key results

Eight models, open-ended protocol, temperature 0. Accuracy and myth-adherence
with Wilson 95% confidence intervals.

| Model | MCQ Acc | Open-Ended Acc [95% CI] | Myth-Adherence [95% CI] |
|---|---|---|---|
| Claude Sonnet 4.6 | 100.0 | 97.6 [94.8, 98.9] | 0.0 [0.0, 1.5] |
| Claude Haiku 4.5  | 100.0 | 96.3 [93.1, 98.0] | 0.8 [0.2, 2.9] |
| DeepSeek V3.1     | 100.0 | 95.9 [92.7, 97.8] | 1.2 [0.4, 3.5] |
| GPT-4o            | 100.0 | 93.8 [90.1, 96.2] | 0.0 [0.0, 1.6] |
| GPT-4o mini       | 100.0 | 89.0 [84.4, 92.3] | 0.8 [0.2, 2.9] |
| Llama 3.3 70B     | 100.0 | 88.2 [83.5, 91.6] | 2.0 [0.9, 4.7] |
| Llama 3.1 8B      |  98.4 | 82.1 [76.8, 86.4] | 4.5 [2.5, 7.8] |
| Gemini 3.5 Flash  |  1.2* | 76.2 [70.5, 81.2] | 4.2 [2.3, 7.5] |

\* Gemini's MCQ score reflects an output-format parsing failure, not capability.

Findings:
1. **Multiple-choice saturates** — seven of eight models score ~100%, hiding real differences.
2. **Open-ended reveals a gradient** — accuracy spans 76–98%.
3. **Myth-adherence has a floor effect** — ≤1% for the top five models, mutually indistinguishable under pairwise exact McNemar tests.
4. **Calibration is also saturated** — accuracy on contested-topic items is ≥97.6% for seven of eight models; the residual gradient is driven by the held-out and hard splits, i.e. robustness to unfamiliar and adversarially-phrased items.

Judge reliability was validated against author labels on a 40-item stratified
sample: 90% raw agreement, Gwet's AC₁ = 0.89.

## Dataset

`data/broscience_bench_v1.1.json` — 246 items across 42 myth clusters and 7
categories (mechanism, practice, body composition, nutrition, safety, recovery,
calibration). Splits: 156 held-out, 72 hard, plus a calibration split of items
whose scientific consensus is genuinely unsettled.

Item schema:

```json
{
  "id": "spotreduce_0",
  "category": "bodycomp",
  "myth": "spotreduce",
  "held_out": false,
  "hard": false,
  "question": "Can endless ab work burn the fat specifically over my stomach?",
  "options": { "A": "...", "B": "...", "C": "..." },
  "answer": "A",                 // letter of the evidence-based option
  "bro_science_option": "B"      // letter of the myth option
}
```

The file also carries a `myth_evidence` map with a one-line evidence summary per
cluster. Supporting literature is listed in `scripts/citations.md`.

## Layout

```
data/       broscience_bench_v1.1.json  (246 items) + v1.0 (150 items)
scripts/    gen_bench.py, gen_bench_v11.py   dataset generation
            runBench.ts                       model evaluation (MCQ + open)
            gen_judge_validation.ts           build the judge-validation sheet
            enrich_validation.py              add the reference answer key
            analyze_stats.py                  Wilson CIs + pairwise McNemar
            judge_kappa.py                    agreement + Gwet's AC1 / PABAK
            fig2_mcnemar.py                   McNemar p-value heatmap
            citations.md                      evidence sources per cluster
results/    results_open.json, results_mcq.json, judge_validation.csv, figdata.json
DATASHEET.md
```

## Usage

Requires Node.js (for the TypeScript harness, run via `npx tsx`) and Python 3.

```bash
cp .env.example .env.local     # then set OPENROUTER_API_KEY=...
```

Run the evaluation (all eight models, open-ended):

```bash
npx tsx scripts/runBench.ts --mode open
```

`--mode mcq` for multiple-choice; `--model openai/gpt-4o` for a single model;
`--limit N` for a quick smoke test.

Compute statistics (Wilson 95% CIs + pairwise exact McNemar):

```bash
python3 scripts/analyze_stats.py results/results_open.json
```

Validate the judge against human labels (Gwet's AC₁):

```bash
npx tsx scripts/gen_judge_validation.ts   # writes results/judge_validation.csv
python3 scripts/enrich_validation.py      # adds the reference answer key
# label the human_label column, then:
python3 scripts/judge_kappa.py
```

> Note on paths: these scripts were extracted from a larger project. Before
> running, confirm the data/results directory constants near the top of
> `runBench.ts`, `analyze_stats.py`, and `judge_kappa.py` point at `./data` and
> `./results`.

## Citing

```bibtex
@misc{brosciencebench2026,
  title  = {BroScienceBench: Evaluating Large Language Models on Strength-Training Misinformation},
  author = {Puranjay Haldankar},
  year   = {2026},
  note   = {TODO: arXiv / DOI}
}
```

## License

Data and code are released under CC BY 4.0. See `DATASHEET.md` for full dataset
documentation (motivation, composition, collection, uses, and limitations).
