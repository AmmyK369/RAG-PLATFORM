import json, os, random, time
from dotenv import load_dotenv
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import Faithfulness, ContextRelevance

load_dotenv()
JUDGE_MODEL = "openai/gpt-oss-120b"   # confirm the exact ID on Groq's models page
LIMIT = 15                            # start small, raise once you see how fast it runs
PAUSE = 5                             # seconds between questions

client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    timeout=120.0,
    max_retries=4,
)
llm = llm_factory(JUDGE_MODEL, client=client)
faith = Faithfulness(llm=llm)
ctx_rel = ContextRelevance(llm=llm)

rows = json.load(open("eval/answers.json", encoding="utf-8"))
targets = [r for r in rows if r["type"] == "answerable" and not r["refused"]]
random.Random(7).shuffle(targets)
targets = targets[:LIMIT]

def safe(fn, **kw):
    try:
        return float(fn(**kw).value)
    except Exception as e:
        print("   failed:", str(e)[:140])
        return None

results = []
for n, r in enumerate(targets, 1):
    f = safe(faith.score, user_input=r["question"], response=r["answer"],
             retrieved_contexts=r["contexts"])
    c = safe(ctx_rel.score, user_input=r["question"], retrieved_contexts=r["contexts"])
    results.append({"id": r["id"], "faithfulness": f, "context_relevance": c,
                    "correct": r["correct"]})
    print(f"{n}/{len(targets)} {r['id']} faithfulness={f} context_relevance={c}")
    time.sleep(PAUSE)

def mean(key):
    vals = [x[key] for x in results if x[key] is not None]
    return (round(sum(vals) / len(vals), 3), len(vals)) if vals else (None, 0)

print("\nFaithfulness (mean, n):", mean("faithfulness"))
print("Context relevance (mean, n):", mean("context_relevance"))
print("Faithfulness below 1.0:",
      [x["id"] for x in results if x["faithfulness"] is not None and x["faithfulness"] < 1.0])
json.dump(results, open("eval/results_ragas.json", "w"), indent=2)