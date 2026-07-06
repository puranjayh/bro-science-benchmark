"""
Headline figure: MCQ vs open-ended accuracy per model. Shows that multiple-choice
saturates (~100% for real models) while the open-ended protocol reveals a
76-98% capability gradient.

    pip install matplotlib numpy
    python3 scripts/fig_mcq_vs_open.py      ->  fig_mcq_vs_open.pdf  (repo root)
"""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = pathlib.Path(__file__).parent.parent / "results"
op = json.load(open(R / "results_open.json"))
mq = json.load(open(R / "results_mcq.json"))


def open_acc(m):
    v = m["n"] - m.get("errors", 0)
    return 100 * m["correct"] / v if v else 0.0


mcq_map = {m["label"]: (100 * m["correct"] / m["n"] if m["n"] else 0.0) for m in mq["models"]}

models = sorted(op["models"], key=lambda m: -open_acc(m))
labels = [m["label"] for m in models]
open_vals = [open_acc(m) for m in models]
mcq_vals = [mcq_map.get(l, 0.0) for l in labels]

x = np.arange(len(labels))
w = 0.38
fig, ax = plt.subplots(figsize=(9, 4.2))
bars_mcq = ax.bar(x - w / 2, mcq_vals, w, label="Multiple-choice", color="#c2c2c2", edgecolor="#8a8a8a")
bars_open = ax.bar(x + w / 2, open_vals, w, label="Open-ended", color="#3b7dd8")

# Gemini's MCQ score is an output-parsing artifact — mark it, don't imply capability.
for i, l in enumerate(labels):
    if "Gemini" in l:
        bars_mcq[i].set_hatch("////")
        bars_mcq[i].set_facecolor("white")
        ax.annotate("* parse\n  failure", (x[i] - w / 2, mcq_vals[i] + 3),
                    ha="center", va="bottom", fontsize=7, color="gray")

ax.axhline(100, ls=":", lw=0.8, color="gray")
for b in bars_open:
    ax.annotate(f"{b.get_height():.0f}", (b.get_x() + b.get_width() / 2, b.get_height() + 1.2),
                ha="center", fontsize=7)

ax.set_ylim(0, 110)
ax.set_ylabel("Accuracy (%)")
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
ax.set_title("Multiple-choice saturates; open-ended reveals a capability gradient")
ax.legend(loc="lower left", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
out = R.parent / "fig_mcq_vs_open.pdf"
fig.savefig(out)
print(f"wrote {out.name}")
