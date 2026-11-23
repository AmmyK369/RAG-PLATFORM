import json, os, time
from dotenv import load_dotenv
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import Faithfulness

load_dotenv()
JUDGE_MODEL = "openai/gpt-oss-120b"  # a bigger model than the one that wrote the answers

client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    timeout=120.0,
    max_retries=3,
)
scorer = Faithfulness(llm=llm_factory(JUDGE_MODEL, client=client))

rows = json.load(open("eval/answers.json", encoding="utf-8"))
targets = [r for r in rows if r["type"] == "answerable" and not r["refused"]]

results = []
for n, r in enumerate(targets, 1):
    try:
        res = scorer.score(
            user_input=r["question"],
            response=r["answer"],
            retrieved_contexts=r["contexts"],
        )
        value = float(res.value)
    except Exception as e:
        print(r["id"], "FAILED:", str(e)[:150])
        value = None
    results.append({"id": r["id"], "faithfulness": value, "correct": r["correct"]})
    print(f"{n}/{len(targets)}", r["id"], value)
    time.sleep(4)  # stay under the free rate limit

ok = [x for x in results if x["faithfulness"] is not None]
print("\nScored:", len(ok), "of", len(targets))
print("Mean faithfulness:", round(sum(x["faithfulness"] for x in ok) / len(ok), 3))
print("Answers below 1.0:", [x["id"] for x in ok if x["faithfulness"] < 1.0])

json.dump(results, open("eval/results_faithfulness.json", "w"), indent=2)