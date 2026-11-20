import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

load_dotenv()
model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

question = input("Question: ")
qvec = model.encode(question).tolist()
result = client.query_points(collection_name="docs", query=qvec, limit=5)

for p in result.points:
    print(round(p.score, 3), p.payload["file_name"], "|", p.payload["text"][:150].replace("\n", " "))
    
    