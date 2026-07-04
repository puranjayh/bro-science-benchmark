"""McNemar p-value heatmap (Fig 2). pip install matplotlib numpy; python3 scripts/fig2_mcnemar.py"""
import json, matplotlib, pathlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
D=json.load(open(pathlib.Path(__file__).parent.parent/"results"/"figdata.json"))
M=[m.replace("Claude ","") for m in D["models"]]; mat=np.array(D["mcnemar"])
fig,ax=plt.subplots(figsize=(6.5,5.5)); im=ax.imshow(mat,cmap="RdYlGn_r",vmin=0,vmax=0.2)
ax.set_xticks(range(len(M)));ax.set_yticks(range(len(M)));ax.set_xticklabels(M,rotation=45,ha="right",fontsize=8);ax.set_yticklabels(M,fontsize=8)
for i in range(len(M)):
 for j in range(len(M)): ax.text(j,i,f"{mat[i][j]:.2f}",ha="center",va="center",fontsize=7)
ax.set_title("Pairwise McNemar p (myth-adherence); green=indistinguishable",fontsize=9)
fig.colorbar(im,label="p-value");fig.tight_layout();fig.savefig(pathlib.Path(__file__).parent.parent/"fig2_mcnemar.png",dpi=150);print("wrote fig2_mcnemar.png")
