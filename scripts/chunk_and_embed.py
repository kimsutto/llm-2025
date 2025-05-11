import os
import json
from sentence_transformers import SentenceTransformer

# 모델 로드
model = SentenceTransformer("BAAI/bge-m3")

# 기본 설정
CHUNK_SIZE = 500
SUPPORTED_EXT = [".py", ".js", ".ts", ".java", ".md", ".tsx"]  # 원하는 확장자

def read_all_code_files(root_path):
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in SUPPORTED_EXT):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                yield filepath, content

def split_into_chunks(text, chunk_size=CHUNK_SIZE):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def get_embedding(text):
    return model.encode(text).tolist()  # numpy -> list 변환

def chunk_repository(repo_path):
    chunks = []
    for filepath, content in read_all_code_files(repo_path):
        file_chunks = split_into_chunks(content)
        for i, chunk in enumerate(file_chunks):
            chunks.append({
                "id": f"{filepath}::chunk{i}",
                "text": chunk
            })
    return chunks

def generate_embedding_json(repo_path, output_path):
    chunks = chunk_repository(repo_path)
    result = []
    for idx, chunk in enumerate(chunks):
        embedding = get_embedding(chunk["text"])
        result.append({
            "id": chunk["id"],
            "text": chunk["text"],
            "embedding": embedding
        })
        if idx % 10 == 0:
            print(f"{idx+1}/{len(chunks)} 처리 중...")

    # 저장 경로 폴더 없으면 생성
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    generate_embedding_json(
    repo_path="/Users/seonghuiyu/Documents/GitHub/blog-client",
    output_path="/Users/seonghuiyu/Documents/GitHub/llm-2025/data/embeddings.json"
)
