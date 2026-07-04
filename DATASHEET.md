# Datasheet — BroScienceBench v1.1

Following *Datasheets for Datasets* (Gebru et al., 2021). Fill the `[TODO]` spots before release.

## Motivation
- **Why created:** to evaluate whether LLMs give evidence-based vs. "bro-science" (myth) advice on strength training — a domain where the failure mode is *confident misinformation*, and where no public benchmark existed.
- **Created by:** [TODO: your name], for the BroScienceBench benchmark. Not yet funded/affiliated. [TODO confirm]

## Composition
- **Instances:** 246 multiple-choice items across 42 myth clusters and 7 categories (mechanism, practice, body composition, nutrition, safety, recovery, calibration).
- **Each item:** a question (incl. adversarial / first-person / leading phrasings), 3 options (one evidence-based `answer`, one `bro_science_option`, one plausible distractor), and flags `held_out` (myth not named in the source system's guardrails — tests generalization) and `hard`.
- **Splits:** 156 held-out, 72 hard; calibration items (the answer is *"not settled"* — tests overclaiming).
- **Labels source:** author-defined, grounded in the exercise-science literature (`citations.md`, `myth_evidence`). **Inter-rater reliability: [TODO — report Cohen's κ from a 2nd rater].**
- **No personal/sensitive data.**

## Collection / construction
- Items hand-/generator-written (`gen_bench.py`, `gen_bench_v11.py`); myths drawn from documented strength-training misconceptions. Options shuffled at eval time.
- **Ground truth:** each myth cluster has a one-line evidence summary + reference(s); contested topics are intentionally encoded as *calibration* items.

## Uses
- **Intended:** benchmarking LLM factual reliability on strength-training advice; a sensitive probe that also detects system-level interventions (knowledge layer / guardrails — see system paper).
- **Out of scope:** not medical advice; not a substitute for a qualified coach/clinician; English-only; strength-training only.

## Distribution
- Released on [TODO: GitHub + HuggingFace]. License: [TODO — e.g. CC BY 4.0]. Eval code released alongside (`runBench_paper2.ts`).

## Maintenance
- Maintained by [TODO]. Versioned (v1.0 = 150 items, v1.1 = 246). Errata/corrections via [TODO: repo issues].

## Limitations (state these plainly in the paper)
- Single domain, English-only, MCQ format (open-ended mode mitigates artificiality but adds judge dependence).
- ~6 items per myth → aggregate/category claims are sound; per-myth claims are underpowered.
- Author-sourced items + (until the κ is in) single-annotator labels.
- Contamination: famous myths may be in model training data → frontier models ceiling on easy items; the hard / held-out / calibration splits carry the discriminative signal.
- Open-mode scoring uses an LLM judge (qwen-2.5-72b, outside the tested model families); validate against human labels (`judge_kappa.py`).
