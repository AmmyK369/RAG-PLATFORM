from rag import answer

role = input("Role (employee/engineer/admin): ").strip()
while True:
    q = input("\nQuestion (or 'quit'): ")
    if q.strip().lower() == "quit":
        break
    out = answer(q, role=role)
    print("\nANSWER:", out["answer"])
    for s in out["sources"]:
        print(f"[{s['n']}] {s['file']}")