import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

# 1. 청크 로딩
def load_chunks(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        chunks_data = json.load(f)
    return chunks_data

# 2. 임베딩 생성
def embed_chunks(model, metadata: list[dict]) -> np.ndarray:
    prompts = [
        f"passage: 이 코드는 vue의 {entry['name']} 컴포넌트 또는 함수이며, 다음과 같은 내용을 포함할 수 있습니다:\n{entry['code']}"
        for entry in metadata
    ]   

    embeddings = model.encode(prompts, normalize_embeddings=True)
    return np.array(embeddings).astype('float32')

# 3. FAISS + 메타데이터 저장
def save_faiss_index(vectors: np.ndarray, metadata: list[dict], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    faiss.write_index(index, os.path.join(output_dir, 'faiss.index'))

    with open(os.path.join(output_dir, 'metadata.pkl'), 'wb') as f:
        pickle.dump(metadata, f)

# 4. 전체 실행
def run_pipeline(json_path: str, output_dir: str):
    print("📦 청크 로딩 중...")
    chunks_data = load_chunks(json_path)

    # chunks = [entry["code"] for entry in chunks_data]
    metadata = [
        {
            "file": entry["filePath"],
            "name": entry.get("name", "unknown"),
            "code": entry["code"]
        }
        for entry in chunks_data
    ]

    print(f"🧠 청크 수: {len(metadata)}")

    print("📥 모델 로딩 중...")
    # model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")
    model = SentenceTransformer("../../multilingual-e5-large-instruct")


    print("🔢 임베딩 중...")
    vectors = embed_chunks(model, metadata)


    print("💾 FAISS 저장 중...")
    save_faiss_index(vectors, metadata, output_dir)

    print("✅ 저장 완료 →", output_dir)


run_pipeline("../data/vue_chunks_annotated.json", "../data/output_faiss")
