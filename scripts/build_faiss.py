# embeddings.json → 벡터와 ID를 꺼내서 
# FAISS 인덱스에 추가하고 .index 파일로 저장

import json
import numpy as np
import faiss
import os

def load_embeddings(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = [item["text"] for item in data]
    ids = [item["id"] for item in data]
    vectors = np.array([item["embedding"] for item in data], dtype="float32")
    return ids, texts, vectors

def save_index(index, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    faiss.write_index(index, output_path)

def save_metadata(ids, texts, output_path):
    metadata = [{"id": id_, "text": text} for id_, text in zip(ids, texts)]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    ids, texts, vectors = load_embeddings("../data/embeddings.json")

    # FAISS index 생성
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    # 저장
    save_index(index, "../data/faiss.index")
    save_metadata(ids, texts, "../data/metadata.json")

    print(f"✅ 인덱스 및 메타데이터 저장 완료. 총 벡터 수: {len(ids)}")
