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
ALL_ROLES = ["employee", "engineer", "admin"]


# Who may see each internal document. This mapping is the source of truth.
INTERNAL_ROLES = {
    "hr_leave_policy.txt": ["employee", "engineer", "admin"],
    "office_rules.txt": ["employee", "engineer", "admin"],
    "engineering_handbook.txt": ["engineer", "admin"],
    "security_policy.txt": ["engineer", "admin"],
    "salary_bands.txt": ["admin"],
    "board_notes.txt": ["admin"],
}

# 1. Load both folders
public_docs =SimpleDirectoryReader("data/wiki_txt").load_data()
internal_docs = SimpleDirectoryReader("data/internal").load_data()
internal_names = {d.metadata["file_name"] for d in internal_docs}
print("Public docs:", len(public_docs), "| Internal docs:", len(internal_docs))


# 2. Chunk (200 tokens, 40 overlap)
splitter = SentenceSplitter(chunk_size=200, chunk_overlap=40)
nodes=splitter.get_nodes_from_documents(public_docs + internal_docs)
print("Chunks:", len(nodes))

# 3.embedding chunk into a vector
model=SentenceTransformer("all-MiniLM-L6-v2")
texts=[n.get_content() for n in nodes]
vectors=model.encode(texts,show_progress_bar=True)

# 4. Decide who may see each chunk
def roles_for(file_name):
    if file_name in INTERNAL_ROLES:
        return INTERNAL_ROLES[file_name]
    if file_name in internal_names:
        print("WARNING: no roles set for", file_name, "- hiding it from everyone")
        return []                      # default deny
    return ALL_ROLES                   # public Wikipedia text

# 5. store in Qdrant
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
    file_name = node.metadata.get("file_name","unknown")
    points.append(PointStruct(
        id=i,
        vector=vec.tolist(),
        payload={
            "text": node.get_content(),
            "file_name": file_name,
            "page": node.metadata.get("page_label"),
            "source":"internal" if file_name in internal_names else "wikipedia",
            "allowed_roles": roles_for(file_name),
        },
    ))
    
for start in range (0,len(points),100):
     client.upsert(collection_name=COLLECTION, points=points[start:start + 100])

admin_only = sum(1 for p in points if p.payload["allowed_roles"] == ["admin"])
print("Stored", len(points), "chunks | admin-only chunks:", admin_only)    
