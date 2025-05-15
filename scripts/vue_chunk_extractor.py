import os
import re
import glob
import json
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# ✅ HyperCLOVAX-SEED LLM 로드
model_name = "naver-hyperclovax/HyperCLOVAX-SEED-Text-Instruct-0.5B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.config.pad_token_id = tokenizer.eos_token_id

# ✅ Vue 파일 청크 추출 함수
def extract_chunks_from_vue(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # <template> 추출
    template_match = re.search(r"<template>(.*?)</template>", content, re.DOTALL)
    template = template_match.group(1).strip() if template_match else ""

    # <script> 추출
    script_match = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    script = script_match.group(1).strip() if script_match else ""

    # 클래스명 추출
    class_match = re.search(r"export default class (\w+)", script)
    class_name = class_match.group(1) if class_match else "Unknown"

    # ✅ methods 코드 블록 추출 (이름 + 코드)
    method_blocks = re.findall(
        r"((?:@\w+\(.*?\)\s*)*(?:public\s+|private\s+|protected\s+)?(?:async\s+)?(?:get|set)?\s*(\w+)\s*\([^)]*\)\s*(?::\s*[^\{]+)?\{[\s\S]*?^\s*}\s*)",
        script,
        re.MULTILINE
    )

    method_descriptions = []
    methods = []

    for full_block, method_name in method_blocks:
        methods.append(method_name)
        short_code = '\n'.join(full_block.strip().splitlines()[:10])
        prompt = f"""<|system|>
너는 Vue.js 코드를 요약하는 한국어 전문가야.
<|user|>
다음 Vue 메서드가 어떤 기능을 하는지 한 문장으로 설명해줘.

```ts
{short_code}
```
<|assistant|>"""

        try:
            inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=1024).to(device)
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=128,
                do_sample=False 
            )
            description = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            if "<|assistant|>" in description:
                description = description.split("<|assistant|>")[-1].strip()

            print(description)
            if not description or re.match(r'^[{.\-=\s]+$', description):
                description = "요약 실패"
        except Exception as e:
            description = f"요약 오류: {str(e)}"

        method_descriptions.append(f"- {method_name}(): {description}")

    # props & emits 그대로 유지
    props = re.findall(r"@Prop\(.*?\)\s+(\w+)!:.*?;", script)
    emits = re.findall(r'this\.\$emit\(["\'](.*?)["\']', script)

    method_summary = "\n".join(method_descriptions) if method_descriptions else "없음"

    # ✅ 임베딩용 텍스트 구성 (앞에 요약 먼저)
    summary = f"""
[Method 요약]
{method_summary}

Vue 컴포넌트 이름: {class_name}
파일 경로: {file_path}

[Template HTML]
{template}

[Script Code]
{script}

[Props]: {', '.join(props) if props else '없음'}
[Methods]: {', '.join(methods) if methods else '없음'}
[Emits]: {', '.join(emits) if emits else '없음'}
""".strip()

    return {
        "filePath": file_path,
        "template": template,
        "script": script,
        "className": class_name,
        "methods": methods,
        "properties": list(set(props)),
        "emits": list(set(emits)),
        "embeddingText": summary
    }

# ✅ 전체 디렉토리 대상 추출
def extract_all_vue_chunks(root_dir):
    vue_files = glob.glob(os.path.join(root_dir, "**/*.vue"), recursive=True)
    chunks = []
    for file_path in vue_files:
        try:
            chunk = extract_chunks_from_vue(file_path)
            chunks.append(chunk)
        except Exception as e:
            print(f"⚠️ {file_path} 파싱 실패: {e}")
    return chunks

# ✅ 사용 예시
if __name__ == "__main__":
    repo_dir = "../repo/vue-ts-realworld-app"
    output_file = "vue_chunks.json"

    result = extract_all_vue_chunks(repo_dir)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ 총 {len(result)}개 청크 추출 완료 → {output_file}")
