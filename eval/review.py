import json

rows = json.load(open("eval/answers.json", encoding="utf-8"))

def show(title, subset):
    print("\n" + "=" * 70 + "\n" + title + f" ({len(subset)})")
    for r in subset:
        print(f"\n[{r['id']}] Q: {r['question']}")
        if r["gold"]:
            print("   GOLD:", r["gold"])
        print("   ANSWER:", r["answer"].replace("\n", " ")[:300])
        print("   FILES:", sorted(set(r["files"])))

show("ANSWERABLE but marked incorrect",
     [r for r in rows if r["type"] == "answerable" and not r["correct"]])
show("UNANSWERABLE but the system answered",
     [r for r in rows if r["type"] == "unanswerable" and not r["refused"]])