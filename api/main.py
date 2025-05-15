from fastapi import FastAPI
from fastapi.responses import Response

from pydantic import BaseModel
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# ✅ 모델 & 인덱스 & 메타데이터 로드
# TODO: 모델  로컬, 원격 받게 수정 
# model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")
model = SentenceTransformer("../../multilingual-e5-large-instruct")
index = faiss.read_index("../data/output_faiss/faiss.index")
tokenizer = AutoTokenizer.from_pretrained("../../codet5-base")
generator = AutoModelForSeq2SeqLM.from_pretrained("../../codet5-base")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
generator.to(device)

with open("../data/output_faiss/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)  # ✅ 우리 구조: { file, name, code }

# ✅ FastAPI 객체 생성
app = FastAPI()

# ✅ 요청 스키마
class RAGRequest(BaseModel):
    question: str
    top_k: int = 5

# ✅ LLM 응답 생성
def generate_answer_with_codet5(question: str, context_chunks: list[str]) -> str:
    context = "\n\n".join([f"// {i+1}번 코드\n{chunk}" for i, chunk in enumerate(context_chunks)])
    prompt = f"""질문: {question}

아래는 우리 프로젝트 내부 코드입니다. 이 코드들을 참고해서 질문에 답해주세요:

{context}

답변:"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
    outputs = generator.generate(
        inputs["input_ids"],
        max_new_tokens=256,
        num_beams=4,
        early_stopping=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# ✅ 검색 API
@app.post("/search")
async def search(req: RAGRequest):
    try:
        # 1. 임베딩 생성 (e5 계열은 query: 접두어 필요)
        query_prompt = f"query: {req.question.strip()}와 관련된 Vue 2 컴포넌트를 찾고 싶습니다."
        query_embedding = model.encode([query_prompt], normalize_embeddings=True)
        query_embedding = np.array(query_embedding, dtype="float32")

        # 2. FAISS 검색
        distances, indices = index.search(query_embedding, req.top_k)

        # 3. 결과 구성 (LLM 응답 생성)
        chunks = []
        references = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx >= len(metadata):
                continue
            entry = metadata[idx]
            chunks.append(entry["code"])
            references.append({
                "file": entry["file"],
                "name": entry["name"],
                "score": float(dist),
                "code": entry["code"]
            })
        answer = generate_answer_with_codet5(req.question, chunks)


        # 4. Markdown 형식의 응답 문자열 구성
        md_lines = [f"# 질문: {req.question}\n", "## 🤖 LLM 응답", answer, "\n## 🔍 참고 코드 (Top {})\n".format(len(references))]

        for i, ref in enumerate(references, 1):
            md_lines.append(f"### {i}. 🔹 {ref['name']} ({ref['file']})")
            md_lines.append(f"**Score:** {ref['score']:.4f}")
            md_lines.append("```ts")
            md_lines.append(ref["code"])
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
