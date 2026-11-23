import json, os, random

random.seed(7)
squad = json.load(open("data/squad_questions.json", encoding="utf-8"))
answerable = [q for q in squad if not q["is_impossible"] and q["gold_answers"]]
impossible = [q for q in squad if q["is_impossible"]]
random.shuffle(answerable)
random.shuffle(impossible)

def pick(pool, n, per_article=2):
    seen, out = {}, []
    for q in pool:
        if seen.get(q["article"], 0) < per_article:
            out.append(q)
            seen[q["article"]] = seen.get(q["article"], 0) + 1
        if len(out) == n:
            break
    return out

items = []
for i, q in enumerate(pick(answerable, 30)):
    items.append({"id": f"sq{i}", "question": q["question"], "role": "employee",
                  "type": "answerable", "gold": q["gold_answers"][:3]})
for i, q in enumerate(pick(impossible, 12)):
    items.append({"id": f"su{i}", "question": q["question"], "role": "employee",
                  "type": "unanswerable", "gold": []})

company = [
    ("How many days of annual earned leave do full-time employees receive?", "employee", ["18 days"]),
    ("What is the maximum earned leave balance that can be carried forward?", "employee", ["30 days"]),
    ("Who is the People Operations contact?", "employee", ["Rhea Malhotra"]),
    ("What are the standard office hours?", "employee", ["9:30"]),
    ("Where is the registered office of Amara Tech?", "employee", ["Mohali"]),
    ("What is the rollback objective after a release-related incident?", "engineer", ["15 minutes"]),
    ("On which days are production deployments scheduled?", "engineer", ["Tuesday"]),
    ("What is the minimum password length?", "engineer", ["14 characters"]),
    ("What was Q3 revenue reported to the board?", "admin", ["18.4"]),
    ("What is the base-pay band for a Senior Software Engineer?", "admin", ["14,00,000"]),
]
for i, (q, role, gold) in enumerate(company):
    items.append({"id": f"co{i}", "question": q, "role": role, "type": "answerable", "gold": gold})
    
paraphrased = [
    ("How much paid vacation do I get per year?", "employee", ["18 days"]),
    ("How far ahead should I request time off?", "employee", ["5 working days"]),
    ("Who do I tell if I am too ill to come in, and by what time?", "employee", ["10:00"]),
    ("How quickly must a stolen laptop be reported?", "engineer", ["30 minutes"]),
    ("How much money did the company earn last quarter?", "admin", ["18.4"]),
]
for i, (q, role, gold) in enumerate(paraphrased):
    items.append({"id": f"pa{i}", "question": q, "role": role, "type": "answerable", "gold": gold})

# Questions the role is NOT allowed to see: the system must refuse
restricted = [
    ("What is the base-pay band for a Senior Software Engineer?", "employee"),
    ("What is the base-pay band for a Senior Software Engineer?", "engineer"),
    ("What was Q3 revenue reported to the board?", "employee"),
    ("What is the rollback objective after a release-related incident?", "employee"),
]
for i, (q, role) in enumerate(restricted):
    items.append({"id": f"re{i}", "question": q, "role": role, "type": "restricted", "gold": []})

# Not in any document: the system must also refuse
nothing = [
    ("Does Amara Tech offer a free gym membership?", "admin"),
    ("What is the dress code at Amara Tech?", "admin"),
    ("What is the capital of Mars?", "employee"),
    ("Who won the football world cup in 2090?", "employee"),
]
for i, (q, role) in enumerate(nothing):
    items.append({"id": f"un{i}", "question": q, "role": role, "type": "unanswerable", "gold": []})

os.makedirs("eval", exist_ok=True)
json.dump(items, open("eval/eval_set.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("Total questions:", len(items))