"""Successful attacks per seed and workflow for each configuration of the LLM runs
(supplementary table): python analysis/strata_llm.py [results dir] [--latex]."""
import collections, json, os, sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
DIR = args[0] if args else os.path.join(os.path.dirname(__file__), "..", "results", "stage2_llm_combined")
R = [json.loads(l) for l in open(os.path.join(DIR, "rows.jsonl")) if l.strip()]
CF, WF = ["B0", "B1", "B2", "L2", "L3"], ["grid", "ptw", "trade", "p2p"]
h, n = collections.Counter(), collections.Counter()
for r in R:
    if r["kind"] != "benign":
        k = (r["config"], r["seed"], r["wf"])
        n[k] += 1
        h[k] += r["harmful_done"]
seeds = sorted({r["seed"] for r in R})
rows = []
for s in seeds:
    for w in WF + ["all"]:
        ws = WF if w == "all" else [w]
        cells = [f"{sum(h[(c, s, x)] for x in ws)}/{sum(n[(c, s, x)] for x in ws)}" for c in CF]
        rows.append((s, w, cells))
if "--latex" in sys.argv:
    for s, w, cells in rows:
        print(f"{s} & {w} & " + " & ".join(cells) + r" \\")
else:
    print("seed wf    " + " ".join(f"{c:>7}" for c in CF))
    for s, w, cells in rows:
        print(f"{s:4} {w:6} " + " ".join(f"{x:>7}" for x in cells))
