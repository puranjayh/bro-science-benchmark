---
license: cc-by-4.0
language:
- en
pretty_name: BroScienceBench
size_categories:
- n<1K
task_categories:
- question-answering
- text-classification
tags:
- benchmark
- llm-evaluation
- health-misinformation
- fitness
- factuality
- calibration
configs:
- config_name: default
  data_files:
  - split: test
    path: data/brosciencebench.jsonl
---

# BroScienceBench

A literature-grounded benchmark for evaluating how large language models handle
**strength-training misinformation** ("bro-science"). 246 items across 42 myth
clusters and 7 categories, each pairing an evidence-based answer against a
documented gym myth and a plausible distractor.

Code, evaluation harness, analysis scripts, figures, and the full datasheet:
**https://github.com/puranjayh/bro-science-benchmark**

> ⚠️ For engineering evaluation and research only. **Not medical advice.**

## Load

```python
from datasets import load_dataset
ds = load_dataset("pur4nj41y/bro-science-benchmark", split="test")
ds[0]

hard     = ds.filter(lambda x: x["hard"])       # 72 adversarial items
held_out = ds.filter(lambda x: x["held_out"])   # 156 generalization items
```

## Recommended protocol

Evaluate **open-ended**: have the model answer in free text as a coach would (no
options shown), then grade with a neutral LLM judge against `answer` /
`bro_science_option`. Multiple-choice saturates (~100%) and does not discriminate
modern models. Grade **calibration**-category items correct only when the model
declines to declare a settled verdict.

## Fields

`id`, `category`, `myth_cluster`, `question`, `options {A,B,C}`, `answer`,
`bro_science_option`, `held_out` (bool), `hard` (bool), `evidence_summary`.
`held_out` (156) and `hard` (72) are **overlapping** analytical slices.

## Limitations

Single-annotator ground truth (literature-mapped; a multi-annotator study is the
top open task), a judge with a known one-directional bias (myth-adherence is a
conservative upper bound), underpowered per-cluster slices (~6 items each),
English-only, and likely pretraining contamination of prominent myths. Full
datasheet in the GitHub repo.

## Citation

```bibtex
@misc{brosciencebench2026,
  title  = {BroScienceBench: Evaluating Large Language Models on Strength-Training Misinformation},
  author = {Puranjay Haldankar},
  year   = {2026},
  url    = {https://github.com/puranjayh/bro-science-benchmark}
}
```

License: **CC BY 4.0**.
