import json, os, re

with open("data/squad/dev-v2.0.json", encoding="utf-8") as f:
    squad = json.load(f)

os.makedirs("data/wiki_txt", exist_ok=True)
questions = []

for article in squad["data"]:
    title = article["title"]
    safe = re.sub(r"[^A-Za-z0-9_]+", "_", title)
    paragraphs = [p["context"] for p in article["paragraphs"]]
    with open(f"data/wiki_txt/{safe}.txt", "w", encoding="utf-8") as f:
        f.write(title + "\n\n" + "\n\n".join(paragraphs))
    for p in article["paragraphs"]:
        for qa in p["qas"]:
            questions.append({
                "article": title,
                "question": qa["question"],
                "is_impossible": qa["is_impossible"],
                "gold_answers": [a["text"] for a in qa["answers"]],
            })
            
with open("data/squad_questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

print("Questions saved:", len(questions))            