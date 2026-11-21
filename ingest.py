import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.models import PayloadSchemaType

load_dotenv()

COLLECTION = "docs"

docs =SimpleDirectoryReader("data/wiki_txt").load_data()
print("Documents loaded:", len(docs))

# chunking
splitter = SentenceSplitter(chunk_size=200, chunk_overlap=40)
nodes=splitter.get_nodes_from_documents(docs)
print("Chunks:", len(nodes))

# embedding chunk into a vector
model=SentenceTransformer("all-MiniLM-L6-v2")
texts=[n.get_content() for n in nodes]
vectors=model.encode(texts,show_progress_bar=True)

# store in Qdrant
client=QdrantClient(url=os.getenv("QDRANT_URL"),
                    api_key=os.getenv("QDRANT_API_KEY"))
if client.collection_exists(COLLECTION):
    client.delete_collection(COLLECTION)
    
client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    
)

client.create_payload_index(
    collection_name=COLLECTION,
    field_name="allowed_roles",
    field_schema=PayloadSchemaType.KEYWORD,
)

points =[]

for i ,(node,vec) in enumerate(zip(nodes, vectors)):
    points.append(PointStruct(
        id=i,
        vector=vec.tolist(),
        payload={
            "text": node.get_content(),
            "file_name": node.metadata.get("file_name", "unknown"),
            "page": node.metadata.get("page_label"),
            "allowed_roles": ["employee", "engineer", "admin"],
        },
    ))
    
for start in range (0,len(points),100):
     client.upsert(collection_name=COLLECTION, points=points[start:start + 100])
     
print("Stored", len(points), "chunks in Qdrant")