from fastapi import FastAPI
from fastapi.responses import Response

from pydantic import BaseModel
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# ✅ 모델 & 인덱스 & 메타데이터 로드
# TODO: 모델  로컬, 원격 받게 수정 
# model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")
model = SentenceTransformer("../../multilingual-e5-large-instruct")
index = faiss.read_index("../data/output_faiss/faiss.index")

with open("../data/output_faiss/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)  # ✅ 우리 구조: { file, name, code }

# ✅ FastAPI 객체 생성
app = FastAPI()

# ✅ 요청 스키마
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

# ✅ 검색 API
@app.post("/search")
async def search(req: QueryRequest):
    try:
        # 1. 임베딩 생성 (e5 계열은 query: 접두어 필요)
        query_prompt = f"query: {req.question.strip()}와 관련된 Vue 2 컴포넌트를 찾고 싶습니다."
        query_embedding = model.encode([query_prompt], normalize_embeddings=True)
        query_embedding = np.array(query_embedding, dtype="float32")

        # 2. FAISS 검색
        distances, indices = index.search(query_embedding, req.top_k)

        # 3. 결과 구성
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx >= len(metadata):
                continue
            item = metadata[idx]
            results.append({
                "file": item["file"], #id 
                "name": item["name"], 
                "code": item["code"], #text? 
                "score": float(dist)
            })

        # 4. Markdown 형식의 응답 문자열 구성
        md_lines = [f"# 검색 결과: {req.question}\n"]
        for i, result in enumerate(results, 1):
            md_lines.append(f"### {i}. 🔹 {result['name']} ({result['file']})")
            md_lines.append(f"**Score:** {result['score']:.4f}\n")
            md_lines.append("```ts")
            md_lines.append(result["code"])
            md_lines.append("```\n")

        md_result = "\n".join(md_lines)

        # 5. 응답 반환 (Markdown 문자열을 results 필드로)
        return Response(content=md_result, media_type="text/markdown")

        """
            아래처럼 json 응답으로 받으실거면 ! 
            쓰는 쪽에서 마크다운 파싱하면 됩니다욧 

            md_lines = [f"# 검색 결과: {req.question}\n"]
            for i, result in enumerate(results, 1):
                md_lines.append(f"### {i}. 🔹 {result['name']} ({result['file']})")
                md_lines.append(f"**Score:** {result['score']:.4f}\n")
                md_lines.append("")  # 줄바꿈
                # ✅ 코드 블록은 들여쓰기 4칸으로 처리
                code_block = "\n".join(["    " + line for line in result["code"].splitlines()])
                md_lines.append(code_block)
                md_lines.append("")  # 줄바꿈

            md_result = "\n".join(md_lines)

            return {
                "question": req.question,
                "status": "ok",
                "results": md_result
            }
        """


    except Exception as e:
        # ❗에러 처리
        return {
            "question": req.question,
            "status": "error",
            "message": str(e)
        }
