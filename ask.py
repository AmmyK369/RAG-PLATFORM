from rag import answer

while True:
    q = input("\nQuestion (or 'quit'): ")
    if q.strip().lower() == "quit":
        break
    out = answer(q)
    print("\nANSWER:", out["answer"])
    print("\nSOURCES:")
    for s in out["sources"]:
        print(f"[{s['n']}] {s['file']}: {s['text'][:100]}...")