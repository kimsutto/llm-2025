import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def load_faiss_index(index_path: str, metadata_path: str):
    index = faiss.read_index(index_path)
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)
    return index, metadata

def search_code(
    query: str,
    model,
    index,
    metadata,
    top_k: int = 5
):
    query_prompt = f"query: {query.strip()}"
    query_vector = model.encode([query_prompt], normalize_embeddings=True).astype('float32')
    distances, indices = index.search(query_vector, top_k)

    results = []
    for i, dist in zip(indices[0], distances[0]):
        if i < len(metadata):
            entry = metadata[i]
            results.append({
                "file": entry["file"],
                "name": entry["name"],
                "code": entry["code"],
                "score": float(dist)
            })
    return results

def run_search(
    query: str,
    index_path: str = "../data/output_faiss2/faiss.index",
    metadata_path: str = "../data/output_faiss2/metadata.pkl",
    model_path: str = "../../multilingual-e5-large-instruct",
    # model_path: str = "intfloat/multilingual-e5-large-instruct",
    top_k: int = 5
):
    print("📥 모델 로딩 중...")
    model = SentenceTransformer(model_path)

    print("📂 FAISS + 메타데이터 로딩 중...")
    index, metadata = load_faiss_index(index_path, metadata_path)

    print(f"\n🔍 질의: {query}")
    results = search_code(query, model, index, metadata, top_k)

    print(f"\n📚 관련된 Vue 컴포넌트 검색 결과 (상위 {top_k}개):")
    for i, result in enumerate(results):
        print(f"\n--- [{i+1}] {result['file']} - <{result['name']}> ---")
        print(f"📊 유사도 Score: {result['score']:.4f}")
        print(f"\n{result['code']}\n")

run_search("통신하는 코드 보여줘")
