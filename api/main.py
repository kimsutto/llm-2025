from fastapi import FastAPI, Request
from pydantic import BaseModel
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 모델 & 인덱스 로드
model = SentenceTransformer("BAAI/bge-m3")
index = faiss.read_index("../data/faiss.index")
with open("../data/metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

# FastAPI 객체 생성
app = FastAPI()

# 요청 body 스키마
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

# 검색 요청 처리
# 사용자 쿼리(question)를 POST로 받음
# 쿼리를 임베딩으로 변환 (BGE-m3 모델 재사용)
# FAISS 인덱스에서 top-k 유사한 벡터 검색
# metadata.json을 통해 결과 ID에 해당하는 텍스트 반환

@app.post("/search")
async def search(req: QueryRequest):
    # 1. 임베딩 생성
    query_embedding = model.encode(req.question)
    query_embedding = np.array([query_embedding], dtype="float32")

    # 2. FAISS 검색
    distances, indices = index.search(query_embedding, req.top_k)

    # 3. 결과 구성
    results = []
    for idx, dist in zip(indices[0], distances[0]):
        item = metadata[idx]
        results.append({
            "id": item["id"],
            "text": item["text"],
            "score": float(dist)
        })

    return {"results": results}
