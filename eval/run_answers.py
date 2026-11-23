import json, os, re, sys, time
sys.path.insert(0, os.getcwd())
from rag import answer

items = json.load(open("eval/eval_set.json", encoding="utf-8"))
REFUSAL = re.compile(r"i don.t know", re.I)

def ask_with_retry(q, role):
    for _ in range(4):
        try:
            return answer(q, role=role, mode="hybrid_rerank")
        except Exception as e:
            print("  retrying after error:", str(e)[:90])
            time.sleep(20)
    raise RuntimeError("giving up on: " + q)

out = []
for n, it in enumerate(items, 1):
    res = ask_with_retry(it["question"], it["role"])
    ans = res["answer"]
    refused = bool(REFUSAL.search(ans))
    correct = None
    if it["type"] == "answerable":
        correct = (not refused) and any(g.lower() in ans.lower() for g in it["gold"])
    out.append({**it, "answer": ans, "refused": refused, "correct": correct,
                "contexts": res["contexts"], "files": [s["file"] for s in res["sources"]]})
    print(n, it["type"], "| refused |" if refused else "| answered |", it["question"][:55])
    time.sleep(8)

json.dump(out, open("eval/answers.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

def pct(rows, key):
    return round(100 * sum(1 for r in rows if r[key]) / max(len(rows), 1), 1)

print("\nAnswerable questions answered correctly (%):", pct([r for r in out if r["type"] == "answerable"], "correct"))
for t in ["unanswerable", "restricted"]:
    print(f"{t} correctly refused (%):", pct([r for r in out if r["type"] == t], "refused")) 