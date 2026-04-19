import faiss
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from agent.semantic_layer import get_all_descriptions

INDEX_PATH = "agent/schema_index.faiss"
METADATA_PATH = "agent/schema_metadata.pkl"

model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model

def build_index():
    descriptions = get_all_descriptions()
    texts = [d["description"] for d in descriptions]
    metadata = [d["table"] for d in descriptions]

    embedder = get_model()
    embeddings = embedder.encode(texts, convert_to_numpy=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype(np.float32))

    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print(f"Schema index built with {len(texts)} tables")
    return index, metadata

def load_index():
    if not os.path.exists(INDEX_PATH):
        return build_index()
    index = faiss.read_index(INDEX_PATH)
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def retrieve_relevant_tables(question: str, top_k: int = 3) -> str:
    index, metadata = load_index()
    embedder = get_model()

    query_embedding = embedder.encode([question], convert_to_numpy=True)
    distances, indices = index.search(query_embedding.astype(np.float32), top_k)

    from agent.semantic_layer import get_table_description
    relevant_schema = ""
    retrieved_tables = []

    for idx in indices[0]:
        if idx < len(metadata):
            table_name = metadata[idx]
            retrieved_tables.append(table_name)
            relevant_schema += get_table_description(table_name) + "\n"

    return relevant_schema, retrieved_tables

if __name__ == "__main__":
    build_index()
    print("Index built successfully!")