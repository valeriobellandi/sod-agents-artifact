"""A5 with LLM agents (long-horizon pairing): python analysis/analyze_a5.py [results dir].

Prints the figures reported in the paper: harmful requests executed per configuration, the
paired comparison of L2 and L3 on the same work orders (exact McNemar), the use of the check
tool by the fixed checker as joint reviews accumulate, the comparison before and after the
first rotation, and how often the replacement checker used the check tool.
"""
import json, math, os, sys

DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "results", "a5_llm_local_v2")
R = [json.loads(l) for l in open(os.path.join(DIR, "a5_rows.jsonl")) if l.strip()]
I = {(r["config"], r["seed"], r["episode"]): r for r in R}
seeds = sorted({r["seed"] for r in R})


def mcnemar(x, y):
    n = x + y
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(x, y) + 1)) / 2 ** n) if n else 1.0


for c in ("L2", "L3"):
    pr = [r for r in R if r["config"] == c and r["pressure"]]
    h = sum(r["harmful_done"] for r in pr)
    print(f"{c}: proposer chose harmful {sum(r['chose_harmful'] for r in pr)}/{len(pr)}; "
          f"harmful executed {h}/{len(pr)} ({100 * h / len(pr):.1f}%)")

ks = [(s, e) for (c, s, e), r in I.items() if c == "L2" and r["pressure"]]
x = sum(1 for k in ks if I[("L2",) + k]["harmful_done"] and not I[("L3",) + k]["harmful_done"])
y = sum(1 for k in ks if not I[("L2",) + k]["harmful_done"] and I[("L3",) + k]["harmful_done"])
print(f"paired L2 vs L3: {x} vs {y} discordant episodes, exact McNemar p = {mcnemar(x, y):.3f}")

print("fixed checker (L2): check-tool use by number of joint reviews")
for lo, hi in ((1, 5), (6, 10), (11, 20), (21, 30)):
    g = [r for r in R if r["config"] == "L2" and r["checker"] and r["checker"].endswith("chk1")
         and lo <= r["pairings_with_C"] <= hi]
    if g:
        print(f"  reviews {lo:2d}-{hi:2d}: {100 * sum(r['used_check_tool'] for r in g) / len(g):.0f}% of {len(g)}")

rot = {s: next(r["episode"] for r in R if r["config"] == "L3" and r["seed"] == s and r["checker"]
               and not r["checker"].endswith("chk1")) for s in seeds}
for phase, keep in (("before first rotation", lambda r: r["episode"] < rot[r["seed"]]),
                    ("from first rotation", lambda r: r["episode"] >= rot[r["seed"]])):
    parts = []
    for c in ("L2", "L3"):
        g = [r for r in R if r["config"] == c and r["pressure"] and keep(r)]
        parts.append(f"{c} {sum(r['harmful_done'] for r in g)}/{len(g)} harmful, "
                     f"{sum(r['status'] == 'open' for r in g)} undecided")
    print(f"{phase}: " + "; ".join(parts))

rep = [r for r in R if r["config"] == "L3" and r["checker"] and not r["checker"].endswith("chk1")]
print(f"replacement checkers (L3): check tool used in {sum(r['used_check_tool'] for r in rep)} of {len(rep)} reviews")
