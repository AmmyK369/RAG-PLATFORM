import json, os, sys, time
sys.path.insert(0, os.getcwd())
from rag import retrieve

items = json.load(open("eval/eval_set.json", encoding="utf-8"))
answerable = [i for i in items if i["type"] == "answerable"]
MODES = ["vector", "hybrid", "hybrid_rerank"]

def first_rank(chunks, gold):
    for pos, c in enumerate(chunks, 1):
        text = c["text"].lower()
        if any(g.lower() in text for g in gold):
            return pos
    return None

ranks = {m: {} for m in MODES}
for it in answerable:
    for mode in MODES:
        ranks[mode][it["id"]] = first_rank(retrieve(it["question"], role=it["role"], mode=mode), it["gold"])
        if mode == "hybrid_rerank":
            time.sleep(7)  # stay under the free Cohere limit
    print(it["id"], {m: ranks[m][it["id"]] for m in MODES})

def summarize(mode, prefix=""):
    rs = [r for i, r in ranks[mode].items() if i.startswith(prefix)]
    n = len(rs)
    return (sum(1 for r in rs if r == 1) / n,
            sum(1 for r in rs if r) / n,
            sum(1 / r for r in rs if r) / n)

print("\nmode            hit@1  hit@5   MRR")
for m in MODES:
    h1, h5, mrr = summarize(m)
    print(f"{m:14} {h1:6.0%} {h5:6.0%} {mrr:6.2f}")

print("\nhit@5 by question group")
for m in MODES:
    parts = [f"{name} {summarize(m, p)[1]:.0%}"
             for name, p in [("wikipedia", "sq"), ("company", "co"), ("paraphrased", "pa")]]
    print(f"{m:14}", " | ".join(parts))

json.dump(ranks, open("eval/results_ranking.json", "w"), indent=2)