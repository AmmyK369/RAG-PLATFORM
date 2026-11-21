import os,re
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
from rank_bm25 import BM25Okapi
import cohere
from groq import Groq

load_dotenv()
COLLECTION = "docs"
GROQ_MODEL = "openai/gpt-oss-20b"
COHERE_MODEL = "rerank-v5.0-fast"
embedder = SentenceTransformer("all-MiniLM-L6-v2")
qdrant = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
cohere_client = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

def tokenize(text):
    return re.findall(r"\w+", text.lower())

def load_all_chunks():
    chunks, offset = [], None
    while True:
        points, offset = qdrant.scroll(
            collection_name=COLLECTION, limit=200, offset=offset,
            with_payload=True, with_vectors=False,
        )
        for p in points:
            chunks.append({"id": p.id, **p.payload})
        if offset is None:
            break
    return chunks

ALL_CHUNKS = load_all_chunks()
CHUNK_BY_ID = {c["id"]: c for c in ALL_CHUNKS}
BM25 = BM25Okapi([tokenize(c["text"]) for c in ALL_CHUNKS])

def vector_search(question, role, k=20):
    vec = embedder.encode(question).tolist()
    role_filter = models.Filter(must=[
        models.FieldCondition(key="allowed_roles", match=models.MatchValue(value=role))
    ])
    res = qdrant.query_points(
        collection_name=COLLECTION, query=vec, query_filter=role_filter, limit=k
    )
    return [p.id for p in res.points]

def keyword_search(question, role, k=20):
    scores = BM25.get_scores(tokenize(question))
    ranked = sorted(range(len(ALL_CHUNKS)), key=lambda i: scores[i], reverse=True)
    ids = []
    for i in ranked:
        chunk = ALL_CHUNKS[i]
        if role in chunk["allowed_roles"]:
            ids.append(chunk["id"])
        if len(ids) == k:
            break
    return ids

def fuse(list_a, list_b, k=60):
    scores = {}
    for ranking in (list_a, list_b):
        for rank, cid in enumerate(ranking):
            scores[cid] = scores.get(cid, 0) + 1 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)

def rerank(question, ids, top_n=5):
    docs = [CHUNK_BY_ID[i]["text"] for i in ids]
    try:
        result = cohere_client.rerank(
            model=COHERE_MODEL, query=question, documents=docs, top_n=top_n
        )
        return [ids[r.index] for r in result.results]
    except Exception as e:
        print("Rerank failed, using fused order instead:", e)
        return ids[:top_n]
    
def retrieve(question, role="employee", mode="hybrid_rerank", top_n=5):
    vec_ids = vector_search(question, role)
    if mode == "vector":
        ids = vec_ids[:top_n]
    else:
        fused = fuse(vec_ids, keyword_search(question, role))
        ids = rerank(question, fused[:20], top_n) if mode == "hybrid_rerank" else fused[:top_n]
    return [CHUNK_BY_ID[i] for i in ids]

SYSTEM = """You answer questions using ONLY the numbered context passages provided.
Rules:
- After each claim, cite the passage you used, like [1] or [2].
- If the passages do not contain the answer, reply exactly: I don't know based on the available documents.
- Never use outside knowledge."""


def answer(question, role="employee", mode="hybrid_rerank"):
    chunks = retrieve(question, role, mode)
    context = "\n\n".join(
        f"[{i+1}] (source: {c['file_name']})\n{c['text']}" for i, c in enumerate(chunks)
    )
    resp = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0,
    )
    return {
        "answer": resp.choices[0].message.content,
        "sources": [
            {"n": i + 1, "file": c["file_name"], "text": c["text"][:200]}
            for i, c in enumerate(chunks)
        ],
    }