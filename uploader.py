# add a new document pipeline

import os
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from qdrant_client.models import PointStruct
import rag

def ingest_file(path, roles):
    docs = SimpleDirectoryReader(input_files=[path]).load_data()
    splitter = SentenceSplitter(chunk_size=200, chunk_overlap=40)
    nodes = splitter.get_nodes_from_documents(docs)
    texts = [n.get_content() for n in nodes]
    vectors = rag.embedder.encode(texts)

    start = max(rag.CHUNK_BY_ID) + 1
    points = []
    for i, (node, vec) in enumerate(zip(nodes, vectors)):
        points.append(PointStruct(
            id=start + i,
            vector=vec.tolist(),
            payload={
                "text": node.get_content(),
                "file_name": node.metadata.get("file_name", os.path.basename(path)),
                "page": node.metadata.get("page_label"),
                "source": "uploaded",
                "allowed_roles": roles,
            },
        ))
    rag.qdrant.upsert(collection_name=rag.COLLECTION, points=points)
    rag.reload_index()   # so BM25 can find the new text immediately
    return len(points)

