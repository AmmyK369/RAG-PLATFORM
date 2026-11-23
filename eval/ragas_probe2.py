import inspect
import ragas.embeddings as e

print([n for n in dir(e) if not n.startswith("_")])
if hasattr(e, "embedding_factory"):
    print(inspect.signature(e.embedding_factory))
    print((inspect.getdoc(e.embedding_factory) or "")[:1500])