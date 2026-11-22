import time
from rag import retrieve, answer

RESTRICTED = {
    "employee": {"engineering_handbook.txt", "security_policy.txt", "salary_bands.txt", "board_notes.txt"},
    "engineer": {"salary_bands.txt", "board_notes.txt"},
    "admin": set(),
}

QUESTIONS = [
    "What is the salary band for a Senior Software Engineer?",
    "What was Q3 revenue according to the board notes?",
    "What is the rollback objective for production deployments?",
    "How many days of annual earned leave do employees get?",
]

leaks = 0
for q in QUESTIONS:
    print("\nQ:", q)
    for role in ["employee", "engineer", "admin"]:
        files = {c["file_name"] for c in retrieve(q, role=role)}
        leaked = files & RESTRICTED[role]
        leaks += len(leaked)
        status = "LEAK: " + str(leaked) if leaked else "ok"
        print(f"  {role:9} sees: {sorted(files)}  {status}")
        time.sleep(7)  # stay under the free Cohere rate limit

print("\nTotal leaks:", leaks)  # must be 0

for role in ["employee", "admin"]:
    out = answer("What is the salary band for a Senior Software Engineer?", role=role)
    print(f"\n[{role}] {out['answer']}")
    time.sleep(7)