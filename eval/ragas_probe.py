import ragas, inspect
print("ragas version:", ragas.__version__)
from ragas.metrics import collections as c
print([n for n in dir(c) if n[:1].isupper()])
for name in ["Faithfulness", "AnswerRelevancy", "ContextRelevance"]:
    cls = getattr(c, name, None)
    if cls is None:
        print(name, "-> not found")
        continue
    print("\n", name, "init:", inspect.signature(cls.__init__))
    print(name, "ascore:", inspect.signature(cls.ascore))